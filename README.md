# Skill Runtime Evaluation Loop

## Overview
**Tiếng Việt:**  
Dự án này là một workspace/harness cho agent skills. Mục tiêu là để một model lớn có thể tạo hoặc sửa skill, sau đó một Python runtime chạy skill đó với model nhỏ lấy từ environment. Mỗi lần chạy đều được ghi lại đầy đủ để audit, debug, đánh giá, và dùng làm feedback cho vòng cải tiến tiếp theo.

**English:**  
This project is a workspace/harness for agent skills. The goal is to let a frontier model create or revise a skill, then have a Python runtime execute that skill with a smaller model configured from the environment. Every run is fully recorded for audit, debugging, evaluation, and feedback-driven iteration.

## Problem
**Tiếng Việt:**  
Skill do model lớn viết ra thường quá dài, quá ngầm định, hoặc không phù hợp để model nhỏ chạy ổn định. Khi chạy thực tế, đội ngũ cần trace, log, artifact, và feedback rõ ràng để hiểu skill hỏng ở đâu và sửa thế nào.

**English:**  
Skills written by larger models are often too long, too implicit, or not tuned for reliable execution by smaller models. In real use, teams need clear traces, logs, artifacts, and feedback to understand why a skill failed and how to improve it.

## Goal
**Tiếng Việt:**  
Mục tiêu v1/hackathon là có một loop end-to-end thật, chạy được trên filesystem trước, không phụ thuộc database:
ingest skill -> run với small model từ env -> lưu trace/artifacts -> evaluate -> generate feedback -> revise -> rerun.

**English:**  
The v1/hackathon goal is a real end-to-end loop on the filesystem first, without a database:
ingest skill -> run with an env-configured small model -> save trace/artifacts -> evaluate -> generate feedback -> revise -> rerun.

## Non-goals
**Tiếng Việt:**  
- Không làm database production
- Không làm UI lớn hoặc dashboard phức tạp
- Không làm multi-user auth
- Không làm model routing nâng cao
- Không làm fine-tuning

**English:**  
- No production database
- No large UI or complex dashboard
- No multi-user auth
- No advanced model routing
- No fine-tuning

## Hero Flow
1. Ingest skill
2. Run with env-configured small model
3. Save trace and artifacts
4. Evaluate run
5. Generate feedback
6. Revise and rerun

**Tiếng Việt:**  
Đây là hero flow của hackathon. Nếu flow này chạy mượt, sản phẩm đã chứng minh được giá trị cốt lõi.

**English:**  
This is the hackathon hero flow. If this flow works cleanly, the product has proven its core value.

## Repository Structure
- `skills/`
- `runs/`
- `datasets/`
- `logs/`
- `reports/`

**Tiếng Việt:**  
Workspace là nguồn sự thật chính. Mọi artifact quan trọng đều nằm trong folder tree, không phụ thuộc state ẩn trong memory hay database.

**English:**  
The workspace is the source of truth. All important artifacts live in the folder tree, not in hidden in-memory state or a database.

## Key Artifacts
- `SKILL.md`
- `run.json`
- `trace.jsonl`
- `eval.json`
- `feedback.json`
- `report.json`
- `report.html`

**Tiếng Việt:**  
Các file này đủ để replay, audit, và compare một run hoặc một skill version.

**English:**  
These files are enough to replay, audit, and compare a run or a skill version.

## Setup
**Tiếng Việt:**  
Yêu cầu:
- Python 3.12+
- Một môi trường `.env` hợp lệ

Ví dụ cài đặt:
```powershell
python -m pip install -e .
```

Ví dụ `.env` cần có:
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

**English:**  
Requirements:
- Python 3.12+
- A valid `.env`

Install:
```powershell
python -m pip install -e .
```

Example `.env` values:
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
**Tiếng Việt:**  
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

**English:**  
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

## Evaluation
**Tiếng Việt:**  
Hệ thống chấm theo:
- độ đúng của output
- có tuân thủ constraint không
- trace có đủ để audit không
- run có terminal status không
- feedback có nêu issue cụ thể không

**English:**  
The system evaluates:
- output correctness
- constraint adherence
- whether the trace is auditable
- whether the run reaches a terminal status
- whether feedback names concrete issues

## Current Status
**Tiếng Việt:**  
Đã xong:
- workspace contract
- skill ingestion
- skill versioning
- runtime chạy bằng model từ env
- trace/log/output persistence
- evaluation
- feedback generation
- revision
- compare runs/versions
- report export and static HTML dashboard
- dashboard summary cards and score trend chart

Chưa xong:
- UI
- database
- multi-user features
- richer benchmark suite
- production orchestration

Known limitations:
- Một số luồng vẫn tối giản để phù hợp hackathon
- Live model smoke phụ thuộc env hợp lệ và network

**English:**  
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
**Tiếng Việt:** Vuong / Codex  
**English:** Vuong / Codex

## License
**Tiếng Việt:** Chưa chốt.  
**English:** Not decided yet.
