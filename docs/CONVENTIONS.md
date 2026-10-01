# CONVENTIONS

Every Antigravity prompt must tell Antigravity to follow this file. Language-specific rules below apply to Python until the stack is decided (DECISIONS.md); other languages get their own section once chosen.

## Repo layout
Follow the layout in HOW_WE_WORK.md Section 2.5 (`dataset/`, `src/{ingestion,processing,analytics}/`, `scripts/`, `config/`, `output/`, `screenshots/`, `docs/`, `pipeline/`). Do not add top-level folders without a DECISIONS.md entry. Large data and outputs are git-ignored; record how to obtain/regenerate them instead.

## Naming
- Files and folders: `lowercase_with_underscores`; scripts describe the action (`load_to_hdfs.sh`).
- Hostnames and service names: fixed in `docs/ARCHITECTURE.md`; never invent new ones in code.
- Parallel-named outputs before promotion: `<name>_new.<ext>`; promote to `<name>.<ext>` only after review.

## Commits and branches
- Commit from your OWN GitHub account, even when Antigravity wrote the code.
- Format: `<type>(<area>): <short summary>` where type is one of `feat`, `fix`, `docs`, `config`, `chore`, `test`; area e.g. `ingestion`, `cluster`, `status`.
  Example: `docs(status): update Gautam section after analysis review`
- Small commits; doc updates in separate commits from code.
- Feature branches `<member>/<topic>`, small PRs into `main`. Never upload the project in one final commit. Never commit the reference repo's files or history.

## Code style (Python)
- Docstring on every module, class and function.
- Type annotations on all function signatures.
- `pathlib.Path` for paths; no hard-coded absolute paths, IPs or credentials (use `config/`).
- `logging` with one consistent format (`%(asctime)s %(levelname)s %(name)s: %(message)s`); no bare `print` for status.
- Explicit error handling; log and raise or exit non-zero, never swallow errors.
- Scripts runnable from the repo root and idempotent where possible.

## Shell scripts
`#!/usr/bin/env bash`, `set -euo pipefail`, a header comment (purpose, usage, prerequisites), no secrets inline.

## Docs
Concrete facts only: exact hostnames, versions, commands, paths. Screenshots go to `screenshots/` as each step works, named `NN_short_description.png`.

## Prompts for Antigravity
Use the template in HOW_WE_WORK.md Section 8. End every prompt with the "changed / broken / how to verify" summary. Paste the full response back to Claude.
