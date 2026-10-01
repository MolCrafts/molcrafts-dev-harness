---
name: bootstrap
description: "Use when initializing or repairing a repo harness (CLAUDE.md, .claude/notes, .claude/specs). Idempotent. Do not use for project source."
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

For CLAUDE.md, prefer a short router (`references/claude-md-template.md`). Don't turn it into a giant prompt.

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
  🟡. A default id present in `references/law-template.md` but
  absent from the project's `law.md` → 🟡 append that template body
  (never reword an id that already exists). A rule stated **only**
  outside `law.md` (a surviving `design-preferences.md`, an absolute in
  `notes.md`) → 🟡 promote; the body moves, CLAUDE.md keeps the
  one-liner. **Rule prose inlined in CLAUDE.md → 🟡**: move it, leave
  the one-liner. Never demote or reword a law during repair.
- **No second rules tier** — a `## Design preferences (default)` section
  or a surviving `.claude/notes/design-preferences.md` is 🟡: fold its
  rules into `law.md` as prohibitions (`references/migration-table.md`). Agents may
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
- Check against `references/migration-table.md`. Any `From (legacy)` path that exists → flag for § 5.

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
- managed-section template body from `references/claude-md-template.md`
- migration table from `references/migration-table.md`
- structural invariants (spec INDEX consistency, stable marker pairing)
- default law ids from `references/law-template.md` (`<!-- mol:law:id:* -->`)

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
- **default-law absorb** — for each `<!-- mol:law:id:<slug> -->` in
  `references/law-template.md` that is absent from the project's
  `.claude/notes/law.md`, **append** that id's template heading + body.
  Never rewrite, reorder, or reword a law whose id already exists.
- **orphan-marker repair** — only when context unambiguous; otherwise demote to manual TODO.
- **INDEX rebuild** — regenerate from actual spec files.
- **migration** — `git mv` (or `mv`) per `references/migration-table.md`; patch INDEX entries that referenced old path.

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

## Templates

The files this skill writes are the references below. Copy them. Do not reword a template in this procedure.

| File | Use |
|---|---|
| `references/claude-md-template.md` | Managed CLAUDE.md body. Refresh only between the markers. |
| `references/law-template.md` | Create-path `law.md`, and every default `<!-- mol:law:id:* -->` absorbed on update. |
| `references/migration-table.md` | The only legal layout moves. |
| `references/starters.md` | Fresh `.claude/notes/` and `.claude/specs/` trees. |

A default law id is present when `references/law-template.md` contains it.

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
- **Don't** invent migrations not in `references/migration-table.md`. That table is the version-spec for layout.
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

## Examples

These select this skill: `/mol:bootstrap`, "初始化 harness", "repair the harness". A feature spec is `/mol:spec`. A module map is `/mol:map`.

Empty repo, no `CLAUDE.md`. Path is create. Show the plan and wait for approval. Then write the router from `references/claude-md-template.md` and `law.md` from `references/law-template.md`. Do not write project source. Do not invoke other mol agents.

Healthy harness → one line: harness in place, nothing to change.

A default law id is missing → plan an append from `references/law-template.md` and wait for go-ahead. Dirty tree without `--allow-dirty` → do not update. A `replace` file → ask before writing it.
