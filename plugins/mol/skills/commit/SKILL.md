---
name: commit
description: "Stage safe paths and commit. The gate is pre-commit run once. No second hook pass, no ship call, no push, no approval wait."
argument-hint: "[<message>]"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /mol:commit — Gated Local Commit

Local only. Pushing is `/mol:push`.

## Procedure

1. `git status --porcelain` empty → stop.
2. Stage the current work. Keep anything already staged. Never stage `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa*`, `*.p12`, or credential files. Stage explicit paths when a secret-looking path is present; otherwise `git add -A` is allowed.
3. Missing `.pre-commit-config.yaml` → invoke `/mol:ci-sync`. Still missing → BLOCK.
4. Run `pre-commit run` once. On failure, fix, re-stage, and re-run only the failed hook ids (`rules/git-publish.md` § Re-running after a failed gate), up to 3 cycles. Still red → BLOCK. Never `--no-verify`.
5. Do not invoke `/mol:ship`. pre-commit is the commit gate.
6. `$ARGUMENTS` non-empty → that subject. Else a conventional subject ≤ 72 characters, imperative, no trailing period. Commit immediately. No amend.

```
/mol:commit: committed <short-sha> on <branch>
  <subject>
```
