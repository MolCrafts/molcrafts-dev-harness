# Information Design — Workbench Entities

Visual polish cannot fix a page that does not know its job. This file is
the **content constitution** for MolCrafts workbench UIs (MolExp and any
product that owns Project → Experiment → Run–shaped records). It answers
*what to show, what to hide, what to merge, and which structure carries
it* — before tokens, cards, or charts.

Read this with `product-archetypes.md` § workbench and
`de-templating.md`. Visual rules live elsewhere; this file owns
**information priority and pattern choice**.

Viewer archetype (MolVis): use only § 1 (single ownership), § 2 (chrome
jobs), and § 8 (anti-patterns). Hierarchy § 4–6 are workbench-only.

---

## 1. Single ownership of every fact

A fact may appear in **at most one chrome surface** in the viewport.
Repeating it in sidebar + header + KPI + identity card + status card is
not "reinforcement" — it is noise that trains the user to skip reading.

| Fact class | Canonical home | Forbidden second homes |
|---|---|---|
| Name / kind / tree position | Left navigator selection + breadcrumb | Identity card, "Entity" section on overview |
| Ancestor path (Project → Exp → Run) | Breadcrumb only | Overview lineage cards, parent crumbs in center |
| Graph edges (parent, workflow, plan, siblings) | Right inspector **Lineage** / **Related** | Center overview "Related" / "Parent" cards |
| Scalar identity (id, config_hash, paths) | Inspector **Details** (or one mono field in MetaStrip if operational) | Full identity card wall on overview |
| Aggregate status of children | One `StatusInline` or MetaStrip tone | Parallel KPI cards for the same counts |
| Live sync / mutation tips | Bottom status bar only | Toast cards, banner stacks, center alerts |
| Primary work inventory | Center overview primary table/list | Empty equal widgets beside it |

**Merge rule.** If two modules would display the same field, delete the
weaker one. Prefer shell chrome (nav / breadcrumb / inspector) over
center re-hosting.

**Hide rule.** If a value does not change the user's next action in the
next ~30s, demote it to inspector, a secondary tab, or omit it.

---

## 2. Chrome jobs (what each region is for)

Workbench shell regions are not interchangeable content slots. Each has
one job.

| Region | Job | Answers | Does not answer |
|---|---|---|---|
| **Left navigator** | Find and select | Where am I in the hierarchy? What exists? | Full params, results, lineage essays |
| **Breadcrumb / work-surface header** | Orientation + primary verbs | What object am I on? What can I do now? | Status history, KPI walls |
| **Center overview** | Situation + next step | What is the state of *this* level's children / attempt? What do I open next? | Full identity dump, graph edges, logs |
| **Center detail tabs** | Full inventory | Complete list of runs / assets / files | Vanity aggregates already on overview |
| **Right inspector** | Context for selection | Properties, lineage, scalar details of *this* object | Primary child inventory (that is center) |
| **Bottom panel** | Live operations | Logs, problems, streaming output, artifacts in flight | Static entity description |

If a module's content fits a different region's job better, **move it**,
do not duplicate it.

---

## 3. Overview vs detail (boundary law)

### Overview (default center surface)

**Responsibility:** one-screen situational awareness and a clear next
action.

Must:

1. State the level's operational posture in ≤1 dense strip (MetaStrip /
   StatusInline — not a wall of StatCards).
2. Put the **primary child inventory** first (Project → experiments;
   Experiment → runs; Run → this attempt's params/results/error).
3. Prefer a table or dense list over a grid of equal cards.
4. Expose drill-down: row click opens the child overview.

Must not:

1. Re-host lineage, parent path, or "Related entities" cards.
2. Ship a SaaS KPI triptych (Total / Success / Failed as three equal
   hero numbers) when a status bar + table already carries the signal.
3. Dump the full parameter schema when only varying keys matter at this
   level (see § 6).
4. Fill empty space with placeholder widgets "for balance."

### Detail tabs / secondary surfaces

**Responsibility:** complete, scannable inventory and tools that would
crowd the overview.

- Full run table with filters, all assets, all files, long logs.
- Comparison / sweep tables when N is large.
- Editors and validators that are not the first question.

### Inspector

**Responsibility:** *this* object's properties and graph edges — not a
second overview.

---

## 4. Hierarchy priority (Project → Experiment → Run)

Information priority follows the object the user selected. Do not apply
a generic "dashboard template" to every level.

### Project

| Priority | Content | Structure |
|---|---|---|
| P0 | Experiments under this project | Dense table/list: name, run count, status distribution, updated |
| P1 | Portfolio posture | StatusInline over all descendant runs; optional success rate in strip |
| P2 | Counts that aid scan | experiments / runs / assets as MetaStrip numbers |
| P3 | Project summary prose | One line if present; never a card essay |
| Demote | Project id, workspace key, raw timestamps beyond "updated" | MetaStrip mono or inspector |
| Never on center | Lineage (none), full run list of every experiment | Runs belong under each experiment |

### Experiment

| Priority | Content | Structure |
|---|---|---|
| P0 | Runs | Table/list: status, **varying** params preview, result preview, duration |
| P1 | Sweep posture | StatusInline; success rate only if runs exist |
| P2 | Workflow pointer | MetaStrip (file + task count) — not a second workflow canvas |
| Demote | Fixed params shared by all runs | Inspector or collapsed "Constants" — not repeated per row |
| Never on center | Parent project card, full lineage, four KPI cards | Breadcrumb + inspector |

### Run

| Priority | Content | Structure |
|---|---|---|
| P0 | Failure / error | Top banner if failed — copyable, not a toast |
| P0 | This attempt's parameters & results | Property grids (two columns max), not nested cards |
| P1 | Operational facts | MetaStrip: started / finished / duration / backend / attempts / assets |
| P2 | Knowledge backlinks | One quiet section if present |
| Demote | config_hash, profile, ids | MetaStrip mono truncate + copy, or inspector Details |
| Never on center | Project / experiment / workflow lineage cards | Inspector Lineage only |

---

## 5. Pattern selection matrix

Agents default to "I have data → make a Card." Wrong. Pick the structure
from the *question*, not from the *payload shape*.

| User question | Structure | Avoid |
|---|---|---|
| What is the posture of this object? | MetaStrip (3–8 operational facts) + optional StatusInline | Grid of StatCards |
| What are the N children? | Dense table or list (primary column + 2–4 scan columns) | Card grid of N identical widgets |
| What are the fields of *one* object? | Property list (label left, mono value right) | Nested cards per field group |
| Where does this sit in the tree? | Navigator + breadcrumb | Center lineage diagram by default |
| How do runs differ in a sweep? | Table with **varying** params as columns; fixed params once above | Params JSON blob in every cell |
| How do A and B compare? | Comparison table or side-by-side property list | Two full dashboards stacked |
| What failed and why? | Error banner + log tab / bottom panel | Only a red badge |
| What aggregated number matters? | One strip metric or table footer | Dashboard of vanity counts |
| How is work progressing live? | Bottom panel + status ramp on the row | Fake progress + center spinner wall |

### Aggregation rule

Show an aggregate only if it is **decision-bearing**:

- Status distribution → yes (where to look next: failed vs running).
- Success rate → yes when N ≥ 1 and the user is scanning a portfolio.
- "Total experiments: 3" when the table already has 3 rows → no (redundant).
- "Average duration" with no action attached → usually no.
- Empty-state zeros presented as KPIs → no.

### Card rule (content, not chrome)

A bordered standalone surface is allowed only for a **standalone object
or primary control** the user can open, edit, remove, or act on alone
(see `de-templating.md`). Sections on an overview are label + separator +
content — never one Card per statistic.

---

## 6. Scientific experiment data layers

Layer the scientific record so the eye hits *what varies* before *what is
constant*.

| Layer | Meaning | Default placement |
|---|---|---|
| **Varying parameters** | Keys that differ across the run set | Experiment run table columns (or first columns of a sweep grid) |
| **Fixed parameters** | Same for every run in the set | Once: MetaStrip, collapsed Constants, or inspector — never repeated per row |
| **Run status** | Lifecycle of each attempt | Status glyph/badge on the row + StatusInline at experiment/project |
| **Results** | Outcomes / metrics | Short preview on experiment list; full property grid on run overview |
| **Error / evidence** | Why failed | Run overview banner + bottom logs / `error.txt` path |
| **Lineage / provenance** | Project, experiment, workflow, plan, config identity | Inspector Lineage + Details; config_hash as mono strip field if needed for copy |
| **Artifacts / assets** | Files produced | Count in MetaStrip; full list on Assets tab or bottom Artifacts |
| **Live ops** | Logs, jobs, heartbeats | Bottom panel + status bar — not overview body |

**Sweep heuristic.** If ≥2 runs share a param key with different values,
that key is *varying* and earns a column. If all values equal, it is
*fixed* and leaves the table.

**Result preview heuristic.** One scalar or short mono string per row
(primary metric if known; else first result key). Full nested objects
wait for the run overview.

---

## 7. Overview composition (canonical skeleton)

Every entity overview uses the same vertical rhythm. Products implement
it with local primitives (`OverviewSurface`, `MetaStrip`, …) but must not
reorder the jobs.

```text
┌─ OverviewSurface (full-bleed work surface) ─────────────────┐
│ [optional] Error / intervention banner                        │
│ MetaStrip — operational facts only (not identity essay)       │
│ StatusInline — child status distribution (if children exist)  │
│ [optional] one-line summary prose                             │
│ PRIMARY inventory (table/list) — majority of the fold         │
│ [optional] secondary section (backlinks, constants) — quiet   │
└───────────────────────────────────────────────────────────────┘
```

Rules:

- Primary inventory is **not** optional when children exist.
- Secondary sections never compete visually with the primary (no equal
  three-column widget row of empty cards).
- Loading / empty / error of the primary inventory uses the product's
  operation-state pattern — never a blank fold with KPI zeros.

---

## 8. Anti-patterns (match and refuse)

| Smell | Fix |
|---|---|
| **Card soup** — every array becomes a card grid | Table/list; Card only for standalone objects |
| **Fact echo** — same id/status in ≥2 chrome regions | Keep canonical home (§ 1); delete the rest |
| **KPI wall** — Total/Succeeded/Failed/Cancelled as equal hero tiles | StatusInline + table; at most one decision metric in strip |
| **Identity card** — large "About this Project" block restating breadcrumb | Delete; inspector Details for scalars |
| **Lineage in center** — parent path / related entities cards on overview | Move to inspector |
| **Overview = empty triptych** — three equal empty widgets for balance | One primary empty state with a next action |
| **Params as JSON wall** on experiment list | Varying columns + fixed strip |
| **Vanity aggregates** — numbers that never change a decision | Remove or bury in inspector |
| **Generic SaaS dashboard** applied to every hierarchy level | Apply § 4 priority for the selected level |
| **Agent reflex: data → Card** | Apply § 5 matrix before any layout code |

---

## 9. Procedure for agents (before writing UI)

When implementing or redesigning a workbench surface, do this **in
order** and keep the answers in the PR or stage report:

1. **Name the selected level** — Project / Experiment / Run / other.
2. **Name the page job** — overview | detail tab | inspector | bottom.
3. **List the user questions** this surface must answer (≤3).
4. **Assign each available field** to a home in § 1–2; mark demote/hide.
5. **Pick one primary structure** from § 5 for the fold's main content.
6. **Apply § 4 and § 6** for scientific layers if the level has runs.
7. **Compose** with § 7 skeleton.
8. **Audit** against § 8 before visual polish.

Skipping to StatCards or shadcn `Card` before step 5 is a process
failure, not a style preference.

---

## 10. Detection (info-stage scan)

Judgment-heavy, but these greps catch common regressions from the
frontend root. Report as 🔴 (structural IA) or 🟡 (drift).

```bash
# 1. Hero KPI / StatCard grids on entity overviews     target: prefer MetaStrip
rg -n -e 'StatGrid' -e 'StatCard' -e 'KPI' \
   --glob '*Viewer*' --glob '*Overview*' src || true

# 2. Lineage / parent re-hosted in center overviews    target: 0 new
rg -n -e 'Lineage' -e 'Parent project' -e 'Related entities' \
   --glob '*Overview*' --glob '*Viewer*' src || true

# 3. Card density on overview modules                  target: sections not cards
rg -n -e '<Card\b' -e 'DashboardCard' \
   --glob '*Overview*' --glob '*Viewer*' src || true

# 4. Duplicate identity fields (id shown many times)   target: ≤1 per view
rg -n -e 'label: "id"' -e "label: 'id'" -e 'project\.id' -e 'experiment\.id' \
   --glob '*Overview*' --glob '*Viewer*' src || true
```

Pair with the mechanical de-templating scan. Shape counts pick the
visual stage; this scan plus the `web-design` agent pick the **info**
stage.
