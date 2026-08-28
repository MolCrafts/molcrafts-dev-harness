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
- `.claude/notes/law.md` — **the** rules file; CLAUDE.md indexes it one line
  per law. There is no second, overridable tier.
- `.claude/notes/notes.md` — passive memory, `/mol:note` writes here
- `.claude/specs/` (empty dir) — `/mol:spec` writes here
- `.claude/notes/architecture.md` stub (one line: `> 跑 /mol:map 填充本蓝图` / "run /mol:map to populate this blueprint") — `librarian` consumes during `/mol:spec` Step 1; populated by `/mol:map`, not bootstrap

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
- **Law** — `.claude/notes/law.md` must exist and hold every rule, one
  `<!-- mol:law:id:<slug> -->` marker each, with `## Law (never
  violated)` in CLAUDE.md as its one-line-per-law index. Missing file →
  🟡. A default id present in this SKILL.md's law.md template but
  absent from the project's `law.md` → 🟡 append that template body
  (never reword an id that already exists). A rule stated **only**
  outside `law.md` (a surviving `design-preferences.md`, an absolute in
  `notes.md`) → 🟡 promote; the body moves, CLAUDE.md keeps the
  one-liner. **Rule prose inlined in CLAUDE.md → 🟡**: move it, leave
  the one-liner. Never demote or reword a law during repair.
- **No second rules tier** — a `## Design preferences (default)` section
  or a surviving `.claude/notes/design-preferences.md` is 🟡: fold its
  rules into `law.md` as prohibitions (see migration table). Agents may
  not be handed two rulebooks of differing force.

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
- default law ids from this SKILL.md's law.md template (`<!-- mol:law:id:* -->`)

Walk harness on disk; produce **structural diff**:

- frontmatter: missing block / missing required field / stale value / required field renamed
- managed sections: marker missing / drifted body / orphan marker
- layout: any `From (legacy)` path that exists in repo
- structural invariants: spec files not in INDEX, INDEX entries with no file, unmatched markers
- default-law absorb: template id missing from `.claude/notes/law.md`

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
  - append missing default law architecture-first (template id absent)
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
- **default-law absorb** — for each `<!-- mol:law:id:<slug> -->` in this
  SKILL.md's law.md template that is absent from the project's
  `.claude/notes/law.md`, **append** that id's template heading + body.
  Never rewrite, reorder, or reword a law whose id already exists.
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
lives in `.claude/notes/law.md`, which bootstrap writes on the create path. A managed body that grows past ~60 lines has stopped being a
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

Full text: `.claude/notes/law.md`. Outranks scope, minimal-diff, and
convenience. There are no overridable defaults — a carve-out exists only if the
operator wrote one into `law.md` naming the subsystem. An agent never grants
itself one. CLAUDE.md carries **one line per law**; it is an index, not the
rulebook.

- **Conceptual integrity.** One problem, one coherent model — never parallel abstractions for the same concept.
- **Architecture first.** Simple shape before local convenience — never a layer only for later or unmeasured performance.
- **Earn complexity.** Every extra concept is paid for by demonstrated pressure.
- **Locality of change.** A local requirement requires a local change — never lockstep, never cycles.
- **Hide decisions, expose contracts.** Never leak representation or lifecycle across a boundary.
- **Dependencies follow policy.** Mechanism depends on policy, never the reverse.
- **Primitive public surface.** Orthogonal primitives; composition is the caller's job.
- **Explicit flow.** Required ordering and ownership are enforceable — never a ritual the caller can skip.
- **One home per fact.** Authority is unique. Representation may be copied; authority may not.
- **No silent debt.** A conscious exception is debt; an invisible one becomes architecture.
- **Tests verify owned behavior.** Tests belong to the owner of the behavior; unit-only by default.

<add project invariants here — public APIs, on-disk formats, wire contracts.
Concrete prohibitions, one line each; body goes in law.md>


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

If user opts into `mol` plugin contract: prepend `mol_project:` YAML per `rules/claude-md-metadata.md`; route body references to chosen `notes_path` and `specs_path`. Set `arch.rules_section: "## Law (never violated)"` unless the project already has a richer Architecture heading (then point `rules_section` at that heading **and** keep the Law index in the managed body — agents always load `law.md` when present). Default `stage: experimental` (right answer pre-1.0; per `rules/stage-policy.md` allowed values are `experimental`, `beta`, `stable`, `maintenance`). If Step 1 found `1.x.y` on disk (`pyproject.toml` / `Cargo.toml` / `package.json`), surface and ask whether `stable` instead — still default `experimental` if no pick.

---

## .claude/notes/law.md (canonical body)

**The project constitution**, not a style guide or pattern catalog.
Written on the create path; on the update path, created when missing
and **absorbed into** — never rewritten — when it already exists.
Missing default ids (present in the template below, absent from the
project file) are **appended**; an existing id is left untouched.

`/mol:compact` resolves every conflict against this file. `/mol:note`
may not weaken a law. Deletion needs operator evidence.

Each law uses the same template: Principle / Intent / Never / Derived
guidance. If a rule cannot identify a concrete forbidden design, it is
guidance, not law — put it in § VIII.

Project invariants (public APIs, on-disk formats, wire contracts) are
additional laws under the same template, one `<!-- mol:law:id:<slug> -->`
each.

```markdown
# Software Engineering Laws

Every rule here outranks scope, minimal-diff, and convenience. There is
no "just this once". CLAUDE.md indexes one line per law.

Adding, changing, or repealing a law is the operator's act via
`/mol:note`. No skill retires a law on its own judgment.

## 0. Purpose

This file is not a style guide and not a pattern catalog.

Laws define **non-negotiable design constraints**. They constrain
architecture, ownership, dependency, state, and change. Patterns and
implementation techniques are subordinate to these laws. A law must be
strong enough to reject a concrete design in review.

If a rule cannot identify a concrete forbidden design, it is guidance,
not law.

A carve-out exists only where this file records it under § VII, naming
the subsystem. An agent never grants itself one.

---

# I. System shape

How the system as a whole should look.

<!-- mol:law:id:conceptual-integrity -->
## 1. Conceptual integrity

**Principle.** One problem should have one coherent conceptual model.

**Intent.** The system uses one set of concepts, terms, and abstractions.
A subsystem does not invent a sibling model of the same idea.

**Never**

- Never create parallel abstractions for the same concept.
- Never introduce aliases that develop independent semantics.
- Never solve local inconvenience by inventing a new conceptual layer.

**Derived guidance.** Prefer extending an existing concept over a sibling
concept. Shared vocabulary is part of architecture.

<!-- mol:law:id:architecture-first -->
## 2. Architecture first

**Principle.** Preserve a simple system shape before optimizing local
convenience.

**Intent.** Local coding convenience must not buy itself by breaking the
whole architecture. Simple, clear shape is the foundation of
maintainability and performance.

**Never**

- Never add a layer only because it may be useful later.
- Never introduce infrastructure for unmeasured performance concerns.
- Never let a local feature dictate global architecture.

**Derived guidance.** Prefer fewer architectural concepts. Prefer
removing indirection over explaining it.

<!-- mol:law:id:earn-complexity -->
## 3. Earn complexity

**Principle.** Every unit of complexity must be justified by demonstrated
pressure.

**Intent.** Complexity is not free. Need, performance, compatibility, or
extension must already exist before an abstraction does. Architecture
first governs shape; this law governs the complexity budget.

**Never**

- Never generalize for hypothetical future requirements.
- Never optimize without evidence.
- Never make something configurable merely because it could vary.
- Never add extensibility without an actual extension point.

---

# II. Boundaries and ownership

How the system is cut.

<!-- mol:law:id:locality-of-change -->
## 4. Locality of change

**Principle.** A local requirement should require a local change.

**Intent.** A good module boundary shows up as change locality, not as
an abstract cohesion score. High cohesion and low coupling are
consequences of this law.

**Never**

- Never require unrelated modules to change in lockstep.
- Never create dependency cycles.
- Never spread one responsibility across multiple owners.
- Never make callers understand unrelated subsystem details.

**Derived guidance.** A unit is green via `$META.build.test_single` on
its mirrored tests with fakes for outbound deps. If proving the unit
requires the full graph, the boundary is wrong — split, inject, or
`/mol:refactor`. Do not compensate with more integration tests.

<!-- mol:law:id:hide-decisions -->
## 5. Hide decisions, expose contracts

**Principle.** Implementation decisions stay behind their owning
boundary.

**Intent.** A module hides **decisions that may change**, not merely
lines in a different file.

**Never**

- Never leak representation details across module boundaries.
- Never expose internal lifecycle or storage decisions as public
  contract.
- Never require callers to reproduce internal policy.

**Derived guidance.** Program against stable contracts. An
implementation detail should be replaceable without rewriting
consumers.

<!-- mol:law:id:dependencies-follow-policy -->
## 6. Dependencies follow policy

**Principle.** Replaceable mechanisms depend on stable policy, never
the reverse.

**Intent.** Core semantics are not defined by UI, binding, framework,
storage, or transport.

    mechanism → policy

not

    policy → mechanism

**Never**

- Never make domain/core depend on UI.
- Never make core depend on a serialization format.
- Never make core depend on Python / Rust / WASM binding concerns.
- Never let a framework define domain semantics.

---

# III. Public surface

How others use the system.

<!-- mol:law:id:primitive-surface -->
## 7. Primitive public surface

**Principle.** Public APIs expose orthogonal primitives; composition
belongs to callers.

**Intent.** The API ships building blocks, not a hidden workflow.

**Never**

- Never provide an all-in-one façade for unrelated operations.
- Never make one public method perform several independently
  meaningful steps.
- Never encode one preferred workflow as the only API.
- Never duplicate primitives with convenience aliases that become
  separate contracts.

**Derived guidance.** High-level workflows may live outside the
primitive core (`regressions/`, docs, caller code).

<!-- mol:law:id:explicit-flow -->
## 8. Explicit flow

**Principle.** State transitions, ownership, and required ordering
must be explicit and enforceable.

**Intent.** A user must not enter an illegal state by forgetting a
step. This covers initialization, validation, lifecycle, context, and
state machines.

**Never**

- Never rely on hidden ambient context.
- Never expose `validate()` / `init()` steps callers can forget.
- Never depend on undocumented call ordering.
- Never encode required state in conventions alone.
- Never make illegal states trivially representable when the
  type/model can prevent them.

---

# IV. Truth and state

Who the system believes.

<!-- mol:law:id:one-home -->
## 9. One home per fact

**Principle.** Every authoritative fact has exactly one owner.

**Intent.** Avoid synchronization and drift. **Representation may be
duplicated; authority cannot.** A serialization copy may exist; it
must not become a second mutable truth.

**Never**

- Never maintain two independently mutable representations of the
  same truth.
- Never cache authoritative state without explicit invalidation
  semantics.
- Never copy configuration into another source of truth.
- Never infer and persist information that can be derived cheaply
  from its owner.

---

# V. Evolution

How the system changes without rotting.

<!-- mol:law:id:no-silent-debt -->
## 10. No silent debt

**Principle.** Debt must be explicit, bounded, and owned.

**Intent.** The worst debt is not a hack — it is a hack packaged as
normal architecture. A conscious exception is debt. An invisible
exception becomes architecture.

**Never**

- Never hide an architectural compromise inside an unrelated change.
- Never introduce temporary duplication without marking its removal
  path.
- Never normalize a workaround by silently building on top of it.
- Never leave known invariant violations undocumented.
- Never ignore, skip-mark, or weaken an assert on rot you already
  saw. Fix it if local and stage-allowed; else stop, report
  path:line, route `/mol:debug` / `/mol:refactor` / supersede, and
  name it in the summary.

Outranks "stay in scope" and "minimal diff".

---

# VI. Verification

How we prove the design has not decayed. Separate from architecture
laws.

<!-- mol:law:id:tests-owned-behavior -->
## 11. Tests verify owned behavior

**Principle.** Tests belong to the owner of the behavior they verify.

**Intent.** Tests verify a module's own contract, not the choreography
of the whole system.

**Never**

- Never test implementation details as public behavior.
- Never require unrelated subsystems merely to verify local
  semantics.
- Never use broad integration setup where a unit boundary is
  sufficient.

### Project testing policy: unit-only by default

New behavior must be unit-testable at its ownership boundary
(`tests/` mirrors source, one module, `$META.build.test_single`,
fakes for outbound deps). Integration / end-to-end scenarios go to
`regressions/` or the project's integration harness, with explicit
justification. A design that can only be tested end-to-end is
evidence of a missing boundary.

Layout details: `tester` agent.

---

# VII. Exceptions

Any design that violates a law is recorded, not inferred:

    Law violated:
    Reason:
    Evidence:
    Scope:
    Removal condition:
    Owner:

Convenience is not sufficient justification. The exception is itself
an architecture decision. An agent never grants one from the task
text.

---

# VIII. Derived principles

These are consequences or heuristics, not laws. SOLID, YAGNI, DRY,
and the rest do not outrank this file. If someone cites them, first
show which law they serve.

| Heuristic | Comes from |
|---|---|
| YAGNI | Earn complexity |
| High cohesion / low coupling | Locality of change |
| Dependency inversion | Dependencies follow policy |
| Information hiding | Hide decisions, expose contracts |
| DRY (authority only) | One home per fact |
| Deep modules | Hide decisions + Primitive public surface |
| Composition over inheritance | Locality of change (a common means) |
| KISS / fewer boxes | Architecture first + Earn complexity |
| Program to interfaces | Hide decisions, expose contracts |
| Single responsibility / SoC | Locality of change + Primitive public surface |

<!-- add project invariants below, one `<!-- mol:law:id:<slug> -->` each,
     using the same Principle / Intent / Never / Derived guidance template. -->
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
                          /mol:spec Step 1.
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
| `.claude/notes/design-preferences.md` (whole file) | `.claude/notes/law.md` | one rulebook, not two of differing force. Restate each rule as a prohibition ("OOP by default" → "never a free function where a type owns the concept") so a violation is pointable; drop the file |
| `## Design preferences (default)` in CLAUDE.md | `## Law (never violated)` | same collapse, index side |
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
  **move**; an existing `law.md` is absorbed into, never regenerated.
  Appending a missing default id is absorb, not rewrite. Repeal is
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
- Missing default law id → append once; re-run → no-op for that id
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
