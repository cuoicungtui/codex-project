<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>AI Agent Dashboard</title>
<style>
:root {
  --bg: #f5f5f5;
  --text: #333;
  --card-bg: #fff;
  --card-border: #e0e0e0;
  --primary: #0066ff;
  --success: #4caf50;
  --error: #f44336;
  --warning: #ff9800;
}
body.dark {
  --bg: #121212;
  --text: #e0e0e0;
  --card-bg: #1e1e1e;
  --card-border: #333;
  --primary: #66b2ff;
  --success: #81c784;
  --error: #e57373;
  --warning: #ffb74d;
}
* { box-sizing: border-box; margin:0; padding:0; }
body { font-family: Arial, sans-serif; background: var(--bg); color: var(--text); padding: 1rem; }
.container { display: flex; gap: 1rem; }
.overview { flex: 3; }
.detail { flex: 1; height: 100vh; overflow-y: auto; background: var(--card-bg); border-left: 1px solid var(--card-border); padding: 1rem; display: none; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1rem; }
.card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 1rem; text-align: center; }
.card h3 { margin-bottom: 0.5rem; font-size: 1rem; }
.card .value { font-size: 1.5rem; font-weight: bold; }
.badge { display: inline-block; background: var(--primary); color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; }
.alert-list { margin-top: 1rem; }
.alert-item { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 6px; padding: 0.5rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; }
.alert-item.success { border-color: var(--success); }
.alert-item.error { border-color: var(--error); }
.alert-item.warning { border-color: var(--warning); }
.table-wrap { overflow-x: auto; margin-top: 1rem; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.5rem; border: 1px solid var(--card-border); text-align: left; }
th { background: var(--primary); color: #fff; cursor: pointer; user-select: none; }
tr:hover { background: rgba(0,0,0,0.05); }
.tr-selected { background: var(--primary) !important; color: #fff; }
.tr-selected td { color: #fff; }
.detail-panel { margin-top: 1rem; }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.detail-header h2 { margin:0; }
.detail-body { display: flex; gap: 1rem; }
.detail-body .timeline { flex: 2; }
.detail-body .activity { flex: 1; }
.timeline { display: flex; flex-direction: column; }
.timeline-item { position: relative; padding-left: 1.5rem; margin-bottom: 0.5rem; }
.timeline-item::before { content:""; position:absolute; left:0; top:0.5rem; width:0.5rem; height:0.5rem; background: var(--primary); border-radius:50%; }
.activity ul { list-style: none; padding-left:0; }
.activity li { margin-bottom:0.3rem; }
@media (max-width: 768px) {
  .container { flex-direction: column; }
  .detail { display: block; height: auto; border-left: none; border-top: 1px solid var(--card-border); }
}
</style>
</head>
<body>
<div class="container">
  <div class="overview">
    <h1 style="margin-bottom:1rem;">AI Agent Dashboard</h1>
    <div class="card-grid" id="kpi-cards">
      <!-- KPI cards will be generated -->
    </div>
    <div id="loading-spinner" style="text-align:center; margin:1rem;">
      <span>Loading...</span>
    </div>
    <div id="empty-state" style="text-align:center; display:none;">
      <p>No data available.</p>
    </div>
    <div id="error-state" style="text-align:center; display:none; color:red;">
      <p>Failed to load data.</p>
    </div>
    <div class="chart-surface" style="margin:1rem 0;">
      <h2>Quality Trend</h2>
      <canvas id="quality-chart" width="400" height="200"></canvas>
    </div>
    <div class="chart-surface" style="margin:1rem 0;">
      <h2>Latency Trend</h2>
      <canvas id="latency-chart" width="400" height="200"></canvas>
    </div>
    <div class="alert-list" id="alerts">
      <h2>Anomalies</h2>
    </div>
    <div class="table-wrap" style="margin-top:1rem;">
      <h2>Runs</h2>
      <table id="runs-table">
        <thead>
          <tr>
            <th data-key="id">ID</th>
            <th data-key="status">Status</th>
            <th data-key="start">Start Time</th>
            <th data-key="end">End Time</th>
            <th data-key="latency">Latency (s)</th>
            <th data-key="agent">Agent</th>
          </tr>
        </thead>
        <tbody>
          <!-- rows will be generated -->
        </tbody>
      </table>
    </div>
  </div>
  <div class="detail" id="detail-panel">
    <div class="detail-header">
      <h2 id="detail-title">Run Details</h2>
      <button id="close-detail" style="background:none; border:none; font-size:1rem; cursor:pointer;">&#215;</button>
    </div>
    <div class="detail-body">
      <div class="timeline" id="timeline">
        <!-- timeline items -->
      </div>
      <div class="activity" id="activity">
        <h3>Activity</h3>
        <ul></ul>
      </div>
    </div>
  </div>
</div>

<script>
/* Mock data */
const runs = [
  {id:1, status:'success', start:'2025-09-20T08:00:00Z', end:'2025-09-20T08:05:12Z', latency:12, agent:'Agent-A'},
  {id:2, status:'failed', start:'2025-09-20T08:06:00Z', end:'2025-09-20T08:07:00Z', latency:180, agent:'Agent-B'},
  {id:3, status:'partial', start:'2025-09-20T08:08:30Z', end:'2025-09-20T08:09:45Z', latency:45, agent:'Agent-C'},
  {id:4, status:'stale', start:'2025-09-18T12:00:00Z', end:'', latency:0, agent:'Agent-D'},
  {id:5, status:'success', start:'2025-09-20T09:00:00Z', end:'2025-09-20T09:02:30Z', latency:150, agent:'Agent-E'},
  {id:6, status:'failed', start:'2025-09-20T09:10:00Z', end:'2025-09-20T09:12:00Z', latency:200, agent:'Agent-F'},
  {id:7, status:'success', start:'2025-09-20T09:20:00Z', end:'2025-09-20T09:25:00Z', latency:10, agent:'Agent-G'},
  {id:8, status:'partial', start:'2025-09-20T09:30:00Z', end:'2025-09-20T09:32:00Z', latency:120, agent:'Agent-H'},
  {id:9, status:'stale', start:'2025-09-19T15:00:00Z', end:'', latency:0, agent:'Agent-I'},
  {id:10, status:'success', start:'2025-09-20T10:00:00Z', end:'2025-09-20T10:01:00Z', latency:5, agent:'Agent-J'}
];
const alerts = [
  {id:1, severity:'error', message:'Agent-B timed out after 3 minutes'},
  {id:2, severity:'warning', message:'High latency on Agent-F (200s)'},
  {id:3, severity:'error', message:'Agent-D has not reported in 24h'},
  {id:4, severity:'warning', message:'Partial run on Agent-H may need review'}
];

/* State */
let selectedRun = null;
let sortState = {key:null, dir:'asc'};

/* Utility */
function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleString('vi-VN', {year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit', second:'2-digit'});
}

/* Render KPI cards */
function renderKPIs() {
  const cards = document.getElementById('kpi-cards');
  cards.innerHTML = '';
  const total = runs.length;
  const success = runs.filter(r=>r.status==='success').length;
  const failed = runs.filter(r=>r.status==='failed').length;
  const partial = runs.filter(r=>r.status==='partial').length;
  const stale = runs.filter(r=>r.status==='stale').length;
  const avgLatency = runs.reduce((sum,r)=> sum + (r.latency||0),0) / total;

  const kpiData = [
    {title:'Total Runs', value: total, bg: 'var(--primary)', textColor: '#fff'},
    {title:'Success Rate', value: success+'/'+total, bg: 'var(--success)', textColor: '#000'},
    {title:'Failed', value: failed, bg: 'var(--error)', textColor: '#fff'},
    {title:'Partial', value: partial, bg: 'var(--warning)', textColor: '#000'},
    {title:'Stale', value: stale, bg: 'var(--primary)', textColor: '#fff'},
    {title:'Avg Latency', value: avgLatency.toFixed(1), bg: 'var(--primary)', textColor: '#fff'}
  ];
  kpiData.forEach(d=>{
    const card = document.createElement('div');
    card.className='card';
    card.innerHTML = `<h3>${d.title}</h3><div style="background:${d.bg};color:${d.textColor};padding:0.5rem;border-radius:4px;">${d.value}</div>`;
    const badge = document.createElement('span');
    badge.className='badge';
    badge.textContent='table';
    card.appendChild(badge);
    cards.appendChild(card);
  });
}

/* Simple canvas charts */
function drawQualityChart() {
  const ctx = document.getElementById('quality-chart').getContext('2d');
  ctx.clearRect(0,0,ctx.canvas.width,ctx.canvas.height);
  const data = runs.map(r=> {
    if(r.status==='success') return 1;
    if(r.status==='failed') return 0;
    if(r.status==='partial') return 0.5;
    return 0;
  });
  const barWidth = ctx.canvas.width / data.length;
  data.forEach((val,i)=>{
    const x = i*barWidth;
    const y = (1-val) * ctx.canvas.height;
    const h = val * ctx.canvas.height;
    ctx.fillStyle = (val===1) ? 'rgba(76,175,80,0.8)' :
                    (val===0) ? 'rgba(244,67,54,0.8)' :
                    (val===0.5) ? 'rgba(255,98,0,0.8)' : 'rgba(173,173,173,0.8)';
    ctx.fillRect(x+1, y, barWidth-2, h);
  });
}
function drawLatencyChart() {
  const ctx = document.getElementById('latency-chart').getContext('2d');
  ctx.clearRect(0,0,ctx.canvas.width,ctx.canvas.height);
  const data = runs.map(r=> r.latency||0);
  const min = 0, max = Math.max(...data);
  const height = ctx.canvas.height;
  const width = ctx.canvas.width;
  const stepX = width / (data.length-1 || 1);
  ctx.strokeStyle = 'rgba(255,165,0,1)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  data.forEach((val,i)=>{
    const x = i*stepX;
    const y = height - ((val - min) / (max - min)) * height;
    if(i===0) ctx.moveTo(x,y);
    else ctx.lineTo(x,y);
  });
  ctx.stroke();
  ctx.fillStyle = 'rgba(255,165,0,1)';
  data.forEach((val,i)=>{
    const x = i*stepX;
    const y = height - ((val - min) / (max - min)) * height;
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI*2);
    ctx.fill();
  });
}

/* Render alerts */
function renderAlerts() {
  const container = document.getElementById('alerts');
  container.innerHTML = '<h2>Anomalies</h2>';
  alerts.forEach(a=>{
    const div = document.createElement('div');
    div.className='alert-item '+a.severity;
    div.innerHTML = `<span>${a.message}</span><span style="font-weight:bold;">[${a.severity.toUpperCase()}]</span>`;
    container.appendChild(div);
  });
}

/* Render runs table with sorting */
function renderTable() {
  const tbody = document.querySelector('#runs-table tbody');
  tbody.innerHTML = '';
  runs.forEach((run, idx) => {
    const tr = document.createElement('tr');
    tr.dataset.idx = idx;
    tr.innerHTML = `
      <td>${run.id}</td>
      <td>${run.status}</td>
      <td>${formatDate(run.start)}</td>
      <td>${run.end ? formatDate(run.end) : ' — '}</td>
      <td>${run.latency||' — '}</td>
      <td>${run.agent}</td>
    `;
    if(run.status==='stale') tr.style.background = 'rgba(255,200,200,0.3)';
    tr.addEventListener('click', () => {
      document.querySelectorAll('#runs-table tr.tr-selected').forEach(r=>r.classList.remove('tr-selected'));
      tr.classList.add('tr-selected');
      selectedRun = run;
      showDetail(run);
    });
    tbody.appendChild(tr);
  });
}

/* Show detail panel */
function showDetail(run) {
  const panel = document.getElementById('detail-panel');
  document.getElementById('detail-title').textContent = 'Run '+run.id+' – '+run.status;
  const timeline = document.getElementById('timeline');
  timeline.innerHTML = '';
  const steps = [
    {label:'Start', time:run.start},
    {label:run.status, time:run.status},
    {label:'End', time:run.end||' — '}
  ];
  steps.forEach(s=>{
    const item = document.createElement('div');
    item.className='timeline-item';
    item.innerHTML = `<strong>${s.label}</strong>: ${s.time}`;
    timeline.appendChild(item);
  });
  const activityList = document.querySelector('#activity ul');
  activityList.innerHTML = '';
  const activities = [
    `Agent ${run.agent} started run at ${formatDate(run.start)}`,
    `Status changed to ${run.status} after ${run.latency||0} seconds`,
    run.end ? `Run completed at ${formatDate(run.end)}` : ' — '
  ];
  activities.forEach(a=> {
    const li = document.createElement('li');
    li.textContent = a;
    activityList.appendChild(li);
  });
  panel.style.display = 'block';
}

/* Close detail */
document.getElementById('close-detail').addEventListener('click', () => {
  document.getElementById('detail-panel').style.display = 'none';
  document.querySelectorAll('#runs-table tr.tr-selected').forEach(r=>r.classList.remove('tr-selected'));
  selectedRun = null;
});

/* Simulate loading */
function init() {
  setTimeout(() => {
    document.getElementById('loading-spinner').style.display = 'none';
    document.getElementById('empty-state').style.display = 'none';
    document.getElementById('error-state').style.display = 'none';
    renderKPIs();
    drawQualityChart();
    drawLatencyChart();
    renderAlerts();
    renderTable();
  }, 1500);
}

/* Dark mode */
function initDarkMode() {
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.body.classList.add('dark');
  }
}

/* Sorting */
function sortBy(key) {
  const asc = sortState.key===key && sortState.dir==='asc';
  sortState = {key, dir: asc?'desc':'asc'};
  runs.sort((a,b)=>{
    const valA = a[key] ? (typeof a[key]==='string'? a[key].toLowerCase(): a[key]) : '';
    const valB = b[key] ? (typeof b[key]==='string'? b[key].toLowerCase(): b[key]) : '';
    if(valA < valB) return asc?1:-1;
    if(valA > valB) return asc?-1:1;
    return 0;
  });
  renderTable();
}
document.querySelectorAll('#runs-table th').forEach(th => {
  th.addEventListener('click', () => sortBy(th.dataset.key));
});

/* Init */
initDarkMode();
init();
</script>
</body>
</html>
