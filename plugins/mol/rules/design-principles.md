# Skill / Agent Design Principles

The harness constrains. It does not prescribe a fixed matrix of steps.

## Layers

| Zone | Holds |
|---|---|
| `docs/` | public docs |
| `.claude/notes/` | passive knowledge: law, notes, architecture |
| `.claude/specs/` | live specs; `/mol:impl` deletes them when done |
| `CLAUDE.md` | router, ≤ ~100 lines, one line per law |

Do not mix zones. Specs never move to `docs/` or `.claude/notes/`.

## Two layers

Skill = procedure (order, gates, handoff). Agent = one expertise axis. Agents do not call agents. Skill → skill only for a different verb.

O1. `architect` answers **compliance**: does this shape obey `law.md`. `librarian` answers **placement**: where the change goes, and what to reuse. They may read the same blueprint.

## Models

The host assigns the agent model. `rules/model-policy.md`. No vendor model name in this tree.

## Workflow

```
/mol:spec
  librarian → grill once → draft → design-mode → impl
/mol:impl
  TDD (test_single) → [docs Mode A if a docs criterion is pending] → one commit
after the diff is green, before that commit, only if the user asks:
  /mol:simplify
after the functional commit, only for scientific / performance criteria:
  /mol:perf → /mol:close
```

`/mol:discuss` does not call grill. `/mol:review` beyond `architect` + `janitor` needs `--axis`.

### W4

Law checks, in this order:

1. `/mol:discuss`, and `/mol:grill` when the user invoked it. A law-violating alternative is not an option.
2. **spec-time librarian** — placement and reuse, before the grill and before drafting.
3. **spec-time architect design-mode** — compliance of the proposed Design. A 🚨/🔴 that cites a law id does not persist.
4. MEDIUM/LARGE `/mol:impl` — one `architect` pass after the tasks. SMALL skips it; design-mode already ran.
5. `/mol:review` — default axes are `architect` and `janitor`. Every other axis requires `--axis`.

### W2

New behavior has a failing test before production lines change. SMALL and `/mol:debug` fix mode: one `implementer` writes that test, then the patch. MEDIUM/LARGE: `tester`, then `implementer`.

### W5

A bug is `/mol:debug`. It does not go through a spec.

## Debt

`law.md:no-silent-debt` covers files you are editing. Fix the rot or stop with path:line. Do not widen the edit to dependents you are not already changing. A review still reports every finding in its scope.

## Output

Findings use `🚨` / `🔴` / `🟡` / `🟢` plus `file:line — message`. `/mol:review` renders the verdict in the main session: any 🚨 → BLOCK; any 🔴 → REQUEST CHANGES; otherwise APPROVE.
