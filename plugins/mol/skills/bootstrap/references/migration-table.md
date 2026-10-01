## Migration table (current-version layout)

| From (legacy)               | To (current)         | Why |
|-----------------------------|----------------------|-----|
| `.agent/specs/`             | `.claude/specs/`     | active vs passive split (pre-v0.3.0; specs are runtime artifacts) |
| `docs/decisions/`           | `.claude/notes/decisions/`  | internal context, not public docs |
| `docs/contracts/`           | `.claude/notes/contracts/`  | internal context |
| `docs/agent-rubrics*.md`    | `.claude/notes/rubrics/`    | internal context |
| `.claude/NOTES.md`          | `.claude/notes/notes.md`    | passive memory belongs in `.claude/notes/`, not `.claude/` root |
| `.agent/notes.md`           | `.claude/notes/notes.md`    | v0.3.0: passive context folds into `.claude/notes/` per Claude Code spec; name avoids collision with `.claude/agents/` |
| `.agent/architecture.md`    | `.claude/notes/architecture.md` | v0.3.0 |
| `.agent/decisions/`         | `.claude/notes/decisions/`  | v0.3.0 |
| `.agent/rubrics/`           | `.claude/notes/rubrics/`    | v0.3.0 |
| `.agent/contracts/`         | `.claude/notes/contracts/`  | v0.3.0 |
| `.agent/debt/`              | `.claude/notes/debt/`       | v0.3.0 |
| `.agent/handoffs/`          | `.claude/notes/handoffs/`   | v0.3.0 |
| `.agent/open-questions.md`  | `.claude/notes/open-questions.md` | v0.3.0 |
| `.agent/README.md`          | `.claude/notes/README.md`   | v0.3.0 |
| `mol_project.notes_path: .agent/...` or `.claude/NOTES.md` | `mol_project.notes_path: .claude/notes/...` | v0.3.0: frontmatter follows the path move |
| `mol_project.perf:` block in CLAUDE.md frontmatter | (delete) | `perf.focus` was a single-value enum that didn't scale; `optimizer` agent now detects catalogs per file |
| `.claude/notes/design-preferences.md` (whole file) | `.claude/notes/law.md` | one rulebook, not two of differing force. Restate each rule as a prohibition ("OOP by default" → "never a free function where a type owns the concept") so a violation is pointable; drop the file |
| `## Design preferences (default)` in CLAUDE.md | `## Law (never violated)` | same collapse, index side |
| `## What must never change casually` (any spelling) in CLAUDE.md | `## Law (never violated)`, body → `.claude/notes/law.md` | project invariants are laws; same file, same protection |

Add new rows as new conventions are codified. Layout violation **not** in this table = content-level drift → manual TODO; do not invent moves.

---
