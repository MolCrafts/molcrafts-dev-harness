# Agent design — producer vs reviewer split

This document explains why some `mol` agents are write-capable and
others are read-only. The asymmetry is principled, not accidental.

## Two-layer model

**One verb = one skill + 0..N agents.** Nest is skill → agent, not skill → skill for the same verb.

| Layer | Who | Job |
|---|---|---|
| **Skill** | thin orchestrator | args, order, gates, multi-turn, handoffs, when to delegate |
| **Agent** | single-axis specialist | findings or artifacts on that axis only |

Skills compose agents. Agents never call agents (O2). Skill → skill only for a *different* verb (e.g. impl → simplify).

## Producer vs reviewer

The agents fall into two kinds, distinguished by **what their
primary output is**:

### Producer agents

Their primary deliverable is **content** — markdown, code, or
artifacts — not findings. They split into two sub-kinds by where
the persistence happens:

#### Producer-write (own write tools)

Persist the artifact themselves. Use when there is no
user-approval gate between drafting and persisting.

| Agent | Produces | Why writing belongs in the agent |
|---|---|---|
| `tester` | test code (RED tests) | the produced test *is* the verification mechanism — running it is the gate. No external orchestration needed for the write itself. |
| `implementer` | production source (one spec task / one fix patch); in `/mol:debug` **fix mode**, also the one new regression test that fix needs | the RED test *is* the gate for the write — the same mechanism that justifies `tester`'s write access; the calling skill still runs the gate and owns revert. |
| `documenter` | docstrings + tutorials | docs don't change runtime behavior — zero behavioral risk. |

#### Producer-return (no write tools)

Draft the artifact and return it as text; the orchestrating
skill persists after a gate (user approval, acceptance check).
Use when the artifact must be reviewable before it lands on
disk.

| Agent | Produces | Why the skill writes, not the agent |
|---|---|---|
| `spec-writer` | spec body + acceptance.md | binding contract; agent drafts, skill persists. |

### Reviewer agents (read-only)

Their primary deliverable is **findings about content** —
`<emoji> file:line — message` tuples. Applying findings as patches
is workflow-level work that needs build/test gates, regression
revert, and cross-cutting judgment — that's skill-layer concerns.

| Agent | Reviews | Write-mode counterpart skill |
|---|---|---|
| `architect` | module boundaries / layer rules / `law.md` shape (review mode on source; **design mode** on a spec draft; inventory mode for `/mol:map`) | `/mol:refactor` (with architect pre/post check); `/mol:spec` persist gate (design mode) |
| `debugger` | failure root cause + fix recommendation | `/mol:debug` Step 3 (`implementer` applies the recommendation; debugger never patches) |
| `optimizer` | perf anti-patterns | `/mol:debug` (perf-driven fix) |
| `scientist` | equations / units / refs | `/mol:debug` (corrected math) or `/mol:spec` (refine derivation) |
| `compute-scientist` | numerical stability / HPC | `/mol:debug` (with regression test from `tester`) |
| `pm` | public-API ergonomics / breaking change | `/mol:refactor` (with deprecation path) |
| `undergrad` | new-user friction | `/mol:docs` (Mode B tutorial) or `/mol:debug` (error message) |
| `user` | doc-first learnability + cross-library composition (no glue) | `/mol:docs` (fix/complete docs) or `/mol:spec` (close a composition seam) |
| `web-design` | visual / a11y / state coverage | `/mol:debug` (one fix per finding) |
| `security-reviewer` | attack surface | `/mol:debug` (sanitize / parameterize / authorize) |
| `ffi-guard` | FFI-boundary safety | `/mol:debug` (error-code path, handle conversion) or `/mol:spec` (API-shape change) |
| `janitor` | hygiene / tech debt | **`/mol:simplify`** (the dedicated cleanup applier) |
| `ci-guard` | CI parity | **`/mol:ci-sync`** (config parity repair) / `/mol:debug` / `/mol:impl` per the agent's `Suggested agent:` route |
| `librarian` | spec-time placement + reuse consult (fixed advisory report) | n/a — advice consumed by `/mol:spec`; the blueprint it reads is refreshed by `/mol:map` |
| `reviewer` | aggregator (findings → table + verdict) | n/a — itself a reviewer over reviewers |

## Why not let `optimizer` or `janitor` write?

Three reasons, in priority order:

1. **The patch isn't 1:1 with the finding.** A perf finding "this
   loop should vectorize" maps to many possible patches —
   `np.einsum` vs explicit broadcasting vs migrating to
   `numba` — and the right choice depends on benchmark numbers,
   call-site context, and whether the test suite has a perf
   guard. That's orchestration.

2. **The apply step needs a gate.** Every behavior-affecting
   change must run `$META.build.test` and revert on regression.
   That's a skill-level loop. Letting an agent own the loop
   conflates "expert in axis X" with "expert in our build
   system."

3. **Two layers is easier to test and refactor.** Single-axis
   agents have a stable contract (input: scope; output:
   findings). Skills can be rewritten without touching agents,
   and vice versa. Adding write capability inside agents would
   couple the layers.

## Why is `tester` the exception?

A test is **its own verification**. Writing a test does not
require the orchestrator to ask "did we regress?" — the test
*is* the regression check. So the "needs a build/test gate"
argument doesn't apply to test files specifically.

Same shape for `documenter`: docs don't affect runtime, so no
gate is needed.

`implementer` extends the same argument to production code:
unlike a reviewer finding, a spec task *is* 1:1 with its patch,
and the gate already exists — the RED test written by `tester`
plus the calling skill's gate. The skill still owns
tick, commit, and revert; `implementer` never does any of the
three.

**Fix mode** (`/mol:debug` small-fix path) is the one place a
single `implementer` writes both the regression test and the patch.
A local bug is one reading of one code region; splitting it across
`debugger` → `tester` → `implementer` makes three agents read the
same lines. The order still holds inside the one invocation: the new
test is written first and must fail for the reported reason before
any production line changes. Existing tests are never edited, and a
feature (spec) task always keeps `tester` and `implementer` separate.

## Handoff packet (every delegation)

An agent starts with no context, so whatever the orchestrator does not
hand over, the agent re-discovers by reading — measured at 50–64 tool
calls / ~11 min for a RED-test round without pointers versus 17–28 calls
/ 2–4 min with them. The orchestrator reads once and hands over:

1. **Pointers** — every `file:line` range the work touches or depends
   on (the symbol to change, its callers, the fixture to copy, the
   existing test module), not just a spec path.
2. **Shapes** — the exact types, signatures and names the agent must
   use or produce (the API a RED test assumes; the API an implementer
   must satisfy).
3. **Assertions** — for a test round, each test's input and expected
   value whenever the spec, a diagnosis or the orchestrator already
   knows it. The agent derives only what nobody has derived yet.
4. **Prior findings verbatim** — a debugger report, a previous agent's
   notes, a reviewer's `file:line` — never paraphrased away.
5. **The verification command, and what not to run** — the inner loop
   is `$META.build.test_single` (see "Verification tiers" below).

The agent reads the pointed ranges plus immediate call sites. When the
pointers turn out insufficient it may search further, and it names the
missing pointer in its report so the orchestrator's next packet carries
it.

## Verification tiers

Each tier runs once per its trigger, never earlier:

| Trigger | Runs | Never runs here |
|---|---|---|
| each task / fix inside a loop | `$META.build.test_single` on the touched units | `$META.build.check` (lint/format/type), the full suite, other build configurations or binders |
| commit | `pre-commit` hooks (`$META.build.check` lives here) | — |
| end of a spec chain (`/mol:impl-all`), push | `$META.build.check` + `$META.build.test`, then the push-tier gate | — |

A tool that recompiles under a different configuration (a linter
driver, a docs build, a second feature set or target) is a second full
build; keeping it out of the loop is most of the loop's speed.


## Adding a new agent

When proposing a new agent, decide which kind it is by walking
two questions in order:

1. **What is the primary output?**
   - findings about content → reviewer (no write tools)
   - content itself (markdown / code / artifacts) → producer
2. **(producer only) Is there a user-approval gate before
   persistence?**
   - no gate → **producer-write** (gets `Write/Edit` tools)
   - yes gate → **producer-return** (no write tools; returns
     text, skill persists after the gate)

If you find yourself writing "and then it applies the fix,"
stop. That's a skill, not an agent.

A producer-return agent is the right move when the content is
load-bearing (a spec, a public API contract, a release
changelog) and a draft-then-review loop is unavoidable.
Letting the agent write directly would mean the user reviews
*after* the file lands — wrong polarity.

## Adding a new skill

When proposing a new skill, decide whether it's:

- An **applier** for an existing reviewer agent → mirrors the
  agent's axis (e.g. `/mol:simplify` ↔ `janitor`).
- An **orchestrator** that composes multiple agents → fan-out +
  aggregator pattern (e.g. `/mol:review`).
- A **gate** → read-only check that returns PROCEED / BLOCK
  (e.g. `/mol:ship`).
- A **runtime evaluator** → drives a live system to verify
  acceptance criteria (e.g. `/mol:perf`).

The git-workflow skills (`/mol:commit`, `/mol:push`, `/mol:pr`,
`/mol:tag`) are a fifth kind — workflow-state mutators that
chain into gates.

Model-tier assignment per agent kind (opus / sonnet / haiku) lives
in `plugins/mol/rules/model-policy.md`.
