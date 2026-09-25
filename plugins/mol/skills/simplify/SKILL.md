---
name: simplify
description: "Diff-scoped quality pass, same moment as Claude Code /simplify: after the change is green, before commit, only on what just changed. Reuse, simplification, efficiency, altitude. Applies the fixes. Not a bug hunt. User-invoked."
argument-hint: "[path or list of files] [focus:reuse|simplification|efficiency|altitude]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:simplify — Apply Hygiene Cleanup

Read CLAUDE.md → `$META`. Read `$META.stage` (default `experimental`).

Same contract as Claude Code `/simplify`:

- When: the diff is already green, before `/mol:commit`. `/mol:impl` does not call this.
- Scope: `git diff` (staged and unstaged), or the paths in `$ARGUMENTS`. Not the whole repo.
- Apply the fixes. Behavior stays. A finding with no concrete cost is a nit; skip it.
- Not a bug hunt. Correctness is `/mol:review` or `/mol:debug`.

`focus:` keeps one angle. Default is all four, in one parallel fan-out. No model argument.

## Angles

| Angle | Look for | Apply |
|---|---|---|
| reuse | new code that duplicates a helper already in the tree | call the existing one |
| simplification | dead branch, needless wrapper, nesting that flattens in place | delete or flatten |
| efficiency | repeated work, serial independent I/O, a copy the caller already has | remove that work |
| altitude | a policy decision buried in a leaf, or a leaf detail leaked upward | move it one level |

Also check the diff against `law.md` and CLAUDE.md. A law break is a finding, not a rewrite of the law.

## Stage

- `maintenance` — dead import, debug residue, stale TODO whose target is already gone. Nothing else.
- `stable` — do not delete a symbol still marked `@deprecated` / `# DEPRECATED`.
- `experimental` / `beta` — all four angles. No new module and no new public name. That is `/mol:refactor`.

## Procedure

1. Scope = named paths, else the working diff. Empty diff → stop.
2. Run `$META.build.test_single` on the touched units. Record tests that already fail.
3. Fan out the angles. Each pass returns `file:line`, the cost, and a behavior-preserving fix.
4. Apply the fixes that stay inside the diff and the stage gate. Skip a false positive. Do not wait.
5. Re-run `test_single`. A test that was green and is now red → revert the whole batch.
6. Do not commit. The caller commits.

```
/mol:simplify: applied N across K files (reuse R, simplification S, efficiency E, altitude A); M skipped
```
