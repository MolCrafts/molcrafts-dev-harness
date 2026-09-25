---
name: impl-all
description: "Drive one spec or a <prefix>-NN chain through /mol:impl. Read each spec's status yourself. One check, one full suite, and `/mol:commit` once at chain end. No per-spec evaluator and no per-spec close."
argument-hint: "<spec-prefix or slug>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:impl-all — Batch Spec Chain Driver

Read CLAUDE.md → `$META`. Never ask questions.

## 1. Discover

Specs matching `<prefix>-NN-<phase>.md`, plus a bare `<prefix>.md` at position 00. Sort by NN. None → stop.

`draft` → stop and name them. `done` → skip.

One matching spec → invoke `/mol:impl <slug>` (no `--chain`) and stop. That run owns its commit.

## 2. Drive

For each remaining spec, in order:

1. Invoke `/mol:impl <slug> --chain`.
2. Read the spec file yourself. Do not dispatch an evaluator.
   - File absent → treat as done. Next.
   - Any criterion `failed`, or status still `approved` / `in-progress` → stop the chain.
   - `code-complete` and every pending criterion has `note: chain-end gate` → next.
   - `code-complete` and any other criterion still pending → stop. Name the owed evaluator. Do not invoke it.
   - `code-complete` and every criterion `verified` → next (chain end deletes it).

## 3. Chain end

Once, for the whole chain:

1. `$META.build.check` and `$META.build.test`. On failure, fix and re-run only what failed (`rules/git-publish.md` § Re-running after a failed gate).
2. A pending `docs` criterion anywhere in the chain → invoke `/mol:docs` Mode A once on the touched public paths, then mark those criteria. Do not invoke `/mol:simplify` or `/mol:perf`.
3. Flip each remaining `note: chain-end gate` criterion that the suite just settled. A `scientific` or `performance` criterion stays pending. A `failed` stops before commit.
4. For every spec whose criteria are all `verified`: set `status: done`, delete the spec, the acceptance file, and the INDEX entry. A spec still waiting on `/mol:perf` stays `code-complete`.
5. Invoke `/mol:commit` once.

Do not invoke `/mol:close`.

## 4. Report

One row per spec: `done` or `stopped`.

```
/mol:impl-all: <N> done, <K> failed; chain <prefix>
```
