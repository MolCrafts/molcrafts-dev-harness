# Model policy

Do not pin a vendor model name. Claude, Codex, and Grok each choose the agent model on their own host. A `model:` value written here is wrong on every host except the one it names.

Shipped agents have no `model` field. Skills dispatch an agent with no model argument. The host default is the agent model.

## Modes

| Mode | Deliverable | Who writes it |
|---|---|---|
| Advisor | words — answer, plan, verdict, diagnosis | the main session. Agents gather evidence. |
| Orchestration | artifacts — code, specs, docs, commits | producer agents. The main loop routes and gates. |

The orchestration loop MUST NOT author production source.

Producers: `implementer` (production; also the one new test in `mode: small` and `mode: fix`), `tester` (MEDIUM/LARGE tests and analyze-mode), `documenter`, `spec-writer` (returns text; the skill persists).

Advisor skills: `discuss`, `grill`, `review`, `test`, `ship`, `litrev`, `note`, `map`.
