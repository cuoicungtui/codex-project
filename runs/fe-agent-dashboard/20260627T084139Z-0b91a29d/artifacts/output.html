<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Agent Operations Dashboard</title>
<style>
:root {
  --bg: #f5f7fa;
  --text: #222;
  --primary: #0066ff;
  --success: #28a745;
  --warning: #ffc107;
  --danger: #dc3545;
  --stale: #6c757d;
  --selected: #e2e6ea;
}
[data-theme="dark"] {
  --bg: #1e1e2f;
  --text: #e0e0e0;
  --primary: #4da6ff;
  --success: #2e7d32;
  --warning: #ffb74d;
  --danger: #c62828;
  --stale: #9e9e9e;
}
body {
  margin:0;
  font-family:system-ui,Arial,sans-serif;
  background:var(--bg);
  color:var(--text);
  display:flex;
  flex-direction:column;
  min-height:100vh;
}
header {
  background:var(--primary);
  color:#fff;
  padding:0.5rem 1rem;
  display:flex;
  align-items:center;
  justify-content:space-between;
}
header h1 { margin:0; font-size:1.2rem; }
#theme-toggle {
  background:none;
  border:none;
  color:#fff;
  font-size:1.2rem;
  cursor:pointer;
}
#filter-controls {
  display:flex;
  gap:0.5rem;
  align-items:center;
}
#filter-controls select, #filter-controls input {
  padding:0.25rem;
  border-radius:4px;
  border:1px solid #ccc;
}
main {
  flex:1;
  display:grid;
  grid-template-columns: 3fr 1fr;
  gap:1rem;
  padding:1rem;
}
section.kpi {
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
  gap:0.5rem;
}
.card {
  background:#fff;
  border-radius:6px;
  padding:0.75rem;
  box-shadow:0 1px 3px rgba(0,0,0,0.1);
  text-align:center;
}
.card h3 { margin:0 0 0.25rem; font-size:0.9rem; }
.card .value { font-size:1.4rem; font-weight:600; }
.alerts {
  background:#fff;
  border-radius:6px;
  padding:0.75rem;
  margin-top:1rem;
}
.alert-item {
  display:flex;
  align-items:center;
  gap:0.5rem;
  margin-bottom:0.5rem;
  padding:0.5rem;
  border-left:4px solid var(--danger);
  background:#f9f9f9;
}
.alert-item.severity-warning { border-left-color:var(--warning); }
.alert-item.severity-info { border-left-color:var(--primary); }
.chart {
  background:#fff;
  border-radius:6px;
  padding:0.75rem;
  margin-top:1rem;
  height:200px;
}
.table-wrapper {
  overflow-x:auto;
}
table {
  width:100%;
  border-collapse:collapse;
  background:#fff;
  border-radius:6px;
  box-shadow:0 1px 3px rgba(0,0,0,0.1);
}
th, td {
  padding:0.5rem;
  text-align:left;
  border-bottom:1px solid #e0e0e0;
}
th {
  cursor:pointer;
  user-select:none;
  background:#f0f0f0;
  position:sticky;
  top:0;
}
tr:hover { background:#f9f9f9; }
.status-pill {
  display:inline-block;
  padding:0.25rem 0.5rem;
  border-radius:0.75rem;
  font-size:0.75rem;
  margin-right:0.5rem;
}
.pill-success { background:var(--success); color:#fff; }
.pill-danger { background:var(--danger); color:#fff; }
.pill-stale { background:var(--stale); color:#fff; }
.pill-warning { background:var(--warning); color:#000; }
.detail-panel {
  background:#fff;
  border-radius:6px;
  padding:0.75rem;
  height:calc(100% - 2rem);
  display:flex;
  flex-direction:column;
  gap:0.5rem;
}
.detail-header {
  display:flex;
  justify-content:space-between;
  align-items:center;
}
.detail-header h2 { margin:0; font-size:1.1rem; }
.detail-body { flex:1; }
.trace-text {
  white-space:pre-wrap;
  background:#f5f5f5;
  padding:0.5rem;
  border-radius:4px;
  font-family:monospace;
  font-size:0.85rem;
}
.next-action { font-weight:600; }
.state-shelf {
  background:#fff;
  border-radius:6px;
  padding:0.75rem;
  margin-top:1rem;
}
.state-item {
  display:flex;
  align-items:center;
  gap:0.5rem;
  padding:0.5rem;
  margin-bottom:0.5rem;
  border-radius:4px;
}
.state-item.loading { background:#e8f5e9; border-left:4px solid #4caf50; }
.state-item.empty { background:#fff3e0; border-left:4px solid #ff9800; }
.state-item.error { background:#ffebee; border-left:4px solid #f44336; }
.state-item.partial { background:#fffde7; border-left:4px solid #ffb300; }
.state-item.selected { background:#e3f2fd; border-left:4px solid #2196f3; }
.state-item.stale { background:#f5f5f5; border-left:4px solid #607d8b; }
@media (max-width: 768px) {
  main { grid-template-columns:1fr; }
  .detail-panel { height:auto; }
}
</style>
</head>
<body>
<header>
  <h1>AI Agent Operations Dashboard</h1>
  <button id="theme-toggle" aria-pressed="false">🌙 Dark</button>
  <div id="filter-controls">
    <select id="status-filter">
      <option value="all">All</option>
      <option value="success">Success</option>
      <option value="failed">Failed</option>
      <option value="partial">Partial</option>
    </select>
    <select id="severity-filter">
      <option value="all">All</option>
      <option value="high">High</option>
      <option value="medium">Medium</option>
      <option value="low">Low</option>
    </select>
    <input type="text" id="search" placeholder="Search runs...">
  </div>
</header>

<main>
  <!-- KPI Cards -->
  <section class="kpi">
    <div class="card">
      <h3>System Health</h3>
      <div class="value" id="health-value">98%</div>
    </div>
    <div class="card">
      <h3
