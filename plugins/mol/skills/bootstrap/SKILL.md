---
name: bootstrap
description: "Initialize or repair a repo harness (CLAUDE.md, .claude/notes, .claude/specs). Idempotent. Never writes project source."
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
- **No silent debt.** Rot in a file you are editing is fixed or reported with path:line.
- **Tests verify owned behavior.** Tests belong to the owner of the behavior; unit-only by default.

<add project invariants here — public APIs, on-disk formats, wire contracts.
Concrete prohibitions, one line each; body goes in law.md>


## Default workflow

For non-trivial work, prefer:
1. `/mol:spec` for a feature, `/mol:debug` for a bug
2. commit happens inside impl; push with `/mol:push`
3. `/mol:review` when you ask for it
4. `/mol:note` when a rule is decided

<!-- mol:bootstrap:managed end -->

<!-- Free-form additions below this line are preserved across re-runs.
     If a section grows past a screen, promote to .claude/notes/<topic>.md. -->
```

If user opts into `mol` plugin contract: prepend `mol_project:` YAML per `rules/claude-md-metadata.md`; route body references to chosen `notes_path` and `specs_path`. Set `arch.rules_section: "## Law (never violated)"` unless the project already has a richer Architecture heading (then point `rules_section` at that heading **and** keep the Law index in the managed body — agents always load `law.md` when present). Default `stage: experimental` (right answer pre-1.0; per `rules/stage-policy.md` allowed values are `experimental`, `beta`, `stable`, `maintenance`). If Step 1 found `1.x.y` on disk (`pyproject.toml` / `Cargo.toml` / `package.json`), surface and ask whether `stable` instead — still default `experimental` if no pick.

---

## .claude/notes/law.md (canonical body)

Written on create. On update, append any missing `<!-- mol:law:id:* -->`. Never reword an id that already exists.

Each law is one prohibition. A rule that names no forbidden design is not a law. Carve-outs live in § VII and name the subsystem. YAGNI, SOLID, and DRY do not outrank a law.

```markdown
# Software Engineering Laws

Every rule here outranks scope and convenience. CLAUDE.md indexes one line per law.
Adding, changing, or repealing a law is `/mol:note`. No skill retires a law.

<!-- mol:law:id:conceptual-integrity -->
## 1. Conceptual integrity

Never create a second abstraction, alias, or layer for a concept that already exists.

<!-- mol:law:id:architecture-first -->
## 2. Architecture first

Never add a layer whose only justification is later use or unmeasured performance.

<!-- mol:law:id:earn-complexity -->
## 3. Earn complexity

Never generalize, add a knob, or add an extension point without a present caller.

<!-- mol:law:id:locality-of-change -->
## 4. Locality of change

Never require unrelated modules to change together, and never introduce a cycle. A unit goes green with `$META.build.test_single` and fakes. If it needs the whole graph, the boundary is wrong.

<!-- mol:law:id:hide-decisions -->
## 5. Hide decisions, expose contracts

Never leak representation, lifecycle, or storage across a boundary.

<!-- mol:law:id:dependencies-follow-policy -->
## 6. Dependencies follow policy

Never let domain code depend on UI, a serialization format, a language binding, or a framework that then defines the semantics.

<!-- mol:law:id:primitive-surface -->
## 7. Primitive public surface

Never ship an all-in-one façade or a second public name that becomes its own contract.

<!-- mol:law:id:explicit-flow -->
## 8. Explicit flow

Never rely on hidden context or on a step the caller can forget.

<!-- mol:law:id:one-home -->
## 9. One home per fact

Never keep two writable copies of the same fact. A serialization copy is fine; a second owner is not.

<!-- mol:law:id:no-silent-debt -->
## 10. No silent debt

Rot in a file you are editing is fixed or reported with path:line. Never skip-mark it, never weaken an assert, never widen the edit to files you are not already changing.

<!-- mol:law:id:tests-owned-behavior -->
## 11. Tests verify owned behavior

Tests live with the owner of the behavior. `tests/` is unit tests of one module. Broader scenarios go under `regressions/` with a stated reason.

# VII. Exceptions

A violation is recorded here, naming the law, the subsystem, the evidence, and the removal condition. An agent does not grant one.

# VIII. Heuristics

YAGNI, SOLID, and DRY are hints. They do not beat a law above.

<!-- project invariants: one `<!-- mol:law:id:<slug> -->` and one prohibition each -->
```

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

- **Don't** invoke other mol agents. This skill is self-contained.
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
