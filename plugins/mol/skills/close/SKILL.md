---
name: close
description: "Standalone. Finish a code-complete spec: re-check the ledger, attest criteria no evaluator can run, delete the spec. Not called by /mol:impl or /mol:impl-all."
argument-hint: "<spec-slug> [--manual]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:close — Spec Closer

Read CLAUDE.md → `$META`. Use this when a spec was left `code-complete` because a non-code criterion was still pending. `/mol:impl` deletes a fully verified spec itself.

## 1. Gate

Spec missing → refuse. Status `draft` / `approved` / `in-progress` → refuse. `done` → no-op.

- A = already `verified`
- B = `pending` `code` or `runtime` with a runnable check
- C = `pending` `scientific`, `performance`, or `docs`

## 2. Clear

B fails → `failed`, abort, route `/mol:debug`. B passes → `verified`.

C: invoke `/mol:perf <slug>` once when `mol_project.bench.repo` is set and the criterion is scientific or performance. Docs → check the path or docstring exists. Anything still pending → `verified` with `verified_by: agent-auto` (or `human` when `--manual` was passed) and one line of what was checked.

## 3. Delete

All verified → `status: done`. Invoke `/mol:commit` with subject `chore(<scope>): close <slug>`. Then delete spec, acceptance, and the INDEX entry, and amend that commit so the deletion is in it. Commit BLOCK → revert the status flip, do not delete.

```
[mol:close] <slug> — N criteria verified, deleted in <sha>
```
