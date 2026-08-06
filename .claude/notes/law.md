# Law — never violated

Every rule here outranks scope, minimal-diff, convenience, and everything in
`notes.md`. There is no "just this once". `CLAUDE.md` carries the one-line index
under `## Law (never violated)`.

Adding, changing, or repealing a law is the operator's act via `/mol:note`. No
skill deletes from this file — `/mol:compact` may dedupe and absorb into it,
nothing more.

<!-- mol:law:id:no-silent-debt -->
## No silent debt

Discover an anti-pattern, failing test, broken invariant, or clear bug in the
surface you touch or depend on → **prioritize or hard-stop**. Never ignore it as
"pre-existing", never skip-mark, never weaken an assert, never land work on top
of known rot. Fix it now if local and stage-allowed; otherwise stop, report
path:line, and route `/mol:debug` / `/mol:refactor` / supersede.

**Name it in the summary** — found, fixed, or blocking. Silence is a process
failure. This outranks "stay in scope" and "minimal diff".

<!-- mol:law:id:tests-unit-only -->
## `tests/` holds unit tests only

**Never write an e2e or full-stack scenario under `tests/`.** Here that means
the Codex/Claude install smoke stays in the `check` skill; `tests/` holds only
the stdlib structural guards, each runnable standalone via `python3 tests/<f>.py`
exactly as pre-commit and CI invoke them.

<!-- mol:law:id:dual-manifest-parity -->
## Dual-manifest parity

Every plugin ships a Claude manifest (`.claude-plugin/plugin.json`) and a Codex
manifest (`.codex-plugin/plugin.json`), and the two marketplace registries
(`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`) must
agree on name, version, and source for every entry. `scripts/validate_repository.py`
gates it at commit, in CI, and in the release gate.

Never hand-edit one side. Never let a version bump land in one registry only.

<!-- mol:law:id:git-publish -->
## Git publish invariants

- `origin` = the fork. Branch pushes only.
- `upstream` = canonical. Reached through a PR with green checks, merged —
  never pushed to directly.
- Pre-commit ≡ CI. Never merge red, never bypass a hook to land.

Full contract: [`plugins/mol/rules/git-publish.md`](../../plugins/mol/rules/git-publish.md).

<!-- mol:law:id:one-workflow-file -->
## One workflow file per skill

A skill's workflow body exists exactly once, in its `SKILL.md`.
`skills/CODEX.md` translates runtime differences only — it is never a second
copy of a workflow. Two copies of a workflow means one of them is already wrong.
