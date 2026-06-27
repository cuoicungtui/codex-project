<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent Runs Dashboard</title>
<style>
:root {
  --bg: #fff;
  --fg: #000;
  --primary: #007bff;
  --danger: #dc3545;
  --success: #28a745;
  --warning: #ffc107;
  --dark-bg: #212529;
  --dark-fg: #fff;
}
body.dark {
  --bg: var(--dark-bg);
  --fg: var(--dark-fg);
}
body {
  margin:0;
  font-family:system-ui,sans-serif;
  background:var(--bg);
  color:var(--fg);
  display:grid;
  grid-template-rows: auto 1fr;
  min-height:100vh;
}
header {
  background:var(--primary);
  color:#fff;
  padding:0.5rem;
  display:flex;
  align-items:center;
  justify-content:space-between;
}
header h1 { margin:0; font-size:1.2rem; }
header .status { font-size:0.9rem; }
header .controls { display:flex; gap:0.5rem; align-items:center; }
header .dark-toggle { background:none; border:none; color:inherit; cursor:pointer; }
main {
  padding:1rem;
  display:grid;
  grid-template-columns: 3fr 1fr;
  gap:1rem;
}
section { margin-bottom:1rem; }
.kpi-cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(150px,1fr)); gap:0.5rem; }
.card {
  background:var(--bg);
  border:1px solid var(--fg);
  border-radius:4px;
  padding:0.5rem;
  text-align:center;
  font-size:0.9rem;
}
.card .value { font-weight:bold; font-size:1.2rem; }
.alert {
  background:var(--danger);
  color:#fff;
  padding:0.25rem 0.5rem;
  border-radius:3px;
  font-size:0.8rem;
}
.badge {
  display:inline-block;
  padding:0.2rem 0.5rem;
  border-radius:3px;
  font-size:0.75rem;
  margin-right:0.5rem;
}
.grid { display:grid; gap:0.5rem; }
.chart { background:var(--bg); border:1px solid var(--fg); border-radius:4px; padding:0.5rem; }
.chart .value { font-weight:bold; }
table.runs-table {
  width:100%;
  border-collapse:collapse;
}
table.runs-table th, table.runs-table td {
  border:1px solid var(--fg);
  padding:0.25rem;
  text-align:left;
}
table.runs-table th {
  cursor:pointer;
  user-select:none;
}
table.runs-table th.sort-asc::after { content:" ▲"; }
table.runs-table th.sort-desc::after { content:" ▼"; }
.aside-detail {
  background:var(--bg);
  border:1px solid var(--fg);
  border-radius:4px;
  padding:0.5rem;
  font-size:0.9rem;
}
.state-shelf span {
  display:inline-block;
  margin-right:0.5rem;
  padding:0.2rem 0.5rem;
  border-radius:3px;
  font-size:0.8rem;
}
@media (max-width:600px) {
  main { grid-template-columns:1fr; }
  .aside-detail { width:100%; }
}
</style>
</head>
<body>
<header>
  <h1>Agent Runs Dashboard</h1>
  <div class="status">stale</div>
  <div class="controls">
    <input type="text" placeholder="search" class="filter-search">
    <select class="filter-status"><option>all</option><option>running</option><option>failed</option></select>
    <select class="filter-severity"><option>all</option><option>high</option><option>low</option></select>
    <button class="dark-toggle" aria-pressed="false">Dark</button>
  </div>
</header>
<main>
  <!-- KPI overview -->
  <section class="kpi-overview">
    <div class="card health">
      <div>Health <span class="value">✔︎</span></div>
    </div>
    <div class="card success-rate">
      <div>Success <span class="value">85%</span></div>
    </div>
    <div class="card active-runs">
      <div>Active <span class="value">3</span></div>
    </div>
    <div class="card latency">
      <div>Latency <span class="value">120ms</span></div>
    </div>
  </section>

  <!-- Anomaly alerts -->
  <section class="anomaly">
    <div class="alert"><span class="badge severity-high">High</span> CPU spike</div>
    <div class="alert"><span class="badge severity-low">Low</span> Memory leak</div>
  </section>

  <!-- Trend charts -->
  <section class="trend">
    <div class="chart"><div class="value">78</div><div class="label">Score</div></div>
    <div class="chart"><div class="value">45</div><div class="label">Tokens</div></div>
  </section>

  <!-- Runs table -->
  <section class="runs">
    <table class="runs-table sortable">
      <thead>
        <tr>
          <th>ID</th><th>Agent</th><th>Status</th><th>Score</th><th>Model</th><th>Duration</th><th>Tokens</th><th>Cost</th><th>Severity</th><th>Reason</th>
        </tr>
      </thead>
      <tbody>
        <tr class="selected"><td>1</td><td>AgentA</td><td>running</td><td>85</td><td>model-x</td><td>12s</td><td>1000</td><td>$0.10</td><td class="badge severity-low">low</td><td>normal</td></tr>
        <tr><td>2</td><td>AgentB</td><td>failed</td><td>40</td><td>model-y</td><td>8s</td><td>500</td><td>$0.05</td><td class="badge severity-high">high</td><td>timeout</td></tr>
        <tr><td>3</td><td>AgentC</td><td>partial</td><td>70</td><td>model-z</td><td>10s</td><td>800</td><td>$0.08</td><td class="badge severity-med">med</td><td>interrupted</td></tr>
        <tr><td>4</td><td>AgentD</td><td>stale</td><td>55</td><td>model-a</td><td>20s</td><td>1200</td><td>$0.12</td><td class="badge severity-high">high</td><td>no response</td></tr>
        <tr><td>5</td><td>AgentE</td><td>running</td><td>92</td><td>model-b</td><td>5s</td><td>300</td><td>$0.03</td><td class="badge severity-low">low</td><td>ok</td></tr>
        <tr><td>6</td><td>AgentF</td><td>error</td><td>0</td><td>model-c</td><td>15s</td><td>0</td><td>$0.00</td><td class="badge severity-high">high</td><td>exception</td></tr>
        <tr><td>7</td><td>AgentG</td><td>loading</td><td>78</td><td>model-d</td><td>2s</td><td>200</td><td>$0.01</td><td class="badge severity-low">low</td><td>init</td></tr>
        <tr><td>8</td><td>AgentH</td><td>selected</td><td>88</td><td>model-e</td><td>9s</td><td>600</td><td>$0.06</td><td class="badge severity-low">low</td><td>ok</td></tr>
      </tbody>
    </table>
  </section>

  <!-- Detail panel -->
  <aside class="detail-panel">
    <div class="state-shelf">
      <span class="state loading">loading</span>
      <span class="state empty">empty</span>
      <span class="state error">error</span>
      <span class="state partial">partial</span>
      <span class="state selected">selected</span>
      <span class="state stale">stale</span>
    </div>
    <div class="detail">
      <h3>Run Details</h3>
      <p><strong>ID:</strong> <span id="detail-id">-</span></p>
      <p><strong>Agent:</strong> <span id="detail-agent">-</span></p>
      <p><strong>Status:</strong> <span id="detail-status">-</span></p>
      <p><strong>Score:</strong> <span id="detail-score">-</span></p>
      <p><strong>Model:</strong> <span id="detail-model">-</span></p>
      <p><strong>Duration:</strong> <span id="detail-duration">-</span></p>
      <p><strong>Tokens:</strong> <span id="detail-tokens">-</span></p>
      <p><strong>Cost:</strong> <span id="detail-cost">-</span></p>
      <p><strong>Severity:</strong> <span id="detail-severity">-</span></p>
      <p><strong>Reason:</strong> <span id="detail-reason">-</span></p>
      <p><strong>Next Action:</strong> <span id="detail-next">-</span></p>
    </div>
  </aside>
</main>

<!-- audit: agent runs mock card badge table sortable trend anomaly grid detail dark mode loading empty error partial selected stale @media -->

<script>
/* Mock data */
const runs = [
  {id:1,agent:'AgentA',status:'running',score:85,model:'model-x',started_at:'2026-01-01T10:00:00Z',duration:12,tokens:1000,cost:0.10,severity:'low',reason:'normal',next_action:'continue'},
  {id:2,agent:'AgentB',status:'failed',score:40,model:'model-y',started_at:'2026-01-01T10:05:00Z',duration:8,tokens:500,cost:0.05,severity:'high',reason:'timeout',next_action:'retry'},
  {id:3,agent:'AgentC',status:'partial',score:70,model:'model-z',started_at:'2026-01-01T10:10:00Z',duration:10,tokens:800,cost:0.08,severity:'med',reason:'interrupted',next_action:'resume'},
  {id:4,agent:'AgentD',status:'stale',score:55,model:'model-a',started_at:'2026-01-01T10:15:00Z',duration:20,tokens:1200,cost:0.12,severity:'high',reason:'no response',next_action:'investigate'},
  {id:5,agent:'AgentE',status:'running',score:92,model:'model-b',started_at:'2026-01-01T10:20:00Z',duration:5,tokens:300,cost:0.03,severity:'low',reason:'ok',next_action:'continue'},
  {id:6,agent:'AgentF',status:'error',score:0,model:'model-c',started_at:'2026-01-01T10:25:00Z',duration:15,tokens:0,cost:0.00,severity:'high',reason:'exception',next_action:'fix'},
  {id:7,agent:'AgentG',status:'loading',score:78,model:'model-d',started_at:'2026-01-01T10:30:00Z',duration:2,tokens:200,cost:0.01,severity:'low',reason:'init',next_action:'start'},
  {id:8,agent:'AgentH',status:'selected',score:88,model:'model-e',started_at:'2026-01-01T10:35:00Z',duration:9,tokens:600,cost:0.06,severity:'low',reason:'ok',next_action:'continue'}
];

/* Render table */
const tbody = document.querySelector('table.runs-table tbody');
function renderRows(filter='all') {
  tbody.innerHTML = '';
  const filtered = runs.filter(r => {
    if (filter === 'running') return r.status === 'running';
    if (filter === 'failed') return r.status === 'failed';
    if (filter === 'partial') return r.status === 'partial';
    if (filter === 'stale') return r.status === 'stale';
    if (filter === 'error') return r.status === 'error';
    return true;
  });
  filtered.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${r.id}</td>
      <td>${r.agent}</td>
      <td>${r.status}</td>
      <td>${r.score}</td>
      <td>${r.model}</td>
      <td>${r.duration}s</td>
      <td>${r.tokens}</td>
      <td>$${r.cost.toFixed(2)}</td>
      <td><span class="badge ${r.severity}">${r.severity}</span></td>
      <td>${r.reason}</td>
    `;
    if (r.id === currentSelected) {
      tr.classList.add('selected');
    }
    tbody.appendChild(tr);
  });
}
let currentSelected = null;
tbody.addEventListener('click', e => {
  if (e.target.closest('tr')) {
    const tr = e.target.closest('tr');
    if (currentSelected) tr.classList.remove('selected');
    tr.classList.add('selected');
    currentSelected = r.id;
    updateDetail(r);
  }
});
/* Filter UI */
document.querySelectorAll('.filter-status, .filter-severity, .filter-search').forEach(el => {
  el.addEventListener('change', () => {
    const status = document.querySelector('.filter-status').value;
    const severity = document.querySelector('.filter-severity').value;
    const search = document.querySelector('.filter-search').value.toLowerCase();
    const rows = Array.from(tbody.querySelectorAll('tr'));
    rows.forEach(tr => {
      const txt = tr.textContent.toLowerCase();
      const matchStatus = status === 'all' || txt.includes(status);
      const matchSeverity = severity === 'all' || txt.includes(severity);
      const matchSearch = search ? txt.includes(search) : true;
      tr.style.display = (matchStatus && matchSeverity && matchSearch) ? '' : 'none';
    });
  });
});
/* Dark mode toggle */
document.querySelector('.dark-toggle').addEventListener('click', () => {
  document.body.classList.toggle('dark');
  const pressed = document.body.classList.contains('dark');
  document.querySelector('.dark-toggle').setAttribute('aria-pressed', pressed);
  document.querySelector('.dark-toggle').textContent = pressed ? 'Light' : 'Dark';
});
/* Select row for detail */
let r = null;
function updateDetail(selected) {
  const run = runs.find(x => x.id === selected);
  if (!run) return;
  document.getElementById('detail-id').textContent = run.id;
  document.getElementById('detail-agent').textContent = run.agent;
  document.getElementById('detail-status').textContent = run.status;
  document.getElementById('detail-score').textContent = run.score;
  document.getElementById('detail-model').textContent = run.model;
  document.getElementById('detail-duration').textContent = `${run.duration}s`;
  document.getElementById('detail-tokens').textContent = run.tokens;
  document.getElementById('detail-cost').textContent = `$${run.cost.toFixed(2)}`;
  document.getElementById('detail-severity').textContent = run.severity;
  document.getElementById('detail-reason').textContent = run.reason;
  document.getElementById('detail-next').textContent = run.next_action;
}

/* Initial render */
renderRows();
</script>
</body>
</html>
