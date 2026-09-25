---
name: review
description: "Static review. Default axes are architect and janitor. Other axes only with --axis. The main session renders the verdict. Read-only."
argument-hint: "[<path> ...] [--axis=<name>[,<name>...]]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:review — Multi-Axis Code Review

Read CLAUDE.md. Read `.claude/notes/law.md` when present.

Scope: paths in `$ARGUMENTS`, else `git diff --name-only`.

| Axis | Agent | When |
|---|---|---|
| `arch` | `architect` | default; also forced when scope has production or test source |
| `hygiene` | `janitor` | default |
| `perf` | `optimizer` | `--axis` |
| `docs` | `documenter` | `--axis` |
| `ux` | `undergrad` | `--axis` |
| `api` | `pm` | `--axis` |
| `science` | `scientist` | `--axis`, and only if science review is enabled |
| `numerics` | `compute-scientist` | `--axis`, same gate |
| `visual` | `web-design` | `--axis`, frontend files only |
| `security` | `security-reviewer` | `--axis` |
| `ffi` | `ffi-guard` | `--axis`, binding surface only |

No `--axis` → `architect` + `janitor`. Docs-only scope honors `--axis` and does not force `architect`. Unknown axis → refuse and list the table.

Dispatch the selected agents in one message. Do not pass a model name. Do not dispatch an aggregator agent.

You render the verdict:

- Same line, two severities → keep the higher.
- Two agents contradict → one 🔴 naming both.
- Any 🚨 → BLOCK. Any 🔴 → REQUEST CHANGES. Else APPROVE.
- Do not drop a finding because it looks pre-existing.

```
/mol:review: <N> files, axes <list>, <verdict>, 🚨<n> 🔴<n> 🟡<n> 🟢<n>
```
