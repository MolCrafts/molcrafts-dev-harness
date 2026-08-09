---
name: check
description: Marketplace self-check for this repo — deterministic dual-manifest validator, semantic contracts, skill/agent content janitor (safe rewrites in place), and Claude/Codex install smoke over every published plugin. Project-local; run after plugin, skill, agent, hook, or marketplace edits, and as the release gate.
argument-hint: "[<plugin>] [--static-only] [--no-write]"
---

# /check — Marketplace Self-Check

Project-local maintenance skill for `molcrafts-harness`. One skill owns the
full marketplace audit (structure + content + install smoke). Do not
reintroduce separate smoke or content-janitor skills. `/mol:release` uses
this skill as its `gate_skill`.

| Phase | What | Mutates source? |
|-------|------|-----------------|
| **Structure** | `scripts/validate_repository.py` + semantic contracts | no |
| **Content** | Skill/agent prose janitor | safe rewrites only (unless `--no-write`) |
| **Smoke** | Claude native validate + isolated Codex install | no (temp home only) |

## Arguments

```
[<plugin>] [--static-only] [--no-write]
```

- no plugin → every plugin in `.claude-plugin/marketplace.json` for structure semantic + content; smoke always whole marketplace
- `<plugin>` → semantic + content scoped to that plugin; deterministic gate + smoke still whole-repo
- `--static-only` → structure + content only; skip Claude CLI validate and Codex install
- `--no-write` → content phase reports only; do not patch skill/agent files

Unknown plugin name → print available names and stop. Unknown flags → print usage and stop.

## Procedure

### 1. Locate the marketplace root

Walk upward from cwd until `.claude-plugin/marketplace.json` exists. No match → BLOCK: run from this repository.

### 2. Structure — deterministic gate

```bash
python3 scripts/validate_repository.py --root <root>
```

Script owns: both marketplace schemas and plugin order; Claude/Codex manifest names, versions, fields, source paths; skill frontmatter/names/H1s/adapter directives; agent frontmatter, model tiers, read-only boundaries; hook JSON; no duplicated Codex skill trees.

Any script error → record as structure failure. Preserve exact path + message. Do not re-implement the script in prose. Continue only if you can still report later phases without invalid trees; otherwise stop after structure report.

**The script only ever reads under `plugins/`. You must cover the rest by
reading it.** Root `README.md`, `CLAUDE.md`, and `.claude/skills/*/SKILL.md`
ship in the same release as the plugins they name, and nothing validates them —
including this skill's own file, which is the release gate. On every run:

- every `/<plugin>:<skill>` mentioned in those files resolves to a skill that
  still exists (a removed plugin's commands may survive **only** inside an
  explicit migration table, and the table must say what replaced them);
- each project-local `.claude/skills/*/SKILL.md` has parseable frontmatter
  whose `name` equals its directory, with a non-empty `description` — a
  malformed one fails to load silently, with no error anywhere;
- no instruction hard-codes the plugin list. Read it from
  `.claude-plugin/marketplace.json`. Prose that names `mol` as though it were
  the only plugin is correct today and wrong on the next one — the coupling
  that made removing `molq`/`molexp` touch far more files than it should have.

### 3. Structure — semantic contracts

For each in-scope plugin, read README, manifests, `skills/*/SKILL.md`, `skills/CODEX.md`, agents, and rules those skills need. Judge only what syntax cannot establish:

- **Responsibility** — descriptions match behavior; one user-facing workflow per skill
- **Boundaries** — read-only vs write explicit; no two skills claim the same mutation/verdict
- **Delegation** — one axis per agent; producer/reviewer split matches `plugins/mol/rules/agent-design.md`
- **Safety** — approval, clean-tree, destructive, push, tag, release gates explicit and ordered
- **Git publish** — when auditing `mol` push/pr/release/tag, require alignment with `plugins/mol/rules/git-publish.md`:
  - branch push target = **`origin` (fork) only**; never branch-push to `upstream`
  - land on org default only via **`/mol:pr` → green checks → merge**
  - release publish steps include wait-for-checks and forbid merging red CI
  - pre-commit ≡ CI called out before push (via `/mol:push` / `/mol:ship push` / `/mol:ci-sync`)
  - skills that contradict this rule → 🔴 FIX REQUIRED
- **Progressive disclosure** — large rules live in shared rule files; skills link them
- **Cross-runtime fidelity** — `skills/CODEX.md` translates runtime only; does not change Claude-first workflow
- **Documentation truth** — READMEs list real capabilities only

Do not flag tone unless it hides an execution rule.

### 4. Content — skill & agent janitor

Inventory:

- `plugins/<plugin>/skills/<skill>/SKILL.md`
- `plugins/<plugin>/agents/<agent>.md`

Scope to `<plugin>` when given. Skip unparseable frontmatter (structure owns that).

Per file, enforce:

- **Single responsibility** — `description` is one job; multi-verb ("validate AND fix") → flag for split
- **Correct placement** — skills = user verbs; agents = orchestrator roles
- **Actionable language** — imperative "do X when Y"; flag motivational / vague prose; flag pure enumerable paragraphs that should be bullets (not causal prose)
- **Length discipline** — flag only when over ~500 words **and** full of non-actionable prose; genuine dual-skill weld → AMBIGUITY
- **No duplicate responsibility** — pairwise job overlap → flag
- **Shared rules in docs** — rule repeated in 3+ files → should live under `plugins/mol/rules/` (or plugin docs) and be referenced
- **Local rules stay local** — one-skill rule stays in that skill

**Safe rewrites** (unless `--no-write`): language normalization, delete repeated principles, remove motivational tone, replace vague phrasing with imperatives. Tighten language inside `description` / H1; **never** rename the skill or change `argument-hint` / contract meaning.

**AMBIGUITY only (never auto-apply):** split file, skill↔agent move, promote shared content, merge two files, change contract surface.

After writes: re-run the deterministic validator once. New error caused by this phase → `git checkout -- <path>` on the offender and re-flag as AMBIGUITY.

### 5. Smoke — cross-runtime install

Skip entire phase if `--static-only`.

#### 5a. Claude Code native validators

Require `claude` CLI. Validate the marketplace and every published plugin — read the plugin list from `.claude-plugin/marketplace.json`, never a hard-coded set:

```bash
claude plugin validate <root>
# then once per registered name (today that is just `mol`):
claude plugin validate <root>/plugins/<name>
```

Error → smoke BLOCK. Warnings → WARN (do not alone block PUBLISH-READY unless severity is error).

#### 5b. Isolated Codex install

Require `codex` CLI. Create a **new** temp dir + `codex-home/` child. Set `CODEX_HOME` only for these commands — never the user's real Codex home, never export into the parent shell.

```bash
CODEX_HOME=<temp>/codex-home codex plugin marketplace add <root> --json
CODEX_HOME=<temp>/codex-home codex plugin list
# then once per registered name (today that is just `mol`):
CODEX_HOME=<temp>/codex-home codex plugin add <name>@molcrafts --json
CODEX_HOME=<temp>/codex-home codex plugin list
```

Final list must show every registered plugin available, installed and enabled at its manifest version.

Inspect each installed plugin cache: `skills/CODEX.md`, every source `skills/*/SKILL.md`, `agents/`, `rules/`.

Note: marketplace-maintenance tooling (this `check` skill, `new-skill`, `release-bump`, `scripts/validate_repository.py`, `tests/`) is **project-local to this repo**, not a published plugin — it is exercised directly here, not through a Codex install.

Delete only this run's temp dir. Failed cleanup → WARN, not BLOCK.

Missing `claude` / `codex` CLI when not `--static-only` → smoke BLOCK with install hint (or skip that sub-gate with WARN only if the CLI is optional on this machine **and** document it; prefer BLOCK for release paths).

### 6. Report

Severity-sorted findings:

```text
<emoji> <path> — <message>
  Phase: structure | content | smoke
  Rule: <…>
  Action: none | applied | ambiguity   # content phase
  Fix: <one concrete recommendation>
```

Severity:

- 🚨 invalid metadata, unsafe destructive behavior, missing required gate, install hard-fail
- 🔴 broken workflow contract, duplicated responsibility, runtime incompatibility
- 🟡 drift / ambiguity / smoke warnings
- 🟢 optional cleanup

Smoke table (omit rows when `--static-only`):

| Gate | Result | Evidence |
|---|---|---|
| repository validator | PASS / BLOCK | error/warning counts |
| semantic | PASS / FIX REQUIRED | finding counts |
| content | PASS / FIX REQUIRED | applied / ambiguity counts |
| Claude marketplace + each registered plugin | PASS / WARN / BLOCK / SKIP | native summary |
| Codex marketplace / each plugin install | PASS / WARN / BLOCK / SKIP | version + cache |

**Verdict**

- `PUBLISH-READY` — deterministic PASS, no 🚨/🔴 structure or content, smoke not BLOCK (PASS or WARN or SKIP via `--static-only`)
- `FIX REQUIRED` — otherwise

Content AMBIGUITY alone does not force FIX REQUIRED unless it is 🚨/🔴; list outstanding AMBIGUITY counts in the summary.

End with:

```
/check: <PUBLISH-READY | FIX REQUIRED> — structure <…>, content <applied/ambiguity>, smoke <PASS|WARN|BLOCK|SKIP>
```

## Guardrails

- **Structure & smoke:** never edit plugin source, manifests, marketplaces, or user Claude/Codex config for those phases.
- **Content writes only** under `plugins/*/skills/**` and `plugins/*/agents/**`, and only safe language rewrites (or nothing with `--no-write`).
- **Never** invent architecture (merge/rename/move skills) — AMBIGUITY only.
- **Never** change contract surfaces (`description` meaning, H1 identity, `argument-hint` shape).
- **Never** install into the user's real Claude or Codex home; smoke uses a temp `CODEX_HOME` only.
- **Never** use network for marketplace sources; both are local paths.
- Keep deterministic rules in `scripts/validate_repository.py` only.
- Claude marketplace metadata remains authoritative over Codex.

## Idempotency

Clean tree + `--no-write` → same findings. Full run with writes on already-clean content → zero applied patches.
