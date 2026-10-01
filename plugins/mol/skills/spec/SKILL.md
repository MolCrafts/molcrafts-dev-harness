---
name: spec
description: "Use when turning a requirement into a spec and acceptance. Librarian, then one grill, then draft. Design-mode gates persist; clean auto-invokes impl-all. Tier C: 落盘/写 spec. Never silent from discuss."
argument-hint: "<feature description>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:spec — Specification Generator

Read CLAUDE.md → `$META`. Specs live under `$META.specs_path` (default `.claude/specs/`). `/mol:impl` refuses without both files and deletes them when done.

After librarian, grill once. Do not grill again after persist. Design-mode is the law gate.

## 1. Research

Kebab-case slug. One sentence.

Read existing specs. Duplicate → stop. Supersede → pass `conflict_decision: supersede:<slug>`. Else independent.

In parallel when possible:

- Physics and `$META.science.required: true` → `scientist`. Keep the reply verbatim.
- Glob the files this will touch.
- Consult `librarian`. Mandatory. Drafting does not start without it. It returns reuse candidates (`reuse` / `generalize` / `pattern`) and a placement. `spec-writer` resolves each candidate in the Design. `stale: true` → `architect` (inventory mode) → `/mol:map` → re-consult `librarian`. If map is deferred, note that and continue.

## 1.5 Grill once

Invoke `/mol:grill` in `post-librarian` mode with the requirement and the librarian report. It asks only what the report left open, then returns decisions. Feed those decisions to `spec-writer`. Redirected or under-formed → stop. Do not draft.

## 2. Draft

Invoke `spec-writer` with request, slug, scope layer, scientist output, conflict decision, librarian report, and the grill decisions.

- `ok` → § 2.5.
- `blocked` → surface the items. Stop.
- `split-needed` → only when Tasks > 10 (`rules/large-spec-split.md`). Do not ask. Re-invoke `spec-writer` once per `<base>-NN-<phase>`. Run § 2.5 on each. Persist none until every part clears.

## 2.5 Architect design-mode

Invoke `architect` with `mode: design` plus Design, Files, and the librarian report.

| Result | Action |
|---|---|
| 🚨/🔴 citing `law.md:` | Re-invoke `spec-writer` once with those findings. Design-mode again. Still red → do not persist. Stop. |
| 🟡/🟢 or none | Persist. |

## 3. Persist

No approval prompt. Write `<slug>.md` at `status: approved` and `<slug>.acceptance.md`. Update `INDEX.md` with one line per spec. Chain → one pair per sub-spec, no parent file.

Show the spec. Call out librarian reuse candidates and how the Design resolved each.

## 3.5 Audit

One pass in this skill. Do not open an interview.

Design-mode cleared every law 🚨/🔴 → `clean`. An unresolved law citation → one supersede (`spec-writer` + § 2.5) or stop on the last good persist.

## 4. Report

Paths, task count, criteria by type, `clean` or `superseded`.

`clean` or `superseded` → auto-invoke `/mol:impl-all` with the slug or chain base. Parked → do not implement.

Chinese input → body in Chinese. Frontmatter keys, INDEX, and Tasks verb-prefixes stay English.

## Examples

These select this skill: "add periodic wrap for positions.", "落盘 box wrap", "写 spec：周期边界". "该不该做 wrap" is `/mol:discuss`. A bug in wrap is `/mol:debug`.

`/mol:spec add periodic wrap for positions.` Slug `box-wrap`. Librarian returns `reuse: molpy.Box.wrap`. Grill, post-librarian, asks only the boundary (orthorhombic only). `spec-writer` returns `ok`. Design-mode is 🟢. Persist `.claude/specs/box-wrap.md` and `box-wrap.acceptance.md`, one INDEX line, then `/mol:impl-all box-wrap`.

Stop and do not draft when that slug already exists and the user did not say supersede, when grill returns redirected, or when design-mode is still 🚨/🔴 after one repair.
