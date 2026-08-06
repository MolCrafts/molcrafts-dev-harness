# molexp plugin

Data-workspace tooling for **[molexp](https://github.com/MolCrafts)** — not the agent harness (`mol`).

Install when you work with experimental data directories and need them under molexp's four-tier layout, with each run readable as a [MolRec](https://github.com/MolCrafts/molrec) record:

```
Workspace → Project → Experiment → Run          # layout
meta + status + metrics/metrics.jsonl           # record (MolRec Run shape)
```

## Skills

| Skill | What |
|---|---|
| `/molexp:adopt-workspace <source> [<target>]` | Inspect a legacy data folder, propose a project/experiment/run mapping, materialize via molexp's Python API, then copy (default) or move each file with per-file SHA-256 verification. Resumable ledger; optional typed-path delete of source after successful copy. |
| ↳ record conversion | Classifies each run's record shape and **asks** whether to convert non-MolRec logs. Default converters: LAMMPS thermo via `molpy.io.read_LAMMPS_log`, TensorBoard scalars via `molexp.plugins.tensorboard` — both written through `molexp.workspace.metrics.MetricsWriter`. Additive: originals are never deleted or rewritten. Run with an already-adopted workspace and no target to convert in place. |

### What conversion produces

A MolRec **Run**-shaped record per run — `meta/meta.json`
(`record_schema_version: 1`), `status/status.json` (`state` required), and the
append-only `metrics/metrics.jsonl` stream with molrec's compact keys
(`t`/`k`/`s`/`w`/`v`/`tags`). Formats with no default converter (`wandb/`,
`mlruns/`, unrecognized dumps) are transferred as plain artifacts and reported —
never approximated.

## Install

```
/plugin install molexp@molcrafts
```

Requires `molexp` importable in the environment (`pip install molexp`).
Record conversion additionally needs `molpy` (LAMMPS logs) and
`molexp[tensorboard]` (tfevents) — each optional, each reported as
*not converted* rather than approximated when missing.

## Relation to other plugins

| Plugin | Domain |
|---|---|
| `mol` | Code project harness (spec / impl / review / git) |
| `molexp` | **Experiment data** workspace adoption |
| `molq` | Job queue lifecycle (molmcp) |
