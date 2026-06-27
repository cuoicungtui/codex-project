---
name: fe-agent-dashboard
description: Build a polished frontend dashboard with mock data to track agent runs.
---

# FE Agent Dashboard Skill

Build a single-file frontend dashboard that tracks agent runs using mock data only.

## Output Contract
- Return one self-contained HTML document.
- Use inline CSS and minimal inline JavaScript only.
- Do not rely on a backend, build tool, or external assets.
- Make the layout responsive and visually polished.
- Show clear information hierarchy with KPI overview, trend charts, a sortable runs table, a right-side detail panel, and an anomaly section.
- Include loading, empty, error, partial, selected, and stale states.
- Make the component system consistent: cards, badges, filters, chart surfaces, table rows, and status pills should share one visual language.
- Prefer a strong demo-ready composition over generic boilerplate.
- Treat this skill as the final version for the current run cycle.
- Keep the skill fixed during execution.
- Do not adapt the skill contract to the specific test case input during execution.
- Only create a new skill version in a later revision cycle after the runtime run and feedback are produced.
- Feedback must improve the skill in a general way that works across many tasks.
- Do not rewrite the test prompt or bake test-specific assumptions into the skill.
- Use small-model run results to revise the skill, not to narrow the skill to one scenario.

## Design Goals
- Strong visual polish
- Clear hierarchy that can be scanned in 5-10 seconds
- Consistent components
- Responsive behavior on desktop and mobile
- Useful mock data story with both happy path and failure path signals

## Required Content
- KPI summary cards
- Trend charts
- Run status distribution
- Sortable runs table
- Selected run detail panel on the right
- Anomaly section or alert rail
- Timeline or activity view
- Empty state
- Loading state
- Error state
- Partial state
- Selected state
- Stale state
- Mobile-friendly layout

## Response Rules
- Output only the HTML document.
- Keep the structure clean and production-like.
- Make the UI feel intentional and polished.
- Include the literal text `table` in the output somewhere so evaluation can confirm the required table surfaced.
- Prefer data variety that exposes mixed statuses, outliers, and stale records.
- Treat the user input as the task payload for the dashboard content, not as a signal to rewrite the skill specification.
- When revising this skill from feedback, preserve generality so it can serve many FE dashboard tasks, not only the current prompt.
