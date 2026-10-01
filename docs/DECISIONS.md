# DECISIONS

Log of team decisions. Newest at the bottom. Claude must not change architecture or conventions without a new entry here.

| ID | Date | By | Decision | Why | Status |
|---|---|---|---|---|---|
| D-001 | 2026-09-30 | Gautam (team) | Docs-only commits count as commits toward the 5-per-student minimum. | Team interpretation of the course rule. Everyone should still have real code commits. | DECIDED (confirm with instructor if unsure) |
| D-002 | 2026-09-30 | Gautam (team) | No two members build the same thing at the same time. `STATUS.md` always shows the current state of the project, whatever it is. | Keeps sessions consistent without a `TASKS.md`. | DECIDED |
| D-003 | 2026-09-30 | Gautam | After each Antigravity task, the member pastes Antigravity's FULL response into the Claude chat (Section 8 rule wins over the Section 7 short-summary tip). | Claude must cross-check real numbers, not prose. | DECIDED |
| D-004 | 2026-09-30 | Gautam | Reference analysis runs BEFORE the repo exists. Output is written to a staging folder outside both the reference clone and the future repo, then copied into `docs/` when the repo is created. | Repo creation waits until the analysis is reviewed. | DECIDED |
| D-005 | 2026-09-30 | Claude (proposed) | Check the reference repo's licence, and credit it in `README.md` (a "Reference" line). | We reimplement a public repo; credit is good practice. | PROPOSED, needs team OK |
| D-006 | 2026-09-30 | Claude (proposed) | Keep `PROJECT_CONTEXT.md` and `ARCHITECTURE.md` as separate stubs for now; revisit merging once the stack is chosen. | Open decision #6 in HOW_WE_WORK. | PROPOSED, needs team OK |
| D-007 | 2026-10-01 | Gautam | The reference analysis was produced by Claude reading the public repo directly (parts A-E, merged into `docs/REFERENCE_ANALYSIS.md`) because the Antigravity attempts were too shallow. | Needed exact, line-referenced detail for reimplementation. | DECIDED |
| D-008 | 2026-10-01 | Gautam | HOW_WE_WORK.md lives only in Claude project knowledge, not in the repo; docs/ holds the other docs. | Keeps repo lean. | DECIDED