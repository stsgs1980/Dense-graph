# P-MAS v2 — Wireframes for fork discussion

Six wireframe sketches exploring the UI for a forked P-MAS. These are **static mockups** (HTML + CSS, no real data flow) — discussion artifacts to align on design system + feature scope before forking P-MAS and building the real thing.

## Files

| File | Page | Purpose | Size |
|---|---|---|---|
| `01-dashboard.html` | Dashboard | Home page: KPI strip, status donut, top performers, network activity chart, system health, activity timeline | 47 KB |
| `02-hierarchy.html` | Agent Hierarchy | Left tree + center force-directed canvas + right agent detail panel (connections, tasks, history). Add Agent modal. | 52 KB |
| `03-workflows.html` | Workflows | 3 tabs: All Workflows / Create New / History. Pipeline canvas with steps + decision diamond + feedback loops. | 63 KB |
| `06-task-management.html` | Tasks | 4 views: Board (Kanban) / List / Timeline / Calendar. Task detail + Create Task modals. Priority colors. | 84 KB |
| `07-formula-explorer.html` | Formula Explorer | 3 tabs: Dependency Graph / Matrix / Catalog. Tier color-coding (Foundational / Verification / Planning / Advanced). | 61 KB |
| `pmas-architector-extension.html` | Architector (RU) | Agent + Skill editor. 5 roles: Orchestrator / Planner / Evaluator / Executor / Monitor. Tabs: Agent Form (4 sections: Basic Info / Cognitive / Tools & Memory / Connections) / Skill Form. | 89 KB |

## Shared design system (consistent across all 6)

```
Background       #000000          (pure black)
Surface tier 1   #0A0A0F          (panels)
Surface tier 2   #111118          (cards in panels)
Surface tier 3   #16161E          (raised elements)
Border           #27272A → #3F3F46
Text 3-tier      #FAFAFA / #A1A1AA / #52525B
Accent           #06B6D4          (cyan, primary CTA + active state)
Accent variants  #22D3EE (light) / #0891B2 (mid) / #0E7490 (deep)
Status
  active/ok      #22C55E or #10B981
  pending/warn   #F59E0B or #EAB308
  failed         #EF4444
  planning       #8B5CF6
Header height    56px
Font             system-ui (01 uses JetBrains Mono for monospace accents)
External deps    none (only 01 loads Google Fonts)
```

All 6 wireframes are single-file HTML with no JS framework — pure CSS mockups with a few inline `onclick` handlers for tab switching.

## Open questions to resolve before forking P-MAS

1. **Backend reuse**: which P-MAS APIs survive the fork, which get replaced?
2. **Data source**: real-time agent state (WebSockets) or polling REST?
3. **Auth**: multi-tenant or single-user?
4. **Missing pages**: no Settings, no Login, no Audit Log, no User Management in the current set
5. **Mobile**: 6 wireframes are all 1440px desktop — is mobile a fork goal?
6. **Naming**: new repo name for the fork? `pmas-v2`, `pmas-cyan`, `agent-orchestrator`?

See [../README.md](../README.md) for repo-level context.
