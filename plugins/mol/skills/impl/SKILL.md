---
name: impl
description: "One-spec TDD loop. SMALL is one implementer; MEDIUM/LARGE is tester then implementer. test_single inside the loop. Docs Mode A only when a docs criterion is pending, then one commit. Does not call simplify, perf, or close."
argument-hint: "<slug | spec-prefix | feature description>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:impl — Spec Tasks Orchestrator

Read CLAUDE.md → `$META`. Print `[mol] stage: <value>`.

This loop routes and gates. It does not author production source. `implementer` writes code. `tester` writes tests only on MEDIUM/LARGE.

Debt (`law.md:no-silent-debt`): rot in a file you are editing → fix it if stage-allowed, or stop with path:line. Do not widen the edit to other files.

A chain prefix with ≥2 specs → invoke `/mol:impl-all` and stop. `--chain` is one spec from impl-all: no commit, no delete.

## 1. Pre-flight

Classify: SMALL (<3 files, existing pattern) / MEDIUM (3–8 files or a new pattern) / LARGE (new top-level concept).

LARGE on one unsplitted spec → re-invoke `/mol:spec` to split, then `/mol:impl-all`. Stop.

Read `<slug>.md` and `<slug>.acceptance.md`. Missing → refuse. `draft` → refuse. `done` → warn (file should be gone). `maintenance` refuses unless `kind: bugfix`.

Resume: for each open task, grep or run `$META.build.test_single`. Tick tasks that already pass.

## 2. Tasks

Every delegation carries the handoff packet (`rules/agent-design.md` § Handoff packet). Inner loop command is `$META.build.test_single` only.

**SMALL.** One `implementer` with `mode: small`. It writes the failing test, confirms RED, then the patch. You re-run `test_single`. Tick the tasks it closed.

**MEDIUM/LARGE.**

- First "write failing tests" task → `tester`. Confirm RED. Tick.
- `regressions/` → `tester` only. Hard-coded expected values. No live third-party import.
- Each other task → `implementer` with the RED command. `green` → you re-run `test_single`, then tick. `still-red` → one retry with the failure attached; still red → stop and re-invoke `/mol:spec`. `blocked:` → stop.
- After the tasks, one `architect` review. A law 🚨/🔴 stops the run.

## 3. Ledger and commit

Update `code` and `runtime` criteria from the tests just run.

A pending `docs` criterion, and not `--chain`: invoke `/mol:docs` Mode A once on the touched public paths, then mark that criterion from what it checked. No `docs` criterion → do not invoke `/mol:docs`.

Do not invoke `/mol:simplify`. That pass is the user's, on this diff, before the commit. Do not invoke `/mol:perf`. Do not invoke `/mol:close`.

`--chain`: criteria that need the full suite, docs, or a bench stay `pending` with `note: chain-end gate`. Set `status: code-complete`. Stop. No commit.

Otherwise:

- A task still open, or a `code`/`runtime` criterion failed → `status: in-progress`. Stop.
- A `scientific` or `performance` criterion still pending → `status: code-complete`. Invoke `/mol:commit` once. Leave the spec. Next phase is `/mol:perf`, then `/mol:close`.
- Every criterion verified → `status: done`. Delete the spec, the acceptance file, and the INDEX entry. Invoke `/mol:commit` once so code and deletion land together.

## 4. Summary

One line: scope, files, `test_single` result, status.
