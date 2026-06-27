---
name: fe-agent-dashboard
description: Build a polished single-file frontend dashboard with mock data for monitoring agent runs.
---

# FE Agent Dashboard Skill

Build one production-like frontend dashboard for monitoring AI agent runs with mock data only. The output must be a single self-contained HTML document with inline CSS and inline JavaScript.

This skill is general-purpose for FE dashboard tasks. Treat the user input as the dashboard brief, not as permission to rewrite this skill. Improve the skill only through later feedback and revision cycles.

## Small-Model Execution Strategy

Small runtime models may run out of output budget or stop early. Optimize for a complete artifact first.

Build in this order:

1. Write the full HTML skeleton: `<!doctype html>`, `<html>`, `<head>`, viewport meta, `<style>`, `</style>`, `<body>`, `header`, `main`, `section`, `aside`, `<script>`, `</script>`, hidden audit marker, `</body>`, and `</html>`.
2. Add the minimum complete dashboard structure before adding polish: KPI cards, anomalies, two charts, runs table, detail panel, and state shelf.
3. Add compact CSS tokens and reusable classes. Do not spend most of the output on decorative CSS before the body exists.
4. Add compact mock data and JavaScript for sorting, filtering, selected run, empty result state, and theme toggle.
5. Add visual polish only after the document is structurally complete.

If output budget feels tight, prefer a simpler but complete dashboard over an ambitious partial dashboard.

## Non-Negotiable Output Contract

- Output only the HTML document, starting with `<!doctype html>` or `<html>`.
- Do not wrap the HTML in markdown fences.
- Use no backend, build tool, imports, CDN, external images, or external libraries.
- Include `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Put all styles in one `<style>` tag and all behavior in one `<script>` tag.
- Use semantic HTML regions: `header`, `main`, `section`, `aside`, and `table`.
- The final output must include a complete `<body>`, one complete `<script>`, and closing `</script>`, `</body>`, and `</html>` tags.
- Never stop inside CSS or JavaScript. Incomplete CSS rules, incomplete HTML, missing body content, or unclosed tags fail the task.
- Include this hidden audit marker near the end of the document:
  `<!-- audit: agent runs mock card badge table sortable trend anomaly grid detail dark mode loading empty error partial selected stale @media -->`

## Required Dashboard Structure

Build the first screen as the real dashboard, not a landing page.

- Top command bar: product title, freshness/stale indicator, dark mode toggle, and compact filter controls.
- KPI overview: 4 prominent cards for system health, success rate, active runs, and p95 latency or token spend.
- Anomaly or alerts section: prioritized issues with severity, affected run, short reason, and suggested action.
- Trend charts: at least 2 lightweight CSS/SVG charts for quality and operations over time.
- Trend charts must include visible context: title, current value or summary, labeled time buckets or axis labels, and a compact legend when multiple series are shown.
- Runs table: a real `<table>` with sortable headers, filterable rows, status pills, mixed mock data, timestamps or freshness, and at least one metric column that can be numerically sorted.
- Right-side detail panel: shows the selected run, trace summary, model, duration, cost/tokens, timestamp/freshness, failure reason, evidence, and recommended next action.
- State shelf: visible examples of loading, empty, error, partial, selected, and stale states.
- Main workflow states: filtering to zero rows must show an empty table state; selected row must update the detail panel; stale and partial states must appear in the main table or alerts, not only in the shelf.
- Responsive mobile layout: collapse to one column, keep table horizontally scrollable or stacked, and move detail panel below the table.

## Mock Data Requirements

Use realistic mock data that exposes both happy and failure paths:

- completed and successful runs
- failed runs
- partial runs
- stale data
- selected run
- at least one anomaly
- different agents, models, durations, token counts, and timestamps
- at least 8 run rows so sorting, filtering, selected state, and failure patterns feel realistic
- Keep mock records compact. A good default is 8-10 run objects with fields: id, agent, status, score, model, started_at, duration, tokens, cost, severity, reason, and next_action.

## Interaction Requirements

- Dark mode toggle must change the page theme using CSS variables.
- Dark mode toggle must update its visible label and `aria-pressed` state.
- Table header clicks must sort rows.
- Filter controls must filter by status or severity.
- Clicking a table row must update the detail panel and selected row state.
- Search or filters that produce no matching rows must render a clear empty state inside the table area.
- Loading, empty, error, partial, selected, and stale states must be visibly represented without requiring a backend.
- Use small local JavaScript helpers for state, sorting, filtering, selected run, and theme behavior. Keep the code understandable and robust; avoid one-off inline event handlers when a named function is clearer.

## Visual Quality Rules

- Prioritize scan speed in 5-10 seconds: overview first, anomalies second, detailed runs third.
- Use compact dashboard typography, not landing-page hero typography.
- Keep the palette restrained but not one-note; use clear semantic colors for success, warning, failure, stale, and selected.
- Avoid disconnected demo cards. Components should feel like one coherent operational dashboard.
- Keep cards, panels, badges, charts, table rows, and controls visually consistent.
- Ensure text does not overflow on mobile.
- Do not make charts decorative only. A user should understand trend direction, metric meaning, and latest value within a few seconds.
- Do not hide operational evidence. Failed and partial runs should expose trace evidence or root cause in the detail panel.
- Prefer production dashboard density: enough rows, compact labels, and clear grouping. Avoid sparse toy examples.
- Keep CSS compact enough for small-model completion. Use a focused design system instead of many long one-off selectors.

## Before Final Output Self-Check

Before returning the HTML, verify these are true:

- The document starts with `<!doctype html>` or `<html>` and is not wrapped in markdown fences.
- The document closes `</style>`, `</script>`, `</body>`, and `</html>`.
- The body exists and contains the actual dashboard UI.
- The first viewport shows dashboard controls and operational data, not a marketing hero.
- KPIs, anomalies, charts, table, and detail panel are all visible or reachable without backend calls.
- Table sorting and filtering work from local mock data.
- Empty, loading, error, partial, selected, and stale states are visible, and at least empty/selected/stale are connected to the main workflow.
- Chart labels and latest values are readable.
- Detail panel includes trace evidence and next action for a failed or partial run.
- Mobile `@media` rules prevent overflow.
- The hidden audit marker is present near the end.

## Evaluation-Oriented Reminders

The final HTML must visibly or semantically include these capabilities: agent runs, mock data, card, badge, table, sortable table, trend chart, anomaly alert, grid layout, detail panel, dark mode, loading state, empty state, error state, partial state, selected state, stale state, and responsive `@media` rules.
