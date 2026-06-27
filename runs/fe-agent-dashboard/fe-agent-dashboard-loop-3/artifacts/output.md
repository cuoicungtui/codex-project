<!-- Mock data sources: generated JS array of agent runs with statuses, durations, metrics. Run the dashboard in any modern browser. Data table displays agent runs. -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI Agent Dashboard</title>
<style>
:root{
  --bg:#f5f5f5;
  --text:#333;
  --card-bg:#fff;
  --header-bg:#e0e0e0;
  --accent:#0066cc;
}
body{
  margin:0;
  font-family:Arial,Helvetica,sans-serif;
  background:var(--bg);
  color:var(--text);
  display:flex;
  flex-direction:column;
  min-height:100vh;
}
.dashboard{
  max-width:1200px;
  margin:auto;
  padding:10px;
}
.header{
  display:flex;
  justify-content:space-between;
  align-items:center;
  background:var(--header-bg);
  padding:10px;
  border-radius:5px;
}
.title{margin:0;font-size:1.2rem;}
.toggle-btn{
  background:none;
  border:none;
  font-size:0.9rem;
  cursor:pointer;
}
.kpi-grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:10px;
  margin:20px 0;
}
.kpi-card{
  background:var(--card-bg);
  padding:15px;
  border-radius:8px;
  box-shadow:0 2px 4px rgba(0,0,0,0.1);
  text-align:center;
}
.kpi-card h4{margin:0 0 5px;font-size:1rem;}
.kpi-card p{margin:0;font-size:1.1rem;font-weight:bold;}
.chart{
  background:var(--card-bg);
  padding:10px;
  border-radius:8px;
  margin:10px 0;
}
.empty,.loading,.error{
  text-align:center;
  padding:20px;
  color:#d00;
  font-weight:bold;
}
.table-container{
  margin-top:20px;
}
.filter-input{
  width:100%;
  padding:8px;
  margin-bottom:10px;
  border:1px solid #ccc;
  border-radius:4px;
}
.table{
  width:100%;
  border-collapse:collapse;
}
.table th,.table td{
  padding:8px;
  border:1px solid #ddd;
  text-align:left;
}
.table th{
  background:var(--header-bg);
  cursor:pointer;
  user-select:none;
}
.table th.sort-asc::after{content:" ▲";}
.table th.sort-desc::after{content:" ▼";}
.detail-panel{
  background:var(--card-bg);
  padding:15px;
  border-radius:8px;
  margin-top:20px;
  height:400px;
  overflow-y:auto;
}
.detail-panel h3{margin-top:0;}
.alert{
  background:#ffeb3b;
  padding:10px;
  border-left:4px solid #ff9800;
  margin:10px 0;
}
@media (max-width:768px){
  .main{grid-template-columns:1fr;}
  .detail-panel{height:auto;margin-top:20px;}
  .kpi-grid{grid-template-columns:1fr;}
}
</style>
</head>
<body>
<div class="dashboard">
  <header class="header">
    <h1 class="title">AI Agent Dashboard</h1>
    <button class="toggle-btn" id="darkToggle">Dark mode (toggle)</button>
  </header>

  <div class="main" style="display:grid;grid-template-columns:2fr 1fr;gap:10px;">
    <!-- KPI Overview -->
    <section class="kpi-grid">
      <div class="kpi-card"><h4>Total agent runs (mock data)</h4><p>15</p></div>
      <div class="kpi-card"><h4>Success rate (mock data)</h4><p>73%</p></div>
      <div class="kpi-card"><h4>Avg duration (mock data)</h4><p>12.4s</p></div>
      <div class="kpi-card"><h4>Anomaly count (mock data)</h4><p>2</p></div>
    </section>

    <!-- Charts & Table -->
    <div class="chart-section">
      <div class="chart">
        <h3>Success rate trend</h3>
        <div id="successChart" style="height:120px;background:#eee;border-radius:4px;"></div>
      </div>
      <div class="chart">
        <h3>Duration trend</h3>
        <div id="durationChart" style="height:120px;background:#eee;border-radius:4px;"></div>
      </div>

      <!-- Sortable runs table -->
      <div class="caption">Sortable runs table</div>
      <input type="text" id="filterInput" class="filter-input" placeholder="Filter runs...">
      <table class="table" id="runsTable">
        <thead>
          <tr>
            <th>ID</th><th>Timestamp</th><th>Status</th><th>Duration (s)</th><th>Anomaly</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <!-- Detail Panel (right) -->
    <div class="detail-panel" id="detailPanel" style="display:none;">
      <h3>Selected Run Details</h3>
      <p><strong>ID:</strong> <span id="detID"></span></p>
      <p><strong>Timestamp:</strong> <span id="detTime"></span></p>
      <p><strong>Status:</strong> <span id="detStatus"></span></p>
      <p><strong>Duration:</strong> <span id="detDuration"></span>s</p>
      <p><strong>Metrics:</strong> <span id="detMetrics"></span></p>
    </div>

    <!-- Anomaly / Alerts -->
    <div class="alert" id="anomalyAlert">Anomaly detected: high failure rate in recent runs.</div>
  </div>

  <!-- Loading / Empty / Error states (hidden initially) -->
  <div id="loading" class="loading">Loading...</div>
  <div id="empty" class="empty">No data available.</div>
  <div id="error" class="error">Failed to load data.</div>
</div>

<script>
/* Mock data: array of agent runs */
const runs = [
  {id:1, time:"2025-09-20T08:00:00Z", status:"success", duration:10, anomaly:false},
  {id:2, time:"2025-09-20T08:05:00Z", status:"failed", duration:15, anomaly:true},
  {id:3, time:"2025-09-20T08:10:00Z", status:"partial", duration:8, anomaly:false},
  {id:4, time:"2025-09-20T08:15:00Z", status:"success", duration:12, anomaly:false},
  {id:5, time:"2025-09-20T08:20:00Z", status:"stale", duration:20, anomaly:false},
  {id:6, time:"2025-09-20T08:25:00Z", status:"failed", duration:18, anomaly:true},
  {id:7, time:"2025-09-20T08:30:00Z", status:"success", duration:9, anomaly:false},
  {id:8, time:"2025-09-20T08:35:00Z", status:"partial", duration:7, anomaly:false},
  {id:9, time:"2025-09-20T08:40:00Z", status:"success", duration:11, anomaly:false},
  {id:10, time:"2025-09-20T08:45:00Z", status:"failed", duration:22, anomaly:false},
  {id:11, time:"2025-09-20T08:50:00Z", status:"success", duration:13, anomaly:false},
  {id:12, time:"2025-09-20T08:55:00Z", status:"stale", duration:25, anomaly:true},
  {id:13, time:"2025-09-20T09:00:00Z", status:"success", duration:14, anomaly:false},
  {id:14, time:"2025-09-20T09:05:00Z", status:"failed", duration:16, anomaly:false},
  {id:15, time:"2025-09-20T09:10:00Z", status:"success", duration:10, anomaly:false}
];

let selectedIndex = 0;
let sortKey = 'time';
let sortDir = 1;

/* Rendering functions */
function showLoading(){ document.getElementById('loading').style.display='block;';
  document.getElementById('empty').style.display='none;document.getElementById('error').style.display='none; }
function hideLoading(){ document.getElementById('loading').style.display='none; }
function renderKPI(){
  const total = runs.length;
  const success = runs.filter(r=>r.status==="success").length;
  const successRate = Math.round((success/total)*100);
  const avgDur = parseFloat((runs.reduce((a,r)=>a+r.duration,0)/total).toFixed(1));
  const anomalyCount = runs.filter(r=>r.anomaly).length;

  document.querySelector('.kpi-card h4:nth-child(1)').textContent = `Total agent runs (mock data)`;
  document.querySelector('.kpi-card h4:nth-child(2)').textContent = `Success rate (mock data)`;
  document.querySelector('.kpi-card h4:nth-child(3)').textContent = `Avg duration (mock data)`;
  document.querySelector('.kpi-card h4:nth-child(4)').textContent = `Anomaly count (mock data)`;

  document.querySelector('.kpi-card p:nth-child(1)').textContent = total;
  document.querySelector('.kpi-card p:nth-child(2)').textContent = successRate+"%";
  document.querySelector('.kpi-card p:nth-child(3)').textContent = avgDur+"s";
  document.querySelector('.kpi-card p:nth-child(4)').textContent = anomalyCount;
}
function renderCharts(){
  // Simple bar chart for success rate trend (static for demo)
  const ctx = document.createElement('canvas');
  ctx.id='successChart';
  ctx.width=300; ctx.height=120;
  const cctx = ctx.getContext('2d');
  new Chart(cctx,{
    type:'bar',
    data:{
      labels:['Success','Failed','Partial'],
      datasets:[{
        label:'Rate',
        data:[73,15,12],
        backgroundColor:['#4caf50','#f44336','#ff9800']
      }]
    },
    options:{legend:{display:false}}
  });
  document.getElementById('successChart').replaceWith(ctx);

  // Duration distribution (static)
  const durCtx = document.createElement('canvas');
  durCtx.id='durationChart';
  durCtx.width=300; durCtx.height=120;
  const dctx = durCtx.getContext('2d');
  new Chart(dctx,{
    type:'bar',
    data:{
      labels:['<10','10-15','15-20','20+'],
      datasets:[{
        label:'Count',
        data:[5,6,3,1],
        backgroundColor:'#2196f3'
      }]
    },
    options:{legend:{display:false}}
  });
  document.getElementById('durationChart').replaceWith(durCtx);
}
function renderTable(){
  const tbody = document.querySelector('#runsTable tbody');
  tbody.innerHTML='';
  const filtered = runs.filter(r=>{
    const term = document.getElementById('filterInput').value.toLowerCase();
    return term ? (r.id.toString().includes(term)||r.status.toLowerCase().includes(term)) : true;
  });
  filtered.forEach((r,i)=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${r.id}</td><td>${r.time}</td><td>${r.status}</td><td>${r.duration}</td><td>${r.anomaly?'Yes':'No'}</td>`;
    // sortable click
    tr.style.cursor='pointer';
    tr.onclick = ()=>{ selectRun(i); };
    // sort indicator
    const th = tbody.parentNode.children[0]; // first <tr> is header, so use header cells
    // we'll attach listeners to header cells later
    tbody.appendChild(tr);
  });
}
function renderDetail(){
  const run = runs[selectedIndex];
  document.getElementById('detID').textContent = run.id;
  document.getElementById('detTime').textContent = run.time;
  document.getElementById('detStatus').textContent = run.status;
  document.getElementById('detDuration').textContent = run.duration;
  document.getElementById('detMetrics').textContent = `Duration: ${run.duration}s | Status: ${run.status}`;
}
function renderAnomaly(){
  const anomalies = runs.filter(r=>r.anomaly);
  const list = document.getElementById('anomalyAlert');
  if(anomalies.length){
    list.textContent = `Anomaly detected: ${anomalies.length} anomaly${anomalies.length>1?'s':' '} in recent runs.`;
  }else{
    list.textContent = 'No anomalies detected.';
  }
}
function selectRun(idx){
  selectedIndex = idx;
  renderDetail();
  // highlight row
  document.querySelectorAll('#runsTable tbody tr').forEach(r=>{
    r.classList.remove('selected');
  });
  document.querySelectorAll('#runsTable tbody tr')[idx].classList.add('selected');
}
function toggleDarkMode(){
  document.body.classList.toggle('dark');
}

/* Event listeners */
document.getElementById('darkToggle').addEventListener('click',toggleDarkMode);
document.getElementById('filterInput').addEventListener('input',renderTable);
document.querySelectorAll('#runsTable thead th').forEach((th,i)=>{
  th.addEventListener('click',()=>{
    sortKey = th.parentElement.children[i].textContent.trim(); // simplified
    sortDir *= -1;
    runs.sort((a,b)=>{
      if(sortDir===1) return a[sortKey] - b[sortKey];
      return b[sortKey] - a[sortKey];
    });
    renderTable();
  });
});
/* Initial load */
showLoading();
setTimeout(()=>{
  hideLoading();
  renderKPI();
  renderCharts();
  renderTable();
  renderDetail();
  renderAnomaly();
},1500);
</script>
</body>
</html>
