# History scrub release procedure

This repository currently contains removed personal recordings in historical
commits. Do not run these commands against a shared remote without the owner's
explicit approval.

> **Owner scope clarification (2026-11-17).** The owner states that `Input/`
> and `Seashells/` are not protected or categorically excluded from project
> work, and is the sole owner of all included stock voice files except
> material already covered by applicable fair-use statutes. No additional
> waiver or ownership documentation is required. See [project authority](PROJECT_AUTHORITY.md).
> The history-rewrite commands below are a separate operation and still
> require their own explicit authorization; this notice is not a standing
> instruction to rewrite or force-push history.

## Verify a scrub in a disposable mirror

```sh
git clone --no-local . /tmp/rhetoric-history-scrub
cd /tmp/rhetoric-history-scrub
git filter-repo --force \
  --path "Seashells/Cody's Seashell.wav" \
  --path "Seashells/Cody's Seashell1.wav" \
  --path 'Seashells/Seashell_ fransisco.wav' \
  --path 'Seashells/Seashell_No_1.wav' \
  --path 'Seashells/Seashell_No_2.wav' \
  --path 'Seashells/seashell fransisco.wav' \
  --path 'Seashells/seashell fransisco_TTS_clean_v5_aggressive_targeted_cleanup.wav' \
  --path 'Input/fransisco help.txt' \
  --invert-paths
git log --all --name-only --format='' | grep -E "Cody's Seashell|fransisco|Seashell_No_[12]|Input/fransisco help" && exit 1 || true
```

The verified local mirror had 464 commits and zero matches after filtering.

## Publish choice

After review, either replace the remote history with the scrubbed refs using a
coordinated force push, or create a new orphan repository from the scrubbed tree.
The current remote is intentionally unchanged until that choice is approved.
