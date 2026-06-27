from __future__ import annotations

import argparse
import json
from pathlib import Path

from skill_runtime.application.bootstrap_workspace import WorkspaceBootstrapper
from skill_runtime.application.compare_runs import RunComparator
from skill_runtime.application.export_report import ReportExporter
from skill_runtime.application.evaluate_run import RunEvaluator
from skill_runtime.application.generate_feedback import FeedbackGenerator
from skill_runtime.application.ingest_skill import SkillIngestor
from skill_runtime.application.revise_skill import SkillReviser
from skill_runtime.application.run_skill import RunExecutor
from skill_runtime.application.version_skill import SkillVersioner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    bootstrap = sub.add_parser("bootstrap-workspace", help="Create workspace folders")
    bootstrap.add_argument("--root", default=".", help="Workspace root path")

    ingest = sub.add_parser("ingest-skill", help="Validate and inspect a skill folder")
    ingest.add_argument("--skill-id", required=True, help="Skill folder name under skills/")
    ingest.add_argument("--workspace-root", default=".", help="Workspace root path")

    version = sub.add_parser("version-skill", help="Snapshot a skill into versions/")
    version.add_argument("--skill-id", required=True, help="Skill folder name under skills/")
    version.add_argument("--version-id", default=None, help="Optional explicit version id")
    version.add_argument("--workspace-root", default=".", help="Workspace root path")

    run = sub.add_parser("run-skill", help="Execute one skill version against one input")
    run.add_argument("--skill-id", required=True, help="Skill folder name under skills/")
    run.add_argument("--version-id", required=True, help="Skill version id under versions/")
    run.add_argument("--input", required=True, help="Task input text")
    run.add_argument("--workspace-root", default=".", help="Workspace root path")

    evaluate = sub.add_parser("evaluate-run", help="Score a run and write eval.json")
    evaluate.add_argument("--skill-id", required=True, help="Skill folder name under skills/")
    evaluate.add_argument("--run-id", required=True, help="Run folder name under runs/")
    evaluate.add_argument("--must-contain", action="append", default=[], help="Required output substring")
    evaluate.add_argument("--must-have-event", action="append", default=[], help="Required trace event")
    evaluate.add_argument("--workspace-root", default=".", help="Workspace root path")

    feedback = sub.add_parser("generate-feedback", help="Generate feedback.json from eval and trace")
    feedback.add_argument("--skill-id", required=True, help="Skill folder name under skills/")
    feedback.add_argument("--run-id", required=True, help="Run folder name under runs/")
    feedback.add_argument("--workspace-root", default=".", help="Workspace root path")

    revise = sub.add_parser("revise-skill", help="Create a new skill version from feedback")
    revise.add_argument("--skill-id", required=True, help="Skill folder name under skills/")
    revise.add_argument("--run-id", required=True, help="Run folder name under runs/")
    revise.add_argument("--workspace-root", default=".", help="Workspace root path")

    compare_runs = sub.add_parser("compare-runs", help="Compare two runs for one skill")
    compare_runs.add_argument("--skill-id", required=True, help="Skill folder name under skills/")
    compare_runs.add_argument("--run-a", required=True, help="First run id")
    compare_runs.add_argument("--run-b", required=True, help="Second run id")
    compare_runs.add_argument("--workspace-root", default=".", help="Workspace root path")

    compare_versions = sub.add_parser("compare-versions", help="Compare two skill versions")
    compare_versions.add_argument("--skill-id", required=True, help="Skill folder name under skills/")
    compare_versions.add_argument("--version-a", required=True, help="First version id")
    compare_versions.add_argument("--version-b", required=True, help="Second version id")
    compare_versions.add_argument("--workspace-root", default=".", help="Workspace root path")

    export_report = sub.add_parser("export-report", help="Export report.json and report.html for one run")
    export_report.add_argument("--skill-id", required=True, help="Skill folder name under skills/")
    export_report.add_argument("--run-id", required=True, help="Run folder name under runs/")
    export_report.add_argument("--workspace-root", default=".", help="Workspace root path")

    build_dashboard = sub.add_parser("build-dashboard", help="Build reports/index.html for all runs")
    build_dashboard.add_argument("--workspace-root", default=".", help="Workspace root path")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "bootstrap-workspace":
        WorkspaceBootstrapper(Path(args.root)).bootstrap()
        return 0

    if args.command == "ingest-skill":
        result = SkillIngestor(Path(args.workspace_root)).ingest(args.skill_id)
        print(
            json.dumps(
                {
                    "skill_id": result.skill_id,
                    "skill_root": str(result.skill_root),
                    "found_paths": list(result.found_paths),
                    "missing_paths": list(result.missing_paths),
                    "metadata": result.metadata,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "version-skill":
        snapshot = SkillVersioner(Path(args.workspace_root)).snapshot(
            args.skill_id,
            version_id=args.version_id,
        )
        print(
            json.dumps(
                {
                    "skill_id": snapshot.skill_id,
                    "version_id": snapshot.version_id,
                    "source_root": str(snapshot.source_root),
                    "version_root": str(snapshot.version_root),
                    "package_root": str(snapshot.package_root),
                    "manifest_path": str(snapshot.manifest_path),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "run-skill":
        result = RunExecutor(Path(args.workspace_root)).execute(
            skill_id=args.skill_id,
            version_id=args.version_id,
            input_text=args.input,
        )
        print(
            json.dumps(
                {
                    "run_id": result.run_id,
                    "status": result.status,
                    "run_root": str(result.run_root),
                    "run_json_path": str(result.run_json_path),
                    "trace_path": str(result.trace_path),
                    "output_path": str(result.output_path),
                    "error_message": result.error_message,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0 if result.status == "completed" else 1

    if args.command == "evaluate-run":
        result = RunEvaluator(Path(args.workspace_root)).evaluate(
            skill_id=args.skill_id,
            run_id=args.run_id,
            required_output_contains=args.must_contain,
            required_trace_events=args.must_have_event,
        )
        print(
            json.dumps(
                {
                    "run_id": result.run_id,
                    "skill_id": result.skill_id,
                    "skill_version_id": result.skill_version_id,
                    "verdict": result.verdict,
                    "score": result.score,
                    "issues": [
                        {
                            "code": issue.code,
                            "message": issue.message,
                            "evidence": list(issue.evidence),
                        }
                        for issue in result.issues
                    ],
                    "eval_json_path": str(result.eval_json_path),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0 if result.verdict == "pass" else 1

    if args.command == "generate-feedback":
        result = FeedbackGenerator(Path(args.workspace_root)).generate(
            skill_id=args.skill_id,
            run_id=args.run_id,
        )
        print(
            json.dumps(
                {
                    "run_id": result.run_id,
                    "skill_id": result.skill_id,
                    "skill_version_id": result.skill_version_id,
                    "summary": result.summary,
                    "recommendations": list(result.recommendations),
                    "evidence": list(result.evidence),
                    "feedback_json_path": str(result.feedback_json_path),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "revise-skill":
        result = SkillReviser(Path(args.workspace_root)).revise(
            skill_id=args.skill_id,
            run_id=args.run_id,
        )
        print(
            json.dumps(
                {
                    "skill_id": result.skill_id,
                    "version_id": result.version_id,
                    "version_root": str(result.version_root),
                    "package_root": str(result.package_root),
                    "manifest_path": str(result.manifest_path),
                    "content_hash": result.content_hash,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "compare-runs":
        result = RunComparator(Path(args.workspace_root)).compare_runs(
            skill_id=args.skill_id,
            run_id_a=args.run_a,
            run_id_b=args.run_b,
        )
        print(
            json.dumps(
                {
                    "comparison_id": result.comparison_id,
                    "subject_a": result.subject_a,
                    "subject_b": result.subject_b,
                    "summary": result.summary,
                    "differences": list(result.differences),
                    "comparison_json_path": str(result.comparison_json_path),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "compare-versions":
        result = RunComparator(Path(args.workspace_root)).compare_versions(
            skill_id=args.skill_id,
            version_a=args.version_a,
            version_b=args.version_b,
        )
        print(
            json.dumps(
                {
                    "comparison_id": result.comparison_id,
                    "subject_a": result.subject_a,
                    "subject_b": result.subject_b,
                    "summary": result.summary,
                    "differences": list(result.differences),
                    "comparison_json_path": str(result.comparison_json_path),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "export-report":
        result = ReportExporter(Path(args.workspace_root)).export_run_report(
            skill_id=args.skill_id,
            run_id=args.run_id,
        )
        print(
            json.dumps(
                {
                    "report_id": result.report_id,
                    "skill_id": result.skill_id,
                    "run_id": result.run_id,
                    "report_json_path": str(result.report_json_path),
                    "report_html_path": str(result.report_html_path),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "build-dashboard":
        result = ReportExporter(Path(args.workspace_root)).build_dashboard_index()
        print(
            json.dumps(
                {
                    "dashboard_root": str(result.dashboard_root),
                    "index_json_path": str(result.index_json_path),
                    "index_html_path": str(result.index_html_path),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
