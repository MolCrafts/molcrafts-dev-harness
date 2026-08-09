# Notes — molcrafts-harness

Evolving decisions. `/mol:note` reconciles entries here; a rule that admits no
exception belongs in `law.md` instead.

## The marketplace is developer tooling; product capability is an MCP tool

This repo ships one plugin, `mol`. A molcrafts *product* never gets a plugin
here — its capability becomes a tool on a molmcp plane, which is where that
surface is defined and enforced.

**The test.** A skill is justified when the *procedure* is the hard part —
deciding, sequencing, gating across a repo's state. Driving a queue or copying
a directory is not: a tool enforces its preconditions in code and returns a
value, where a prompt only asks the model to remember. A skill whose body is a
list of tool calls is a second, untested copy of that tool.
