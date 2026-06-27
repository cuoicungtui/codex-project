from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skill_runtime.application.compare_runs import RunComparator
from skill_runtime.application.evaluate_run import RunEvaluator
from skill_runtime.application.export_report import ReportExporter
from skill_runtime.application.generate_feedback import FeedbackGenerator
from skill_runtime.application.revise_skill import SkillReviser
from skill_runtime.application.run_skill import RunExecutor
from skill_runtime.application.version_skill import SkillVersioner
from skill_runtime.domain.runs import RuntimeModelConfig
from skill_runtime.domain.workspace import WorkspaceContract


@dataclass(frozen=True, slots=True)
class DemoLoopRun:
    loop_index: int
    version_id: str
    run_id: str
    run_status: str
    verdict: str
    score: float


@dataclass(frozen=True, slots=True)
class DemoLoopResult:
    skill_id: str
    initial_version_id: str
    final_version_id: str
    runs: tuple[DemoLoopRun, ...]
    dashboard_html_path: Path
    final_skill_md_path: Path


class DemoLoopRunner:
    def __init__(
        self,
        workspace_root: Path,
    ) -> None:
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
        max_tokens_cap: int = 12000,
    ) -> DemoLoopResult:
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
        loop_runs: list[DemoLoopRun] = []
        previous_run_id: str | None = None

        for loop_index in range(1, loop_count + 1):
            run_id = f"{skill_id}-loop-{loop_index}"
            run_result = self._executor.execute(
                skill_id=skill_id,
                version_id=current_version_id,
                input_text=input_text,
                run_id=run_id,
                model_config=effective_config,
            )
            eval_result = self._evaluator.evaluate(skill_id=skill_id, run_id=run_id)
            self._feedback.generate(skill_id=skill_id, run_id=run_id, model_config=effective_config)
            self._reports.export_run_report(skill_id=skill_id, run_id=run_id)
            if previous_run_id is not None:
                self._comparator.compare_runs(skill_id=skill_id, run_id_a=previous_run_id, run_id_b=run_id)
            loop_runs.append(
                DemoLoopRun(
                    loop_index=loop_index,
                    version_id=current_version_id,
                    run_id=run_id,
                    run_status=run_result.status,
                    verdict=eval_result.verdict,
                    score=eval_result.score,
                )
            )
            previous_run_id = run_id
            if loop_index < loop_count:
                revised = self._reviser.revise(
                    skill_id=skill_id,
                    run_id=run_id,
                    model_config=effective_config,
                )
                current_version_id = revised.version_id

        dashboard = self._reports.build_dashboard_index()
        final_skill_md_path = self._workspace.skills_dir / skill_id / "versions" / current_version_id / skill_id / "SKILL.md"
        return DemoLoopResult(
            skill_id=skill_id,
            initial_version_id=initial_version.version_id,
            final_version_id=current_version_id,
            runs=tuple(loop_runs),
            dashboard_html_path=dashboard.index_html_path,
            final_skill_md_path=final_skill_md_path,
        )
