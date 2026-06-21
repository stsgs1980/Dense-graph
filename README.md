# Dense-graph

Interactive D3.js v7 visualization of the **Z-ai platform ID-graph**: 60 identifiers across 4 repos, 113 edges (`Related:` + `Aligned_with:`), with BFS shortest-path search, per-ID detail panel, and force-directed zoom/pan layout.

> Single-file HTML — open in any browser, no build step, no server needed.

## What's in this repo

| Path | What | Size |
|---|---|---|
| `viewer/id-graph-dense-viewer.html` | **Main artifact.** Full D3.js v7 force-directed viewer with zoom/pan, BFS path search, edge-type filters, per-ID panel | 47 KB |
| `viewer/submodule-graph.html` | Submodule dependency graph (4 repos) + dense-viewer preview matrix | 51 KB |
| `data/id-graph-full.json` | Complete ID-graph: 60 nodes + 113 links + summary. Each node has `id`, `repo`, `file`, `title`, `prefix`, degrees. Each link has `src`, `tgt`, `src_repo`, `tgt_repo`, `type`. | 35 KB |
| `data/id-graph-full-inline.json` | Compact form (short keys: `m`=matrix, `o`/`i`=top-15 hubs, `e`=edges as arrays, `s`=summary) for embedding inline in HTML | 14 KB |
| `data/id-graph-inline.json` | Compact form, related-edges only (no `Aligned_with:`) | 7 KB |
| `data/id-graph-snapshot.json` | Minimal baseline snapshot (IDs + edge counts) — for diff against future runs | 2 KB |
| `data/id-graph-data.json` | Raw extractor output v1 (pre file-path support) — kept for history | 36 KB |
| `renders/id-graph.dot` | Graphviz DOT source for the static baseline render | 16 KB |
| `renders/id-graph.svg` | Static SVG render of the baseline graph | 105 KB |
| `renders/id-graph.png` | Static PNG render (1200×900 raster) | 1.2 MB |
| `scripts/extract_id_graph.py` | Python extractor v1 — scans standards/guard/skills trees for `Related:` / `Aligned_with:` edges between IDs | 6 KB |
| `scripts/extract_id_graph_full.py` | Python extractor v2 — v1 + per-node `file` path + `title` extraction | 10 KB |

## Graph statistics

```
IDs total         : 60
  STD (standards) : 19
  RULE (guard)    : 17
  ZAI (skills)    : 24
  TOOL (platform) :  0  (no TOOL-prefixed IDs in current baseline)

Edges total       : 113
  Related:        : 106
  Aligned_with:   :   7

Top hub (in-degree): STD-SKILL-001 — 23 in-edges
  (the foundational skill-format contract; most-referenced ID in the graph)
```

## Viewer features

### `id-graph-dense-viewer.html`

- **Force-directed layout** (D3.js v7 `forceSimulation`)
  - Live-adjustable charge & link distance sliders
  - Reheat button (re-randomize velocities)
  - Reset zoom / double-click to reset
- **Zoom & pan** (d3-zoom) — mouse wheel + drag
- **Per-ID detail panel** (right side)
  - All `in` edges (who references this ID)
  - All `out` edges (what this ID references)
  - Repo, file path, prefix, total degree
- **BFS shortest-path search**
  - Pick `from` and `to` IDs from dropdowns
  - Highlights the path; dims non-path nodes/edges
  - Reports "no path" if disconnected
- **Edge-type filter** — toggle `Related:` vs `Aligned_with:`
- **Prefix filter** — show only STD / RULE / ZAI subsets
- **Repo filter** — show only standards / guard / skills subsets
- **Search** — type ID substring to highlight matching nodes
- **Color scheme** — each repo gets its own color (standards blue, guard green, skills purple)

### `submodule-graph.html`

- Submodule dependency graph: L0 platform → L1 standards → L2 guard → L3 skills
- 3 edge layers (toggleable):
  - **Solid**: git submodule pointers
  - **Dashed**: CI workflow (`verify-*.js` verifiers)
  - **Faint**: ID-graph aggregate (cross-repo `Related:`/`Aligned_with:`)
- `P-MAS_init` phantom node (L4\*) — deferred consumer from the roadmap, marks an architectural hole
- Click any node → details panel
- Dense-viewer preview embedded: Matrix / Edge list / Top hubs tabs

## How to use

```bash
# 1. Clone
git clone https://github.com/stsgs1980/Dense-graph.git
cd Dense-graph

# 2. Open the main viewer in any browser
open viewer/id-graph-dense-viewer.html       # macOS
xdg-open viewer/id-graph-dense-viewer.html   # Linux
start viewer/id-graph-dense-viewer.html      # Windows
```

No build step. No server. No dependencies to install. The viewer loads D3.js v7 from a CDN, so you need internet on first open (cached after).

## Regenerating the data

If you have the source Z-ai platform repos checked out locally:

```bash
# Requires Python 3.10+
# Adjust paths inside the script to point at your local checkout
python3 scripts/extract_id_graph_full.py \
  --standards /path/to/Z-ai-platform/standards \
  --guard     /path/to/Z-ai-platform/guard \
  --skills    /path/to/Z-ai-platform/skills \
  --out       data/id-graph-full.json
```

The extractor walks each repo's `*.md` files, parses blockquote headers for ID declarations (`> **ID:** STD-XXX-NNN`), and parses inline references (`Related: STD-XXX-NNN`, `Aligned_with: RULE-XXX-NNN`).

## Tech stack

- **D3.js v7** (force simulation, zoom, drag) — loaded from CDN
- **Vanilla JS + CSS** — no framework, no build step
- **Python 3.10+** — only for the extractor scripts (not needed to view)
- **Graphviz** — only for the static `.dot`/`.svg`/`.png` baseline renders (not needed to view)

## Source

Extracted from the **Z-ai platform** monorepo (platform + standards + guard + skills submodules) at tag `v2.6.0` (2026-06-22).

## License

Internal use. See with repo owner if you need to fork/redistribute.
