---
name: compact
description: "Sweep the whole harness and drop what the repo no longer supports — dead paths, contradicted claims, duplicated rules, finished specs. Free-form: 压缩记忆/harness 臃肿了/清理过时的/compact the notes. Writes harness knowledge only."
argument-hint: "<optional scope: a notes file, a topic, or empty for the whole harness>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:compact — Harness Memory Compaction

Read CLAUDE.md → parse `mol_project:` (`$META`); else emit adoption hint and stop.

`/mol:note` keeps one topic honest at the moment you decide something.
`/mol:compact` sweeps **everything else** — the claims nobody revisited. Harness
rot is silent by construction: a note that describes a deleted module keeps
reading like fact, and the next agent believes it.

**Staleness is decided by evidence, never by age.** A rule written a year ago
that still matches the repo is current. A rule written last week naming a file
that no longer exists is dead. Sorting by timestamp and keeping "the latest"
would delete load-bearing knowledge and keep fresh mistakes — do not do it.

## Write surface

| Edit | Never |
|---|---|
| `CLAUDE.md` (preserve `mol_project:`) | Project source, tests, public `docs/` |
| `$META.notes_path` and `.claude/notes/**` | Spec **bodies** (only INDEX rows + done-spec removal) |
| `.claude/specs/INDEX.md` | Plugin agent/skill definitions |
| `architecture.md` — strike dead claims only; full rebuild → `/mol:map` | Anything you did not verify |

## Procedure

### 1. Inventory

List before reading: `CLAUDE.md`, `$META.notes_path`, every file under
`.claude/notes/**`, `.claude/specs/INDEX.md` and the spec files. Record each
file's line count — the sweep reports size as well as truth.

`$ARGUMENTS` may narrow the scope to one file or one topic. Empty = whole harness.

### 2. Extract checkable claims

Walk every harness file and pull out each assertion that names something the
repo can confirm or deny:

| Claim shape | How to check |
|---|---|
| a path (`src/foo/bar.ts`, `scripts/x.mjs`) | does it exist |
| a symbol (`FooClass`, `register_bar`) | grep the source |
| a command / script (`npm run check:contract`, `cargo xtask`) | is it in the manifest |
| a config key or field (`resolve.dedupe`, `[tool.ruff]`) | read the config |
| a count ("four plugins", "118 elements") | count it |
| a dependency or version floor | read the manifest / lockfile |

Prose with no anchor — style preferences, rationale, "why we chose X" — is
**not** a checkable claim. It is carried forward untouched.

### 3. Classify

Every checkable claim lands in exactly one bucket, each with its evidence:

- **dead** — the named thing does not exist. *Evidence: the miss.*
- **contradicted** — the repo says the opposite (a note says `dist/` is
  committed; `.gitignore` ignores it). *Evidence: path:line on both sides.*
- **duplicate** — the same rule stated in two or more places. *Evidence: the
  list of locations.* Keep the one closest to where it is enforced; the others
  become a pointer, not a copy.
- **superseded** — two live claims about one topic disagree. The one the repo
  supports wins; the other is dead.
- **holds** — verified true. Untouched, and **not** reported as noise.
- **unverifiable** — a checkable-looking claim whose anchor could not be
  resolved (private submodule, generated file, external service). **Kept**, and
  listed separately so a human can rule on it.

Also collect, without classifying as claims:

- specs with `status: done` still present → flag (deletion belongs to `/mol:impl`)
- INDEX rows with no file, and files with no INDEX row
- notes files nothing links to and nothing references
- files over ~200 lines, and `CLAUDE.md` over ~100 → split candidates

### 4. Report before writing

Grouped by file, each line carrying its evidence:

```
.claude/notes/notes.md
  dead        L25  "CI runs `check:contract`" — no such script in package.json
  contradicted L20 "dist/ committed" — .gitignore:45 ignores it
  duplicate   L31  meta-version scheme — also CLAUDE.md:88, kept there
CLAUDE.md
  dead        L43  "src/types/contract*.ts" — no match in repo
unverifiable
  .claude/notes/release.md L12 "signing key in 1Password" — cannot check
```

Then a size table: file, lines before, lines after.

**Wait for approval.** Compaction is the one harness operation whose whole job
is removal; a wrong call costs knowledge. Per-item rejection allowed. Nothing
is written before the user answers.

### 5. Apply

- **dead** — delete the claim. If it was the only content of a section, delete
  the section. If deleting it leaves a file empty, delete the file and its
  inbound links.
- **contradicted** — rewrite to what the repo actually does, naming the
  evidence path in the new text so the next sweep can re-check it cheaply.
- **duplicate** — keep one, replace the rest with a one-line pointer.
- **superseded** — delete the loser.
- **holds / unverifiable** — untouched.

Never rewrite a claim into something vaguer to make it survive. If it cannot be
stated checkably, it is prose — move it to the rationale paragraph or drop it.

git is the archive. Do not add "removed X on YYYY-MM-DD" tombstones; that is
how the file grew in the first place.

### 6. Verify

Re-run § 2 extraction on the written files. Every remaining checkable claim
must verify, or be on the unverifiable list. Report any that do not — a claim
you rewrote and that still fails is a bug in the rewrite, not a leftover.

### 7. Report

- files touched, claims removed / rewritten / merged by bucket
- size table before → after
- unverifiable list, verbatim, for the user to rule on
- specs flagged for `/mol:impl` to delete

One-line F2 summary:

```
/mol:compact: 7 dead, 2 contradicted, 3 duplicates across 4 files; 612 → 431 lines
```

No-op branch:

```
/mol:compact: every checkable claim still holds; nothing to compact
```

## Guardrails

- **Never delete what you did not check.** A claim you do not understand is
  `unverifiable`, not `dead`. Silence is not evidence.
- **Never compact by age.** No "keep the newest N", no timestamp sort, no
  "this looks old". The repo is the only authority.
- **Never touch project source, tests, `docs/`, or spec bodies.** Harness
  knowledge only.
- **Never delete a user-authored note wholesale** because it is long. Long and
  true is a split candidate, not a deletion.
- **Never write before approval.** Unlike `/mol:map`, this skill removes.
- **No tombstones, no changelog sections, no "(deprecated)" annotations.** Git
  holds the history; the file holds the current truth.
- **One pass, no recursion.** If applying reveals more drift, report it and let
  the user re-run rather than looping.

## Idempotency

- Nothing stale → single-line no-op, zero writes.
- Re-run right after a run → no-op, since every surviving claim just verified.
- A claim rewritten to name its evidence path verifies faster on the next sweep.

## Bilingual

Chinese argument → report in Chinese; file paths, markdown headings, frontmatter
keys and stable-marker comments stay in English for deterministic parsing.
