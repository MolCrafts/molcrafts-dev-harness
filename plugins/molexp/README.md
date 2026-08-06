# molexp plugin

Data-workspace tooling for **[molexp](https://github.com/MolCrafts)** — not the agent harness (`mol`).

Install when you work with experimental data directories and need them under molexp's four-tier layout, with each run's logs turned into readable metrics:

```
Workspace → Project → Experiment → Run     # layout
<run>/metrics/metrics.jsonl                # legible curves
```

## Skills

| Skill | What |
|---|---|
| `/molexp:adopt-workspace <source> [<target>]` | Inspect a legacy data folder, propose a project/experiment/run mapping, materialize via molexp's Python API, then copy (default) or move each file with per-file SHA-256 verification. Resumable ledger; optional typed-path delete of source after successful copy. |
| ↳ metrics ingestion | Classifies each run's logs by **content** and **asks** whether to ingest them into the run's metrics buffer. One call into molexp's own converters — `molexp.plugins.metrics_ingest.ingest_run` — covering LAMMPS thermo (via molpy's log reader), TensorBoard scalars, and mapped CSV. Additive: originals are never touched. Run against an already-adopted workspace with no target to ingest in place. |

### What ingestion produces

`<run>/metrics/metrics.jsonl` — the append-only host buffer that
`GET …/runs/{id}/metrics` and the UI already read — plus the derived
`metrics/index.json` series cache. **Not** `meta/` or `status/`: a molexp Run is
a host, not a scientific record package. Formats with no converter (`wandb/`,
`mlruns/`, unrecognised dumps) stay plain artifacts and are reported — never
approximated.

## Install

```
/plugin install molexp@molcrafts
```

Requires `molexp` importable in the environment (`pip install molexp`).
Metrics ingestion additionally needs `molexp[tensorboard]` for tfevents —
reported as *not ingested* rather than approximated when missing.

## Relation to other plugins

| Plugin | Domain |
|---|---|
| `mol` | Code project harness (spec / impl / review / git) |
| `molexp` | **Experiment data** workspace adoption |
| `molq` | Job queue lifecycle (molmcp) |
