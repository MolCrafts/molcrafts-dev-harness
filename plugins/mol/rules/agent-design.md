# Agent design

Skill orchestrates. Agent does one axis. Agents do not call agents. Skill → skill only for a different verb.

The host assigns the model (`rules/model-policy.md`). Do not put a model name on an agent or a dispatch.

## Producers

| Agent | Writes | Notes |
|---|---|---|
| `implementer` | production source | also the one new test in `mode: small` and `mode: fix`. Never edits an existing test. Never ticks, commits, or reverts. |
| `tester` | tests | MEDIUM/LARGE RED tests, `regressions/`, analyze-mode. |
| `documenter` | docstrings, tutorials | no runtime change. |
| `spec-writer` | spec text, returned | skill persists after design-mode. |

Reviewers return `emoji file:line — message` and do not write. The skill applies or discards.

## Handoff packet

Every delegation includes:

1. `file:line` ranges for the edit, callers, and the test to copy.
2. Types and names the agent must use.
3. Each new test's input and expected value, when already known.
4. Prior findings verbatim.
5. The command: `$META.build.test_single`. Say not to run check or the full suite.

The agent reads those ranges first. If it has to search, it names the missing pointer.

## Verification tiers

Each tier runs once per its trigger, never earlier:

| Trigger | Runs | Does not run |
|---|---|---|
| each task or fix | `$META.build.test_single` | `$META.build.check`, the full suite |
| commit (`/mol:commit`) | `pre-commit` once | a second hook run, `ci-guard` |
| chain end (`/mol:impl-all`) | `$META.build.check` + `$META.build.test` once, then `/mol:commit` once | a commit per spec |
| push | `pre-commit run --all-files` once, then `$META.build.test` once | a second pre-commit |

## New agent

Findings → reviewer, no Write/Edit. Content with no approval gate → producer-write. Content the skill must gate before disk → producer-return.

A patch that needs a test gate is a skill, not an agent.
