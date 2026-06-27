---
name: fe-agent-dashboard
description: Build a compact single-file frontend dashboard with mock data for monitoring agent runs.
---

# FE Agent Dashboard Skill

Return only one complete HTML document. Start immediately with `<!doctype html>`. Do not explain, do not use markdown fences, and do not think out loud.

## Output Contract

- Single file HTML/CSS/JS only.
- No backend, build tools, imports, CDN, external images, or external libraries.
- Include viewport meta.
- Include exactly one `<style>` block and one `<script>` block.
- Use `header`, `main`, `section`, `aside`, and a real `<table>`.
- Always close `</style>`, `</script>`, `</body>`, and `</html>`.
- Include this marker near the end:
  `<!-- audit: agent runs mock card badge table sortable trend anomaly grid detail dark mode loading empty error partial selected stale @media -->`

## Build Order

Write the complete document in this order:

1. HTML skeleton with closed tags.
2. Compact CSS variables, grid layout, badges, table, responsive `@media`.
3. Body: header, KPI cards, anomaly strip, two trend charts, run table, detail aside, state shelf.
4. Script: mock data, render table, sort, filter, selected detail, dark mode toggle, empty result state.
5. Audit marker and closing tags.

Complete valid HTML is more important than visual complexity.

## Required UI

- Header with title, stale/freshness indicator, filter controls, and dark mode toggle.
- KPI overview with 4 cards: health, success rate, active runs, latency or token spend.
- Anomaly section with at least 2 alerts and severity badges.
- Two labeled trend charts with latest value labels.
- Sortable and filterable runs table with 6-8 mock rows.
- Right-side detail panel for the selected run.
- State shelf showing: loading, empty, error, partial, selected, stale.
- Mobile responsive layout using `@media`.

## Mock Data

Use compact mock run objects with:
`id`, `agent`, `status`, `score`, `model`, `started_at`, `duration`, `tokens`, `cost`, `severity`, `reason`, `next_action`.

Data must include success, failed, partial, stale, selected, and happy-path runs.

## Interaction

- Dark mode changes CSS variables and updates `aria-pressed`.
- Clicking table headers sorts rows.
- Search/status/severity filters update rows.
- Zero matching rows shows an empty state.
- Clicking a row updates selected state and detail panel.

## Required Exact Words

Ensure these exact words appear in visible text, class names, or concise comments:
`mock`, `agent runs`, `badge`, `sortable`, `trend`, `anomaly`, `dark mode`, `loading`, `empty`, `error`, `partial`, `selected`, `stale`, `grid`, `detail`, `@media`.

## Size Discipline

- Target under 180 lines.
- Keep CSS compact.
- Use short labels.
- Avoid decorative extras until the document is complete.
