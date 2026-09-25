---
name: ship
description: "Read-only gate before push or merge. push runs the test suite once; merge runs check and the suite once. commit is not a tier — /mol:commit already ran pre-commit."
argument-hint: "<push | merge>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:ship — CI Parity Gate

Read CLAUDE.md → `$META`. Read-only. Do not edit. Do not delegate to `ci-guard`. Do not pass a model name.

| Arg | Runs | Does not run |
|---|---|---|
| `commit` or empty | nothing | hooks. Print that `/mol:commit` owns `pre-commit run` once. PROCEED. |
| `push` | `$META.build.test` once | pre-commit. `/mol:push` already ran `pre-commit run --all-files`. |
| `merge` | `$META.build.check` and `$META.build.test` once | a second pass of either |

Missing `build.test` on push or merge → BLOCK.

BLOCK names the failing command and the skill that fixes it (`/mol:debug`, `/mol:ci-sync`). This skill does not fix.

```
/mol:ship <tier>: PROCEED
/mol:ship <tier>: BLOCK — <one phrase>
```
