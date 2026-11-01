"""Compiled license core: parity with the Python reference, and its contract.

The Rust extension is an *optimisation of the same decision*, not a second
policy. Every case below runs both implementations and demands identical
``LicenseStatus`` values, so a divergence fails here instead of on a user's
install. The module skips when the core is not built (a plain source checkout
and CI without a Rust toolchain stay green through the Python fallback).

**Registry pinning:** no test holds the ``k2`` signing seed, so a typo in the
compiled production key would otherwise be invisible. ``production_keys()``
exposes the compiled bytes for exactly this check; the development test key is
never part of that table.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from the_oracle import _native  # noqa: E402
from the_oracle.licensing import tokens  # noqa: E402
from tests.licensing_fixtures import (  # noqa: E402
    PRODUCTION_KEYS,
    TEST_KEY_ID,
    TEST_SEED,
    payload as fixture_payload,
)

CORE = _native.load()
pytestmark = [
    pytest.mark.usefixtures("test_license_registry"),
    pytest.mark.skipif(CORE is None, reason="compiled license core not built"),
]

NOW = 1_700_000_100.0
MACHINE = "b6df06371429a19074c3e8d9762e8aa7"


def _token(**overrides: object) -> str:
    return tokens.mint(dict(fixture_payload(), **overrides), TEST_SEED)


def _native_status(token: object, *, now: float = NOW, machine_hash: str = "") -> object:
    return tokens._status_from_native(token, now=now, machine_hash=machine_hash)  # type: ignore[arg-type]


def _reference_status(token: object, *, now: float = NOW, machine_hash: str = "") -> object:
    return tokens._verify_token_python(token, now=now, machine_hash=machine_hash)  # type: ignore[arg-type]


def _legacy(**overrides: object) -> str:
    body = dict(fixture_payload(), v=1, edition="studio", **overrides)
    return tokens.mint(body, TEST_SEED)


def _raw(body: bytes, *, signed: bytes | None = None) -> str:
    from the_oracle import _ed25519

    signed = body if signed is None else signed
    signature = _ed25519.sign(TEST_SEED, signed)
    return f"{tokens.TOKEN_PREFIX}.{tokens._b64url_encode(body)}.{tokens._b64url_encode(signature)}"


def _tampered_signature(token: str) -> str:
    prefix, body, signature = token.split(".")
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    replacement = alphabet[(alphabet.index(signature[0]) + 1) % len(alphabet)]
    return f"{prefix}.{body}.{replacement}{signature[1:]}"


CASES = {
    "valid_perpetual": (_token(), NOW, ""),
    "valid_expiring_later": (_token(exp=1_700_003_600), NOW, ""),
    "expired_exactly_at_boundary": (_token(exp=1_700_000_100), NOW, ""),
    "expired_after": (_token(exp=1_700_000_000), NOW, ""),
    "machine_matches": (_token(machine_hash=MACHINE), NOW, MACHINE),
    "machine_mismatch": (_token(machine_hash=MACHINE), NOW, "another-machine"),
    "machine_unprovided": (_token(machine_hash=MACHINE), NOW, ""),
    "legacy_v1": (_legacy(), NOW, ""),
    "unknown_key_id": (_token(key_id="k9"), NOW, ""),
    "bad_signature": (_tampered_signature(_token()), NOW, ""),
    "padded_with_whitespace": ("  " + _token() + "\n", NOW, ""),
    "iat_as_string": (_token(iat="1700000000"), NOW, ""),
    "iat_null": (_token(iat=None), NOW, ""),
    "lic_id_null": (_token(lic_id=None), NOW, ""),
    "licensee_null": (_token(licensee=None), NOW, ""),
    "exp_as_float": (_token(exp=1_700_000_000.9), NOW, ""),
    "extra_key_v2": (_token(edition="studio"), NOW, ""),
    "legacy_extra_key": (_legacy(serial="x"), NOW, ""),
    "not_json_object": (_raw(b"[]"), NOW, ""),
    "not_utf8": (_raw(b"\xff\xfe"), NOW, ""),
    "wrong_prefix": ("ORACLE2." + _token().split(".", 1)[1], NOW, ""),
    "two_parts": ("ORACLE1.abc", NOW, ""),
    "garbage": ("not-a-serial", NOW, ""),
}


@pytest.mark.parametrize("case", sorted(CASES))
def test_native_and_reference_agree_on_every_case(case: str) -> None:
    token, now, machine_hash = CASES[case]
    native = _native_status(token, now=now, machine_hash=machine_hash)
    reference = _reference_status(token, now=now, machine_hash=machine_hash)
    assert native is not None, "compiled core declined a str token"
    assert native == reference
    assert native.payload == reference.payload
    assert native.detail == reference.detail


def test_non_string_tokens_fall_back_and_stay_malformed() -> None:
    for bad in (None, b"ORACLE1.x.y", 17):
        assert _native_status(bad) is None
        assert tokens.verify_token(bad).state == "malformed"  # type: ignore[arg-type]


def test_public_entry_point_delegates_to_the_core(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[tuple[str, str, float, object]] = []

    class FakeCore:
        TEST_KEYS_ACCEPTED = False

        @staticmethod
        def verify_serial(token: str, machine_hash: str, now: float, table: object) -> dict:
            seen.append((token, machine_hash, now, table))
            return {
                "ok": True,
                "state": "valid",
                "licensee": "Stub",
                "lic_id": "stub-id",
                "key_id": TEST_KEY_ID,
                "exp": None,
                "machine_locked": False,
                "detail": "",
                "payload": None,
            }

    monkeypatch.setattr(_native, "load", lambda: FakeCore)
    status = tokens.verify_token("ORACLE1.anything", now=NOW, machine_hash=MACHINE)
    assert status.state == "valid" and status.licensee == "Stub"
    assert seen == [("ORACLE1.anything", MACHINE, NOW, None)]


def test_missing_core_uses_the_reference_implementation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_native, "load", lambda: None)
    status = tokens.verify_token("not-a-serial")
    assert status.state == "malformed"
    assert _native.available() is False


def test_evaluation_build_accepts_the_injected_registry() -> None:
    assert _native.accepts_test_keys() is True
    assert CORE is not None
    assert getattr(CORE, "TEST_KEYS_ACCEPTED") is True


def test_compiled_production_registry_matches_the_python_registry() -> None:
    assert CORE is not None
    compiled = {key_id: bytes(value) for key_id, value in CORE.production_keys().items()}
    assert compiled == {entry.key_id: entry.public_key for entry in PRODUCTION_KEYS}


def test_compiled_production_registry_never_contains_the_test_key() -> None:
    assert CORE is not None
    assert TEST_KEY_ID not in CORE.production_keys()


def test_core_cannot_mint_or_expose_signing_material() -> None:
    assert CORE is not None
    names = {name for name in dir(CORE) if not name.startswith("__")}
    assert "verify_serial" in names and "production_keys" in names
    assert not any("sign" in name or "mint" in name or "seed" in name for name in names)


def test_test_key_registry_is_feature_gated_in_the_source() -> None:
    source = (REPO_ROOT / "crates" / "rhetoric_native" / "src" / "lib.rs").read_text(encoding="utf-8")
    assert re.search(
        r'#\[cfg\(feature = "test-keys"\)\]\s*\nconst TEST_KEYS', source
    ), "the RFC 8032 test key must never compile into a release build"
    assert 'default = []' in (REPO_ROOT / "crates" / "rhetoric_native" / "Cargo.toml").read_text(
        encoding="utf-8"
    ), "test-keys must stay opt-in so a bare cargo build is the release build"
