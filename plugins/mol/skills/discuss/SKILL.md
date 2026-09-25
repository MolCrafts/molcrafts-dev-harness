---
name: discuss
description: "Design discussion until converge or discard. Free-form: 该不该做/几种方案/should we/trade-offs. Read-only. Does not start grill or spec."
argument-hint: "<topic or question>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:discuss — Design Discussion

Read CLAUDE.md → `$META`. Read `.claude/notes/law.md` when present. A law-violating alternative is discarded, not offered.

Trade-offs before a spec. A formed plan is `/mol:grill`. A clear requirement is `/mol:spec`. A decided rule is `/mol:note`.

Never auto-invoke `/mol:grill` or `/mol:spec`.

## Loop

One-sentence frame. List what you read. Vague → one question, then stop.

Each turn:

```
Convergence pulse
- Agreed: …
- Open: …
- My read: converging | diverging | stuck
```

Converge: user accepts, or Open is empty, or two turns add nothing. Discard: diverging two turns, user drops it, or 8 turns with no converge.

## Exit

Converge → one paragraph requirement, the alternative that lost, paths read. Stop. User runs `/mol:grill` or `/mol:spec`.

Discard → one sentence. Write nothing.

```
/mol:discuss <topic>: converged | discarded (<reason>)
```
