# Skill Runtime Evaluation Loop

## Overview
This project is a workspace and harness for agent skills. A frontier model can create or revise a skill, then a Python runtime executes that skill with a smaller model configured from the environment. Every run is recorded for audit, debugging, evaluation, and feedback-driven iteration.

## Problem
Skills written by larger models are often too long, too implicit, or not tuned for reliable execution by smaller models. In practice, teams need clear traces, logs, artifacts, and feedback to understand why a skill failed and how to improve it.

## Goal
The v1 and hackathon goal is a real end-to-end loop on the filesystem first, without a database:
ingest skill -> run with an env-configured small model -> save trace and artifacts -> evaluate -> generate feedback -> revise -> rerun.

## Non-goals
- Production database
- Large UI or complex dashboard
- Multi-user auth
- Advanced model routing
- Fine-tuning

## Hero Flow
1. Ingest skill
2. Run with env-configured small model
3. Save trace and artifacts
4. Evaluate run
5. Generate feedback
6. Revise and rerun

## Repository Structure
- `skills/`
- `runs/`
- `datasets/`
- `logs/`
- `reports/`

## Key Artifacts
- `SKILL.md`
- `run.json`
- `trace.jsonl`
- `eval.json`
- `feedback.json`
- `report.json`
- `report.html`

## Setup
Requirements:
- Python 3.12+
- A valid `.env`

Install:
```powershell
python -m pip install -e .
```

Example `.env`:
```env
SMALL_LLM_PROVIDER=openai_compatible
SMALL_LLM_MODEL=your-model-id
SMALL_LLM_BASE_URL=https://your-openai-compatible-endpoint/v1
SMALL_LLM_API_KEY=your_api_key_here
SMALL_LLM_TEMPERATURE=0.0
SMALL_LLM_MAX_TOKENS=4096
SMALL_LLM_TIMEOUT_SECONDS=120
SKILL_RUNTIME_WORKSPACE_ROOT=.
SKILL_RUNTIME_TRACE_LEVEL=standard
```

## Run Demo
Bootstrap workspace:
```powershell
skill-runtime bootstrap-workspace --root .
```

Ingest skill:
```powershell
skill-runtime ingest-skill --skill-id echo-skill --workspace-root .
```

Create a skill version:
```powershell
skill-runtime version-skill --skill-id echo-skill --workspace-root .
```

Run the skill:
```powershell
skill-runtime run-skill --skill-id echo-skill --version-id <version_id> --input "say hello in one sentence" --workspace-root .
```

Evaluate:
```powershell
skill-runtime evaluate-run --skill-id echo-skill --run-id <run_id> --workspace-root .
```

Generate feedback:
```powershell
skill-runtime generate-feedback --skill-id echo-skill --run-id <run_id> --workspace-root .
```

Revise:
```powershell
skill-runtime revise-skill --skill-id echo-skill --run-id <run_id> --workspace-root .
```

Compare:
```powershell
skill-runtime compare-runs --skill-id echo-skill --run-a <run_a> --run-b <run_b> --workspace-root .
skill-runtime compare-versions --skill-id echo-skill --version-a <version_a> --version-b <version_b> --workspace-root .
```

Export dashboard report:
```powershell
skill-runtime export-report --skill-id echo-skill --run-id <run_id> --workspace-root .
skill-runtime build-dashboard --workspace-root .
```

The dashboard includes summary cards and a simple score trend chart.

Real run example for the FE dashboard skill:
```powershell
skill-runtime demo-loop `
  --skill-id fe-agent-dashboard `
  --rounds 6 `
  --scenarios-per-round 4 `
  --series-id fe-dashboard-demo `
  --prompt-policy auto `
  --input "Hãy xây một dashboard giám sát vận hành AI agents bằng mock data, dùng single-file HTML/CSS/JS. Ưu tiên visual hierarchy rõ, KPI nổi bật, trend charts, bảng runs sort/filter, detail panel bên phải, anomaly/alerts, dark mode, responsive mobile, và các state loading/empty/error/partial/selected/stale." `
  --workspace-root .
```

Each round runs 4 scenarios, scores them all, then aggregates feedback before revising the skill. Use `--prompt-policy auto` to let the runner decide whether the next round keeps the same scenario pack or rotates it. If you omit `--series-id`, the tool generates a new series id automatically so previous runs stay intact.

## Evaluation
The system evaluates:
- output correctness
- constraint adherence
- whether the trace is auditable
- whether the run reaches a terminal status
- whether feedback names concrete issues

## Current Status
Done:
- workspace contract
- skill ingestion
- skill versioning
- env-driven runtime execution
- trace/log/output persistence
- evaluation
- feedback generation
- revision
- run/version comparison
- report export and static HTML dashboard
- dashboard summary cards and score trend chart

Not done:
- UI
- database
- multi-user features
- richer benchmark suite
- production orchestration

Known limitations:
- Some flows are intentionally minimal for hackathon speed
- Live model smoke depends on valid env values and network access

## Maintainer
Vuong / Codex

## License
Not decided yet.
