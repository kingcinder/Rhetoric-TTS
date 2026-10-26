# Rhetoric Rename Decisions

Baseline inventory: [RENAME_INVENTORY.md](RENAME_INVENTORY.md), captured from
the repository tree before the rename. `Seashells/` is excluded by the owner
instruction and remains untouched.

| Occurrence category | 1.5.0 decision | Compatibility treatment |
|---|---|---|
| Customer-visible product wording | Use **Rhetoric** in app windows, dialogs, CLI help and diagnostics, generated reports, FLAC vendor and software tags, support links, README, and current customer documentation. | No product-facing “The Oracle” copy is retained. |
| Installers, distribution names, desktop entries, icons, and artifact names | Use `rhetoric` for the Python distribution, command, manager, installer scripts, Linux packages, Windows installer, and generated artifacts. | Old command and script names forward to the Rhetoric implementation with a one-line legacy notice. `the-oracle` remains a console and managed-launcher alias. |
| Internal Python/package identifiers | Keep the `the_oracle` import package and established class identifiers to avoid breaking internal imports and saved integrations. | These are implementation names, not customer-facing product labels. |
| Serial token prefix and `ORACLE_*` environment variables | Keep `ORACLE1` tokens valid and retain established environment variable names. | `ORACLE1` is the historical 1.5.0 token prefix; no token migration is needed. |
| Per-user data and cache paths | Keep existing `~/.config/the-oracle` and `~/.cache/the-oracle` locations. | Preserves settings, model caches, support records, and upgrade compatibility. |
| Historical release notes and provenance | Keep prior release records as dated history, with superseded commercial plans moved under `docs/release/archive/`. | Old-repository commits and CI results are provenance only and do not qualify this repository's release gates. |
| Contact address | Keep `codysa90@gmail.com`. | Do not use the address as an email-based purchase/serial workflow; storefront and payment remain deferred. |

The distribution name is `rhetoric`; the Python import name remains
`the_oracle`. Windows and GPU qualification remain independent release gates.
