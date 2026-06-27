<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Agent Operations Dashboard</title>
<style>
:root {
  --bg: #f9f9f9;
  --text: #222;
  --primary: #0066ff;
  --success: #28a745;
  --warning: #ffc107;
  --danger: #dc3545;
  --stale: #6c757d;
  --dark-bg: #212529;
  --dark-text: #e9ecef;
}
body {
  margin:0;
  font-family:system-ui,Arial,sans-serif;
  background: var(--bg);
  color: var(--text);
  display:flex;
  flex-direction:column;
  min-height:100vh;
}
header {
  background: var(--primary);
  color:#fff;
  padding:0.5rem 1rem;
  display:flex;
  align-items:center;
  justify-content:space-between;
}
header h1 { margin:0; font-size:1.2rem; }
.dark-mode {
  background: var(--dark-bg);
  color: var(--dark-text);
}
.dark-mode :root {
  --bg: var(--dark-bg);
  --text: var(--dark-text);
  --primary: #66aaff;
  --success: #52c41a;
  --warning: #ffb300;
  --danger: #ff6b6b;
  --stale: #868e96;
}
#theme-toggle {
  background:none;
  border:none;
  color:inherit;
  font-size:1.2rem;
  cursor:pointer;
}
main {
  flex:1;
  padding:1rem;
  display:grid;
  grid-template-columns: 1fr 300px; /* main content + detail panel */
  gap:1rem;
}
@media (max-width: 768px) {
  main { grid-template-columns: 1fr; }
  #detail { display:none; }
}
section {
  margin-bottom:1rem;
}
.kpi-grid {
  display:grid;
  grid-template-columns: repeat(2, 1fr);
  gap:0.5rem;
}
.kpi-card {
  background:#fff;
  border:1px solid #ddd;
  padding:0.75rem;
  border-radius:4px;
  text-align:center;
}
.kpi-card .value { font-size:1.4rem; font-weight:bold; color:var(--primary); }
.kpi-card .label { font-size:0.85rem; color:#555; }
.alerts {
  background:#fff;
  border:1px solid #ddd;
  padding:0.75rem;
  border-radius:4px;
}
.alert-item {
  display:flex;
  align-items:center;
  gap:0.5rem;
  margin-bottom:0.5rem;
}
.alert-item .severity {
  display:inline-block;
  padding:0.2rem 0.5rem;
  border-radius:3px;
  font-size:0.8rem;
  color:#fff;
}
.alert-item .severity.severe { background:var(--danger); }
.alert-item .severity.warning { background:var(--warning); }
.alert-item .severity.info { background:var(--primary); }
.alert-item .details { flex:1; }
.alert-item .action { font-size:0.85rem; color:#0066ff; }
.trend-chart {
  background:#fff;
  border:1px solid #ddd;
  padding:0.5rem;
  border-radius:4px;
  position:relative;
}
.trend-chart .title { font-size:0.9rem; margin-bottom:0.3rem; }
.trend-chart .value { font-size:1rem; font-weight:bold; }
.chart-bars {
  height:12px;
  display:flex;
  gap:2px;
}
.chart-bar {
  flex:1;
  background:var(--primary);
}
.chart-bar.warning { background:var(--warning); }
.chart-bar.danger { background:var(--danger); }
.chart-bar.stale { background:var(--stale); }
table {
  width:100%;
  border-collapse:collapse;
  background:#fff;
  border:1px solid #ddd;
}
thead th {
  background:#f0f0f0;
  cursor:pointer;
  user-select:none;
  padding:0.5rem;
  text-align:left;
  border-bottom:2px solid transparent;
}
thead th.sort-asc::after { content:" ▲"; }
thead th.sort-desc::after { content:" ▼"; }
tbody tr {
  border-bottom:1px solid #eee;
}
tbody tr:hover { background:#f9f9f9; }
.status-pill {
  display:inline-block;
  padding:0.2rem 0.5rem;
  border-radius:3px;
  font-size:0.8rem;
  margin-right:0.5rem;
}
.status-pill.success { background:var(--success); color:#fff; }
.status-pill.failure { background:var(--danger); color:#fff; }
.status-pill.partial { background:var(--warning); color:#000; }
.status-pill.stale { background:var(--stale); color:#fff; }
.empty-state, .loading-state, .error-state {
  padding:1rem;
  text-align:center;
  color:#555;
}
.detail-panel {
  background:#fff;
  border:1px solid #ddd;
  padding:0.75rem;
  border-radius:4px;
  max-height:500px;
  overflow-y:auto;
}
.detail-panel .header {
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:0.5rem;
}
.detail-panel .header .status-pill { margin:0; }
.detail-panel .trace { white-space:pre-wrap; font-family:monospace; font-size:0.85rem; background:#f7f7f7; padding:0.5rem; border-radius:4px; }
</style>
</head>
<body>
<header>
  <h1>AI Agent Operations Dashboard</h1>
  <div>
    <span id="stale-indicator">Stale: <strong>2 mins</strong></span>
    <button id="theme-toggle" aria-pressed="false">🌙 Dark</button>
  </div>
</header>

<main>
  <!-- KPI Grid -->
  <section class="kpi-grid">
    <div class="kpi-card">
      <div class="label">System Health</div>
      <div class="value" id="health-value">98%</div>
    </div>
    <div class="kpi-card">
      <div class="label">Success Rate</div>
      <div class="value" id="success-rate">94%</div>
    </div>
    <div class="kpi-card">
      <div class="label">Active Runs</div>
      <div class="value" id="active-runs">5</div>
    </div>
    <div class="kpi-card">
      <div class="label">p95 Latency</div>
      <div class="value" id="p95-latency">120ms</div>
    </div>
  </section>

  <!-- Anomaly Alerts -->
  <section class="alerts">
    <div class="alert-item severe">
      <span class="severity severe">Severe</span>
      <div class="details">Run #42 failed due to timeout</div>
      <div class="action">Retry now</div>
    </div>
    <div class="alert-item warning">
      <span class="severity warning">Warning</span>
      <div class="details">Run #37 partial result</div>
      <div class="action">Investigate</div>
    </div>
  </section>

  <!-- Trend Charts -->
  <section class="trend-chart">
    <div class="title">Quality Score Trend</div>
    <div class="value" id="quality-value">87</div>
    <div class="chart-bars" id="quality-bars">
      <div class="chart-bar" style="width:30%; background:var(--primary);"></div>
      <div class="chart-bar" style="width:25%; background:var(--warning);"></div>
      <div class="chart-bar" style="width:20%; background:var(--danger);"></div>
      <div class="chart-bar" style="width:15%; background:var(--stale);"></div>
      <div class="chart-bar" style="width:10%; background:var(--success);"></div>
    </div>
  </section>

  <section class="trend-chart">
    <div class="title">Operations Load</div>
    <div class="value" id="load-value">45</div>
    <div class="chart-bars" id="load-bars">
      <div class="chart-bar" style="width:40%; background:var(--primary);"></div>
      <div class="chart-bar" style="width:30%; background:var(--warning);"></div>
      <div class="chart-bar" style="width:20%; background:var(--danger);"></div>
      <div class="chart-bar" style="width:10%; background:var(--stale);"></div>
    </div>
  </section>

  <!-- Runs Table -->
  <section>
    <input type="text" id="filter-search" placeholder="Search runs..." style="margin-bottom:0.5rem; width:100%; max-width:300px;">
    <div style="margin-bottom:0.5rem;">
      <select id="filter-status">
        <option value="">All Status</option>
        <option value="completed">Completed</option>
        <option value="failed">Failed</option>
        <option value="partial">Partial</option>
      </select>
      <select id="filter-severity">
        <option value="">All Severity</option>
        <option value="severe">Severe</option>
        <option value="warning">Warning</option>
        <option value="info">Info</option>
      </select>
    </div>
    <table id="runs-table">
      <thead>
        <tr>
          <th data-key="id" class="sortable">ID <span class="sort-indicator"></span></th>
          <th data-key="agent" class="sortable">Agent <span class="sort-indicator"></span></th>
          <th data-key="status" class="sortable">Status <span class="sort-indicator"></span></th>
          <th data-key="score" class="sortable">Score <span class="sort-indicator"></span></th>
          <th data-key="model" class="sortable">Model <span class="sort-indicator"></span></th>
          <th data-key="started_at" class="sortable">Started <span class="sort-indicator"></span></th>
          <th data-key="duration" class="sortable">Duration <span class="sort-indicator"></span></th>
          <th data-key="tokens" class="sortable">Tokens <span class="sort-indicator"></span></th>
          <th data-key="cost" class="sortable">Cost <span class="sort-indicator"></span></th>
          <th data-key="severity" class="sortable">Severity <span class="sort-indicator"></span></th>
        </tr>
      </thead>
      <tbody>
        <!-- rows will be injected -->
      </tbody>
    </table>

    <!-- Empty state -->
    <div id="empty-state" class="empty-state" style="display:none;">No runs match your filters.</div>
    <div id="loading-state" class="loading-state" style="display:none;">Loading runs...</div>
    <div id="error-state" class="error-state" style="display:none;">Error loading runs.</div>
  </section>

  <!-- Detail Panel (right side) -->
  <aside id="detail" class="detail-panel" style="display:none;">
    <div class="header">
      <strong id="detail-title"></strong>
      <span id="detail-status" class="status-pill"></span>
    </div>
    <div id="detail-trace"
