---
name: grill
description: "One-question interview. /mol:spec calls it once after librarian. Also free-form 盘问/grill. Read-only. Never writes and never starts impl."
argument-hint: "[mode:plan|post-librarian|spec-audit] <plan, requirement, or slug>"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:grill — Plan / Spec Interrogation

Read CLAUDE.md → `$META`. Read `.claude/notes/law.md` when present. A recommended answer must satisfy it. Do not offer a waiver.

Never auto-invoke `/mol:spec` or `/mol:impl`.

| Mode | When |
|---|---|
| post-librarian | `/mol:spec` just got the librarian report and has not drafted |
| plan | the user brought a plan |
| spec-audit | the user named a slug under `$META.specs_path` |

`post-librarian` needs the requirement and the librarian report. plan with no plan, or spec-audit with no file → stop.

## Loop

Self-answer anything the librarian report or the code already settles. Ask only what is still open. One question per turn. Recommend an answer in one line. Wait for the user.

```
Grill pulse
- Resolved: …
- Open: …
- Next: …
```

Nothing open on the first pass → return immediately. Open grows for two turns → under-formed. Stop.

## Done

- post-librarian → decisions (`question → answer → why`) back to `/mol:spec`. Do not draft. Do not tell the user to 落盘.
- plan → sharpened plan and the same decisions. The user may 落盘 / 写 spec.
- spec-audit → `audit_result: clean` or `supersede_needed` plus a short delta. Do not write.

```
/mol:grill post-librarian: <N> decisions
/mol:grill plan: sharpened (<N>)
/mol:grill spec-audit <slug>: clean | supersede_needed
```
