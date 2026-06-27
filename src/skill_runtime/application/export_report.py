from __future__ import annotations

import html
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from skill_runtime.domain.reports import DashboardIndex, RunReport
from skill_runtime.domain.workspace import WorkspaceContract


def generate_report_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_trace(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _truncate(text: str, limit: int = 240) -> str:
    clean = " ".join(text.split())
    return clean if len(clean) <= limit else clean[: limit - 1] + "…"


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class ReportExporter:
    def __init__(self, workspace_root: Path) -> None:
        self._workspace = WorkspaceContract(workspace_root)

    def export_run_report(self, *, skill_id: str, run_id: str) -> RunReport:
        run_root = self._workspace.runs_dir / skill_id / run_id
        report_id = generate_report_id()
        report_root = self._workspace.reports_dir / skill_id / run_id
        report_root.mkdir(parents=True, exist_ok=True)
        report_json_path = report_root / "report.json"
        report_html_path = report_root / "report.html"

        run_record = _load_json(run_root / "run.json")
        eval_record = _load_json(run_root / "eval.json") if (run_root / "eval.json").exists() else {}
        feedback_record = _load_json(run_root / "feedback.json") if (run_root / "feedback.json").exists() else {}
        trace = _load_trace(run_root / "trace.jsonl")
        output_path = run_root / "artifacts" / "output.md"
        output_html_path = run_root / "artifacts" / "output.html"
        output_text = output_path.read_text(encoding="utf-8") if output_path.exists() else ""

        comparison_text = self._best_effort_improvement_hint(skill_id=skill_id, run_id=run_id, current_eval=eval_record)
        report = {
            "schema_version": 1,
            "report_id": report_id,
            "skill_id": skill_id,
            "run_id": run_id,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "run": run_record,
            "evaluation": eval_record,
            "feedback": feedback_record,
            "metrics": {
                "trace_event_count": len(trace),
                "output_char_count": len(output_text.strip()),
            },
            "highlights": {
                "output_preview": _truncate(output_text, 300),
                "improvement_hint": comparison_text,
            },
            "artifacts": {
                "run_json": str(run_root / "run.json"),
                "trace_jsonl": str(run_root / "trace.jsonl"),
                "eval_json": str(run_root / "eval.json"),
                "feedback_json": str(run_root / "feedback.json"),
                "output_md": str(output_path),
                "output_html": str(output_html_path) if output_html_path.exists() else None,
            },
            "trace": trace,
        }
        report_json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        report_html_path.write_text(self._render_run_html(report), encoding="utf-8")
        return RunReport(
            report_id=report_id,
            skill_id=skill_id,
            run_id=run_id,
            report_root=report_root,
            report_json_path=report_json_path,
            report_html_path=report_html_path,
            created_at=report["generated_at"],
        )

    def build_dashboard_index(self) -> DashboardIndex:
        dashboard_root = self._workspace.reports_dir
        index_json_path = dashboard_root / "index.json"
        index_html_path = dashboard_root / "index.html"
        entries: list[dict[str, object]] = []
        for report_json_path in sorted(dashboard_root.glob("*/*/report.json")):
            report = _load_json(report_json_path)
            entries.append(
                {
                    "skill_id": report.get("skill_id"),
                    "run_id": report.get("run_id"),
                    "report_json": str(report_json_path),
                    "report_html": str(report_json_path.with_name("report.html")),
                    "verdict": report.get("evaluation", {}).get("verdict") if isinstance(report.get("evaluation"), dict) else None,
                    "score": report.get("evaluation", {}).get("score") if isinstance(report.get("evaluation"), dict) else None,
                    "generated_at": report.get("generated_at"),
                    "improvement_hint": report.get("highlights", {}).get("improvement_hint") if isinstance(report.get("highlights"), dict) else None,
                }
            )
        entries.sort(key=lambda item: str(item.get("generated_at") or ""))
        scores = [_safe_float(item.get("score")) for item in entries]
        verdict_counts = Counter(str(item.get("verdict") or "unknown") for item in entries)
        pass_count = verdict_counts.get("pass", 0)
        total_runs = len(entries)
        avg_score = round(sum(scores) / total_runs, 2) if total_runs else 0.0
        pass_rate = round((pass_count / total_runs) * 100, 1) if total_runs else 0.0
        index_record = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "reports": entries,
            "summary": {
                "total_runs": total_runs,
                "pass_count": pass_count,
                "fail_count": verdict_counts.get("fail", 0),
                "pass_rate": pass_rate,
                "avg_score": avg_score,
            },
        }
        index_json_path.write_text(json.dumps(index_record, indent=2, ensure_ascii=False), encoding="utf-8")
        index_html_path.write_text(self._render_dashboard_html(index_record), encoding="utf-8")
        return DashboardIndex(
            dashboard_root=dashboard_root,
            index_json_path=index_json_path,
            index_html_path=index_html_path,
            created_at=index_record["generated_at"],
        )

    def _best_effort_improvement_hint(self, *, skill_id: str, run_id: str, current_eval: dict[str, object]) -> str:
        run_root = self._workspace.runs_dir / skill_id / run_id
        version_id = str(_load_json(run_root / "run.json").get("skill_version_id", ""))
        version_root = self._workspace.skills_dir / skill_id / "versions"
        versions = sorted(p.name for p in version_root.iterdir() if p.is_dir()) if version_root.exists() else []
        if len(versions) < 2:
            verdict = current_eval.get("verdict", "unknown") if isinstance(current_eval, dict) else "unknown"
            return f"Single-run snapshot. Verdict: {verdict}. Add a second run or version to show improvement."
        previous_versions = [v for v in versions if v != version_id]
        if not previous_versions:
            return "No earlier version found to compare against."
        return f"Current version {version_id} can be compared with {previous_versions[-1]} for improvement analysis."

    def _render_run_html(self, report: dict[str, object]) -> str:
        run = report.get("run", {})
        evaluation = report.get("evaluation", {})
        feedback = report.get("feedback", {})
        highlights = report.get("highlights", {})
        trace = report.get("trace", [])

        def esc(value: object) -> str:
            return html.escape("" if value is None else str(value))

        issues_html = ""
        if isinstance(evaluation, dict):
            issues = evaluation.get("issues", [])
            if isinstance(issues, list) and issues:
                issues_html = "".join(
                    f"<li><strong>{esc(issue.get('code'))}</strong>: {esc(issue.get('message'))}</li>"
                    for issue in issues
                    if isinstance(issue, dict)
                )
            else:
                issues_html = "<li>No issues</li>"

        recommendations_html = ""
        if isinstance(feedback, dict):
            recommendations = feedback.get("recommendations", [])
            if isinstance(recommendations, list) and recommendations:
                recommendations_html = "".join(f"<li>{esc(item)}</li>" for item in recommendations)
            else:
                recommendations_html = "<li>No feedback items</li>"

        trace_rows = "".join(
            f"<tr><td>{esc(item.get('timestamp'))}</td><td>{esc(item.get('event'))}</td><td><pre>{esc(json.dumps(item.get('payload', {}), ensure_ascii=False, indent=2))}</pre></td></tr>"
            for item in trace
            if isinstance(item, dict)
        )

        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Skill Runtime Report - {esc(report.get('skill_id'))} / {esc(report.get('run_id'))}</title>
  <style>
    :root {{
      --bg: #0b1020;
      --panel: #121a31;
      --panel-2: #18233f;
      --text: #e6ecff;
      --muted: #94a3b8;
      --accent: #7dd3fc;
      --good: #4ade80;
      --bad: #f87171;
      --border: rgba(148, 163, 184, 0.22);
      font-family: Inter, Segoe UI, Arial, sans-serif;
    }}
    body {{
      margin: 0;
      background: radial-gradient(circle at top, #16213e, var(--bg));
      color: var(--text);
    }}
    .wrap {{ max-width: 1200px; margin: 0 auto; padding: 32px 20px 56px; }}
    .hero {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }}
    .card {{
      background: rgba(18, 26, 49, 0.88);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 20px 60px rgba(0,0,0,.25);
    }}
    h1, h2 {{ margin: 0 0 12px; }}
    h1 {{ font-size: 2rem; }}
    h2 {{ font-size: 1.1rem; color: var(--accent); }}
    .muted {{ color: var(--muted); }}
    .grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); margin-top: 16px; }}
    .metric {{ font-size: 1.5rem; font-weight: 700; }}
    .status-good {{ color: var(--good); }}
    .status-bad {{ color: var(--bad); }}
    code, pre {{ font-family: Consolas, monospace; }}
    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      background: var(--panel-2);
      padding: 12px;
      border-radius: 12px;
      border: 1px solid var(--border);
      overflow: auto;
    }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid var(--border); padding: 10px; text-align: left; vertical-align: top; }}
    th {{ color: var(--accent); }}
    ul {{ margin: 8px 0 0 18px; }}
    a {{ color: var(--accent); }}
    .pill {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(125, 211, 252, 0.12);
      border: 1px solid rgba(125, 211, 252, 0.3);
      margin-right: 8px;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div class="card">
        <h1>Skill Runtime Report</h1>
        <p class="muted">Skill: <code>{esc(report.get('skill_id'))}</code></p>
        <p class="muted">Run: <code>{esc(report.get('run_id'))}</code></p>
        <p class="muted">Generated: {esc(report.get('generated_at'))}</p>
      </div>
      <div class="card">
        <h2>Verdict</h2>
        <div class="metric {'status-good' if evaluation.get('verdict') == 'pass' else 'status-bad'}">{esc(evaluation.get('verdict', 'unknown'))}</div>
        <div class="muted">Score: {esc(evaluation.get('score', 'n/a'))}</div>
      </div>
      <div class="card">
        <h2>Improvement Hint</h2>
        <p>{esc(highlights.get('improvement_hint'))}</p>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <h2>Run Summary</h2>
        <p><span class="pill">status: {esc(run.get('status'))}</span><span class="pill">skill version: {esc(run.get('skill_version_id'))}</span></p>
        <p class="muted">Model: {esc((run.get('model') or {}).get('model') if isinstance(run, dict) else '')}</p>
        <p class="muted">Output preview:</p>
        <pre>{esc(highlights.get('output_preview'))}</pre>
      </div>
      <div class="card">
        <h2>Issues</h2>
        <ul>{issues_html}</ul>
      </div>
      <div class="card">
        <h2>Feedback</h2>
        <ul>{recommendations_html}</ul>
      </div>
      <div class="card">
        <h2>Artifacts</h2>
        <ul>
          <li><a href="{esc(report['artifacts']['run_json'])}">run.json</a></li>
          <li><a href="{esc(report['artifacts']['trace_jsonl'])}">trace.jsonl</a></li>
          <li><a href="{esc(report['artifacts']['eval_json'])}">eval.json</a></li>
          <li><a href="{esc(report['artifacts']['feedback_json'])}">feedback.json</a></li>
          <li><a href="{esc(report['artifacts']['output_md'])}">output.md</a></li>
          {"<li><a href=\"" + esc(report['artifacts']['output_html']) + "\">output.html</a></li>" if report['artifacts'].get('output_html') else ""}
        </ul>
      </div>
    </div>

    <div class="card" style="margin-top: 16px;">
      <h2>Trace Timeline</h2>
      <table>
        <thead>
          <tr><th>Timestamp</th><th>Event</th><th>Payload</th></tr>
        </thead>
        <tbody>{trace_rows}</tbody>
      </table>
    </div>
  </div>
</body>
</html>"""

    def _render_dashboard_html(self, index_record: dict[str, object]) -> str:
        reports = index_record.get("reports", [])
        summary = index_record.get("summary", {})
        rows = ""
        chart_svg = self._render_trend_svg(reports if isinstance(reports, list) else [])
        summary_cards = ""
        if isinstance(summary, dict):
            summary_cards = f"""
            <div class="grid">
              <div class="card"><h2>Total Runs</h2><div class="metric">{html.escape(str(summary.get('total_runs', 0)))}</div></div>
              <div class="card"><h2>Pass Rate</h2><div class="metric">{html.escape(str(summary.get('pass_rate', 0.0)))}%</div></div>
              <div class="card"><h2>Average Score</h2><div class="metric">{html.escape(str(summary.get('avg_score', 0.0)))}</div></div>
              <div class="card"><h2>Pass / Fail</h2><div class="metric">{html.escape(str(summary.get('pass_count', 0)))}/{html.escape(str(summary.get('fail_count', 0)))}</div></div>
            </div>
            """
        if isinstance(reports, list):
            rows = "".join(
                f"<tr><td>{html.escape(str(item.get('skill_id')))}</td><td>{html.escape(str(item.get('run_id')))}</td><td>{html.escape(str(item.get('verdict')))}</td><td>{html.escape(str(item.get('score')))}</td><td><a href='{html.escape(str(item.get('report_html')))}'>Open</a></td></tr>"
                for item in reports
                if isinstance(item, dict)
            )
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Skill Runtime Dashboard</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 0; background: #0b1020; color: #e6ecff; }}
    .wrap {{ max-width: 1200px; margin: 0 auto; padding: 32px 20px 56px; }}
    .card {{ background: #121a31; border: 1px solid rgba(148,163,184,.22); border-radius: 18px; padding: 18px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid rgba(148,163,184,.22); padding: 10px; text-align: left; }}
    th {{ color: #7dd3fc; }}
    a {{ color: #7dd3fc; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Skill Runtime Dashboard</h1>
    <p>Generated at {html.escape(str(index_record.get('generated_at')))}</p>
    {summary_cards}
    <div class="card" style="margin-top: 16px;">
      <h2>Score Trend</h2>
      {chart_svg}
    </div>
    <div class="card">
      <table>
        <thead>
          <tr><th>Skill</th><th>Run</th><th>Verdict</th><th>Score</th><th>Report</th></tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>
</body>
</html>"""

    def _render_trend_svg(self, reports: list[dict[str, object]]) -> str:
        if not reports:
            return "<p class='muted'>No runs yet.</p>"

        points = []
        for index, item in enumerate(reports):
            score = _safe_float(item.get("score"))
            x = 40 + index * 120
            y = 180 - int(score * 140)
            points.append((x, y, score, str(item.get("run_id") or "")))

        width = max(320, 80 + (len(points) - 1) * 120)
        line_points = " ".join(f"{x},{y}" for x, y, _, _ in points)
        circles = "".join(
            f"<circle cx='{x}' cy='{y}' r='6' fill='#7dd3fc'><title>{html.escape(run_id)} score={score}</title></circle>"
            for x, y, score, run_id in points
        )
        labels = "".join(
            f"<text x='{x}' y='205' fill='#94a3b8' font-size='12' text-anchor='middle'>{html.escape(run_id[:12])}</text>"
            for x, _, _, run_id in points
        )
        return f"""
        <svg viewBox='0 0 {width} 230' width='100%' height='230' role='img' aria-label='Run score trend chart'>
          <defs>
            <linearGradient id='trend-fill' x1='0' x2='0' y1='0' y2='1'>
              <stop offset='0%' stop-color='#7dd3fc' stop-opacity='0.35'/>
              <stop offset='100%' stop-color='#7dd3fc' stop-opacity='0'/>
            </linearGradient>
          </defs>
          <rect x='0' y='0' width='{width}' height='230' rx='16' fill='#0f172a' opacity='0.72'/>
          <line x1='40' y1='40' x2='{width - 40}' y2='40' stroke='rgba(148,163,184,.18)' />
          <line x1='40' y1='90' x2='{width - 40}' y2='90' stroke='rgba(148,163,184,.18)' />
          <line x1='40' y1='140' x2='{width - 40}' y2='140' stroke='rgba(148,163,184,.18)' />
          <polyline points='{line_points}' fill='none' stroke='#7dd3fc' stroke-width='3' stroke-linejoin='round' stroke-linecap='round'/>
          {circles}
          {labels}
        </svg>
        """
