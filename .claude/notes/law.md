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

Discover an anti-pattern, failing test, broken invariant, or clear bug in a
file you are editing → **fix it or hard-stop**. Never ignore it as
"pre-existing", never skip-mark, never weaken an assert, never land work on top
of known rot in that file. Fix it now if stage-allowed; otherwise stop, report
path:line, and route `/mol:debug` / `/mol:refactor` / supersede. Do not widen
the edit to dependents you are not already changing.

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

**A version bump belongs to the release commit and nowhere else.** Never carry
one in a `feat:` / `fix:` / `refactor:` commit — `release-bump` stages, the
`release` skill owns the commit. A bump that rides along in a feature commit
leaves the manifests disagreeing at HEAD, and `bump_version.py` refuses a
mismatched tree, so the next `/mol:release` is blocked by a number nobody meant
to change. Before releasing, `python3 scripts/bump_version.py --check` must
print a single `current=` value; if it lists offenders instead, reconcile them
in one commit first.

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

<!-- mol:law:id:no-skill-copy-of-tool -->
## Never a skill that copies a tool

This marketplace is developer tooling. A molcrafts **product** capability
is an MCP tool on a molmcp plane — never a plugin skill here.

A skill is justified when the *procedure* is the hard part (deciding,
sequencing, gating across a repo's state). **Never** add a skill whose
body is a list of tool calls: that is a second, untested copy of the
tool. A tool enforces preconditions in code and returns a value; a
prompt only asks the model to remember.
