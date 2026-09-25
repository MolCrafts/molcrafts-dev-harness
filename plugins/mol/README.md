# mol

Shared molcrafts project-workflow skills and common-axis agents,
built around **harness engineering**: give the repository a small,
well-shaped harness — principled boundaries, predictable layers, and
just enough scaffolding to make safe defaults the obvious move — so
the *next* agent that walks in succeeds without re-deriving the rules.

`mol` is the day-to-day toolbox: spec, implement, review, fix,
refactor, simplify, ship. The harness *itself* (CLAUDE.md, `.claude/notes/`,
`.claude/specs/`) is installed and maintained by `/mol:bootstrap`.

Claude Code is the canonical runtime. Codex loads the same skills through the
plugin's native `.codex-plugin/plugin.json`; `skills/CODEX.md` translates tool,
subagent, and plugin-path concepts without duplicating workflow bodies.

Skills adapt to each project by reading a `mol_project:` YAML
frontmatter block at the top of the project's `CLAUDE.md` — so one
plugin serves Atomiverse, molpy, molexp, molrs, molvis, molq, and
molnex without per-project forks.

## Install

### Claude Code (primary)

```
/plugin marketplace add https://github.com/MolCrafts/molcrafts-dev-harness
/plugin install mol@molcrafts-dev
```

For local development:
`/plugin marketplace add <path-to-molcrafts-dev-harness-checkout>`.

### Codex

```bash
codex plugin marketplace add MolCrafts/molcrafts-dev-harness
codex plugin add mol@molcrafts-dev
```

For local development:
`codex plugin marketplace add <path-to-molcrafts-dev-harness-checkout>`.
Restart Codex and test updated skills in a new thread.

## Four-zone layering (active vs passive)

Every well-shaped repository the `mol` plugin works on separates four
kinds of content. Top-level layout follows Claude Code's project
convention (`.claude/` is the canonical project folder); the
active/passive split lives inside `.claude/`.

| Zone (path)              | Purpose                                                                                 |
|--------------------------|-----------------------------------------------------------------------------------------|
| `docs/`                  | public-facing documentation (tutorials, API, user guides)                               |
| `.claude/notes/`         | **passive** internal context (project notes, blueprint, decisions, contracts, handoffs, rubrics, debt, open questions) — outlives any feature |
| `.claude/specs/`         | **active** runtime artifacts — alive, ticked off as `/mol:impl` works, deleted on completion |
| `.claude/agents/`, `.claude/skills/`, `.claude/hooks/`, `.claude/settings.json` | Claude Code's own runtime configuration |
| `CLAUDE.md`              | thin entry router — points to where things live; no manual                              |

> Note: `.claude/notes/` (passive *project knowledge*) is a different
> folder from `.claude/agents/` (Claude Code's *agent definitions*). The
> naming is deliberately distinct — "notes" = what the agent reads,
> "agents" = what the agent *is*.

Notes are kept; specs are intentionally ephemeral. Full rules in
[`rules/design-principles.md`](rules/design-principles.md). Run
`/mol:bootstrap` to verify compliance.

## Conversation modes

Every skill runs in one of two modes, defined in
[`rules/model-policy.md`](rules/model-policy.md):

- **Advisor** — deliverable is words; main conversation authors;
  agents gather evidence (`discuss`, `grill`, `review`, `test`, …).
- **Orchestration** — deliverable is artifacts; main loop
  plans/routes/gates; producers write (`implementer` / `tester` /
  `documenter`; never production source in the main loop).

Default skills are **model-invoked** (user, free-form, or sibling).
User-only only when nothing else may fire them (`release`). Form:
**one verb = one skill + agents** — not entry/body dual skills. See
[`rules/design-principles.md`](rules/design-principles.md) § 2–2.6.

Agents do not pin a model. The host assigns it (`rules/model-policy.md`).

## Skills

All `mol` skills require a `mol_project:` frontmatter in CLAUDE.md
(see [`rules/claude-md-metadata.md`](rules/claude-md-metadata.md)) and
fail fast with an adoption hint when it is missing. To create
CLAUDE.md and the surrounding harness, run `/mol:bootstrap`
first.

One frontmatter field worth knowing about up front:
`mol_project.stage` — `experimental` (default) / `beta` / `stable` /
`maintenance` — governs how aggressive the writing skills and
reviewers may be when touching existing code. `experimental` lets
`/mol:impl` rewrite legacy on sight; `stable` requires deprecation
shims for public-signature changes; `maintenance` makes
`/mol:refactor` and new-feature `/mol:impl` refuse outright (only
`/mol:debug` proceeds). Full matrix in
[`rules/stage-policy.md`](rules/stage-policy.md).

Skills group by intent. Each row shows what it does, when to
reach for it, and a one-line example.

### 0 — Harness lifecycle

| Skill | What | When | Example |
|---|---|---|---|
| `/mol:bootstrap` | Create or repair CLAUDE.md, `.claude/notes/`, `.claude/specs/`. Writes a short `law.md` (one prohibition per id). Appends a missing id; never rewords an existing one. Never writes project source. | First harness, or after it drifts. | `/mol:bootstrap` |

### 1 — Plan & specify

| Skill | What | When | Example |
|---|---|---|---|
| `/mol:discuss <topic>` | Trade-off discussion. Converge writes a requirement and stops. Does not call grill or spec. 8-turn cap. | The requirement is not decided. | `/mol:discuss should /mol:perf own remote bench runs?` |
| `/mol:grill` | One question at a time. Spec calls it once, `post-librarian`, before the draft. Also when you ask. Does not write and does not start impl. | Inside spec, or 盘问. | `/mol:grill` |
| `/mol:spec` | Librarian, then one grill, then `spec-writer`, then architect design-mode. No second grill. Clean → `/mol:impl-all`. Split only when Tasks > 10. | 落盘 / 写 spec. | `/mol:spec add Morse bond potential to molpy` |
| `/mol:litrev` | Literature + reference-implementation review (gated on `mol_project.science.required`). Returns equations, validation targets, open questions. | Before specifying a domain-critical feature. | `/mol:litrev Nose-Hoover thermostat` |

### 2 — Implement (writes code)

| Skill | What | When | Example |
|---|---|---|---|
| `/mol:impl` | TDD with `test_single`. Docs Mode A once, before the commit, only when a `docs` criterion is pending. Does not call simplify or perf. Scientific / performance criteria stay for `/mol:perf`. | After `/mol:spec`. | `/mol:impl morse-bond` |
| `/mol:impl-all <prefix>` | Drive `<prefix>-NN-*`. Reads each spec's status in-process. Chain end: `check` + full suite once, then `/mol:commit` once, specs deleted in that commit. | A split feature, or the default entry spec uses. | `/mol:impl-all morse-bond` |
| `/mol:close <slug>` | Standalone. Finish a spec left at `code-complete` (scientific / performance / docs criteria). Not called by impl or impl-all. | After `/mol:perf`, or when those criteria can be attested. | `/mol:close morse-bond` |
| `/mol:debug [--diagnose-only]` | The bug loop, in one skill: reproduce → diagnose via `debugger` → minimal patch via `implementer` → verify. Calls `tester` for a regression test when the root cause suggests a missing one. Proceeds at every `mol_project.stage` (bugs are always in scope). `--diagnose-only` stops at the root-cause report and edits nothing. | When a test fails or a bug is reported. | `/mol:debug energy NaN at zero distance` &nbsp;·&nbsp; `/mol:debug --diagnose-only segfault in dipole kernel` |
| `/mol:refactor` | Restructure code while preserving all architectural invariants. Snapshot → incremental change → re-verify. Calls `architect` pre and post. | When the structure needs to change but behavior must not. | `/mol:refactor split forces module by backend` |
| `/mol:ci-sync [<root>]` | Audit and repair CI / pre-commit parity — write-mode counterpart of the `ci-guard` agent. Delegates the audit to `ci-guard`, then patches `.pre-commit-config.yaml` and the CI workflow so both sides run identical commands from `mol_project.build`; scaffolds both files for projects that have neither. Writes config files only, never source. | When CI catches things pre-commit missed (or vice versa); when adopting a project with no CI at all. | `/mol:ci-sync` |
| `/mol:simplify` | Claude Code `/simplify` moment: green diff, before commit. Reuse, simplification, efficiency, altitude. Applies fixes. Not a bug hunt. Impl does not call it. | After the code is green, or 整理代码. | `/mol:simplify` |
| `/mol:ui [<stage>]` | MolCrafts frontend design system. Detects the archetype (`viewer` like molvis / `workbench` like molexp), audits the surface against the shared visual language **and information design**, then applies **one ladder stage** per run: `skeleton` → `info` → `tokens` → `components` → `de-card` → `states` → `motion`. Stage `info` owns page jobs, fact ownership, overview vs detail, and Project→Experiment→Run priority (`references/information-design.md`). Delegates the judgment axis to the `web-design` agent, drives an optional screenshot pass through whatever browser-automation MCP is installed, records the result in `.claude/notes/ui-guidelines.md`. Hard-refuses shared cross-product UI packages and Tailwind presets. **Tier C** free-form (前端设计 / UI 改造 / 太像模板了 / de-shadcn / information design / dashboard). | When a frontend looks like a shadcn template, entity overviews are card soup / KPI walls, or before growing a product's component vocabulary. | `/mol:ui audit` &nbsp;·&nbsp; `/mol:ui info` &nbsp;·&nbsp; `/mol:ui tokens` |

### 3 — Review (read-only)

| Skill | What | When | Example |
|---|---|---|---|
| `/mol:review` | Default axes: `architect` + `janitor`. The main session renders the verdict. Other axes (`perf`, `docs`, `ux`, `api`, `science`, `numerics`, `visual`, `security`, `ffi`) only with `--axis`. | You asked for a review. | `/mol:review` &nbsp;·&nbsp; `/mol:review --axis=security` |
| `/mol:test` | Run the suite via `mol_project.build.test`; delegate to `tester` in **analyze-mode** for category coverage and tolerance discipline. (Test *writing* lives in `/mol:impl` and `/mol:debug`.) | When you want to know the state of the suite + what categories are missing. | `/mol:test` &nbsp;·&nbsp; `/mol:test tests/forces/` |
| `/mol:ship <push\|merge>` | Read-only. `push` runs the test suite once (pre-commit already ran). `merge` runs check + the suite once. `commit` is not a tier. | Before push, or to mirror CI before merge. | `/mol:ship merge` |

### 4 — Runtime evaluator

| Skill | What | When | Example |
|---|---|---|---|
| `/mol:perf <slug>` | Bench repo for `scientific` and `performance` criteria. After the functional commit, before `/mol:close`. Impl does not call it. | A spec left `code-complete` on those criteria. | `/mol:perf morse-bond` |

### 4b — Scientific HPC / CUDA (design & optimize)

| Skill | What | When | Example |
|---|---|---|---|
| `/mol:cuda [path]` | GPU-native scientific CUDA C++ design/impl/opt — SIMT mapping gate, numerical reference, CUDA-X library choice, profiler-driven one-change experiments. Not ML/cuTile; not domain QC theory. | CUDA kernels, reductions, stencils, pair/neighbor work, irregular screened tasks. | `/mol:cuda redesign ERI kernel mapping` |
| `/mol:hpc [path]` | CPU scientific HPC design/impl/opt — OpenMP, MPI, SIMD, cache layout, numerical reference, same experiment-loop discipline as `/mol:cuda`. | CPU backend hot paths, vectorization, parallel reductions. | `/mol:hpc src/cpu/` |

### 5 — Documentation & knowledge

| Skill | What | When | Example |
|---|---|---|---|
| `/mol:docs` | Mode A: docstrings, before the feature commit, when a `docs` criterion is pending or you ask 补文档. Mode B: a tutorial, only when you ask 写教程. | Public API text. | `/mol:docs molpy.forces.morse` |
| `/mol:note` | **Harness knowledge sync** (not append-only). Reconciles a decided rule across `CLAUDE.md` + `.claude/notes/**`: supersede/delete fossils, stale sweep, single canonical home, promote stable rules. New decision wins on conflict. Free-form: 记下来 / 约定变了 / we decided / supersede. | When a convention is decided or an old note is wrong and would pollute agents. | `/mol:note use n_atoms (not natoms)` &nbsp;·&nbsp; `/mol:note supersede: forces live under molpy.potentials` |
| `/mol:map [<scope>]` | Build or refresh `.claude/notes/architecture.md` — the passive project blueprint (modules, public surface, style summary, layer roles) consumed by `librarian` during `/mol:spec` Step 1. Delegates inventory to the `architect` agent; diffs against the existing blueprint; writes automatically when the inventory drifts (no approval wait). Idempotent — a re-run with no drift exits without writing. | After significant architectural changes; before a sprint of new specs that need accurate placement / reuse advice. | `/mol:map` &nbsp;·&nbsp; `/mol:map src/forces/` |
| `/mol:compact [<scope>]` | **Harness compaction** — `/mol:note`'s reconcile applied to every topic at once. Clusters every rule across `law.md` + `CLAUDE.md` + `AGENTS.md` + `.claude/notes/**` + `.claude/specs/INDEX.md` by topic and leaves **one live statement each**; superseded / duplicate / finished get deleted. Conflicts resolve against `law.md`, then **against the source** — of two competing requirements the current one is the one the code already follows — then git recency. Writes the harness only; source is read-only evidence, and an uncontested rule the code violates is reported as debt, never repealed. Approval-gated; can never delete a law. Free-form: 压缩记忆 / harness 臃肿了 / 清理过时的 / 只保留最新的. | When the harness has bloated — the same rule in four files in three versions, finished migrations still described as pending. | `/mol:compact` &nbsp;·&nbsp; `/mol:compact .claude/notes/release.md` |

### 6 — Git workflow (writes / pushes)

A linear **PR-first** chain. Shared invariants live in
`plugins/mol/rules/git-publish.md`. Each step gates with `/mol:ship`
underneath.

**Remotes:** `origin` = your **fork** (only place branches are pushed);
`upstream` = **canonical MolCrafts repo** (land via PR + merge only —
never `git push upstream <branch>`). Pre-commit must mirror CI so
failures are caught before any push; that keeps org-repo Actions green
and avoids failure emails to all watchers.

```
/mol:commit  →  /mol:push (origin)  →  /mol:pr  →  green checks  →  merge  →  [/mol:tag]
```

| Skill | What | When | Example |
|---|---|---|---|
| `/mol:commit [<msg>]` | Stage + `pre-commit run` once + commit. Does not call `/mol:ship`. Does not push. | A local commit outside impl. | `/mol:commit` |
| `/mol:push [<branch>]` | Push to **origin only** (fork), after full `pre-commit run --all-files` + `/mol:ship push` (CI parity). Auto-commits if dirty. **Never** pushes branches to `upstream`. | Whenever you'd run `git push` to your fork. | `/mol:push` |
| `/mol:pr [<title>]` | Open a PR from `origin` → `upstream/<default_branch>` via `gh`. Calls `/mol:push` first. The **only** legal path onto the org default branch. Drafts title + body; idempotent if PR already open. | When the branch is ready to land on the canonical repo. | `/mol:pr` |
| `/mol:release <patch\|minor\|major>` | Release end-to-end for **any `mol*` repo** — libraries and the `molcrafts-dev-harness` marketplace. Dep/docs/harness gates (or a project's `mol_project.release` `gate_skill`) → version bump (or `bump_skill`) → commit → push(origin) → pr → **wait green checks** → merge → `/mol:tag`. | Shipping molrs / molpack / molpy / … to crates.io · PyPI · npm, or cutting a marketplace release. | `/mol:release patch` |
| `/mol:tag [<tag>]` | Push an existing release tag (created by `/mol:release`) to **upstream** so a `on: push: tags:` workflow fires. Refuses orphan tags and force overwrites. | After the release PR has merged. | `/mol:tag v0.2.0` |

## Common workflows

```
/mol:spec <feature>          # librarian + spec-writer + design-mode → impl-all
/mol:debug <bug>             # local bug: one implementer, new test then patch
/mol:push && /mol:pr         # origin only, then PR — never push upstream
```

`/mol:discuss` and `/mol:grill` only when you ask. `/mol:review` defaults to architecture + hygiene. `--axis=` adds security, perf, science, ffi, and the other axes. `/mol:ship merge` mirrors CI locally.

## Agents

Skills call agents. The host picks the model. One axis each. Detail: [`rules/agent-design.md`](rules/agent-design.md).

| Agent | Axis |
|---|---|
| `architect` | layer compliance; design-mode on a spec; inventory for `/mol:map` |
| `librarian` | placement and reuse at spec time |
| `spec-writer` | spec text; the skill persists it |
| `implementer` | one task, or small/fix mode (new test, then patch) |
| `tester` | MEDIUM/LARGE tests; analyze-mode |
| `debugger` | root cause; does not patch |
| `janitor` | hygiene findings |
| `documenter` | docstrings and tutorials |
| `optimizer` | hot-path findings |
| `scientist` | equations and references |
| `compute-scientist` | numerical stability |
| `pm` | public API and breaking change |
| `undergrad` | first-use friction |
| `user` | doc-first composition across molcrafts libraries |
| `web-design` | frontend visual and states |
| `security-reviewer` | attack surface |
| `ffi-guard` | FFI boundary |
| `ci-guard` | CI vs pre-commit drift (`/mol:ci-sync`) |
| `harness-actor` | `/mol:evo` trial arm |
| `harness-observer` | `/mol:evo` blind score |

Findings: `🚨` / `🔴` / `🟡` / `🟢` plus `file:line`. `/mol:review` turns them into BLOCK, REQUEST CHANGES, or APPROVE.

## Design contract

Harness form: **one verb = one skill + agents**; skill → skill only
for a different verb. Producer vs reviewer:
[`rules/agent-design.md`](rules/agent-design.md). Full rules + audit:
[`rules/design-principles.md`](rules/design-principles.md). Project
check: `/mol:bootstrap`; marketplace self-check: project-local `/check`.

## Adopt in a project

1. Run `/mol:bootstrap` from the project root. It inspects the
   repo, asks what to add, and installs only what's justified —
   including the `mol_project:` frontmatter if you opt in.
2. Smoke-test with `/mol:bootstrap` (re-run to verify harness health)
   and `/mol:review --axis=arch` (architecture).

Each project's harness is rewritten in place rather than migrated in
phases — this is continuous iteration.

## License

MIT — see the root [LICENSE](../../LICENSE).
