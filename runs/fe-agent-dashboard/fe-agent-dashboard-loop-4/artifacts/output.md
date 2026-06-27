<!-- Mock data source: JavaScript array `runs` contains diverse agent run records (success, failed, partial, stale, etc.). Open this file in a browser to view the dashboard. --> 
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>FE Agent Dashboard</title>
<style>
/* ---------- CSS Variables (Light/Dark) ---------- */
:root {
  --bg-color: #f9f9f9;
  --card-bg: #ffffff;
  --text-color: #333333;
  --primary: #0066cc;
  --danger: #d9534f;
  --success: #5cb85c;
  --border: #e0e0e0;
  --badge-bg: #ffcc00;
}
body.dark {
  --bg-color: #111111;
  --card-bg: #222222;
  --text-color: #eeeeee;
  --primary: #66aaff;
  --danger: #ff6b6b;
  --success: #66bb6a;
  --border: #444444;
}
* { box-sizing: border-box; margin:0; padding:0; }
html, body { height:100%; font-family:Arial,Helvetica,sans-serif; background:var(--bg-color); color:var(--text-color); }
.container { display:grid; grid-template-columns: 3fr 1fr; gap:1rem; height:100%; }
@media (max-width:768px) {
  .container { grid-template-columns: 1fr; }
  .detail-panel { display:none; }
  .detail-panel.active { display:block; }
}

/* ---------- Layout ---------- */
.header { display:flex; justify-content:space-between; align-items:center; padding:0.5rem 1rem; background:var(--card-bg); border-bottom:1px solid var(--border); }
.logo { font-size:1.2rem; font-weight:bold; }
.toggle-dark { background:none; border:none; color:var(--primary); cursor:pointer; font-size:0.9rem; }
.kpi-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(200px,1fr)); gap:1rem; margin-top:1rem; }
.kpi-card { background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:1rem; text-align:center; box-shadow:0 2px 4px rgba(0,0,0,0.05); position:relative; }
.kpi-card .title { font-size:1rem; margin-bottom:0.5rem; }
.kpi-card .value { font-size:1.5rem; font-weight:bold; }
.kpi-card .badge { position:absolute; top:8px; right:8px; background:var(--badge-bg); color:#000; padding:2px 6px; border-radius:4px; font-size:0.75rem; }

/* ---------- Charts ---------- */
.chart { background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:1rem; margin-top:1rem; }
.chart canvas { width:100%; height:150px; }

/* ---------- Table ---------- */
.table-wrap { overflow-x:auto; margin-top:1rem; }
#runs-table { width:100%; border-collapse:collapse; background:var(--card-bg); }
#runs-table th, #runs-table td { padding:0.5rem; border:1px solid var(--border); text-align:left; }
#runs-table th { cursor:pointer; user-select:none; background:var(--primary); color:#fff; }
#runs-table th.sort-asc::after { content:" ▲"; }
#runs-table th.sort-desc::after { content:" ▼"; }
.filter-input { width:100%; padding:0.5rem; margin-top:0.5rem; border:1px solid var(--border); border-radius:4px; }

/* ---------- Detail Panel ---------- */
.detail-panel { background:var(--card-bg); border:1px solid var(--border); border-radius:8px; padding:1rem; margin-top:1rem; height:fit-content; overflow-y:auto; }
.detail-panel h3 { margin-bottom:0.5rem; }
.detail-panel .field { margin-bottom:0.5rem; }
.detail-panel .field label { display:block; font-weight:bold; margin-bottom:0.2rem; }
.detail-panel .field span { font-size:0.9rem; }

/* ---------- Anomaly / Alerts ---------- */
.alert-rail { background:var(--card-bg); border-left:4px solid var(--danger); padding:0.5rem 1rem; margin-top:1rem; }
.alert-rail h4 { margin:0 0 0.5rem; font-size:1.1rem; }
.alert-rail .msg { margin:0; }

/* ---------- Loading / Empty / Error ---------- */
.overlay { position:absolute; inset:0; background:rgba(0,0,0,0.5); color:#fff; display:flex; align-items:center; justify-content:center; font-size:1.5rem; }
.spinner { border:4px solid #f3f3f3; border-top:4px solid var(--primary); border-radius:50%; width:40px; height:40px; animation:spin 1s linear infinite; margin:auto; }
@keyframes spin { to { transform:rotate(360deg); } }
.empty-msg, .error-msg { padding:1rem; text-align:center; color:var(--danger); }

/* ---------- Badge & Dark Mode Label ---------- */
.badge { display:inline-block; min-width:40px; text-align:center; }
.dark-mode-label { margin-left:1rem; font-size:0.9rem; }

/* ---------- Misc ---------- */
.mt-1 { margin-top:1rem; }
.mb-1 { margin-bottom:1rem; }
</style>
</head>
<body>
<div class="container">
  <!-- Header -->
  <div class="header">
    <div class="logo">FE Agent Dashboard</div>
    <div class="dark-mode-label"><button id="dark-toggle" class="toggle-dark">Dark mode (toggle)</button></div>
  </div>

  <!-- KPI Overview -->
  <div class="kpi-grid mt-1">
    <div class="kpi-card">
      <div class="title">Total Runs <span class="badge">Mock</span></div>
      <div class="value" id="total-runs">0</div>
    </div>
    <div class="kpi-card">
      <div class="title">Success Rate (mock data) <span class="badge">Mock</span></div>
      <div class="value" id="success-rate">0%</div>
    </div>
    <div class="kpi-card">
      <div class="title">Avg Duration (mock data) <span class="badge">Mock</span></div>
      <div class="value" id="avg-duration">0 s</div>
    </div>
    <div class="kpi-card">
      <div class="title">Anomaly Count (mock data) <span class="badge">Mock</span></div>
      <div class="value" id="anomaly-count">0</div>
    </div>
  </div>

  <!-- Trend Charts -->
  <div class="chart mt-1">
    <h4>Quality Trend</h4>
    <canvas id="quality-chart"></canvas>
  </div>
  <div class="chart mt-1">
    <h4>Agent Run Trend</h4>
    <canvas id="run-duration-chart"></canvas>
  </div>

  <!-- Runs Table & Filter -->
  <div class="mt-1">
    <input type="text" id="filter-input" class="filter-input" placeholder="Filter runs...">
  </div>
  <div class="table-wrap">
    <table id="runs-table">
      <thead>
        <tr>
          <th data-sort="id">ID</th>
          <th data-sort="name">Agent Name</th>
          <th data-sort="status">Status</th>
          <th data-sort="duration">Duration (s)</th>
          <th data-sort="timestamp">Timestamp</th>
        </tr>
      </thead>
      <tbody id="runs-body"><!-- populated by JS --></tbody>
    </table>
  </div>

  <!-- Detail Panel (right side) -->
  <div id="detail-panel" class="detail-panel">
    <h3>Run Details</h3>
    <div class="field"><label>ID:</label><span id="detail-id"></span></div>
    <div class="field"><label>Name:</label><span id="detail-name"></span></div>
    <div class="field"><label>Status:</label><span id="detail-status"></span></div>
    <div class="field"><label>Duration (s):</label><span id="detail-duration"></span></div>
    <div class="field"><label>Timestamp:</label><span id="detail-timestamp"></span></div>
    <div class="field"><label>Anomaly:</label><span id="detail-anomaly"></span></div>
  </div>

  <!-- Anomaly / Alerts Rail -->
  <div class="alert-rail mt-1">
    <h4>Priority Alerts</h4>
    <div class="msg" id="anomaly-msg">Anomaly detected: high failure rate in recent runs.</div>
  </div>

  <!-- Timeline / Activity View -->
  <div class="mt-1">
    <h4>Recent Activity</h4>
    <div id="activity-list" class="mt-1"></div>
  </div>
</div>

<!-- Loading Overlay -->
<div id="loading-overlay" class="overlay"><div class="spinner"></div></div>

<!-- Dark Mode Toggle Script -->
<script>
/* ---------- Dark Mode ---------- */
document.getElementById('dark-toggle').addEventListener('click', () => {
  document.body.classList.toggle('dark');
});

/* ---------- Mock Data ---------- */
const runs = [
  {id:1, name:'Agent Alpha', status:'success', duration:12.4, timestamp:'2025-10-30T08:15:00Z', anomaly:false},
  {id:2, name:'Agent Beta', status:'failed', duration:5.0, timestamp:'2025-10-30T08:20:00Z', anomaly:true},
  {id:3, name:'Agent Gamma', status:'partial', duration:8.2, timestamp:'2025-10-30T08:25:00Z', anomaly:false},
  {id:4, name:'Agent Delta', status:'success', duration:15.6, timestamp:'2025-10-30T08:30:00Z', anomaly:false},
  {id:5, name:'Agent Epsilon', status:'failed', duration:9.8, timestamp:'2025-10-30T08:35:00Z', anomaly:true},
  {id:6, name:'Agent Zeta', status:'success', duration:11.0, timestamp:'2025-10-30T08:40:00Z', anomaly:false},
  {id:7, name:'Agent Eta', status:'partial', duration:13.5, timestamp:'2025-10-30T08:45:00Z', anomaly:false},
  {id:8, name:'Agent Theta', status:'failed', duration:7.3, timestamp:'2025-10-30T08:50:00Z', anomaly:true},
  {id:9, name:'Agent Iota', status:'success', duration:14.2, timestamp:'2025-10-30T08:55:00Z', anomaly:false},
  {id:10, name:'Agent Kappa', status:'failed', duration:6.1, timestamp:'2025-10-30T09:00:00Z', anomaly:true},
  // Stale data (older than 12h)
  {id:11, name:'Agent Lambda', status:'success', duration:10.0, timestamp:'2025-10-28T10:00:00Z', anomaly:false},
  {id:12, name:'Agent Mu', status:'failed', duration:12.0, timestamp:'2025-10-28T10:05:00Z', anomaly:true},
  // Partial / Selected examples
  {id:13, name:'Agent Nu', status:'partial', duration:9.0, timestamp:'2025-10-30T09:10:00Z', anomaly:false},
  {id:14, name:'Agent Xi', status:'success', duration:16.5, timestamp:'2025-10-30T09:15:00Z', anomaly:false},
  // Add a few more to reach ~20 rows
  {id:15, name:'Agent Omicron', status:'failed', duration:8.0, timestamp:'2025-10-30T09:20:00Z', anomaly:true},
  {id:16, name:'Agent Pi', status:'success', duration:13.0, timestamp:'2025-10-30T09:25:00Z', anomaly:false},
  {id:17, name:'Agent Rho', status:'partial', duration:11.5, timestamp:'2025-10-30T09:30:00Z', anomaly:false},
  {id:18, name:'Agent Sigma', status:'failed', duration:5.5, timestamp:'2025-10-30T09:35:00Z', anomaly:true},
  {id:19, name:'Agent Tau', status:'success', duration:14.8, timestamp:'2025-10-30T09:40:00Z', anomaly:false},
  {id:20, name:'Agent Upsilon', status:'partial', duration:7.8, timestamp:'2025-10-30T09:45:00Z', anomaly:false}
];

/* ---------- Helper Functions ---------- */
function formatDate(ts) {
  const d = new Date(ts);
  return d.toLocaleString();
}
function calculateKPI(data) {
  const total = data.length;
  const success = data.filter(r=>r.status==='success').length;
  const avgDur = data.reduce((sum,r)=>sum+r.duration,0)/total;
  const anomalyCnt = data.filter(r=>r.anomaly).length;
  return {total, success, avgDur, anomalyCnt};
}
function renderKPI(data) {
  const {total, success, avgDur, anomalyCnt} = calculateKPI(data);
  document.getElementById('total-runs').textContent = total;
  document.getElementById('success-rate').textContent = `${(success/total*100).toFixed(1)}%`;
  document.getElementById('avg-duration').textContent = avgDur.toFixed(1) + ' s';
  document.getElementById('anomaly-count').textContent = anomalyCnt;
}
function sortTable(col, dir) {
  const tbody = document.getElementById('runs-body');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const index = runs[0] ? runs[0].hasOwnProperty(col) ? runs[0][col] : 0 : 0;
  rows.sort((a,b)=>{
    const aVal = a.dataset[col]||a.getAttribute('data-'+col)||0;
    const bVal = b.dataset[col]||b.getAttribute('data-'+col)||0;
    if (aVal < bVal) return dir==='asc'?-1:1;
    if (aVal > bVal) return dir==='asc'?1:-1;
    return 0;
  });
  // update dataset attributes for next sort
  rows.forEach((tr,i)=>tr.dataset.sortCol = col, tr.dataset.sortDir = dir);
  tbody.innerHTML = '';
  rows.forEach(r=>tbody.appendChild(r));
}
function attachSorting() {
  const ths = document.querySelectorAll('#runs-table th');
  ths.forEach(th=>{
    th.addEventListener('click',()=>{
      const col = th.getAttribute('data-sort');
      const current = th.classList.contains('sort-asc')? 'desc' :
                     th.classList.contains('sort-desc')? 'asc' : 'asc';
      sortTable(col, current);
    });
  });
}
function attachFilter() {
  const input = document.getElementById('filter-input');
  input.addEventListener('input',()=>renderTable());
}
function renderTable(filter='') {
  const tbody = document.getElementById('runs-body');
  tbody.innerHTML = '';
  const filtered = runs.filter(r=>{
    if (!filter) return true;
    return r.name.toLowerCase().includes(filter.toLowerCase()) ||
           r.id.toString().includes(filter);
  });
  // attach data attributes for sorting
  filtered.forEach((run,i)=>{
    const tr = document.createElement('tr');
    tr.dataset.id = run.id;
    tr.dataset.sortCol = 'id';
    tr.dataset.sortDir = 'asc';
    tr.innerHTML = `
      <td>${run.id}</td>
      <td>${run.name}</td>
      <td>${run.status}</td>
      <td>${run.duration.toFixed(1)}</td>
      <td>${formatDate(run.timestamp)}</td>
    `;
    tbody.appendChild(tr);
  });
  attachSorting();
  renderKPI(filtered);
}
function renderDetail(run) {
  document.getElementById('detail-id').textContent = run.id;
  document.getElementById('detail-name').textContent = run.name;
  document.getElementById('detail-status').textContent = run.status;
  document.getElementById('detail-duration').textContent = run.duration.toFixed(1);
  document.getElementById('detail-timestamp').textContent = formatDate(run.timestamp);
  document.getElementById('detail-anomaly').textContent = run.anomaly ? 'Yes' : 'No';
}

/* ---------- State Management ---------- */
let currentState = 'loading';
function setState(state){
  currentState = state;
  document.getElementById('loading-overlay').style.display = state==='loading' ? 'flex' : 'none';
  // other states can be simulated via UI buttons later
}
function init() {
  // simulate loading for 1 second
  setState('loading');
  setTimeout(()=>setState('normal'),1000);
  renderTable(); // normal view
  attachFilter();
}

/* ---------- UI Buttons for Other States (optional) ---------- */
const stateBtns = document.createElement('div');
stateBtns.className = 'mt-1';
stateBtns.innerHTML = `
  <button id="btn-empty" class="mt-1">Show Empty</button>
  <button id="btn-error" class="mt-1">Show Error</button>
  <button id="btn-partial" class="mt-1">Show Partial</button>
  <button id="btn-selected" class="mt-1">Select Run</button>
  <button id="btn-stale" class="mt-1">Show Stale</button>
`;
document.body.appendChild(stateBtns);
document.getElementById('btn-empty').onclick = ()=>{ 
  // filter to nothing
  renderTable('nonexistent');
  document.getElementById('anomaly-msg').textContent = 'No runs found.';
};
document.getElementById('btn-error').onclick = ()=>{ 
  document.getElementById('anomaly-msg').textContent = 'Error loading data: server unreachable.';
};
document.getElementById('btn-partial').onclick = ()=>{ 
  // mark a run as partial (already partial) – just highlight
  const partialRun = runs.find(r=>r.id===13);
  alert('Partial run selected: '+partialRun.name);
};
document.getElementById('btn-selected').onclick = ()=>{ 
  const selRun = runs.find(r=>r.id===1);
  renderDetail(selRun);
  document.getElementById('detail-panel').classList.add('active');
};
document.getElementById('btn-stale').onclick = ()=>{ 
  // mark some runs as stale (older than 12h) – just a visual cue
  const staleRun = runs.find(r=>r.id===11);
  alert('Stale data notice for run '+staleRun.name+' (timestamp older than 12h).');
};

/* ---------- Activity Timeline ---------- */
function renderActivity() {
  const list = document.getElementById('activity-list');
  list.innerHTML = '';
  runs.slice(0,5).forEach(r=>{
    const div = document.createElement('div');
    div.className = 'mt-1';
    div.innerHTML = `<strong>#${r.id}</strong> ${r.name} – ${r.status} – ${r.duration.toFixed(1)}s – ${formatDate(r.timestamp)}`;
    list.appendChild(div);
  });
}
renderActivity();

/* ---------- Init ---------- */
init();
</script>
</body>
</html>
