---
name: compact
description: "Compress the harness itself — law, CLAUDE.md, AGENTS.md, notes, README, architecture, spec index. One live statement per topic; superseded/duplicate/finished get deleted. Free-form: 压缩记忆/harness 臃肿了/清理过时的/只保留最新的/compact the notes. Writes harness knowledge only; never reads project source."
argument-hint: "<optional scope: a harness file, a topic key, or empty for the whole harness>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:compact — Harness Compaction

Read CLAUDE.md → parse `mol_project:` (`$META`); else emit adoption hint and stop.

`/mol:note` reconciles **one** topic when you decide it. `/mol:compact` runs
that same reconcile across **every** topic at once, leaving one live statement
per topic. Every skill writes into the harness; this is the only one that
sweeps it.

**Compacts the harness; consults the code.** The write surface is harness-only.
But which of two competing requirements is the *current* one is usually only
visible in the source — so when a topic holds conflicting statements, read the
code that would obey them and let it break the tie.

This is **not** an audit of the repo. You never enumerate paths or symbols to
fact-check the harness; that is `/mol:map`, and it produces different findings.
You read only as much source as it takes to decide which requirement is in
force.

## Surface

Project source is **read-only evidence** — consult it, never edit it.

| Write | Never write |
|---|---|
| `.claude/notes/law.md` — **dedupe and absorb only, never delete** | Project source, tests, public `docs/`, public `README.md` |
| `CLAUDE.md`, `AGENTS.md` / `AGENT.md` (preserve `mol_project:`) | Spec **bodies** — INDEX rows and done-spec flagging only |
| `$META.notes_path` and `.claude/notes/**`, incl. its `README.md` | Plugin agent / skill definitions |
| `.claude/notes/architecture.md` — strike superseded claims; rebuild is `/mol:map` | Any statement whose topic you could not place |
| `.claude/specs/INDEX.md` | |

## Order of authority

Every conflict resolves down this list — never by file size, never by which
file you happened to read first.

1. **law** — `.claude/notes/law.md`. Outranks everything, the code included. A
   harness statement contradicting a law is dead on sight, whatever its date.
   Code contradicting a law is **rot**, never a repeal.
2. **the code, between competing statements** — when a topic holds two or more
   conflicting requirements, the one the source actually follows is the current
   one. Open the files that would obey each and look. A rule the codebase has
   already adopted outranks the one nobody implemented.
3. **git recency** — when the code cannot disambiguate (process rules,
   conventions with no code footprint, two rules both unimplemented), the
   later-written statement wins. `git log -1 --format=%ad -- <file>`,
   `git blame -L<n>,<n>` for a line — not how a sentence sounds. Untracked or
   uncommitted → treat as newest.
4. **closest to enforcement** — a rule stated where it is executed beats the
   same rule retold in prose somewhere else.

Two **laws** in conflict is not yours to resolve: report both and stop.

One statement with **no competitor** never reaches this ladder. Rule 2 breaks
ties; it does not retire an uncontested rule the code happens to violate — see
§ When a rule may be deleted.

## When a rule may be deleted

The question every deletion answers: **can this rule still be violated?**

| State | Meaning | Action |
|---|---|---|
| violated right now | subject exists, code disobeys | **debt** — keep, report with a route |
| obeyed | subject exists, code complies | **holds** — keep, silent |
| **moot** | the thing it governs is gone — no code could obey or break it | **propose deletion** |
| **overturned** | the operator reversed it, in the harness or on record | **propose deletion** |

Only the last two rows delete, and only two things count as evidence:

1. **An explicit reversal by the operator.** "改成…", "不再…", "以后只能用 X",
   `**Supersedes**:` written by `/mol:note`, a newer rule that cannot coexist
   with the old one (obeying either necessarily violates the other). Different
   emphasis on the same topic is not a reversal.
2. **The subject ceased to exist.** A rule about a module, format, command, or
   flag that no longer appears anywhere. Nothing can comply with it and nothing
   can break it, so it constrains nothing. This is the one deletion that
   *requires* reading the source — and it is a question about the subject's
   existence, never about whether the code obeys.

Everything else survives. A rule can be old, unfashionable, inconvenient, or
currently broken by the code, and still be in force.

**Both rows still need approval, laws included.** `law.md` has no separate
deletion path — it has the same two evidences plus the standing rule that you
propose and the operator disposes.

## Procedure

### 1. Inventory

List paths and line counts *before* reading: `law.md`, `CLAUDE.md`,
`AGENTS.md`, `$META.notes_path`, every file under `.claude/notes/**`,
`.claude/specs/INDEX.md` and each spec's frontmatter. The sweep reports size as
well as truth.

Read `law.md` first — it is the tie-breaker for every step below.

`$ARGUMENTS` narrows to one file or one topic key. Empty = whole harness.

### 2. Cluster by topic

Reduce every rule, claim, and decision to a **topic key** — same slug
vocabulary `/mol:note` uses (`naming-n-atoms`, `arch-forces-layout`, …). A
cluster with one member in one file is healthy; skip it. Clusters that span
files, or hold more than one statement, are the entire job.

Prose carrying no rule — rationale, "why we chose X", worked examples — is not
a statement. It passes through untouched.

### 3. Classify

Exactly one member of each cluster survives, chosen by § Order of authority.
Every other member is one of:

- **superseded** — same topic, contradicted by the survivor. *Evidence: both
  path:line, plus which witness decided it — the source file that follows the
  survivor, or the two dates.*
- **duplicate** — same topic, agrees with the survivor. *Evidence: the location
  list.* Canonical home per `/mol:note` § 5; the rest become a one-line pointer
  or nothing.
- **finished** — describes work that is done: `status: done` specs, landed
  migrations, "will do X" where X is now stated as done, `(deprecated)`
  annotations, dated diary entries stacked on one topic, `removed X on
  YYYY-MM-DD` tombstones.
- **moot** — the subject is gone; nothing could obey or break it. *Evidence:
  the name, and that it appears nowhere in the source.* See § When a rule may
  be deleted.
- **overturned** — the operator reversed it. *Evidence: the reversal — a
  `**Supersedes**:` line, or a newer rule that cannot coexist with it.*
- **violates-law** — contradicts `law.md`. Dead regardless of date.
- **holds** — the survivor. Untouched, and **not** reported as noise.
- **unplaceable** — no topic could be assigned, or two statements could not be
  ordered. **Kept**, and listed separately for the user to rule on.

Also collect, without deleting:

- **uncontested but unmet** — a rule with no competitor that the source does
  not follow. **Not stale.** It is debt, or a requirement not yet implemented.
  Report it as a compliance gap with a route (`/mol:debug` / `/mol:refactor`).
- inviolable-sounding rules living outside `law.md` → **promotion** candidates (§ 5)
- `status: done` specs still on disk → flag; deletion belongs to `/mol:close`
- INDEX rows with no file, files with no INDEX row
- `CLAUDE.md` over ~100 lines (managed body over ~60), any notes file over
  ~200 → split candidates

### 4. Report, then wait

Grouped by file, evidence on every line:

```
.claude/notes/notes.md
  superseded  L25  spec-status wording — CLAUDE.md:88 restates it, newer (2026-07-02 vs 2026-03-11)
  finished    L40  "migrate .agent/ → .claude/" — landed; migration table row exists
  duplicate   L31  meta-version scheme — also CLAUDE.md:88, canonical there
CLAUDE.md
  violates-law L43 "skip the failing test to unblock" — law.md:no-silent-debt
promotions
  .claude/notes/conventions.md L10  "never mutate a Frame in place" → law.md
unplaceable
  .claude/notes/release.md L12  "signing key rotation" — no other statement on this topic, no date
```

Then a size table (file, lines before, lines after).

**Wait for approval.** This is the one harness skill whose job is deletion; a
wrong call costs knowledge. Per-item rejection allowed. Nothing is written
before the user answers.

### 5. Apply

- **superseded / violates-law / finished / moot / overturned** — delete the
  statement. Section left empty → delete the section. File left empty → delete
  the file and its inbound links.
- **duplicate** — keep the canonical one; others become a one-line pointer, or
  nothing.
- **promotion** — **move** into `law.md` under `<!-- mol:law:id:<slug> -->`,
  leaving a one-line index entry at the origin. Only for items the user
  approved **as a law** — never promote on your own reading of emphasis.
- **unplaceable / holds** — untouched.

Never soften a statement to make it survive. If it cannot stand as one live
rule, it is prose: keep it as rationale, or drop it.

git is the archive. No tombstones, no changelog sections, no `(deprecated)`
annotations — that residue is exactly what this skill exists to remove.

### 6. Verify

Re-cluster the written files. Every topic must hold exactly one live statement;
nothing may contradict `law.md`; every pointer must resolve. A cluster still
holding two survivors is a bug in the apply, not leftover rot.

### 7. Report

Files touched, per-bucket counts, size table before → after, unplaceable list
verbatim, promotions applied, specs flagged for `/mol:close`, and the
**compliance gaps** — uncontested rules the source does not follow, each with a
route. Those are debt you surfaced, not compaction; never silently omitted.

```
/mol:compact: 7 superseded, 3 duplicates, 2 finished across 5 files; 612 → 431 lines; 1 promoted to law
```

No-op branch:

```
/mol:compact: one live statement per topic already; nothing to compact
```

## Guardrails

- **Never delete a law on your own judgment.** Dedupe and absorb freely;
  deletion needs one of the two evidences in § When a rule may be deleted, and
  even then you *propose* — the operator disposes. A skill able to retire its
  own constraints has none.
- **Never resolve two conflicting laws.** Report both and stop.
- **Never treat inconvenience as obsolescence.** "This rule makes the diff
  bigger" is the rule working.
- **Never compact by age alone.** Recency breaks ties *within* a topic. Old and
  unopposed is current, not stale — "keep the newest N" would delete
  load-bearing knowledge and keep fresh mistakes.
- **Code non-compliance is never a repeal.** An uncontested rule the source
  violates is debt, not a dead rule — keep it and report the gap. Deleting
  rules the code breaks would launder every violation into a decision, and the
  harness would converge on describing whatever the code already does. Rule 2
  breaks ties **between competing requirements**; it never retires a lone one.
- **Never audit the repo.** Read source to decide which of two requirements is
  in force — never to fact-check a claim's paths, symbols, or counts. That is
  `/mol:map`'s job and it yields different findings.
- **Never delete a long user-authored note for being long.** Long and unopposed
  is a split candidate.
- **Never touch project source, tests, `docs/`, public `README.md`, or spec bodies.**
- **Never write before approval.** Unlike `/mol:map`, this skill removes.
- **One pass, no recursion.** If applying reveals more drift, report it and let
  the user re-run rather than looping.

## Idempotency

- Nothing stale → single-line no-op, zero writes.
- Re-run right after a run → no-op; every surviving topic is already singular.
- Narrowed by `$ARGUMENTS` → only that file or topic, same rules.

## Bilingual

Chinese argument → report in Chinese; file paths, markdown headings, frontmatter
keys and stable-marker comments stay in English for deterministic parsing.
