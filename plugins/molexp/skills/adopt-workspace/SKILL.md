---
name: adopt-workspace
description: Lift a messy data directory into a molexp Workspace→Project→Experiment→Run layout, and offer to convert its logs/metrics into MolRec Run records (LAMMPS thermo, TensorBoard scalars). Inspect, propose mapping, SHA-256 copy/move, resumable ledger. Data-safety first — every destructive step gated. Distinct from /mol:bootstrap (agent harness).
argument-hint: "<source-dir> [<target-workspace-root>]  |  <existing-workspace>  (convert-only)"
---

> **Codex:** Read `../CODEX.md` before executing this shared workflow. Claude Code follows the workflow directly.

# /molexp:adopt-workspace — Workspace Adoption

Take an existing folder of experimental data — whatever shape the operator happens to have — and lift it into a molexp workspace whose layout matches the four-tier `Workspace → Project → Experiment → Run` `Folder` family defined in `molexp/CLAUDE.md`. Distinct from `/mol:bootstrap` (which scaffolds the *agent* harness — CLAUDE.md, `.claude/notes/`, `.claude/specs/`): this skill scaffolds the *data* harness. Read-mostly until the operator approves; writes are gated, verified, and journaled.

**Two layers, one skill.** Layout adoption puts files in the right folders.
Record adoption makes each run *readable by other tools* — a molexp run is a
MolRec **Run**-shaped record (`meta` + `status`, plus `metrics` / `method`;
molrec [`docs/spec/run.md`](https://github.com/MolCrafts/molrec)). A folder of
`log.lammps` and `events.out.tfevents.*` is organized but still private. § 2
classifies record shape, § 3 asks, § 7 converts — never silently.

Bilingual: Chinese argument → operator-facing prompts in Chinese; ledger keys, slugs, and headings stay in English for deterministic parsing.

## Procedure

### 1. Preflight

Resolve `$ARGUMENTS`:

- `<source-dir>` — absolute or cwd-relative; the existing data directory.
- `<target-workspace-root>` — optional; where the new molexp workspace will live. Default: `<source-dir>.molexp/` sibling. Must NOT exist as a non-empty dir unless it already contains a resumable ledger from a prior run.

Hard checks before any output:

- `import molexp` succeeds (`python -c "import molexp"`); on `ImportError`, BLOCK with `pip install molexp` hint and stop.
- `<source-dir>` exists, is a directory, is readable.
- `<source-dir>` is **not** itself a molexp workspace (no `workspace.json` at its root) — **unless** no `<target>` was given, in which case this is **convert-only mode**: the layout is already right and the operator wants § 2 classification + § 3 question + § 7 conversion over the existing runs. Skip §§ 4–6 entirely (no mapping, no transfer, no delete gate) and say so in one line before continuing. A workspace source *with* a `<target>` is still a BLOCK — copying a workspace is a plain `cp -a`, not this skill.
- `<target>` is **not** equal to, a parent of, or a child of `<source-dir>`. BLOCK on overlap (prevents copy-into-source feedback loops).
- The parent of `<target>` is writable.
- No environment requires `--yes` / `--force` shortcuts; never accept one.

Then read `<target>/.molexp-migration.json` if it exists — this is the resume ledger. A ledger whose `source` / `target` / `mode` fields disagree with the current invocation is a fatal mismatch (BLOCK; do not silently re-plan).

### 2. Inspect the source

Walk `<source-dir>` breadth-first up to depth 6. For every directory, capture:

- file count, total size, deepest descendant depth
- presence of run-shaped artifacts: `*.log`, `params*.json`, `result*`, `checkpoint*`, `out*`, `*.dat`, `*.npy`, `*.h5`, `*.csv`, `events.out.tfevents.*`
- broken symlinks, symlinks pointing **outside** `<source-dir>` (record absolute target), zero-byte files, non-readable files (permission), hardlinks to outside files
- hidden directories (`.git/`, `.venv/`, `.cache/`, `__pycache__/`) — flag for **exclude by default** (operator can override per-path)

Heuristic classification (purely advisory — operator edits next):

- Leaf-ish dir containing run artifacts → **run candidate**.
- Dir whose children are all run candidates → **experiment candidate**.
- Dir whose children are all experiment candidates → **project candidate**.
- Anything else → **loose** (files outside the project/experiment/run hierarchy).

**Record-shape classification** (per run candidate) — what would it take for this
run to be a MolRec Run record:

| On disk | Shape | Default converter |
|---|---|---|
| `meta/` directory present | already a MolRec root — leave alone | — |
| `metrics/metrics.jsonl` | MolRec metrics stream present | — |
| `log.lammps`, or `*.log` with a thermo table | LAMMPS thermo | `molpy.io.read_LAMMPS_log` |
| `events.out.tfevents.*` | TensorBoard scalars | `molexp.plugins.tensorboard` |
| `*.csv` whose first column is a monotonic step | tabular metrics | none — needs a column mapping from the operator |
| `wandb/`, `mlruns/`, `.neptune/` | third-party run store | **none** |
| any other numeric dump | **unknown** | **none — never guessed** |

Confirm by content, never by extension: a LAMMPS log carries a `Per MPI rank
memory allocation` line followed by a thermo header row; a tfevents file opens
with TF record framing. A file you could not confirm stays `unknown` and is
transferred as a plain artifact — that is a correct outcome, not a gap.

Render a one-screen summary table: counts per kind, total bytes, depth distribution, oddities list, **and a record-shape row: `already MolRec: N · convertible: M (by format) · unknown: K`**. **No writes yet.**

### 3. Propose the mapping

Build the proposal as a YAML manifest the operator can hand-edit. Per top-level project candidate:

```yaml
projects:
  - source: relative/path/from/source
    name: <human-readable>           # used to derive slug via molexp's slugify
    experiments:
      - source: relative/path
        name: <human-readable>
        runs:
          - source: relative/path
            id: <slug>                # optional override; default = auto-generated by molexp
            parameters: {}            # optional, lifted from params.json if present
            attach_files:             # files in this run's dir that we will transfer
              - <relative path>
```

Loose files at intermediate levels: present each one as a question — *attach to nearest run / attach to nearest experiment as a run-bag / skip / route to a new "miscellaneous" run under a chosen project*. Default: skip with audit entry in the ledger.

Slug collisions: two source names that slugify to the same `id` are surfaced as a conflict; operator must rename one before proceeding.

Render the proposed tree (`project / experiment / run / N files (S MB)`) and the manifest YAML side-by-side.

**Then ask the record question — once, here, not after the transfer.** Only when
§ 2 found at least one convertible run:

```
N runs hold logs/metrics that are not MolRec records:
  12 × LAMMPS thermo        (log.lammps)          → molpy.io.read_LAMMPS_log
   4 × TensorBoard scalars  (events.out.tfevents) → molexp.plugins.tensorboard
   2 × CSV                  (needs a column mapping from you)
   1 × unknown              (transferred as a plain artifact, not converted)

Convert them to MolRec Run records (meta + status + metrics/metrics.jsonl)?
The original files are copied in either way and are never deleted or rewritten.

  [all] [per-format] [none]
```

`none` is a perfectly good answer — the workspace is still valid, the runs are
just not cross-tool readable yet, and re-running this skill against the adopted
workspace with no `<target>` converts later (convert-only mode, § 1).

Record the answer per format in the manifest as `convert: lammps|tensorboard|csv|none`.
CSV additionally needs the operator to name the step column and which columns
become series; without that mapping, CSV falls back to `none`.

Operator may:

- **approve** → continue
- **edit** → operator hands back an edited YAML; re-validate (slug uniqueness, source-path existence, no orphan parents) and re-render
- **abort** → stop; no files touched, no ledger written

Do not advance to step 4 without explicit approval.

### 4. Choose transfer mode

Ask the operator: `copy` (recommended, default) or `move`?

- **copy** — source remains intact until step 8's optional delete gate. Disk usage temporarily doubles. Safest.
- **move** — implemented as per-file *copy → verify → unlink-source*, never plain `mv`, so a mid-run failure still leaves the source partially intact and the ledger records what was unlinked. Disk usage stays flat.

`move` requires the operator type the literal word `move` back at the prompt. No silent default to `move`.

### 5. Materialize the new workspace

Drive molexp through its Python API directly (not the CLI — Python returns IDs / paths the next step needs). Use a transient Python invocation per high-level operation, e.g.:

```python
from molexp.workspace import Workspace
ws = Workspace("<target>", name="<derived-name>")
ws.materialize()
project = ws.add_project("<from-manifest>")                # name positional, slug-based id
experiment = project.add_experiment("<from-manifest>")     # name positional
run = experiment.add_run(parameters={...}, id="<slug>")    # parameters positional; explicit id
print(project.id, experiment.id, run.id)
print(project.root, experiment.root, run.root)
```

`add_project` is idempotent on slugified name; `add_experiment` is idempotent on slugified name; `add_run` is idempotent on `id` (auto-generated when omitted, but the manifest should pin `id` to a stable slug derived from the source dir name so resumes hit the same run). Re-running with the same manifest is safe.

Before transferring any payload bytes, write the migration ledger to `<target>/.molexp-migration.json` (atomic: temp + `os.rename`). Ledger shape:

```json
{
  "version": 1,
  "started_at": "<ISO-8601>",
  "source": "<absolute>",
  "target": "<absolute>",
  "mode": "copy",
  "entries": [
    {
      "kind": "project|experiment|run|file|skip",
      "source": "<absolute>",
      "target": "<absolute>",
      "size": 1234,
      "sha256": null,
      "status": "pending"
    }
  ]
}
```

Each entry is appended in deterministic order (project → experiment → run → file, then conversions). The ledger is the source of truth for step 9 and for resume.

### 6. Transfer

Process ledger entries in order. For each `file` entry:

1. Stream-read source, compute SHA-256 while writing to `<target>.partial`.
2. `os.rename(target.partial, target)` — atomic on local POSIX.
3. Re-read target, recompute SHA-256, compare with the in-memory hash from step 1.
4. On match → mark `status: verified`; on mismatch → BLOCK immediately, leave both files for the operator, write a `.molexp-migration.ERROR.json` next to the ledger with the diverging hashes. Do not proceed.
5. Preserve mtime (`os.utime`) and permission bits (`shutil.copymode`) on the target.
6. If `mode == "move"`: only after step 4 success, `os.unlink(source)`; ledger flips to `status: moved`.

Symlinks: copy as symlinks (`os.symlink` with the source's target string). If the symlink points outside `<source-dir>`, do **not** dereference; surface it as a per-symlink question in step 3 (operator may opt in to copy-by-value); default is to record the link as-is and warn in the final report.

Hardlinks to files outside `<source-dir>`: copy by value; warn.

Hidden / excluded dirs from step 2: skipped silently unless the operator opted in.

Ledger writes after each entry update are atomic (temp + rename). Resume is supported: re-running the skill with the same arguments and an existing ledger picks up at the first non-`verified` / non-`moved` entry, with a one-line preamble *"resuming from entry N of M"*.

Throughout, progress reporting: every 25 files or every 5 seconds, whichever first.

### 7. Record conversion (only the formats approved in § 3)

**Additive.** The source log has already been transferred and is never deleted,
rewritten, or moved by this step. Conversion writes *new* sections beside it, so
a bad conversion is thrown away by deleting three directories.

Skipped entirely when the operator answered `none`.

For each approved run, write the Run-shaped sections — molrec `docs/spec/run.md`
requires `meta` always and `status` (with `state`) whenever `status` exists:

**`meta/meta.json`** and **`status/status.json`** are plain JSON documents
(molrec `docs/spec/{meta,status}.md`). molexp has **no writer** for them — the
`land` op only *detects* a MolRec root by `meta/` presence
(`molexp/agent/ops/land.py:_infer_tags`) — so emit them directly, atomically:

```json
{"record_schema_version": 1, "format_name": "molrec",
 "creator": {"name": "molexp-adopt-workspace"},
 "created_at": "<ISO-8601>", "source": "<original path, relative to run root>"}
```

```json
{"state": "succeeded", "updated_at": "<ISO-8601>"}
```

`state` for an adopted run: `succeeded` only when the source says it finished
(LAMMPS `Total wall time:` line present; tfevents stream closed cleanly).
A log that ends mid-stream is `failed` with `status/error`, or `pending` if you
genuinely cannot tell. **Never default to `succeeded`** — a fabricated green
state is worse than no status section.

**`metrics/metrics.jsonl`** goes through molexp's writer, never hand-rolled JSON —
it owns the compact-key encoding, validation, and the derived index:

```python
from molexp.workspace.metrics import MetricsWriter   # not exported from workspace/__init__
w = MetricsWriter(run_dir)                            # writes run_dir/metrics/
...
w.flush()                                             # once per run — rebuilds index.json
```

#### LAMMPS thermo → metrics

```python
from molpy.io import read_LAMMPS_log

parsed = read_LAMMPS_log(src)                 # LAMMPSLog; .runs is a tuple
for ri, r in enumerate(parsed.runs):          # one entry per `run` command block
    th = r.thermo                             # LAMMPSThermo | None
    if th is None:
        continue
    step_i = th.columns.index("Step") if "Step" in th.columns else None
    for row in th.data:                        # np.ndarray, shape (n_rows, n_cols)
        step = float(row[step_i]) if step_i is not None else None
        for ci, col in enumerate(th.columns):
            if ci == step_i:
                continue
            w.scalar(f"lammps/{col}", float(row[ci]), step=step,
                     tags={"run_index": ri, "wall_time_source": "ingest"})
```

**A thermo row carries no wall-clock.** `MetricsWriter` stamps `w` with *now*,
which is ingest time, not measurement time. Tag it as above so nothing plots it
as a time axis. Do not synthesize timestamps from `loop_time` — that is
fabricated data.

Column names stay verbatim (`Temp`, `E_pair`, `TotEng`) under a `lammps/`
prefix. Do not rename them to a house vocabulary; the thermo style is the
operator's, and a renamed series can no longer be matched back to the log.

#### TensorBoard scalars → metrics

Optional dependency: `molexp[tensorboard]`. Call `require_tensorboard()` first
and, on `ImportError`, report the run as **not converted** with the install hint
— never fall back to parsing tfevents by hand.

```python
import datetime
from molexp.plugins.tensorboard import discover_logdirs, read_scalars, require_tensorboard

require_tensorboard()
for ld in discover_logdirs(run_dir):                       # dirs holding events.out.tfevents.*
    for series in read_scalars(ld, relative_to=run_dir):   # -> ScalarSeries(tag, logdir, points)
        for pt in series.points:                           # ScalarPoint(step, wall_time, value)
            w.scalar(series.tag, pt.value, step=pt.step,
                     wall_time=datetime.datetime.fromtimestamp(pt.wall_time, datetime.UTC),
                     tags={"logdir": series.logdir})
```

tfevents points **do** carry a real `wall_time` — pass it through; do not let the
writer stamp ingest time. Tags keep their original slash names (`train/loss`),
which are already the molrec `key` convention.

#### CSV → metrics

No default converter. Only with the operator's column mapping from § 3: one
column is `step`, each named column becomes `k`, `w` is ingest time (tag it).
Without a mapping, leave the CSV as a plain artifact.

#### Ledger

Each conversion appends an entry before it writes:

```json
{"kind": "convert", "run": "<run id>", "format": "lammps|tensorboard|csv",
 "source": "<absolute>", "sections": ["meta", "status", "metrics"],
 "records": 0, "status": "pending"}
```

flipping to `converted` with the final `records` count, or `skipped` with a
reason (missing optional dep, unreadable source, operator declined). Conversion
failure **never** blocks the run — the files are already safely transferred;
record the failure, keep going, and list it in § 10.

### 8. Verify

After all entries transfer:

- Re-open the workspace: `Workspace("<target>")`; iterate projects → experiments → runs; count files under each run's `artifacts/` (or wherever the manifest mapped them).
- Compare against the ledger's per-run file count. Any mismatch → BLOCK with a per-run diff table; do not advance.
- Run `molexp workspace <target> info` for a human-readable confirmation panel; capture its output verbatim into the ledger's `verified_at` block.

For every run marked `converted`, re-open the record and confirm it is actually
readable — a conversion that wrote files nobody can parse is not a conversion:

```python
import json
from molexp.workspace.metrics import read_run_metrics
meta = json.loads((run_dir / "meta" / "meta.json").read_text())
assert meta["record_schema_version"] == 1
assert json.loads((run_dir / "status" / "status.json").read_text())["state"]
res = read_run_metrics(run_dir)                 # MetricReadResult
assert res.parse_errors == 0
assert len(res.records) == ledger_entry["records"]
```

`parse_errors > 0`, a record count that disagrees with the ledger, or a missing
`state` is a per-run BLOCK on the conversion only — the transferred files stay
verified and the workspace stays usable.

If transfer verification fails partway, leave the new workspace intact and the source untouched (copy mode) or partially drained (move mode, with ledger noting which entries were unlinked). The operator can correct and re-run.

### 9. Optional delete of the source

**Only reachable when `mode == "copy"` AND step 8 passed clean.** Otherwise skip with a one-line note.

Present the gate as:

```
Source: <absolute source path>
Total: <N files, S MB>
Mode: <delete-permanent | move-to-trash>

To delete, type the absolute source path back exactly:
```

Accept ONLY a verbatim match of the absolute source path. Anything else (empty, partial, `yes`, `y`) → cancel, leave the source intact, exit cleanly.

Prefer move-to-trash where available (macOS: `osascript -e 'tell application "Finder" to delete (POSIX file "<path>" as alias)'`; Linux: `gio trash` if present). Fall back to `rm -rf` only if the operator selects `delete-permanent` explicitly and types the path a *second* time.

Record the deletion (or skip) in the ledger as a `deleted_at` block with the chosen method.

### 10. Report

One-line summary at the end:

```
/molexp:adopt-workspace: copied N files (P projects, E experiments, R runs) into <target>; ledger at <target>/.molexp-migration.json
```

or `moved` / `resumed-and-completed` / `converted-only` / `BLOCKED: <reason>` / `ABORTED at step <n>` as appropriate. Final stats: total bytes, elapsed wall time, number of symlinks copied vs dereferenced, number of skipped entries, and — when § 7 ran — runs converted per format, metric records written, and every run **not** converted with its reason (unknown format, missing optional dep, operator declined).

## Resumability

The ledger at `<target>/.molexp-migration.json` is the single source of truth for resume. Re-running the skill with the same `<source-dir>` and `<target>` arguments:

1. Reads the ledger.
2. Refuses if `source` / `target` / `mode` differ from the current invocation.
3. Skips entries already `verified` / `moved`.
4. Re-runs SHA-256 on entries marked `pending` or `copied` (post-write but pre-verify) to detect corruption.
5. Continues at the first non-terminal entry.

`.molexp-migration.json` is committed to the new workspace's root **alongside** `workspace.json`. The operator can delete it manually once they are done auditing — it is not a runtime dependency of molexp itself.

## Guardrails

- **No `--yes`, no `--force`, no batch-mode shortcuts.** Every destructive step has an explicit operator gate (typed-back paths, typed-back mode words).
- **Never overwrites existing target files.** A pre-existing file at the target path with a non-matching hash aborts the transfer for that entry; the operator must move it aside.
- **Never dereferences out-of-source symlinks without an operator opt-in.**
- **Refuses overlap** between `<source>` and `<target>` (one is parent / child / equal to the other).
- **Atomic writes everywhere**: temp file + `os.rename` for ledger, target files, error reports, manifest.
- **Refuses to start** without `molexp` importable; will not silently fall back to a hand-rolled directory layout.
- **Never edits the source** in copy mode prior to step 8.
- **Per-file SHA-256 verification** is non-negotiable; there is no `--skip-verify`.
- **Resumes cleanly** after `Ctrl-C` / crash — re-running picks up where it stopped without re-copying already-verified files.
- **Idempotent** when the ledger already records the planned work; a no-op exit reports `already complete` and stops.
- **Read-only on the agent harness** — does not touch CLAUDE.md, `.claude/notes/`, or `.claude/specs/`. That is `/mol:bootstrap`'s job.
- **Conversion is additive and opt-in.** Never converts without the § 3 answer.
  Never deletes, rewrites, moves, or truncates the source log — the record
  sections are written beside it, so an unwanted conversion is undone by
  removing `meta/`, `status/`, and `metrics/`.
- **Never guesses a format.** A file whose shape you could not confirm by
  content is `unknown` and stays a plain artifact. No default converter exists
  for `wandb/` or `mlruns/`; say so rather than approximating one.
- **Never hand-rolls `metrics.jsonl`.** `molexp.workspace.metrics.MetricsWriter`
  owns the compact-key encoding and the derived index. Writing those lines
  yourself forks the binding.
- **Never fabricates a timestamp or a state.** LAMMPS thermo rows carry no
  wall-clock — tag `w` as ingest time rather than inventing one from
  `loop_time`. A run whose log ends mid-stream is not `succeeded`.
- **Never renames a series** into a house vocabulary. `Temp` stays `Temp`; a
  renamed key can no longer be matched back to the log it came from.
- **A conversion failure never fails the adoption.** The bytes are already
  transferred and verified; record the failure and continue.

End with the one-line F2 summary defined in step 9.
