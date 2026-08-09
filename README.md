# MolCrafts plugin marketplace

A Claude Code-first plugin marketplace for the MolCrafts workspace, with a
native Codex marketplace and manifests that reuse the same skill workflows.
Claude Code remains the canonical runtime and project-harness format.

It supports Atomiverse, molpy, molexp, molrs, molvis, molq, and molnex, built around
**harness engineering**: small, well-shaped harnesses with principled
boundaries (public docs / passive internal context / runtime + active
artifacts / thin router) so the next agent that walks in succeeds
without re-deriving the rules.

**This marketplace is developer tooling only.** It ships exactly one plugin,
`mol` — the code-project harness. Product capabilities are MCP tools on
[molmcp](https://github.com/MolCrafts/molmcp), not skills here: job queues are
the `molq` plane (`list_jobs`, `submit_job`, …) and experiment-data workspaces
are the `molexp` plane (`plan_adoption`, `run_adoption`, `adoption_status`,
`ingest_metrics`). Agents call those tools directly; there is no slash command
in between and no prompt re-deriving what a tool already does.

## Layout

```
molcrafts-harness/
├── .github/workflows/validate-plugins.yml # stdlib-only metadata CI
├── .claude-plugin/marketplace.json   # marketplace registry
├── .agents/plugins/marketplace.json  # native Codex marketplace registry
├── plugins/
│   └── mol/                          # workflow skills + single-axis agents (counts live in marketplace.json)
│       ├── .claude-plugin/plugin.json
│       ├── .codex-plugin/plugin.json
│       ├── README.md
│       ├── rules/
│       │   ├── claude-md-metadata.md # mol_project frontmatter contract
│       │   ├── design-principles.md  # harness layering + design rules
│       │   ├── agent-design.md       # producer/reviewer split rationale
│       │   ├── model-policy.md       # conversation modes + agent model tiers
│       │   ├── evaluator-protocol.md # planner/generator/evaluator contract
│       │   ├── large-spec-split.md   # auto-split rule for oversized specs
│       │   └── stage-policy.md       # mol_project.stage behavior matrix
│       ├── skills/                   # shared Claude/Codex skills + one CODEX.md runtime adapter
│       └── agents/                   # one .md per agent (incl. librarian, implementer, spec-writer)
├── scripts/                          # LLM-free repo tooling (CI-callable)
│   ├── validate_repository.py        # deterministic dual-manifest validator
│   └── bump_version.py               # release version bump across all manifests
├── tests/                            # stdlib structural guards (CI runs these)
├── CLAUDE.md                         # this repo is itself a mol* project
├── .claude/
│   ├── skills/                       # project-local maintenance: check, new-skill, release-bump
│   └── notes/                        # passive project knowledge
├── LICENSE
└── README.md
```

## Plugins

| Plugin | Purpose |
|---|---|
| [`mol`](plugins/mol/README.md) | Day-to-day **code** project work (planner→generator→evaluator harness): bootstrap, spec, impl, review, git chain, …. Adapts via `mol_project:` frontmatter. |

One plugin, on purpose. A skill earns its place when the *procedure* is the
hard part — deciding, sequencing, gating. Driving a queue or copying a
directory is not that: it is work a tool does better, with real preconditions
and a real return value instead of a prompt hoping the model follows steps.
Those live in molmcp:

| Was | Is now |
|---|---|
| `/molq:jobs`, `/molq:submit`, `/molq:cancel` | `molmcp serve molq` → `list_jobs`, `get_job`, `job_logs`, `list_destinations`, `list_queue`, `submit_job`, `cancel_job` |
| `/molexp:adopt-workspace` | `molmcp serve molexp` → `plan_adoption`, `run_adoption`, `adoption_status`, `ingest_metrics` |

Maintaining the marketplace itself is not a plugin: this repo is a `mol*`
project (`CLAUDE.md`) with project-local skills in `.claude/skills/`
(`/check`, `/new-skill`, `/release-bump`) and deterministic tooling in
`scripts/` + `tests/`. Release it with `/mol:release` like any other `mol*`
repo.

## Install

### Claude Code (primary)

```
/plugin marketplace add https://github.com/MolCrafts/molcrafts-harness
/plugin install mol@molcrafts
```

For job queues and experiment-data workspaces, connect the molmcp planes
instead — `molmcp client claude -o ~/.claude.json` writes the config for all
of them.

For local development, `/plugin marketplace add <path-to-this-checkout>`
works too. Restart the session or `/reload-plugins` to pick up new
skills.

### Codex

```bash
codex plugin marketplace add MolCrafts/molcrafts-harness
codex plugin add mol@molcrafts
```

For local development, run
`codex plugin marketplace add <path-to-this-checkout>`. Restart Codex and use a
new thread after changing plugin skills so the installed plugin cache is
refreshed. Codex reads `.agents/plugins/marketplace.json` and each plugin's
`.codex-plugin/plugin.json`; it does not rely on the legacy Claude marketplace
fallback.

Both platforms load the same `plugins/<plugin>/skills/` files. Codex-specific
tool, subagent, and path translation lives in `skills/CODEX.md`, so workflow
changes remain single-source.

## Adopt in a project

1. Install `mol` (above).
2. From the project root, run `/mol:bootstrap`. It inspects the
   repo, asks what to add, and installs only what's justified
   (CLAUDE.md + `.claude/notes/` for passive context + `.claude/specs/`
   for active work, plus the `mol_project:` frontmatter when you opt
   into the mol contract).
3. Smoke-test with `/mol:bootstrap` (re-run to verify harness health)
   and `/mol:review --axis=arch` (architecture).

Each project's harness is rewritten in place rather than migrated in
phases — this is continuous iteration. When the plugin is upgraded
later, run `/mol:bootstrap` to refresh templates and frontmatter.

## License

MIT — see [LICENSE](LICENSE).
