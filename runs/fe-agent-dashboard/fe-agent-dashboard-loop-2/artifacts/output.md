<!--
  Mock Data Dashboard (single-file HTML/CSS/JS)
  -------------------------------------------------
  This file generates all UI and mock data client‑side.
  Open the file in any modern browser to view the dashboard.
  The mock data includes a variety of agent runs (success, failed,
  partial, stale, selected, loading, empty, error) to demonstrate
  the required visual hierarchy and states.
-->

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>FE Agent Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  :root {
    --bg-light: #f9fafb;
    --bg-dark: #1e1e1e;
    --text-light: #212529;
    --text-dark: #e5e5e5;
    --primary: #0066ff;
    --primary-dark: #004ecc;
    --success: #28a745;
    --danger: #dc3545;
    --warning: #ffc107;
    --card-bg: var(--bg-light);
    --card-bg-dark: var(--bg-dark);
    --border: #dee2e6;
  }
  body {
    margin:0;
    font-family:system-ui,Arial,sans-serif;
    background: var(--card-bg);
    color: var(--text-light);
    transition: background .3s, color .3s;
  }
  body.dark {
    background: var(--bg-dark);
    color: var(--text-dark);
  }
  header {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:1rem;
    background: var(--primary);
    color:#fff;
  }
  .dark-mode-toggle {
    background:none;
    border:none;
    color:var(--text-dark);
    font-size:1.2rem;
    cursor:pointer;
  }
  .container {
    display:grid;
    grid-template-columns: 3fr 1fr;
    gap:1rem;
    padding:1rem;
  }
  @media (max-width:768px) {
    .container {
      grid-template-columns:1fr;
    }
  }
  .kpi-grid {
    display:grid;
    grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
    gap:1rem;
  }
  .kpi-card {
    background:var(--card-bg);
    border:1px solid var(--border);
    border-radius:8px;
    padding:1rem;
    text-align:center;
    box-shadow:0 2px 4px rgba(0,0,0,0.05);
  }
  .kpi-card.dark {
    background:var(--card-bg-dark);
    border-color:var(--border);
  }
  .kpi-card h3 {
    margin:0 0 .5rem;
    font-size:1.1rem;
  }
  .kpi-card p {
    margin:0;
    font-size:1.4rem;
    font-weight:600;
  }
  .trend-chart {
    background:var(--card-bg);
    border:1px solid var(--border);
    border-radius:8px;
    padding:1rem;
    margin-top:1rem;
  }
  .trend-title {
    font-weight:600;
    margin-bottom:.5rem;
  }
  .table-wrapper {
    overflow-x:auto;
  }
  .runs-table {
    width:100%;
    border-collapse:collapse;
    background:var(--card-bg);
    border:1px solid var(--border);
    border-radius:8px;
    overflow:hidden;
  }
  .runs-table.dark {
    background:var(--card-bg-dark);
    border-color:var(--border);
  }
  .runs-table th,
  .runs-table td {
    padding:.75rem;
    text-align:left;
    border-bottom:1px solid var(--border);
  }
  .runs-table th {
    background:var(--primary);
    color:#fff;
    cursor:pointer;
    user-select:none;
  }
  .runs-table th.sort-asc::after {
    content:" ▲";
  }
  .runs-table th.sort-desc::after {
    content:" ▼";
  }
  .runs-table tr:hover {
    background:rgba(0,0,0,0.05);
  }
  .runs-table.dark tr:hover {
    background:rgba(255,255,255,0.05);
  }
  .filter-input {
    width:100%;
    padding:.5rem;
    margin-bottom:.5rem;
    border:1px solid var(--border);
    border-radius:4px;
    background:var(--card-bg);
    color:var(--text-light);
  }
  .filter-input.dark {
    background:var(--card-bg-dark);
    color:var(--text-dark);
    border-color:var(--border);
  }
  .detail-panel {
    background:var(--card-bg);
    border:1px solid var(--border);
    border-radius:8px;
    padding:1rem;
    margin-top:1rem;
    box-shadow:0 2px 4px rgba(0,0,0,0.05);
  }
  .detail-panel.dark {
    background:var(--card-bg-dark);
    border-color:var(--border);
  }
  .detail-panel h2 {
    margin-top:0;
    font-size:1.2rem;
  }
  .detail-info {
    margin: .5rem 0;
  }
  .detail-info span {
    font-weight:600;
  }
  .anomaly-section {
    background:var(--card-bg);
    border:1px solid var(--border);
    border-radius:8px;
    padding:1rem;
    margin-top:1rem;
  }
  .anomaly-section.dark {
    background:var(--card-bg-dark);
    border-color:var(--border);
  }
  .anomaly-item {
    padding:.5rem 0;
    border-bottom:1px solid var(--border);
  }
  .anomaly-item:last-child {
    border-bottom:none;
  }
  .spinner {
    border:4px solid #f3f3f3;
    border-top:4px solid var(--primary);
    border-radius:50%;
    width:36px;
    height:36px;
    animation:spin 1s linear infinite;
    margin:2rem auto;
  }
  @keyframes spin {
    0% {transform:rotate(0deg);}
    100% {transform:rotate(360deg);}
  }
  .empty-state, .error-state {
    text-align:center;
    padding:2rem;
    font-size:1.1rem;
  }
  .timeline {
    position:relative;
    margin-top:1rem;
  }
  .timeline::before {
    content:"";
    position:absolute;
    left:50%;
    top:0;
    width:2px;
    height:100%;
    background:var(--border);
    transform:translateX(-50%);
  }
  .timeline-item {
    position:relative;
    margin:1rem 0;
    padding-left:1.5rem;
  }
  .timeline-item::before {
    content:"";
    position:absolute;
    left:0;
    top:50%;
    width:12px;
    height:12px;
    background:#0066ff;
    border-radius:50%;
    transform:translateY(-50%);
  }
  .timeline-text {
    font-size:.95rem;
  }
</style>
</head>
<body>
<header>
  <h1>AI Agent Dashboard</h1>
  <button class="dark-mode-toggle" id="darkToggle">Dark mode (toggle)</button>
</header>

<div class="container">
  <!-- KPI Overview -->
  <section class="kpi-grid" id="kpiGrid">
    <div class="kpi-card" id="kpiTotalRuns">
      <h3>Total Agent Runs (mock data)</h3>
      <p id="totalCount">0</p>
    </div>
    <div class="kpi-card" id="kpiSuccessRate">
      <h3>Success Rate</h3>
      <p id="successRate">0%</p>
    </div>
    <div class="kpi-card" id="kpiAvgDuration">
      <h3>Avg Duration (s)</h3>
      <p id="avgDuration">0</p>
    </div>
  </section>

  <!-- Trend Charts -->
  <section class="trend-chart" id="qualityTrend">
    <div class="trend-title">Quality Trend</div>
    <canvas id="qualityChart" width="300" height="150"></canvas>
  </section>

  <section class="trend-chart" id="runtimeTrend">
    <div class="trend-title">Runtime Trend</div>
    <canvas id="runtimeChart" width="300" height="150"></canvas>
  </section>

  <!-- Runs Table -->
  <div class="table-wrapper">
    <input type="text" class="filter-input" placeholder="Filter runs by status..." id="filterInput">
    <table class="runs-table" id="runsTable">
      <caption>Sortable runs table</caption>
      <thead>
        <tr>
          <th data-key="id">ID</th>
          <th data-key="timestamp">Timestamp</th>
          <th data-key="status">Status</th>
          <th data-key="duration">Duration (s)</th>
          <th data-key="quality">Quality</th>
        </tr>
      </thead>
      <tbody id="runsBody"></tbody>
    </table>
  </div>

  <!-- Detail Panel (right side) -->
  <aside class="detail-panel" id="detailPanel" style="display:none;">
    <h2 id="detailTitle">Run Details</h2>
    <div class="detail-info"><span>ID:</span> <span id="detailId"></span></div>
    <div class="detail-info"><span>Timestamp:</span> <span id="detailTime"></span></div>
    <div class="detail-info"><span>Status:</span> <span id="detailStatus"></span></div>
    <div class="detail-info"><span>Duration (s):</span> <span id="detailDuration"></span></div>
    <div class="detail-info"><span>Quality:</span> <span id="detailQuality"></span></div>
    <div class="detail-info"><span>Notes:</span> <span id="detailNotes"></span></div>
  </aside>

  <!-- Anomaly / Alerts -->
  <section class="anomaly-section" id="anomalySection">
    <h3>Priority Anomaly Alerts</h3>
    <div class="anomaly-item" id="anomaly1">High failure rate detected in last 5 runs.</div>
    <div class="anomaly-item" id="anomaly2">Stale data observed for agent 7.</div>
    <div class="anomaly-item" id="anomaly3">Latency spike > 2s in 3 consecutive runs.</div>
  </section>

  <!-- Loading / Empty / Error States -->
  <div id="loadingState" class="spinner"></div>
  <div id="emptyState" class="empty-state" style="display:none;">
    <p>No agent runs available.</p>
  </div>
  <div id="errorState" class="error-state" style="display:none;">
    <p>Failed to load agent run data. Please try again later.</p>
  </div>
</div>

<script>
(() => {
  // Mock data generation
  const generateMockRuns = () => {
    const statuses = ['success', 'failed', 'partial', 'stale'];
    const runs = [];
    const now = Date.now();
    for (let i = 1; i <= 30; i++) {
      const idx = Math.floor(Math.random() * statuses.length);
      const status = statuses[idx];
      const timestamp = now - (i * 3600000) + Math.floor(Math.random() * 3600000); // +/- up to 1h
      const duration = Math.round(Math.random() * 10 + 30); // 30-40s
      const quality = Math.min(100, Math.max(0, Math.round(Math.random() * 100)));
      runs.push({
        id: `run-${i}`,
        timestamp,
        status,
        duration,
        quality,
        notes: status === 'failed' ? 'Task failed due to timeout' : status === 'partial' ? 'Partial completion' : ''
      });
    }
    return runs;
  };

  // Render KPI cards
  const renderKPIs = (runs) => {
    const total = runs.length;
    const success = runs.filter(r => r.status === 'success').length;
    const avgDur = runs.reduce((sum, r) => sum + r.duration, 0) / total;
    document.getElementById('totalCount').textContent = total;
    document.getElementById('successRate').textContent = `${(success / total * 100).toFixed(1)}%`;
    document.getElementById('avgDuration').textContent = avgDur.toFixed(1);
  };

  // Render trend charts (simple line using canvas)
  const renderTrends = (runs) => {
    const qualityData = runs.map(r => ({x: runs.indexOf(r), y: r.quality}));
    const runtimeData = runs.map(r => ({x: runs.indexOf(r), y: r.duration}));
    const ctxQ = document.getElementById('qualityChart').getContext('2d');
    const ctxR = document.getElementById('runtimeChart').getContext('2d');

    // destroy if exists
    if (window.qualityChart) window.qualityChart.destroy();
    if (window.runtimeChart) window.runtimeChart.destroy();

    window.qualityChart = new Chart(ctxQ, {
      type: 'line',
      data: {
        labels: qualityData.map(d => d.x),
        datasets: [{
          label: 'Quality',
          data: qualityData.map(d => d.y),
          borderColor: 'var(--primary)',
          backgroundColor: 'rgba(0,102,255,0.1)',
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {beginAtZero:true, max:100}
        }
      }
    });

    window.runtimeChart = new Chart(ctxR, {
      type: 'line',
      data: {
        labels: runtimeData.map(d => d.x),
        datasets: [{
          label: 'Runtime (s)',
          data: runtimeData.map(d => d.y),
          borderColor: 'var(--danger)',
          backgroundColor: 'rgba(220,53,69,0.1)',
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {beginAtZero:true}
        }
      }
    });
  };

  // Render runs table with sorting & filtering
  const runsTable = document.getElementById('runsBody');
  const runs = generateMockRuns();
  let currentSortKey = 'id';
  let currentSortDir = 'asc';

  const sortRuns = (key) => {
    currentSortKey = key;
    currentSortDir = currentSortDir === 'asc' ? 'desc' : 'asc';
    runs.sort((a,b) => {
      const aVal = a[key];
      const bVal = b[key];
      if (aVal === bVal) return 0;
      if (aVal < bVal) return currentSortDir === 'asc' ? -1 : 1;
      return currentSortDir === 'asc' ? 1 : -1;
    });
    renderTable();
  };

  const renderTable = () => {
    // filter
    const filter = document.getElementById('filterInput').value.toLowerCase();
    const filtered = runs.filter(r => {
      if (!filter) return true;
      return Object.values(r).some(v => String(v).toLowerCase().includes(filter));
    });
    // sort
    sortRuns(currentSortKey);
    // actually render after sort
    runsTable.innerHTML = '';
    filtered.forEach((r, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.id}</td>
        <td>${new Date(r.timestamp).toLocaleString()}</td>
        <td>${r.status}</td>
        <td>${r.duration}</td>
        <td>${r.quality}</td>
      `;
      // click to select
      tr.style.cursor = 'pointer';
      tr.addEventListener('click', () => showDetail(r));
      runsTable.appendChild(tr);
    });
  };

  document.getElementById('filterInput').addEventListener('input', renderTable);
  document.querySelectorAll('#runsTable th').forEach(th => {
    th.addEventListener('click', () => sortRuns(th.dataset.key));
  });

  // Show detail panel
  const showDetail = (run) => {
    document.getElementById('detailId').textContent = run.id;
    document.getElementById('detailTime').textContent = new Date(run.timestamp).toLocaleString();
    document.getElementById('detailStatus').textContent = run.status;
    document.getElementById('detailDuration').textContent = run.duration;
    document.getElementById('detailQuality').textContent = run.quality;
    document.getElementById('detailNotes').textContent = run.notes;
    document.getElementById('detailPanel').style.display = 'block';
  };

  // Dark mode toggle
  const darkToggle = document.getElementById('darkToggle');
  darkToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
  });

  // Simulate loading -> data -> possible error/empty
  const loading = document.getElementById('loadingState');
  const empty = document.getElementById('emptyState');
  const error = document.getElementById('errorState');

  // Simulate async load with 1.5s delay
  setTimeout(() => {
    // 80% chance success, 10% empty, 10% error
    const scenario = Math.random();
    if (scenario < 0.8) {
      // success
      loading.style.display = 'none';
      renderKPIs(runs);
      renderTrends(runs);
      renderTable();
      document.getElementById('detailPanel').style.display = 'none';
    } else if (scenario < 0.9) {
      // empty
      loading.style.display = 'none';
      empty.style.display = 'block';
    } else {
      // error
      loading.style.display = 'none';
      error.style.display = 'block';
    }
  }, 1500);
})();
</script>
</body>
</html>
