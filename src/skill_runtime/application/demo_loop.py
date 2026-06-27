from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from skill_runtime.application.compare_runs import RunComparator
from skill_runtime.application.evaluate_run import RunEvaluator
from skill_runtime.application.export_report import ReportExporter
from skill_runtime.application.generate_feedback import FeedbackGenerator
from skill_runtime.application.revise_skill import SkillReviser
from skill_runtime.application.run_skill import RunExecutor
from skill_runtime.application.version_skill import SkillVersioner, generate_version_id
from skill_runtime.domain.runs import RuntimeModelConfig
from skill_runtime.domain.workspace import WorkspaceContract


@dataclass(frozen=True, slots=True)
class ScenarioPrompt:
    scenario_index: int
    label: str
    input_text: str


@dataclass(frozen=True, slots=True)
class ScenarioRun:
    round_index: int
    scenario_index: int
    label: str
    version_id: str
    run_id: str
    run_status: str
    verdict: str
    score: float


@dataclass(frozen=True, slots=True)
class RoundSummary:
    round_index: int
    version_id: str
    round_run_id: str
    prompt_mode: str
    decision: str
    average_score: float
    best_score: float
    worst_score: float
    scenario_count: int


@dataclass(frozen=True, slots=True)
class DemoLoopResult:
    skill_id: str
    series_id: str
    initial_version_id: str
    final_version_id: str
    rounds: tuple[RoundSummary, ...]
    scenarios: tuple[ScenarioRun, ...]
    dashboard_html_path: Path
    final_skill_md_path: Path


class DemoLoopRunner:
    def __init__(self, workspace_root: Path) -> None:
        self._workspace = WorkspaceContract(workspace_root)
        self._versioner = SkillVersioner(workspace_root)
        self._executor = RunExecutor(workspace_root)
        self._evaluator = RunEvaluator(workspace_root)
        self._feedback = FeedbackGenerator(workspace_root)
        self._reviser = SkillReviser(workspace_root)
        self._reports = ReportExporter(workspace_root)
        self._comparator = RunComparator(workspace_root)

    def run(
        self,
        *,
        skill_id: str,
        input_text: str,
        loop_count: int,
        model_config: RuntimeModelConfig,
        series_id: str | None = None,
        max_tokens_cap: int = 12000,
        scenarios_per_round: int = 4,
        prompt_policy: str = "auto",
    ) -> DemoLoopResult:
        effective_series_id = series_id or generate_version_id()
        effective_config = RuntimeModelConfig(
            provider=model_config.provider,
            model=model_config.model,
            base_url=model_config.base_url,
            api_key=model_config.api_key,
            temperature=model_config.temperature,
            max_tokens=min(model_config.max_tokens, max_tokens_cap),
            timeout_seconds=model_config.timeout_seconds,
        )
        initial_version = self._versioner.snapshot(skill_id)
        current_version_id = initial_version.version_id
        all_scenarios: list[ScenarioRun] = []
        round_summaries: list[RoundSummary] = []
        previous_round_average: float | None = None
        previous_summary_run_id: str | None = None
        scenario_pack = self._build_prompt_pack(base_input=input_text, round_index=1, mode="canonical")

        for round_index in range(1, loop_count + 1):
            if round_index > 1:
                decision = self._select_prompt_policy(
                    prompt_policy=prompt_policy,
                    previous_round_average=previous_round_average,
                )
                scenario_pack = self._build_prompt_pack(
                    base_input=input_text,
                    round_index=round_index,
                    mode=decision,
                )
            else:
                decision = "canonical"

            round_run_id = f"{skill_id}-{effective_series_id}-round-{round_index}"
            round_dir = self._workspace.runs_dir / skill_id / round_run_id
            round_dir.mkdir(parents=True, exist_ok=False)
            round_trace_path = round_dir / "trace.jsonl"
            round_output_path = round_dir / "artifacts" / "output.md"
            round_output_path.parent.mkdir(parents=True, exist_ok=True)

            round_trace = self._workspace_trace_writer(round_trace_path, round_run_id)
            round_trace.append(
                "round_started",
                {
                    "skill_id": skill_id,
                    "round_index": round_index,
                    "version_id": current_version_id,
                    "prompt_mode": decision,
                    "scenario_count": scenarios_per_round,
                },
            )

            scenario_results = self._run_scenarios(
                skill_id=skill_id,
                series_id=effective_series_id,
                round_index=round_index,
                version_id=current_version_id,
                prompts=scenario_pack[:scenarios_per_round],
                config=effective_config,
            )
            all_scenarios.extend(scenario_results)

            round_summary = self._summarize_round(
                skill_id=skill_id,
                series_id=effective_series_id,
                round_index=round_index,
                round_run_id=round_run_id,
                version_id=current_version_id,
                prompt_mode=decision,
                scenario_prompts=scenario_pack[:scenarios_per_round],
                scenario_results=scenario_results,
                round_output_path=round_output_path,
                round_trace=round_trace,
            )
            round_summaries.append(round_summary)
            previous_round_average = round_summary.average_score

            self._reports.export_run_report(skill_id=skill_id, run_id=round_run_id)
            self._feedback.generate(skill_id=skill_id, run_id=round_run_id, model_config=effective_config)
            revised = self._reviser.revise(skill_id=skill_id, run_id=round_run_id, model_config=effective_config)
            current_version_id = revised.version_id

            if previous_summary_run_id is not None:
                self._comparator.compare_runs(skill_id=skill_id, run_id_a=previous_summary_run_id, run_id_b=round_run_id)
            previous_summary_run_id = round_run_id

        dashboard = self._reports.build_dashboard_index()
        final_skill_md_path = self._workspace.skills_dir / skill_id / "versions" / current_version_id / skill_id / "SKILL.md"
        return DemoLoopResult(
            skill_id=skill_id,
            series_id=effective_series_id,
            initial_version_id=initial_version.version_id,
            final_version_id=current_version_id,
            rounds=tuple(round_summaries),
            scenarios=tuple(all_scenarios),
            dashboard_html_path=dashboard.index_html_path,
            final_skill_md_path=final_skill_md_path,
        )

    def _run_scenarios(
        self,
        *,
        skill_id: str,
        series_id: str,
        round_index: int,
        version_id: str,
        prompts: tuple[ScenarioPrompt, ...],
        config: RuntimeModelConfig,
    ) -> list[ScenarioRun]:
        scenario_results: list[ScenarioRun] = []
        for prompt in prompts:
            run_id = f"{skill_id}-{series_id}-round-{round_index}-scenario-{prompt.scenario_index}"
            run_result = self._executor.execute(
                skill_id=skill_id,
                version_id=version_id,
                input_text=prompt.input_text,
                run_id=run_id,
                model_config=config,
            )
            eval_result = self._evaluator.evaluate(skill_id=skill_id, run_id=run_id)
            self._feedback.generate(skill_id=skill_id, run_id=run_id, model_config=config)
            self._reports.export_run_report(skill_id=skill_id, run_id=run_id)
            scenario_results.append(
                ScenarioRun(
                    round_index=round_index,
                    scenario_index=prompt.scenario_index,
                    label=prompt.label,
                    version_id=version_id,
                    run_id=run_id,
                    run_status=run_result.status,
                    verdict=eval_result.verdict,
                    score=eval_result.score,
                )
            )
        return scenario_results

    def _summarize_round(
        self,
        *,
        skill_id: str,
        series_id: str,
        round_index: int,
        round_run_id: str,
        version_id: str,
        prompt_mode: str,
        scenario_prompts: tuple[ScenarioPrompt, ...],
        scenario_results: list[ScenarioRun],
        round_output_path: Path,
        round_trace,
    ) -> RoundSummary:
        round_root = self._workspace.runs_dir / skill_id / round_run_id
        round_run_json = round_root / "run.json"
        round_eval_json = round_root / "eval.json"
        round_feedback_json = round_root / "feedback.json"
        round_trace_path = round_root / "trace.jsonl"

        scores = [scenario.score for scenario in scenario_results]
        verdict_counts = Counter(scenario.verdict for scenario in scenario_results)
        best_scenario = max(scenario_results, key=lambda item: item.score)
        worst_scenario = min(scenario_results, key=lambda item: item.score)
        average_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        best_score = round(best_scenario.score, 2) if scenario_results else 0.0
        worst_score = round(worst_scenario.score, 2) if scenario_results else 0.0
        decision = self._select_next_decision(average_score=average_score, best_score=best_score, prompt_mode=prompt_mode)
        created_at = self._utc_now()

        round_run_record = {
            "schema_version": 1,
            "run_id": round_run_id,
            "skill_id": skill_id,
            "series_id": series_id,
            "skill_version_id": version_id,
            "round_index": round_index,
            "round_type": "summary",
            "status": "completed",
            "started_at": created_at,
            "completed_at": created_at,
            "workspace_root": str(self._workspace.root),
            "artifacts_dir": str(round_root / "artifacts"),
            "trace_path": str(round_trace_path),
            "output_path": str(round_output_path),
            "output_html_path": None,
            "input": {
                "kind": "scenario_pack",
                "prompt_mode": prompt_mode,
                "scenarios": [self._prompt_to_dict(prompt) for prompt in scenario_prompts],
            },
            "summary": {
                "version_id": version_id,
                "scenario_count": len(scenario_results),
                "average_score": average_score,
                "best_score": best_score,
                "worst_score": worst_score,
                "best_run_id": best_scenario.run_id,
                "worst_run_id": worst_scenario.run_id,
                "decision": decision,
            },
            "results": [
                {
                    "scenario_index": item.scenario_index,
                    "label": item.label,
                    "run_id": item.run_id,
                    "score": item.score,
                    "verdict": item.verdict,
                }
                for item in scenario_results
            ],
        }
        round_eval_record = {
            "schema_version": 1,
            "run_id": round_run_id,
            "skill_id": skill_id,
            "skill_version_id": version_id,
            "verdict": "pass" if average_score >= 0.75 and verdict_counts.get("fail", 0) == 0 else "fail",
            "score": average_score,
            "metrics": {
                "scenario_count": len(scenario_results),
                "average_score": average_score,
                "best_score": best_score,
                "worst_score": worst_score,
                "pass_count": verdict_counts.get("pass", 0),
                "fail_count": verdict_counts.get("fail", 0),
            },
            "issues": self._aggregate_issues(scenario_results),
            "created_at": created_at,
        }
        round_feedback_record = {
            "schema_version": 1,
            "run_id": round_run_id,
            "skill_id": skill_id,
            "skill_version_id": version_id,
            "summary": f"Round {round_index} aggregate feedback for {skill_id}",
            "recommendations": self._aggregate_recommendations(scenario_results, decision=decision),
            "evidence": [f"{item.label}: {item.verdict} ({item.score})" for item in scenario_results],
            "raw_feedback": "Aggregated from 4 scenario runs",
            "created_at": created_at,
        }

        round_run_json.write_text(json.dumps(round_run_record, indent=2, ensure_ascii=False), encoding="utf-8")
        round_eval_json.write_text(json.dumps(round_eval_record, indent=2, ensure_ascii=False), encoding="utf-8")
        round_feedback_json.write_text(json.dumps(round_feedback_record, indent=2, ensure_ascii=False), encoding="utf-8")
        round_output_path.write_text(self._render_round_summary_md(round_run_record, round_eval_record, round_feedback_record), encoding="utf-8")
        round_trace.append("round_finished", {"decision": decision, "average_score": average_score})

        return RoundSummary(
            round_index=round_index,
            version_id=version_id,
            round_run_id=round_run_id,
            prompt_mode=prompt_mode,
            decision=decision,
            average_score=average_score,
            best_score=best_score,
            worst_score=worst_score,
            scenario_count=len(scenario_results),
        )

    def _aggregate_issues(self, scenario_results: list[ScenarioRun]) -> list[dict[str, object]]:
        verdict_counts = Counter(item.verdict for item in scenario_results)
        issues: list[dict[str, object]] = []
        if verdict_counts.get("fail", 0):
            issues.append(
                {
                    "code": "round_has_failed_scenarios",
                    "message": f"{verdict_counts.get('fail', 0)} of {len(scenario_results)} scenarios failed.",
                    "evidence": [item.run_id for item in scenario_results if item.verdict == "fail"],
                }
            )
        if scenario_results and max(item.score for item in scenario_results) - min(item.score for item in scenario_results) > 0.5:
            issues.append(
                {
                    "code": "score_spread_high",
                    "message": "Scores vary significantly across scenarios, suggesting the skill is not yet robust.",
                    "evidence": [f"{item.run_id}:{item.score}" for item in scenario_results],
                }
            )
        return issues

    def _aggregate_recommendations(self, scenario_results: list[ScenarioRun], *, decision: str) -> list[str]:
        best = max(scenario_results, key=lambda item: item.score)
        worst = min(scenario_results, key=lambda item: item.score)
        recommendations = [
            f"Use the strongest scenario ({best.label}) as the design anchor, then close gaps exposed by {worst.label}.",
            "Keep the skill general enough to serve multiple FE dashboard briefs instead of one prompt variant.",
            f"Next round prompt policy: {decision}.",
        ]
        if any(item.verdict == "fail" for item in scenario_results):
            recommendations.append("Reinforce the table, anomaly, and state coverage because at least one scenario still failed.")
        return recommendations

    def _render_round_summary_md(
        self,
        run_record: dict[str, object],
        eval_record: dict[str, object],
        feedback_record: dict[str, object],
    ) -> str:
        results = run_record.get("results", [])
        lines = [
            f"# Round {run_record.get('round_index')} Summary",
            "",
            f"- Skill: `{run_record.get('skill_id')}`",
            f"- Series: `{run_record.get('series_id')}`",
            f"- Version: `{run_record.get('summary', {}).get('version_id')}`",
            f"- Decision: `{run_record.get('summary', {}).get('decision')}`",
            f"- Average score: `{eval_record.get('score')}`",
            "",
            "## Scenario Results",
            "",
            "| Scenario | Run | Verdict | Score |",
            "| --- | --- | --- | --- |",
        ]
        for item in results:
            lines.append(
                f"| {item.get('label')} | `{item.get('run_id')}` | {item.get('verdict')} | {item.get('score')} |"
            )
        lines.extend(
            [
                "",
                "## Recommendations",
                "",
            ]
        )
        for item in feedback_record.get("recommendations", []):
            lines.append(f"- {item}")
        return "\n".join(lines) + "\n"

    def _select_prompt_policy(self, *, prompt_policy: str, previous_round_average: float | None) -> str:
        if prompt_policy in {"keep", "rotate"}:
            return prompt_policy
        if previous_round_average is None:
            return "canonical"
        return "rotate" if previous_round_average < 0.75 else "keep"

    def _select_next_decision(self, *, average_score: float, best_score: float, prompt_mode: str) -> str:
        if average_score >= 0.8:
            return "keep"
        if best_score >= 0.7:
            return "rotate"
        return "canonical" if prompt_mode == "canonical" else "rotate"

    def _build_prompt_pack(self, *, base_input: str, round_index: int, mode: str) -> tuple[ScenarioPrompt, ...]:
        base = base_input.strip()
        if mode == "rotate":
            return (
                ScenarioPrompt(
                    1,
                    "Overview-first",
                    self._compose_prompt(
                        base,
                        "Focus on a fast overview with strong KPI hierarchy and a production-like feel.",
                        "Keep the first screen calm and scannable.",
                    ),
                ),
                ScenarioPrompt(
                    2,
                    "Table-depth",
                    self._compose_prompt(
                        base,
                        "Emphasize the sortable/filterable runs table and make row states easy to compare.",
                        "The table should carry the operational story.",
                    ),
                ),
                ScenarioPrompt(
                    3,
                    "Alert-heavy",
                    self._compose_prompt(
                        base,
                        "Stress anomaly and alert handling with clear severity and actionability.",
                        "Make the problems jump out within five seconds.",
                    ),
                ),
                ScenarioPrompt(
                    4,
                    "State coverage",
                    self._compose_prompt(
                        base,
                        "Show loading, empty, error, partial, selected, and stale states in a believable way.",
                        "Make mobile behavior and edge states feel first-class.",
                    ),
                ),
            )
        if mode == "keep":
            return self._build_prompt_pack(base_input=base_input, round_index=round_index, mode="canonical")
        return (
            ScenarioPrompt(
                1,
                "Balanced overview",
                self._compose_prompt(
                    base,
                    "Build a production-grade overview that surfaces the main health of the agents system in 5-10 seconds.",
                    "Prioritize KPI hierarchy and clear dashboard structure.",
                ),
            ),
            ScenarioPrompt(
                2,
                "Run table detail",
                self._compose_prompt(
                    base,
                    "Make the runs table sortable and filterable, with a strong selected-state detail panel.",
                    "The table must feel like the operational control surface.",
                ),
            ),
            ScenarioPrompt(
                3,
                "Anomaly focus",
                self._compose_prompt(
                    base,
                    "Bring anomalies and alerts to the foreground without overwhelming the overview.",
                    "Signal what needs attention immediately.",
                ),
            ),
            ScenarioPrompt(
                4,
                "Responsive states",
                self._compose_prompt(
                    base,
                    "Exercise loading, empty, error, partial, selected, and stale UI states on desktop and mobile.",
                    "Keep the layout coherent under smaller screens.",
                ),
            ),
        )

    def _compose_prompt(self, base: str, focus: str, reminder: str) -> str:
        parts = [base] if base else []
        parts.extend([focus, reminder])
        return " ".join(part.strip() for part in parts if part.strip())

    def _prompt_to_dict(self, prompt: ScenarioPrompt) -> dict[str, object]:
        return {
            "scenario_index": prompt.scenario_index,
            "label": prompt.label,
            "input_text": prompt.input_text,
        }

    def _workspace_trace_writer(self, path: Path, run_id: str):
        from skill_runtime.application.run_skill import JsonlTraceWriter

        return JsonlTraceWriter(path, run_id)

    def _utc_now(self) -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
