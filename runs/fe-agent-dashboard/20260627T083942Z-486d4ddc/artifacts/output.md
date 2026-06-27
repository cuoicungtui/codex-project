<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Agent Operations Dashboard</title>
<style>
:root {
  --bg:#f5f5f5;
  --text:#333;
  --primary:#0066ff;
  --success:#28a745;
  --warning:#ffc107;
  --danger:#dc3545;
  --stale:#6c757d;
  --selected:#ff9800;
}
body {
  margin:0;
  font-family:Arial, sans-serif;
  background:var(--bg);
  color:var(--text);
  transition:background 0.3s, color 0.3s;
}
body.dark {
  --bg:#212121;
  --text:#e0e0e0;
  --primary:#90caf9;
  --success:#81c784;
  --warning:#ffb74d;
  --danger:#e57373;
  --stale:#9e9e9e;
  --selected:#ff8f00;
}
header {
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:10px 15px;
  background:var(--bg);
  border-bottom:1px solid #ddd;
}
header h1 {
  margin:0;
  font-size:1.2rem;
  color:var(--primary);
}
.freshness {
  font-size:0.9rem;
  margin-left:10px;
}
#darkModeToggle {
  background:none;
  border:1px solid var(--primary);
  color:var(--primary);
  padding:5px 10px;
  border-radius:4px;
  cursor:pointer;
}
#darkModeToggle[aria-pressed="true"] {
  background:var(--primary);
  color:#fff;
}
.filter-controls {
  display:flex;
  gap:10px;
  align-items:center;
  margin-left:15px;
}
.filter-controls select,
.filter-controls input {
  padding:5px 8px;
  border:1px solid #ccc;
  border-radius:4px;
}
.kpi-grid {
  display:grid;
  grid-template-columns:repeat(auto-fit, minmax(200px,1fr));
  gap:15px;
  margin:20px 15px;
}
.kpi-card {
  background:#fff;
  padding:15px;
  border-radius:8px;
  box-shadow:0 2px 4px rgba(0,0,0,0.1);
  text-align:center;
}
.kpi-card h3 {
  margin:0 0 8px;
  font-size:0.9rem;
  color:#555;
}
.kpi-card .value {
  font-size:1.4rem;
  font-weight:bold;
}
.kpi-card .icon {
  font-size:1.2rem;
  margin-bottom:8px;
}
.anomaly
