//! Compiled license-verification core for Rhetoric.
//!
//! `the_oracle.licensing.tokens.verify_token` delegates to [`verify_serial`]
//! when this extension is built and importable; the pure-Python implementation
//! remains the reference and the development fallback. Delegation order,
//! payload canonicalisation and every user-visible detail string are pinned by
//! the Python suite (tests/test_licensing_tokens.py, tests/test_licensing_keys.py)
//! and mirrored here byte for byte.
//!
//! Threat model (docs/LICENSING_DESIGN.md §10): this raises the cost of patching
//! a verdict by moving the decision out of readable Python source. It is not a
//! security boundary — whoever can edit the install can edit the binary too.
//! What it buys is that a bypass is neither a one-line edit nor obvious, and
//! that every release rebuilds the code a patch has to find.
//!
//! Trust anchors are compiled in. A release build accepts no caller-supplied
//! key table at all; only the `test-keys` feature (development builds) mirrors
//! the Python registry so the suite can inject its published RFC 8032 test key.

use std::collections::BTreeMap;

use base64::engine::general_purpose::{STANDARD, URL_SAFE};
use base64::Engine;
use ed25519_dalek::{Signature, VerifyingKey};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use serde_json::{Map, Value};

pub const TOKEN_PREFIX: &str = "ORACLE1";

const KNOWN_PAYLOAD_KEYS: [&str; 7] = [
    "v",
    "key_id",
    "lic_id",
    "licensee",
    "machine_hash",
    "iat",
    "exp",
];

/// v1 tokens additionally carried an edition; recognised only so a genuine old
/// token is reported as `reissue_required` instead of `malformed`.
const LEGACY_EXTRA_KEY: &str = "edition";

const DETAIL_MALFORMED: &str =
    "The serial number is malformed. Re-enter it exactly as issued.";
const DETAIL_BAD_PAYLOAD: &str =
    "The serial number payload is malformed. Re-enter it exactly as issued.";
const DETAIL_REISSUE: &str =
    "This serial number uses an old format and no longer activates. Contact support for a reissued serial number.";
const DETAIL_UNKNOWN_KEY: &str =
    "The serial number was issued under a key this install does not know. Upgrade the suite, or contact support with the serial number.";
const DETAIL_BAD_SIGNATURE: &str =
    "The serial number is not a genuine Rhetoric license. Check for truncation; if it matches what you received, contact support.";
const DETAIL_EXPIRED: &str =
    "This license has expired. Contact support to renew — verification never requires a network connection.";
const DETAIL_MACHINE: &str =
    "This license is locked to a different machine. Contact support to have it re-issued.";

struct KeyEntry {
    key_id: &'static str,
    public_key: [u8; 32],
}

/// Production verify keys, oldest first. ``k2`` was registered 2026-10-19; its
/// signing seed lives only in the owner's secret manager. A retired key stays
/// here until every serial minted under it has been reissued.
const PRODUCTION_KEYS: &[KeyEntry] = &[KeyEntry {
    key_id: "k2",
    public_key: [
        0xcf, 0xb1, 0x5a, 0x80, 0x29, 0xad, 0x74, 0xa9, 0x9a, 0xe3, 0xf5, 0x2e, 0xad, 0xdd,
        0x92, 0xa0, 0x11, 0xf3, 0x87, 0x86, 0xba, 0x6d, 0xe1, 0x9f, 0x38, 0xde, 0x0b, 0x88,
        0xee, 0xde, 0x0a, 0x88,
    ],
}];

/// RFC 8032 §7.1 TEST 1 public key — a *published* vector, so this table is
/// compiled in only for development builds (`--features test-keys`) and can
/// never make a shipped install trust a forgeable key.
#[cfg(feature = "test-keys")]
const TEST_KEYS: &[KeyEntry] = &[KeyEntry {
    key_id: "ktest",
    public_key: [
        0xd7, 0x5a, 0x98, 0x01, 0x82, 0xb1, 0x0a, 0xb7, 0xd5, 0x4b, 0xfe, 0xd3, 0xc9, 0x64,
        0x07, 0x3a, 0x0e, 0xe1, 0x72, 0xf3, 0xda, 0xa6, 0x23, 0x25, 0xaf, 0x02, 0x1a, 0x68,
        0xf7, 0x07, 0x51, 0x1a,
    ],
}];

struct Payload {
    key_id: String,
    lic_id: String,
    licensee: String,
    machine_hash: String,
    iat: i64,
    exp: Option<i64>,
}

enum Verdict {
    Malformed,
    BadPayload,
    Reissue,
    UnknownKey,
    BadSignature,
    Expired(Payload),
    MachineMismatch(Payload),
    Valid(Payload),
}

/// Split a token into its payload map and signature bytes; `None` mirrors the
/// Python `parse()` returning None (malformed envelope).
fn split_token(token: &str) -> Option<(Map<String, Value>, Vec<u8>)> {
    let parts: Vec<&str> = token.trim().split('.').collect();
    if parts.len() != 3 || parts[0] != TOKEN_PREFIX {
        return None;
    }
    let body = decode_b64url(parts[1])?;
    let signature = decode_b64url(parts[2])?;
    let text = std::str::from_utf8(&body).ok()?;
    let parsed: Value = serde_json::from_str(text).ok()?;
    match parsed {
        Value::Object(map) => Some((map, signature)),
        _ => None,
    }
}

/// Lenient base64url decode, matching Python's `b64decode(..., altchars=b"-_")`:
/// whitespace is ignored, padding is optional, and the standard alphabet is
/// accepted as a fallback.
fn decode_b64url(text: &str) -> Option<Vec<u8>> {
    let stripped: String = text.chars().filter(|c| !c.is_ascii_whitespace()).collect();
    let body = stripped.trim_end_matches('=');
    let mut padded = String::with_capacity(body.len() + 3);
    padded.push_str(body);
    let remainder = body.len() % 4;
    if remainder == 1 {
        return None;
    }
    if remainder != 0 {
        padded.push_str(&"=".repeat(4 - remainder));
    }
    URL_SAFE
        .decode(&padded)
        .or_else(|_| STANDARD.decode(&padded))
        .ok()
}

fn is_known_shape(map: &Map<String, Value>, legacy: bool) -> bool {
    let expected = if legacy { 8 } else { 7 };
    if map.len() != expected {
        return false;
    }
    map.keys().all(|key| {
        KNOWN_PAYLOAD_KEYS.contains(&key.as_str())
            || (legacy && key == LEGACY_EXTRA_KEY)
    })
}

/// Canonical JSON: sorted keys, compact separators, UTF-8 — the exact bytes the
/// Ed25519 signature covers. serde_json's default object is a BTreeMap, but the
/// rebuild is explicit so a future `preserve_order` feature cannot silently
/// change the signed bytes.
fn canonical_bytes(map: &Map<String, Value>) -> String {
    let sorted: BTreeMap<&str, &Value> = map.iter().map(|(k, v)| (k.as_str(), v)).collect();
    serde_json::to_string(&sorted).expect("string map serialises")
}

fn verify_signature(public_key: &[u8; 32], message: &[u8], signature: &[u8]) -> bool {
    let Ok(signature) = Signature::from_slice(signature) else {
        return false;
    };
    let Ok(key) = VerifyingKey::from_bytes(public_key) else {
        return false;
    };
    // `verify_strict` rejects small-order and non-canonical encodings, which is
    // the same standard the vendored Python verifier applies.
    key.verify_strict(message, &signature).is_ok()
}

fn embedded_key(key_id: &str) -> Option<[u8; 32]> {
    #[cfg(feature = "test-keys")]
    let tables: [&[KeyEntry]; 2] = [PRODUCTION_KEYS, TEST_KEYS];
    #[cfg(not(feature = "test-keys"))]
    let tables: [&[KeyEntry]; 1] = [PRODUCTION_KEYS];

    tables
        .iter()
        .flat_map(|table| table.iter())
        .find(|entry| entry.key_id == key_id)
        .map(|entry| entry.public_key)
}

#[cfg(feature = "test-keys")]
fn table_key(table: &Bound<'_, PyDict>, key_id: &str) -> Option<[u8; 32]> {
    for (key, value) in table.iter() {
        let Ok(name) = key.extract::<String>() else {
            continue;
        };
        if name != key_id {
            continue;
        }
        let Ok(bytes) = value.extract::<Vec<u8>>() else {
            return None;
        };
        return bytes.try_into().ok();
    }
    None
}

/// Resolve `key_id` to a 32-byte public key. Release builds only ever consult
/// the compiled-in registry; development builds mirror the caller's table when
/// one is supplied (the suite's injected test registry).
fn resolve_key(key_id: &str, table: Option<&Bound<'_, PyDict>>) -> Option<[u8; 32]> {
    #[cfg(feature = "test-keys")]
    if let Some(table) = table {
        return table_key(table, key_id);
    }
    #[cfg(not(feature = "test-keys"))]
    let _ = table;
    embedded_key(key_id)
}

fn python_str(value: &Value) -> Option<String> {
    match value {
        Value::String(text) => Some(text.clone()),
        Value::Number(number) => Some(number.to_string()),
        Value::Bool(true) => Some("True".to_string()),
        Value::Bool(false) => Some("False".to_string()),
        Value::Null => Some("None".to_string()),
        Value::Array(_) | Value::Object(_) => None,
    }
}

fn python_int(value: &Value) -> Option<i64> {
    match value {
        Value::Number(number) => number
            .as_i64()
            .or_else(|| number.as_u64().and_then(|n| i64::try_from(n).ok()))
            .or_else(|| number.as_f64().map(|f| f.trunc() as i64)),
        Value::Bool(flag) => Some(i64::from(*flag)),
        Value::String(text) => text.trim().parse::<i64>().ok(),
        _ => None,
    }
}

fn falsy(value: Option<&Value>) -> bool {
    match value {
        None | Some(Value::Null) => true,
        Some(Value::Bool(flag)) => !flag,
        Some(Value::Number(number)) => number.as_f64() == Some(0.0),
        Some(Value::String(text)) => text.is_empty(),
        Some(Value::Array(items)) => items.is_empty(),
        Some(Value::Object(map)) => map.is_empty(),
    }
}

fn coerce_payload(map: &Map<String, Value>, key_id: &str) -> Option<Payload> {
    let lic_id = python_str(map.get("lic_id")?)?;
    let licensee = if falsy(map.get("licensee")) {
        String::new()
    } else {
        python_str(map.get("licensee")?)?
    };
    let machine_hash = if falsy(map.get("machine_hash")) {
        String::new()
    } else {
        python_str(map.get("machine_hash")?)?
    };
    let iat = python_int(map.get("iat")?)?;
    let exp = match map.get("exp") {
        None | Some(Value::Null) => None,
        Some(value) => Some(python_int(value)?),
    };
    Some(Payload {
        key_id: key_id.to_string(),
        lic_id,
        licensee,
        machine_hash,
        iat,
        exp,
    })
}

fn verify(token: &str, machine_hash: &str, now: f64, table: Option<&Bound<'_, PyDict>>) -> Verdict {
    let Some((map, signature)) = split_token(token) else {
        return Verdict::Malformed;
    };
    let legacy = map.get("v").and_then(|v| v.as_i64()) == Some(1) && is_known_shape(&map, true);
    if legacy {
        return Verdict::Reissue;
    }
    if map.get("v").and_then(|v| v.as_i64()) != Some(2) || !is_known_shape(&map, false) {
        return Verdict::Malformed;
    }

    let Some(key_id) = map.get("key_id").and_then(|v| v.as_str()) else {
        return Verdict::UnknownKey;
    };
    let Some(public_key) = resolve_key(key_id, table) else {
        return Verdict::UnknownKey;
    };

    let body = canonical_bytes(&map);
    if !verify_signature(&public_key, body.as_bytes(), &signature) {
        return Verdict::BadSignature;
    }

    let Some(payload) = coerce_payload(&map, key_id) else {
        return Verdict::BadPayload;
    };
    if payload.exp.is_some_and(|exp| now >= exp as f64) {
        return Verdict::Expired(payload);
    }
    if !payload.machine_hash.is_empty()
        && !machine_hash.is_empty()
        && payload.machine_hash != machine_hash
    {
        return Verdict::MachineMismatch(payload);
    }
    Verdict::Valid(payload)
}

/// Verify a serial number. Returns a plain dict shaped like the Python
/// `LicenseStatus` fields, omitting the license attributes a failure branch does
/// not set. `now` is always supplied by the caller (the module owns no clock),
/// keeping verification a pure function of its inputs.
#[pyfunction]
#[pyo3(signature = (token, machine_hash, now, trusted_keys=None))]
fn verify_serial(
    py: Python<'_>,
    token: &str,
    machine_hash: &str,
    now: f64,
    trusted_keys: Option<&Bound<'_, PyDict>>,
) -> PyResult<Py<PyAny>> {
    let result = PyDict::new(py);
    match verify(token, machine_hash, now, trusted_keys) {
        Verdict::Malformed => {
            result.set_item("ok", false)?;
            result.set_item("state", "malformed")?;
            result.set_item("detail", DETAIL_MALFORMED)?;
        }
        Verdict::BadPayload => {
            result.set_item("ok", false)?;
            result.set_item("state", "malformed")?;
            result.set_item("detail", DETAIL_BAD_PAYLOAD)?;
        }
        Verdict::Reissue => {
            result.set_item("ok", false)?;
            result.set_item("state", "reissue_required")?;
            result.set_item("detail", DETAIL_REISSUE)?;
        }
        Verdict::UnknownKey => {
            result.set_item("ok", false)?;
            result.set_item("state", "unknown_key")?;
            result.set_item("detail", DETAIL_UNKNOWN_KEY)?;
        }
        Verdict::BadSignature => {
            result.set_item("ok", false)?;
            result.set_item("state", "bad_signature")?;
            result.set_item("detail", DETAIL_BAD_SIGNATURE)?;
        }
        Verdict::Expired(payload) => {
            set_failure_with_license(&result, "expired", &payload, DETAIL_EXPIRED)?;
        }
        Verdict::MachineMismatch(payload) => {
            set_failure_with_license(&result, "machine_mismatch", &payload, DETAIL_MACHINE)?;
        }
        Verdict::Valid(payload) => {
            result.set_item("ok", true)?;
            result.set_item("state", "valid")?;
            result.set_item("licensee", payload.licensee.clone())?;
            result.set_item("lic_id", payload.lic_id.clone())?;
            result.set_item("key_id", payload.key_id.clone())?;
            match payload.exp {
                Some(exp) => result.set_item("exp", exp)?,
                None => result.set_item("exp", py.None())?,
            }
            result.set_item("machine_locked", !payload.machine_hash.is_empty())?;
            result.set_item("detail", "")?;
            result.set_item("payload", payload_dict(py, &payload)?)?;
        }
    }
    Ok(result.into_any().unbind())
}

fn set_failure_with_license(
    result: &Bound<'_, PyDict>,
    state: &str,
    payload: &Payload,
    detail: &str,
) -> PyResult<()> {
    result.set_item("ok", false)?;
    result.set_item("state", state)?;
    result.set_item("licensee", payload.licensee.clone())?;
    result.set_item("lic_id", payload.lic_id.clone())?;
    result.set_item("key_id", payload.key_id.clone())?;
    match payload.exp {
        Some(exp) => result.set_item("exp", exp)?,
        None => result.set_item("exp", result.py().None())?,
    }
    result.set_item("machine_locked", !payload.machine_hash.is_empty())?;
    result.set_item("detail", detail)?;
    Ok(())
}

fn payload_dict(py: Python<'_>, payload: &Payload) -> PyResult<Py<PyAny>> {
    let dict = PyDict::new(py);
    dict.set_item("v", 2)?;
    dict.set_item("key_id", payload.key_id.clone())?;
    dict.set_item("lic_id", payload.lic_id.clone())?;
    dict.set_item("licensee", payload.licensee.clone())?;
    dict.set_item("machine_hash", payload.machine_hash.clone())?;
    dict.set_item("iat", payload.iat)?;
    match payload.exp {
        Some(exp) => dict.set_item("exp", exp)?,
        None => dict.set_item("exp", py.None())?,
    }
    Ok(dict.into_any().unbind())
}

/// The compiled-in production registry as ``{key_id: public_key}``. Public keys
/// only — this exists so the Python suite can pin the shipped bytes against
/// ``the_oracle.licensing.keys`` (no test holds the k2 signing seed). The
/// development test key is deliberately never returned.
#[pyfunction]
fn production_keys(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let table = PyDict::new(py);
    for entry in PRODUCTION_KEYS {
        table.set_item(entry.key_id, PyBytes::new(py, &entry.public_key))?;
    }
    Ok(table.into_any().unbind())
}

#[pymodule]
fn rhetoric_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(verify_serial, m)?)?;
    m.add_function(wrap_pyfunction!(production_keys, m)?)?;
    //: True when this build mirrors the caller's key table (development only).
    m.add("TEST_KEYS_ACCEPTED", cfg!(feature = "test-keys"))?;
    m.add("CORE_VERSION", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn hex(encoded: &str) -> Vec<u8> {
        (0..encoded.len())
            .step_by(2)
            .map(|i| u8::from_str_radix(&encoded[i..i + 2], 16).unwrap())
            .collect()
    }

    #[test]
    fn k2_matches_the_python_registry_hex() {
        let expected = hex("cfb15a8029ad74a99ae3f52eaddd92a011f38786ba6de19f38de0b88eede0a88");
        assert_eq!(PRODUCTION_KEYS[0].public_key.to_vec(), expected);
        assert_eq!(PRODUCTION_KEYS[0].key_id, "k2");
    }

    #[cfg(feature = "test-keys")]
    #[test]
    fn test_key_matches_rfc8032_test1() {
        let expected = hex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a");
        assert_eq!(TEST_KEYS[0].public_key.to_vec(), expected);
    }

    #[test]
    fn rfc8032_test1_signature_verifies_and_a_flip_fails() {
        let key = hex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a");
        let mut signature =
            hex("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155\
                 5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b");
        let key: [u8; 32] = key.try_into().unwrap();
        assert!(verify_signature(&key, b"", &signature));
        signature[0] ^= 0x01;
        assert!(!verify_signature(&key, b"", &signature));
    }

    #[test]
    fn canonical_bytes_sort_keys_and_drop_whitespace() {
        let parsed: Value =
            serde_json::from_str(r#"{"v":2,"key_id":"k2","lic_id":"x","licensee":"A B"}"#)
                .unwrap();
        let Value::Object(map) = parsed else {
            unreachable!()
        };
        assert_eq!(
            canonical_bytes(&map),
            r#"{"key_id":"k2","lic_id":"x","licensee":"A B","v":2}"#
        );
    }

    #[test]
    fn base64url_accepts_missing_padding_and_whitespace() {
        assert_eq!(decode_b64url("YQ").unwrap(), b"a");
        assert_eq!(decode_b64url("Y Q ==").unwrap(), b"a");
        assert_eq!(decode_b64url("-_8").unwrap(), vec![0xfb, 0xff]);
        assert!(decode_b64url("Y").is_none());
    }

    #[test]
    fn token_envelope_rejects_wrong_prefix_and_arity() {
        assert!(split_token("NOPE.a.b").is_none());
        assert!(split_token("ORACLE1.a").is_none());
    }

    #[test]
    fn python_scalar_coercions_match_the_reference() {
        assert_eq!(python_str(&Value::Null).unwrap(), "None");
        assert_eq!(python_str(&Value::Bool(true)).unwrap(), "True");
        assert_eq!(python_str(&Value::from(7)).unwrap(), "7");
        assert_eq!(python_int(&Value::from(" 12 ")).unwrap(), 12);
        assert_eq!(python_int(&Value::from(true)).unwrap(), 1);
        assert!(python_int(&Value::from("12.5")).is_none());
        assert!(falsy(Some(&Value::from(""))));
        assert!(falsy(None));
        assert!(!falsy(Some(&Value::from("x"))));
    }

    #[test]
    fn legacy_and_current_shapes_are_exact_key_sets() {
        let legacy: Map<String, Value> = serde_json::from_str(
            r#"{"v":1,"key_id":"k","lic_id":"i","licensee":"l","machine_hash":"","iat":1,"exp":null,"edition":"studio"}"#,
        )
        .unwrap();
        assert!(is_known_shape(&legacy, true));
        assert!(!is_known_shape(&legacy, false));
        let mut current = legacy;
        current.remove("edition");
        assert!(is_known_shape(&current, false));
        current.insert("extra".to_string(), Value::from(1));
        assert!(!is_known_shape(&current, false));
    }
}
