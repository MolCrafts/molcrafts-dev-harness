---
name: bootstrap
description: Initialize or maintain a repo's agent harness. Inspects the repo; if no harness exists, creates CLAUDE.md + .claude/notes/ + .claude/specs/ from scratch. If a harness already exists, audits it (health + design compliance) and applies structural repairs (frontmatter, managed sections, layout migrations). Idempotent — safe to re-run. Never writes project source.
argument-hint: "[<project-root>]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:bootstrap — Agent Harness Bootstrap

Initialize or maintain a repo's agent-facing setup. One entry point, three paths:

```
no harness  →  create fresh
harness exists  →  check (audit)  →  update (repair)
healthy harness  →  single-line no-op
```

Does not require existing `mol_project:` frontmatter — this is the tool that creates CLAUDE.md and optionally populates that frontmatter.

**Never invokes other mol agents.** Self-contained — inspect, classify, write, verify, all inline.

---

## Core principle — four-zone separation, active vs passive

```
docs/                    public-facing documentation
.claude/                 (canonical Claude Code project folder)
  notes/                 passive internal context — law.md, notes,
                         architecture.md, decisions, contracts, handoffs,
                         rubrics, debt, open questions. Outlives features.
  specs/                 active runtime artifacts — alive, ticked off as
                         /mol:impl works, deleted on completion.
  agents/, skills/,      Claude Code's own runtime configuration.
  hooks/, settings.json
CLAUDE.md                thin entry router — points at where things live;
                         does not embed all the rules.
```

`.claude/` is Claude Code's canonical project folder. Inside, **active vs passive**: `.claude/notes/` passive (kept), `.claude/specs/` active (ephemeral).

`.claude/notes/` (project knowledge agent reads) ≠ `.claude/agents/` (Claude Code agent definitions).

Never: pollute `docs/` with internal agent artifacts; put specs in `docs/` or `.claude/notes/`; put long-lived knowledge in `.claude/specs/`. Keep CLAUDE.md short.

If the repo already has a working equivalent for any zone, **respect that**.

---

## Procedure

### 1. Inspect

In parallel where possible:

- cwd, git status, primary language(s) (`git ls-files | awk -F. '{print $NF}' | sort | uniq -c | sort -rn | head`)
- whether `docs/`, `.claude/notes/`, `.claude/`, `CLAUDE.md` exist + their content
- existing build/test/format commands (`pyproject.toml`, `Cargo.toml`, `package.json`, `CMakeLists.txt`, `go.mod`, `Makefile`, `.pre-commit-config.yaml`, `.github/workflows/*`)
- doc conventions (where tutorials / API docs go; project-specific style)
- existing CLAUDE.md, agent definitions, skill directories
- repo shape: library / app / docs / workflow / UI / scientific / mixed

State result in one paragraph.

### 2. Detect state

**Harness present?** — `CLAUDE.md` exists AND at least one of `.claude/notes/`, `.claude/specs/` exists.

- **NO** → go to § 3 (Create).
- **YES** → go to § 4 (Check), then § 5 (Update).

If harness is already healthy (check returns zero findings, update plan is empty) → single-line no-op and stop.

---

### 3. Create (no harness)

#### 3.1 Classify what already exists

For every file you'd consider creating:

- **keep** — exists, fits, leave alone
- **merge** — exists, partially fits; add managed section with stable markers
- **replace** — broken/superseded; ask before overwriting
- **create** — does not exist

Flag any **misplaced** file (agent contracts in `docs/`, public tutorials in `.claude/`). Recommend a move; never auto-move.

#### 3.2 Decide minimal addition

Smallest set that gives this repo a useful harness. Reasonable defaults:

- thin `CLAUDE.md` (router) — always
- `.claude/notes/README.md` — explains directory
- `.claude/notes/law.md` — the inviolable rules; the one file `/mol:compact`
  may never delete from
- `.claude/notes/notes.md` — passive memory, `/mol:note` writes here
- `.claude/notes/design-preferences.md` — full rule text CLAUDE.md indexes
- `.claude/specs/` (empty dir) — `/mol:spec` writes here
- `.claude/notes/architecture.md` stub (one line: `> 跑 /mol:map 填充本蓝图` / "run /mol:map to populate this blueprint") — `librarian` consumes during `/mol:spec` Step 4.5; populated by `/mol:map`, not bootstrap

Add more only when justified by the repo:

- `.claude/notes/contracts/` — real agent handoff contracts
- `.claude/notes/rubrics/` — real review checklists
- `.claude/notes/decisions/` — substantial architectural history
- `.claude/notes/debt/` — tracked technical debt
- `.claude/notes/handoffs/` — work regularly paused mid-flight
- `.claude/skills/`, `.claude/agents/` — only if the project benefits from custom skills/agents

Prefer adding small things later on demand.

If the user wants the full `mol`-plugin contract (`mol_project:` frontmatter + canonical mol skills/agents), offer as opt-in.

#### 3.3 Reach approval

Show short plan: what was inspected, classifications (keep/merge/replace/create/misplaced), proposals with one-line justifications, what's left alone.

Wait for explicit approval before writing.

#### 3.4 Apply

Write only the approved set. Use stable markers (`<!-- mol:bootstrap:managed begin -->` … `end -->`) for managed sections so re-runs update in place.

For CLAUDE.md, prefer a short router (template at bottom). Don't turn it into a giant prompt.

If a target path exists with content you'd replace, **ask per-file**. Never silently overwrite.

Skip to § 6 (Self-check).

---

### 4. Check (harness exists)

Audit the harness in two passes. Read-only — findings feed § 5.

#### 4.1 Health (presence & consistency)

Cheap checks first; fail-fast if the harness is broken:

- **Presence** — `CLAUDE.md` and at least one of `.claude/notes/`, `.claude/specs/` exist? If none → go back to § 3 (Create).
- **`mol_project:` frontmatter** (when project opted into `mol` contract) — YAML at top of CLAUDE.md parseable? Required fields populated (`stage`, `language`, `build`, `doc` per `rules/claude-md-metadata.md`)? Flag missing/malformed as 🔴.
- **Spec INDEX consistency** — every file in `.claude/specs/` listed in `INDEX.md`? Every entry has a file? Mismatches are 🟡.
- **Status/checkbox consistency** per spec:
  - `status: done` + file still present → 🟡 (`/mol:impl` should have deleted)
  - `status: done` + unchecked task boxes → 🔴 contradiction
- **Stable markers** — every `<!-- mol:bootstrap:managed begin -->` has matching `end -->`. Orphans are 🔴.

#### 4.2 Design (key structural checks)

Condensed from `rules/design-principles.md`. Focus on structural drift; skip content-level judgement calls (those are manual TODOs, not auto-repairs).

**Layering (L):**
- `docs/` — only public-user content? Flag agent contracts / handoffs / specs under `docs/`.
- `.claude/notes/` — free of specs? Free of public-user prose?
- `.claude/` — any loose `.md` files at root? (Always a smell.)
- `CLAUDE.md` — line-count it. **≤ ~100 lines**; the managed body ≤ ~60 of
  them. Over budget is almost always inlined rule prose — flag 🟡 and name
  the section to move to `.claude/notes/`.
- **Design preferences** — managed section should carry
  `## Design preferences (default)` as **one line per rule** (OOP,
  primitive APIs, no factories, no god context, no all-in-one façade,
  mirrored tests) plus a pointer to
  `.claude/notes/design-preferences.md`, which must exist and hold the
  full text. Missing → 🟡 repair via managed-section refresh. **Rule
  prose inlined in CLAUDE.md → 🟡**: move it to the notes file and
  leave the one-liner.
- **Law** — `.claude/notes/law.md` must exist and hold the inviolable
  rules, one `<!-- mol:law:id:<slug> -->` marker each, with
  `## What must never change casually` in CLAUDE.md as its one-line
  index. Missing file → 🟡. An inviolable rule stated **only** outside
  `law.md` (an "iron law" section in `design-preferences.md`, an
  absolute in `notes.md`) → 🟡 promote; the body moves, CLAUDE.md keeps
  the one-liner. Never demote or reword a law during repair.

For projects with `mol_project:` frontmatter:
- `specs_path` → under `.claude/specs/`. Flag if `docs/`, `.claude/notes/`, or bare `.claude/`.
- `notes_path` → under `.claude/notes/`. Flag if under `.claude/specs/`, `.claude/` root, or `docs/`.

**Orthogonality (O):**
- Each project agent owns a single axis. Flag overlap.
- Agents must not call agents. Grep for `delegate to .* agent` / `invoke .*-agent` in agent bodies.

**Knowledge (K):**
- Agent prompts don't duplicate CLAUDE.md content.
- Skill prompts don't restate domain rules; reference CLAUDE.md.

**Capability (C):**
- Read-only agents declare only Read/Grep/Glob/Bash. Flag Write/Edit on non-write-capable roles.

**Idempotency (I):**
- Bootstrap-style skills detect existing files; offer merge/replace/keep.
- Managed sections use stable markers.

**Layout migrations needed:**
- Check against migration table (§ Migration table). Any `From (legacy)` path that exists → flag for § 5.

#### 4.3 Output check findings

Severity-sorted list:

```
🚨 / 🔴 / 🟡 / 🟢  <path> — message
  Fix: <recommendation>
```

Summary table:

| Family | 🚨 | 🔴 | 🟡 | 🟢 |
|--------|----|----|----|----|
| Health |    |    |    |    |
| Layering |    |    |    |    |
| Orthogonality |    |    |    |    |
| Knowledge |    |    |    |    |
| Capability |    |    |    |    |
| Idempotency |    |    |    |    |

---

### 5. Update (harness exists, after check)

Apply structural repairs derived from § 4 findings. Only auto-fix what the version-spec dictates; everything else is a manual TODO.

#### 5.1 Compute structural diff

Build "current version's expected shape" from plugin source:

- frontmatter contract from `rules/claude-md-metadata.md`
- managed-section template body from this SKILL.md's CLAUDE.md template (§ below)
- migration table (§ below)
- structural invariants (spec INDEX consistency, stable marker pairing)

Walk harness on disk; produce **structural diff**:

- frontmatter: missing block / missing required field / stale value / required field renamed
- managed sections: marker missing / drifted body / orphan marker
- layout: any `From (legacy)` path that exists in repo
- structural invariants: spec files not in INDEX, INDEX entries with no file, unmatched markers

Content-level findings from § 4 (Layering / Orthogonality / Knowledge / Capability / Idempotency beyond what's auto-repaired) → manual TODO bucket.

#### 5.2 Rescan repo (only when frontmatter values are queued)

If upgrade plan rewrites any `mol_project:` field's value (e.g. `build.test`), re-run inspection — primary language, build tool, test runner, formatter, linter — to derive ground-truth value. Compare against existing frontmatter; record old → new.

Skip if no frontmatter values need rewriting.

#### 5.3 Reach approval

Show one combined plan:

```
Upgrade plan (n items, target = current plugin version):
  - install mol_project frontmatter (block missing)
  - rename mol_project.foo → mol_project.bar (renamed in current contract)
  - refresh CLAUDE.md managed section (template body changed)
  - move .agent/specs/ → .claude/specs/ (current convention)
  - rebuild .claude/specs/INDEX.md (3 files unindexed)

Manual TODO (m items from content-level review):
  🔴 .claude/notes/notes.md — agent contract content here belongs in .claude/agents/
  🟡 abc-feature.md — status: done but file still present
  ...
```

Empty upgrade plan + non-empty manual list → report manual TODOs and stop.
Both empty → single-line no-op.

Wait for explicit go-ahead. Allow per-item rejection.

#### 5.4 Apply

Per approved item:

- **frontmatter (install)** — write fresh `mol_project:` YAML at top of CLAUDE.md per current contract. Preserve any pre-existing first-line content by moving below new frontmatter.
- **frontmatter (field rename/repair)** — rewrite only affected fields. Preserve user-customization fields the contract doesn't enforce.
- **managed-section refresh** — replace contents between stable markers with current template body.
- **orphan-marker repair** — only when context unambiguous; otherwise demote to manual TODO.
- **INDEX rebuild** — regenerate from actual spec files.
- **migration** — `git mv` (or `mv`) per table; patch INDEX entries that referenced old path.

After each apply, one-line action log.

---

### 6. Self-check

Verify result satisfies layering rules:

- `docs/` (if exists) — only public-user content (no specs, contracts, rubrics)
- `.claude/notes/` (if created/modified) — only passive internal context (no public-user prose, no specs)
- `.claude/` — only behavior (skills/agents/hooks/settings) and active artifacts (`specs/`)
- `CLAUDE.md` — thin router (≤ ~100 lines, managed body ≤ ~60), points rather than embeds
- nothing overwritten without approval

For create path: verify all layering rules pass.
For update path: re-run § 4 (Check) on updated harness. Verify structural findings disappeared; no new structural findings introduced. Manual TODOs expected to remain.

Surface any 🚨 / 🔴.

### 7. Report

- inspected
- path taken: create / update / no-op
- added or changed (with paths)
- left untouched (and why)
- open questions recorded in `.claude/notes/open-questions.md` (create path only)
- suggested next step

End with one-line summary.

---

## CLAUDE.md template (router)

Managed body is the **default MolCrafts project contract**. Re-running
bootstrap refreshes everything between the markers. Project-specific overrides
go **outside** the markers, or via `/mol:note` with an explicit
functional-style exception.

**CLAUDE.md is an index, not the rulebook.** One line per rule; the full text
lives in `.claude/notes/design-preferences.md`, which bootstrap writes on the
create path. A managed body that grows past ~60 lines has stopped being a
router — move the prose to notes and leave the pointer.

```markdown
# CLAUDE.md

<!-- mol:bootstrap:managed begin -->
<!-- This block is regenerated by /mol:bootstrap. Custom content goes
     OUTSIDE these markers. -->

## What this repo is

<one paragraph: what the project does, who it serves, language/stack>

## Where things live

- Source code: `<path>`
- Tests: `tests/` (mirrors source: `src/foo/boo.py` → `tests/test_foo/test_boo.py`)
- Public documentation: `docs/`
- Passive project knowledge (notes, decisions, debt, blueprint): `.claude/notes/`
- Active runtime specs (alive, deleted on completion): `.claude/specs/`
- Claude Code runtime config (agents, skills, hooks, settings):
  `.claude/agents/`, `.claude/skills/`, `.claude/hooks/`, `.claude/settings.json`

## Law (never violated)

Full text: `.claude/notes/law.md`. These outrank scope, minimal-diff, and every
preference below. No exception without the operator repealing the law; no skill
may weaken or delete one, `/mol:compact` included.

- **No silent debt.** Rot you touch gets fixed or hard-stops the work; never skip-marked, never left silent in the summary.
- **High cohesion, low coupling.** One job per module; deps through explicit seams. A unit is green via `$META.build.test_single` alone — if it needs the full suite, a sibling module's real implementation, or external processes, the design is wrong.
- **`tests/` is unit tests only.** Never an e2e or full-stack scenario under `tests/` — those go to `regressions/` or the integration harness.

<add project invariants here — public APIs, on-disk formats, contracts that need
a deliberate decision to break. Concrete prohibitions, one line each; body goes
in law.md>

## Design preferences (default)

Full text: `.claude/notes/design-preferences.md`. Defaults, **not** law — the
operator can name an exception via `/mol:note`. CLAUDE.md carries **one line
per rule**; it is an index, not the rulebook.

- **OOP by default.** Types with methods, not free helpers.
- **Primitive APIs.** Construct → configure → one concern → read result.
- **Inline until the second use.** Extract at a second call site, not before.
- **No factory functions** as the primary constructor story.
- **No god context bags** — pass the fields a call needs.
- **No all-in-one façades** — composition is the caller's job.
- **Tests mirror source**, single-function, one module → its own tests only.

<add project-specific one-liners here — never paragraphs>


## Default workflow

For non-trivial work, prefer:
1. plan (`/mol:spec` or free-form → discuss / grill)
2. implement (`/mol:impl` or `/mol:debug`)
3. review (`/mol:review`)
4. capture decisions (`/mol:note` — harness sync, not append-only)

<!-- mol:bootstrap:managed end -->

<!-- Free-form additions below this line are preserved across re-runs.
     If a section grows past a screen, promote to .claude/notes/<topic>.md. -->
```

If user opts into `mol` plugin contract: prepend `mol_project:` YAML per `rules/claude-md-metadata.md`; route body references to chosen `notes_path` and `specs_path`. Set `arch.rules_section: "## Design preferences (default)"` unless the project already has a richer Architecture heading (then point `rules_section` at that heading **and** keep Design preferences in the managed body — agents always load Design preferences when present). Default `stage: experimental` (right answer pre-1.0; per `rules/stage-policy.md` allowed values are `experimental`, `beta`, `stable`, `maintenance`). If Step 1 found `1.x.y` on disk (`pyproject.toml` / `Cargo.toml` / `package.json`), surface and ask whether `stable` instead — still default `experimental` if no pick.

---

## .claude/notes/law.md (canonical body)

The inviolable rules. Written on the create path; on the update path, created
when missing and **absorbed into** — never rewritten — when it already exists.

A law is not a strong preference. It is the fixed point the rest of the harness
is measured against: `/mol:compact` resolves every conflict against this file
and may not delete from it, and `/mol:note` may not weaken one. Adding or
repealing a law is the operator's act, stated as such.

Keep each law to a heading, a stable id marker, and a short imperative body.
Project invariants (public APIs, on-disk formats, wire contracts) go here too —
that is what `## What must never change casually` used to hold.

```markdown
# Law — never violated

Every rule here outranks scope, minimal-diff, convenience, and everything in
`design-preferences.md`. There is no "just this once". CLAUDE.md carries the
one-line index under `## Law (never violated)`.

Adding, changing, or repealing a law is the operator's act via `/mol:note`. No
skill deletes from this file — `/mol:compact` may dedupe and absorb into it,
nothing more.

<!-- mol:law:id:no-silent-debt -->
## No silent debt

Discover anti-pattern / failing test / broken invariant / clear bug in the
surface you touch or depend on → **prioritize or hard-stop**:

1. **Do not ignore** ("pre-existing, leave it"), skip-mark, weaken asserts, or
   land features on known rot.
2. **Fix now** if local + stage-allowed; else **stop**, report path:line, route
   `/mol:debug` / `/mol:refactor` / supersede.
3. **Name it** in the summary (found / fixed / blocking). Silence = process failure.

Outranks "stay in scope" and "minimal diff" whenever those mean knowingly
leaving rot you already saw.

<!-- mol:law:id:cohesion-coupling -->
## High cohesion, low coupling

**Every module** (file / type / package) is a self-contained unit. Applies to
every file, not only the important ones.

- **High cohesion** — one clear responsibility. Split when a unit accumulates
  more than one coherent job.
- **Low coupling** — depend only on narrow, explicit interfaces. No
  reach-through into other modules' internals; no ambient god context; no
  hidden global registries required to exercise the unit.

**Unit-test consequence (hard):** proving a module works uses **only that
module's unit tests**, with fakes for outbound deps. The loop is
`$META.build.test_single` on the mirrored path — not full-suite, not
cross-module regression. `$META.build.test` and `regressions/` are CI nets.

If a change "only works when the whole suite runs", or a unit test must boot
sibling modules' real implementations, the full app, network, or external
processes → the design is too coupled. **Stop**, split the boundary, inject the
dependency, or route `/mol:refactor`. Do not "fix it with more integration tests."

<!-- mol:law:id:tests-unit-only -->
## `tests/` holds unit tests only

**Never write an e2e or full-stack scenario under `tests/`.** `tests/` mirrors
source path-for-path, one module per file, single-function tests, fakes for
outbound deps. Public-API and end-to-end scenarios go to `regressions/` (with
hard-coded goldens) or the project's own integration / browser harness.

One e2e file under `tests/` breaks the unit gate for every module it touches:
`$META.build.test_single` stops being a statement about one module, and § high
cohesion, low coupling becomes unenforceable.

<!-- add project invariants below, one `<!-- mol:law:id:<slug> -->` each.
     Laws are concrete prohibitions, not sentiments: name the thing that must
     never happen and where. "Never write e2e under tests/" is a law;
     "write good tests" is not. -->
```

---

## .claude/notes/design-preferences.md (canonical body)

Written on the create path, refreshed on update when the file is missing or
predates the current contract. This is where the prose lives so CLAUDE.md can
stay an index.

**Preferences, not law.** Anything here can be overridden by the operator for a
named subsystem. If a rule cannot be overridden, it belongs in `law.md`.

```markdown
# Design preferences — full text

CLAUDE.md carries the one-line index of these rules. This file is the detail.
Inviolable rules are not here — they are in `.claude/notes/law.md`.

**Default for all MolCrafts projects.** Apply unless the operator **explicitly**
requires a functional (or other) style for a named subsystem — then capture the
exception with `/mol:note` and scope it. Do **not** invent a functional style on
your own.

## Prefer

- **OOP by default.** Types with methods, not free-floating helpers.
  Module-level functions only for true free operations or thin re-exports.
- **Primitive, single-responsibility public APIs.** Construct → configure →
  one concern → read result.
- **Inline until the second real use.** Extract at a second call site, or when
  a unit test must target that unit.
- **Testable-in-isolation boundaries.** A module you cannot unit-test without
  its real graph is unfinished design.

## Forbid

- **Factory functions as the primary constructor story.** Prefer `Foo(...)`;
  alternate constructors only with distinct semantics (`Foo.from_file`).
- **God data structures.** No mega-dict / ambient "context" blob.
- **All-in-one façade APIs.** Composition is the caller's job.
- **Coupling that forces full-graph testing.** No hidden cross-module state,
  import-time side effects, or hard-wired concrete collaborators.

## Shape check (before adding a public symbol)

1. Natural owning type? → method on that type, not a free function.
2. More than one user-visible step? → split into primitives.
3. Only one in-tree call site? → do not extract.
4. Tempted to hang another field on a "context" bag? → new parameter instead.
5. Can this unit's tests pass with fakes only? If no → redesign the seam.

## Tests

Layout: `tests/` mirrors source path-for-path, types mirror types
(`FooClass` → `TestFooClass`), single-function tests, one module → its own
mirrored tests. What may **not** live there is law, not preference —
`law.md` § `tests/` holds unit tests only. Details: `tester` agent.
```

---

## .claude/notes/ starter (if creating fresh)

```
.claude/notes/
  README.md             # what this directory is for, how to navigate
  law.md                # the inviolable rules + project invariants. Outranks
                          every other file here. /mol:compact may absorb into
                          it, never delete from it.
  notes.md              # evolving decisions, captured by /mol:note
  architecture.md       # project blueprint — modules, public surface, style,
                          layer roles. Stub points at /mol:map; populated
                          by /mol:map. Consumed by `librarian` during
                          /mol:spec Step 4.5.
  design-preferences.md # full text of the *overridable* design rules CLAUDE.md
                          indexes. Written by bootstrap; CLAUDE.md links.
  open-questions.md     # things uncertain during bootstrap; user fills over time
```

Add `contracts/`, `rubrics/`, `decisions/`, `debt/`, `handoffs/` **only when** repo has real content. Empty directories are not value.

## .claude/ starter (if creating fresh)

```
.claude/
  specs/                # active runtime artifacts; /mol:spec writes here,
                          /mol:impl ticks + deletes
    INDEX.md            # one-line entry per live spec; updated by /mol:spec,
                          pruned by /mol:impl
```

Skills/agents/hooks/settings under `.claude/` added later only when justified. Don't pre-create empty `skills/` or `agents/`.

---

## Migration table (current-version layout)

| From (legacy)               | To (current)         | Why |
|-----------------------------|----------------------|-----|
| `.agent/specs/`             | `.claude/specs/`     | active vs passive split (pre-v0.3.0; specs are runtime artifacts) |
| `docs/decisions/`           | `.claude/notes/decisions/`  | internal context, not public docs |
| `docs/contracts/`           | `.claude/notes/contracts/`  | internal context |
| `docs/agent-rubrics*.md`    | `.claude/notes/rubrics/`    | internal context |
| `.claude/NOTES.md`          | `.claude/notes/notes.md`    | passive memory belongs in `.claude/notes/`, not `.claude/` root |
| `.agent/notes.md`           | `.claude/notes/notes.md`    | v0.3.0: passive context folds into `.claude/notes/` per Claude Code spec; name avoids collision with `.claude/agents/` |
| `.agent/architecture.md`    | `.claude/notes/architecture.md` | v0.3.0 |
| `.agent/decisions/`         | `.claude/notes/decisions/`  | v0.3.0 |
| `.agent/rubrics/`           | `.claude/notes/rubrics/`    | v0.3.0 |
| `.agent/contracts/`         | `.claude/notes/contracts/`  | v0.3.0 |
| `.agent/debt/`              | `.claude/notes/debt/`       | v0.3.0 |
| `.agent/handoffs/`          | `.claude/notes/handoffs/`   | v0.3.0 |
| `.agent/open-questions.md`  | `.claude/notes/open-questions.md` | v0.3.0 |
| `.agent/README.md`          | `.claude/notes/README.md`   | v0.3.0 |
| `mol_project.notes_path: .agent/...` or `.claude/NOTES.md` | `mol_project.notes_path: .claude/notes/...` | v0.3.0: frontmatter follows the path move |
| `mol_project.perf:` block in CLAUDE.md frontmatter | (delete) | `perf.focus` was a single-value enum that didn't scale; `optimizer` agent now detects catalogs per file |
| `## Iron law — …` sections in `.claude/notes/design-preferences.md` | `.claude/notes/law.md` | inviolable rules need a file `/mol:compact` is forbidden to delete from; preferences are overridable, laws are not |
| `## What must never change casually` (any spelling) in CLAUDE.md | `## Law (never violated)`, body → `.claude/notes/law.md` | project invariants are laws; same file, same protection |

Add new rows as new conventions are codified. Layout violation **not** in this table = content-level drift → manual TODO; do not invent moves.

---

## Guardrails

- **Don't** invoke other mol agents (architect, janitor, reviewer, etc.). This skill is self-contained.
- **Don't** blindly overwrite. Use stable markers; ask per-file otherwise.
- **Don't** create boilerplate. Each file must be justified by something *observed* in the repo.
- **Don't** put agent contracts / handoffs / rubrics / temp plans / private reasoning in `docs/`. Those belong in `.claude/notes/`.
- **Don't** turn CLAUDE.md into a long manual. Router only.
- **Don't** duplicate info that exists elsewhere in the repo.
- **Don't** invent architecture rules without evidence. If unclear, record as open question.
- **Don't** create fake precision. Don't claim pytest if you didn't check.
- **Don't** modify project source. This skill never writes project source.
- **Don't** assume `mol_project:` is wanted. Offer it; let user opt in.
- **Don't** rewrite anything outside managed sections, `mol_project:` block, or paths approved for migration.
- **Don't** invent migrations not in the table. The table *is* the version-spec for layout.
- **Don't** delete user-authored notes / decisions / specs during migration. Move, never drop.
- **Don't** delete, reword, or soften a law. Migration into `law.md` is a
  **move**; an existing `law.md` is absorbed into, never regenerated. Repeal is
  the operator's act.
- **Don't** auto-delete `status: done` spec — deletion contract belongs to `/mol:impl`. Flag as manual TODO.
- **Don't** run update on dirty tree without explicit `--allow-dirty` override.

---

## Idempotency

Re-runs must be safe:

- No harness → create fresh
- Existing well-shaped harness → single-line *"harness in place, nothing to change"*
- Existing drifted harness → check reports findings, update repairs structural items, manual TODOs listed
- Managed sections → updated in place via stable markers
- User-authored notes / decisions / docs → never deleted or rewritten
- Repeated update runs → converge to no-op (structural diff empty after first repair)
- Post-update re-check → structural findings at zero; manual TODOs remain as listed

---

## Output format

- **Inspect**: one short paragraph.
- **Detect**: one line — *"no harness — creating fresh"* / *"harness found — checking"* / *"harness healthy — no-op"*.
- **Create path** (§ 3): short bulleted plan with classifications → per-file action lines (`created`, `merged`, `kept`, `skipped — needs your call`).
- **Check path** (§ 4): severity-sorted findings with summary table.
- **Update path** (§ 5): two-section plan (Upgrade plan / Manual TODO) → per-item action lines.
- **Self-check** (§ 6): 🚨 / 🔴 findings, or *"layering check passed"* / *"structural check clean"*.
- **Final summary**: one line — what was created/repaired, skipped, next step.
