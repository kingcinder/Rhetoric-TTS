# Proposed EULA language — updates and support conditions

**Status: proposal for the legal lane to fold into `EULA.md`.** This file
is not part of the EULA. It records the smallest truthful language that
discloses the update/support conditions the program now enforces, so the
disclosure the software shows in Settings and in `docs/SUPPORT.md` matches
the license text. Drafted to stay consistent with the finalized EULA
(commit ba125b7) and its Washington validation memo
(`EULA_WA_VALIDATION.md`): the support condition is disclosed here and in
customer-facing support docs before purchase/support use, not hidden.

## Proposed section (for insertion as the Updates/Support section)

> **Updates.** Rhetoric may check for, download, and (for install-managed
> builds) install updates automatically. Automated updates are on by
> default and can be turned off in Settings → Advanced ("Turn off
> automated updates"). Update packages are verified against a signed-off
> release manifest (SHA-256 and size) before anything is installed; an
> update that fails verification is never applied.
>
> **Support conditions.** Customer support — including submitting bug
> tickets and receiving any other form of customer support — is provided
> only for installations that (a) have automated updates enabled and
> (b) are fully updated to the current version, with the reported issue
> re-checked using the program's automatic bug catcher on the fully
> updated installation. Turning automated updates off, or remaining on
> an older version, suspends access to support until automated updates
> are re-enabled, the program has been fully updated, and the issue has
> been re-checked as described above. Creating a local diagnostic bundle
> for your own inspection is always available and is not support.
>
> These conditions are in addition to, and do not limit, the Licensor's
> existing discretion over updates and support stated elsewhere in this
> Agreement, the all-sales-final policy in Section 7.2, and any rights
> that cannot be waived under applicable law (including the Washington
> Consumer Protection Act, RCW 19.86).

## Why this wording

- The Settings opt-out warning and `docs/SUPPORT.md` state the same
  conditions in the same substance, so the term is disclosed in three
  places a customer actually sees (license, settings, support docs).
- The "rights that cannot be waived" sentence keeps the clause from
  reading as a waiver of non-waivable consumer rights, matching the
  care standard applied in the WA validation pass.
- No promise of update frequency, support response time, or perpetual
  availability is made — those remain at the Licensor's discretion under
  the existing EULA language.
