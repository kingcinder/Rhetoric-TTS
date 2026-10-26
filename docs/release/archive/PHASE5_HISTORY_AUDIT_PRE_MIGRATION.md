> Superseded historical record. **Provenance: pre-migration repository.** Commit hashes and CI run IDs below are retained solely as provenance and do not qualify the Rhetoric 1.5.0 release head.

# Phase 5 History Audit — completed scrub and push

Audit date: 2026-10-25 UTC

## Recovery anchor

- Full-ref bundle: `/tmp/the-oracle-pre-scrub-20261025T143643Z.bundle`
- SHA-256: `3c2133098a5d9c875afe987941d3d42822bf3b7e42808eb04fbabd22efe97623`
- The bundle was created outside the repository with `git bundle create ... --all`
  before rewriting.

## Refs retained and removed

The pre-scrub local audit covered 18 refs. The rewritten public refs retain the two release branches and non-archive tags
`alpha-0.1` and `v0.2.0`. Archive tags and Codex-only refs were deleted. GitHub-managed
`refs/pull/*` were not rewriteable from the mirror; PR heads 2–5 remain an
open remote retention issue and are not covered by the clean-ref claims below.

## Scrub rules and verification

- `STATE.md`, `JUNO_FIXES.log`, `RELEASE-CHECKLIST-V1.3.2.md`,
  `docs/superpowers/**`, `.secrets.baseline`, and `Profiles/*.json` were removed
  from every retained ref.
- `/home/USER` and `/media/USER` were replaced with neutral placeholders;
  `/home/test-user` remains an intentional test fixture.
- The three current voice/audio blobs were preserved because the owner directed
  that Seashells recordings are not scrub targets.
- `git log --all -- <scrubbed path>` returned zero entries for every scrubbed
  path in the rewritten mirror’s retained branches and tags. This does not
  cover GitHub-managed pull-request refs.
- `gitleaks git --log-opts='--all' --redact --no-banner` scanned 721 rewritten
  commits and returned no leaks (exit 0).
- A grep across the rewritten mirror’s retained branches and tags found no
  `/home/USER` or `/media/USER` strings and no production signing-seed filenames.
  GitHub-managed pull-request refs require Support removal and a fresh remote
  audit.
- Commit citations in release records and suite-count baselines were remapped
  with filter-repo's commit map. The rewritten-head full suite reproduced
  **2,120 passed, 3 skipped, 0 failed, 6 warnings**; the Vulkan device test was
  the only environment skip.

## Push and post-push verification

The owner authorized the exact instruction **`push the scrub`**. The prepared
mirror is verified before using:

```sh
git push --force --all origin
git push --force --tags origin
git push origin --delete \
  archive/codex-cross-platform-install-refactor \
  archive/codex-hardening-fix \
  archive/ingest-refactor-hints \
  archive/serpent-circle-renovation \
  archive/voice-craft-and-recording-studio
```

After the push, a fresh remote clone verified the retained refs. GitHub-managed
`refs/pull/2`–`refs/pull/5` still expose pre-scrub history and must be removed by
GitHub Support together with cached views before the public scrub can be called
complete. Anyone with a checkout should re-clone, and any credential identified
by later review must be rotated.
