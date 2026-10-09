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

## Code style (TypeScript / React frontend, src/frontend/)
- TypeScript strict mode. No `any` (use `unknown` and narrow). No `@ts-ignore`.
- Function components and hooks only; one component per file, named like the file (`Login.tsx`); hooks in `useX.ts`.
- A short JSDoc comment at the top of every module and on every exported function, component and hook.
- All HTTP goes through `src/services/api.ts` (no `fetch` in components). The API base comes from `import.meta.env.VITE_API_BASE_URL`. Never put secrets in `VITE_*` variables: they are shipped to the browser.
- Tailwind: write complete class names. Never build class names from template strings (`bg-${color}-500` is not detected); use an explicit lookup object.
- Do not create folders named `lib`, `build` or `env` under `src/frontend/` (the repo's .gitignore ignores those names). Never commit `node_modules/`, `dist/` or `.env`.
- Tests: Vitest + Testing Library, next to the code (`Name.test.tsx`). Run `npm test`; lint with `npm run lint`; type-check and build with `npm run build`.
- Commit `package-lock.json`. Add a dependency only when code uses it.