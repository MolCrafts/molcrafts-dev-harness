---
name: evo
description: "Blind A/B evaluation of two harness commits against the project's own case set. Manifest first, two read-only actors per cell, one blind observer, then the project's Python gate decides. Produces a verdict and never moves a pointer."
argument-hint: "<source-name> [--champion=<sha>] [--challenger=<sha>] [--rounds=1,2,3]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:evo — Blind A/B Harness Evaluation

Compare two harness commits by running the same tasks under each and counting
what happened. You orchestrate; you never judge. Every dispatch below is a
subagent, which is why this is a skill and not a CLI: only the agent host can
start one. The one Python step compares readings, and it is the only thing in
this procedure allowed to reach a verdict.

**Half of this evaluation ships with the harness; half belongs to the project.**

- *Travels with the harness* — the two agents, this procedure, the blind
  protocol, the manifest discipline. Identical in every project.
- *Supplied by the project* — the **case set** and the **gate entry point**.
  Cases test rules a project's own `CLAUDE.md` states, so they cannot travel:
  one repo's rule is another repo's nonsense. A case you wrote yourself here
  measures nothing.

Three roles, three separations, all load-bearing:

- **actor** (`harness-actor`) — works one task under one harness, read-only,
  never told which side it is and never shown the case criteria.
- **observer** (`harness-observer`) — reads two transcripts under the labels
  `A` and `B`, holds the criteria, counts. Never told what `A` and `B` are.
- **gate** (the project's entry point) — unblinds the labels from the manifest
  and turns the readings into one verdict. Four readings compared one at a
  time, never summed into a score.

## Step 0 — Locate what the project supplies

Find both before dispatching anything.

**The case set.** A list of cases, each carrying:

- `id` — stable, so a reading can be attributed;
- `graduated` — `true` for a correctness contract the challenger must not
  break, `false` for a measurement replayed on both sides. There is no third
  kind;
- `task` — one user request, phrased the way a user would phrase it, naming no
  rule and hinting at nothing being checked. The actor's, verbatim;
- `expect` / `forbid` — the criteria, in the observer's vocabulary. The
  observer's, and never the actor's. No criterion string may appear inside its
  own case's `task`.

**The gate entry point.** One command that takes the manifest and the
observation and prints a verdict, and that says clearly whether a verdict was
produced at all. It unblinds `A` and `B` from the manifest — nothing else in
this procedure may.

Worked example (molmcp): `scripts/harness_cases.py` holds `CASES`, and
`scripts/harness_eval.py` is the entry point, run from the molmcp checkout
because it imports its sibling case module and the `molmcp` package. Another
project puts both wherever it likes; ask the project where, do not assume this
layout.

**Neither exists → stop.** Report that the project has no case set or no gate
and that the evaluation cannot run. Do not write cases to fill the gap, and do
not substitute your own judgement of the two transcripts for the gate.

Then take a fresh run directory `$RUN`, outside every repository under
evaluation, with `transcripts/` inside it. One run, one directory, never
reused.

## Step 1 — Identify champion and challenger by commit

Both commits must be **published in the store**. Activation is a per-source
pointer with one `active` commit, so the pair is not "two activated commits";
what makes the blind A/B possible is that publishing is immutable and
additive, so both trees stay readable side by side.

```bash
molmcp config get cacheDir          # empty → ~/.cache/molmcp/discovery
cat <cacheDir>/harness.<source>.pointer
```

The pointer is JSON: `active` is the commit serving now, `previous` is the one
the last `molmcp harness sync` displaced. The ordinary pair is
`champion = previous`, `challenger = active`, straight after a sync. Take
`--champion` / `--challenger` over that when given.

Store root for every path below and for the gate:
`STORE=<cacheDir>/harness`. Check both trees before anything is dispatched:

```bash
ls $STORE/commits/<sha>/metadata.json $STORE/commits/<sha>/tree
```

Missing → run `molmcp harness sync <source>` for the commit that is missing,
or stop. A report on a tree nobody can check out could not be reproduced.
Both SHAs must be 40 lowercase hex characters; a short SHA or a ref is refused.

## Step 2 — Write the manifest, before any dispatch

Write `$RUN/manifest.json` now. Not after the run, not alongside it: a
manifest written afterwards can be fitted to the outcome, and the assignment
of blind labels is the one fact this whole procedure rests on.

Exactly these six keys, no others:

```json
{
  "champion_sha": "<40 hex>",
  "challenger_sha": "<40 hex>",
  "component": "skill.<name>",
  "affected_paths": ["skills/<name>/SKILL.md"],
  "seeds": [1, 2, 3],
  "sides": {"A": "challenger", "B": "champion"}
}
```

- `sides` maps each of `A` and `B` onto exactly one of `champion` /
  `challenger`. Decide it by a coin flip before the run and never re-open it.
- `component` is the harness component id the challenger changes
  (`skill.x`, `agent.x`, `rule.x`, `provider.x`, `overlay.x`);
  `affected_paths` are the repository paths it touches. Read them off the
  challenger's diff, do not invent them.
- `seeds` are repeat-round indices — run 1, 2, 3 of an identical prompt, not
  random seeds. Distinct; a repeat weights that round twice and is refused.

`$RUN/manifest.json` is shown to no actor and no observer, at any point.

## Step 3 — Build one harness prompt per side

For each side, read that commit's published tree at
`$STORE/commits/<sha>/tree/` and concatenate, **verbatim**, the component
files its `harness.toml` declares — each component's `path` resolved under the
catalog's `component_root`. Do not summarise, reorder or paraphrase.

The same file set in the same order on both sides. Only the tree root differs;
anything else that differs is a second variable and the round measures two
things at once.

## Step 4 — Run the grid of actors

One cell per (side, round, case), over **every** case in the project's case
set — graduated ones included, they are part of the grid the gate checks for
completeness. Three cases and three rounds is 18 actor dispatches.

Each dispatch: subagent `harness-actor`, clean context, prompt containing
exactly two sections and nothing else:

```
<harness-under-test>
...that side's harness text from Step 3, verbatim...
</harness-under-test>

<task>
...the case's `task` string, verbatim...
</task>
```

Never put in an actor prompt: the case `id`, `expect`, `forbid`, the round
number, either SHA, the blind label, or the words champion and challenger. An
actor that can see what is being measured optimises for it, and the round then
measures exam technique rather than the harness.

Save each transcript — the tool-call trail and the final message — to
`$RUN/transcripts/<label>-<seed>-<case_id>.md`. The observer holds only `Read`
and reaches transcripts by path.

Do not vary the actor's model or tool list between sides or between rounds;
take both from the agent definition. The tool list is part of what is being
compared.

**The round is read-only.** The actor holds no write tool and no shell; when a
task ends in an edit it returns the edit as its answer. After the grid, confirm
the working tree is byte-identical:

```bash
git -C <repo-under-work> status --porcelain
git -C <repo-under-work> diff
```

Non-empty → the round is void. Discard `$RUN` and start over; an actor that
wrote is not the actor that was measured.

## Step 5 — Observe each cell blind

One dispatch per (case, round): subagent `harness-observer`, handed

- the `case_id`,
- that case's `expect` and `forbid` lists, verbatim,
- the round number as `seed`,
- the two transcript paths, labelled `A` and `B`.

Never hand it the manifest, either SHA, the `sides` map, the word champion or
challenger, or any earlier cell's readings. It returns one JSON object with two
readings, six keys each: `case_id`, `seed`, `side`, `contract_met`,
`tool_errors`, `call_count`.

If it reports a transcript it could not read and emits no reading for it,
re-run that one cell from Step 4 — same label, same round, same case — and
observe it again. Never fabricate the row and never zero it: a zeroed row reads
as a short, clean, error-free run.

## Step 6 — Assemble the observation

Merge every observer's readings into `$RUN/observation.json`, rows copied
verbatim, with exactly two keys:

```json
{"schema": "harness-eval/1", "readings": [ ... ]}
```

One row per (side, round, case), no gaps and no duplicates — a missing cell
changes the denominator of a mean, a duplicated one weights that round twice.
Add nothing. `sides`, `champion`, `challenger`, `champion_sha`,
`challenger_sha`, `tokens` and `latency_s` are each refused by name: an
observation that can name a side was not blind, and a reading no transcript
carries is an estimate wearing a count's clothes.

## Step 7 — Let the gate decide

Run the project's entry point on the two files and the store.

```bash
# molmcp, from its own checkout:
uv run python scripts/harness_eval.py \
  --observation $RUN/observation.json \
  --manifest $RUN/manifest.json \
  --store-root $STORE
```

Read its outcome in two states, never one:

- **a verdict was produced** — accepted *or* rejected. A rejection is a
  successful evaluation. molmcp's entry point exits 0 here.
- **no verdict could be produced** — the payload was refused, and the output
  names exactly what. molmcp's entry point exits 1 and prints a line beginning
  `no report:`. Fix the input or re-run the offending cell. Never hand-edit a
  reading to get past a refusal; the refusal is protecting a number that would
  otherwise still have looked plausible.

Do not rank, average, round, or eyeball two numbers anywhere in this
procedure. The comparison this skill performs is the one that command prints.

## Step 8 — Report the verdict and the reading that decided it

Render the gate's output as printed, then one line naming the verdict and its
cause. The reasons below are `molmcp.evolution.evaluate`'s, which is the gate
behind the worked example; a project with its own vocabulary reports its own,
and you name whichever reading it says decided.

| `reason` | What decided |
| --- | --- |
| `accepted` | No reading regressed and at least one improved. Name the readings that moved, from the two printed metric lines. |
| `regression_failed` | A graduated case failed on the challenger. Decided before any replay, so no reading decided it and both metric lines are zeroes. |
| `worse_tool_errors` | The `tool_errors` mean. First in comparison order; a gain elsewhere never offsets it. |
| `worse_call_count` | The `call_count` mean. |
| `no_practical_gain` | Nothing worse, nothing better. A tie. The champion keeps the seat and the challenger does not land. |

A tie is a real outcome and the round succeeded. Report it as the verdict it
is, never as a failure to decide and never as a reason to go looking again for
a margin.

`worse_tokens` and `worse_latency` are unreachable through this procedure:
both readings are pinned to zero on both sides, because no transcript carries
them. Either reason appearing means the payload did not come from here.

**Never promote.** The report is evidence, not a promotion: the gate's drop
thresholds assume a repeatable replay and three model runs are not repeatable.
Moving the champion pointer is the operator's own `molmcp harness sync` or
`molmcp harness rollback`, and this skill does neither.

## Refusals — stop, do not work around

- The project has no case set, or no gate entry point → stop and say so.
  Never author cases here; cases encode the project's rules, not this skill's.
- The manifest was written, touched, or re-decided after any dispatch → void
  the run.
- An observer saw anything from the manifest, or an actor saw a case's
  criteria, id, or side → void the run.
- The working tree is not byte-identical after the grid → void the run.
- A **held-out** case reads `contract_met: false`: the gate refuses the whole
  round, because an unfinished run reads cheaper than a finished one and
  averaging it in makes giving up look like a gain. Either fix the harness or
  graduate the case in the project's case set — in its own commit, never
  mid-run.
- "No verdict produced" is not a verdict. Report the refusal text; do not
  report a winner.

End with one line: `evo: <champion sha[:8]> vs <challenger sha[:8]> — <reason>,
decided by <reading | contract | tie>; <N> cells over <M> rounds; run at $RUN`.
