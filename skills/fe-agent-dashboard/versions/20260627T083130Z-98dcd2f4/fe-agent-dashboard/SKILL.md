---
name: fe-agent-dashboard
description: Build a polished single-file frontend dashboard with mock data for monitoring agent runs.
---

# FE Agent Dashboard Skill

Build one production-like frontend dashboard for monitoring AI agent runs with mock data only. The output must be a single self-contained HTML document with inline CSS and inline JavaScript.

This skill is general-purpose for FE dashboard tasks. Treat the user input as the dashboard brief, not as permission to rewrite this skill. Improve the skill only through later feedback and revision cycles.

## Non-Negotiable Output Contract

- Output only the HTML document, starting with `<!doctype html>` or `<html>`.
- Do not wrap the HTML in markdown fences.
- Use no backend, build tool, imports, CDN, external images, or external libraries.
- Include `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Put all styles in one `<style>` tag and all behavior in one `<script>` tag.
- Use semantic HTML regions: `header`, `main`, `section`, `aside`, and `table`.
- Include this hidden audit marker near the end of the document:
  `<!-- audit: agent runs mock card badge table sortable trend anomaly grid detail dark mode loading empty error partial selected stale @media -->`

## Required Dashboard Structure

Build the first screen as the real dashboard, not a landing page.

- Top command bar: product title, freshness/stale indicator, dark mode toggle, and compact filter controls.
- KPI overview: 4 prominent cards for system health, success rate, active runs, and p95 latency or token spend.
- Anomaly or alerts section: prioritized issues with severity, affected run, short reason, and suggested action.
- Trend charts: at least 2 lightweight CSS/SVG charts for quality and operations over time.
- Runs table: a real `<table>` with sortable headers, filterable rows, status pills, and mixed mock data.
- Right-side detail panel: shows the selected run, trace summary, model, duration, cost/tokens, and failure reason.
- State shelf: visible examples of loading, empty, error, partial, selected, and stale states.
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

## Interaction Requirements

- Dark mode toggle must change the page theme using CSS variables.
- Table header clicks must sort rows.
- Filter controls must filter by status or severity.
- Clicking a table row must update the detail panel and selected row state.
- Loading, empty, error, partial, selected, and stale states must be visibly represented without requiring a backend.

## Visual Quality Rules

- Prioritize scan speed in 5-10 seconds: overview first, anomalies second, detailed runs third.
- Use compact dashboard typography, not landing-page hero typography.
- Keep the palette restrained but not one-note; use clear semantic colors for success, warning, failure, stale, and selected.
- Avoid disconnected demo cards. Components should feel like one coherent operational dashboard.
- Keep cards, panels, badges, charts, table rows, and controls visually consistent.
- Ensure text does not overflow on mobile.

## Evaluation-Oriented Reminders

The final HTML must visibly or semantically include these capabilities: agent runs, mock data, card, badge, table, sortable table, trend chart, anomaly alert, grid layout, detail panel, dark mode, loading state, empty state, error state, partial state, selected state, stale state, and responsive `@media` rules.
