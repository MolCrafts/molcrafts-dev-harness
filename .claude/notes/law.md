# Law — never violated

Every rule here outranks scope, minimal-diff, and convenience. There is no
"just this once". `CLAUDE.md` carries the one-line index under
`## Law (never violated)`.

Adding, changing, or repealing a law is the operator's act via `/mol:note`. No
skill retires a law on its own judgment: `/mol:compact` may dedupe and absorb
into this file freely, but may only *propose* a deletion, and only on evidence
that the law was overturned on record or that the thing it governed no longer
exists.

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
manifest (`.codex-plugin/plugin.json`). **Version lives in the manifests** —
the two must never disagree, and the Claude registry entry must match its
manifest.

The **Codex registry** (`.agents/plugins/marketplace.json`) carries name,
source, policy, and category — **never `version` or `description`**, which
belong to the manifest. Both registries must point a plugin at the same source
directory.

`scripts/validate_repository.py` gates all of it — registry shape at
:262-264, manifest and entry parity at :286-289, source path at :296-300 —
at commit, in CI, and in the release gate.

Never hand-edit one side. Never let a version bump land in one manifest only.

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
