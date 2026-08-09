# Notes — molcrafts-harness

Evolving decisions. `/mol:note` reconciles entries here; a rule that admits no
exception belongs in `law.md` instead.

## The marketplace is developer tooling; product capability is an MCP tool

This repo ships one plugin, `mol`. The `molq` and `molexp` plugins were
deleted and their capability now lives on molmcp planes:

- `molq` — the seven job tools already existed (`list_jobs`, `get_job`,
  `job_logs`, `list_destinations`, `list_queue`, `submit_job`, `cancel_job`).
  The three skills were procedure narration over tools that already carried
  their own preconditions, so removing them lost nothing.
- `molexp` — `/molexp:adopt-workspace` had no tool behind it, so it became
  four: `plan_adoption`, `run_adoption`, `adoption_status`, `ingest_metrics`
  (`molmcp/src/molmcp/providers/molexp/adopt/`).

**The test.** A skill is justified when the *procedure* is the hard part —
deciding, sequencing, gating across a repo's state. Driving a queue or copying
a directory is not: a tool enforces its preconditions in code and returns a
value, where a prompt only asks the model to remember. A skill whose body is a
list of tool calls is a second, untested copy of that tool.

Do not add a plugin here for a molcrafts *product*. Add the tool to molmcp.

**Left to the operator:** the adoption tools deliberately have no
delete-the-source verb. Everything else in that flow is provable and
resumable; an irreversible delete is neither, so it stays a human decision
made with the ledger in hand.
