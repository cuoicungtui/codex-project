---
title: Skill Runtime Evaluation Loop - Epics and Stories
created: 2026-06-27
updated: 2026-06-27
status: draft
stepsCompleted:
  - prd-reviewed
  - scope-locked
---

# Epics and Stories

## Epic 1 - Workspace Foundation and Skill Ingestion
Establish the folder-first workspace and make skill folders readable by the runtime.

### Story 1.1 - Create the workspace contract
As an AI engineer, I can use a predictable folder structure for skills, runs, datasets, logs, and artifacts.

Acceptance:
- The workspace contains `skills/`, `runs/`, `datasets/`, and `logs/`.
- The contract is documented in the repository and does not depend on a database.
- A human can inspect the folders and understand where inputs, outputs, and traces live.

### Story 1.2 - Ingest a skill package
As an AI engineer, I can point the system at a skill folder and have it recognize the skill package.

Acceptance:
- The system reads `SKILL.md` and any present metadata, examples, tests, and assets.
- Missing optional files do not block ingestion.
- The ingestion result records which files were found and which were absent.

### Story 1.3 - Version the skill snapshot
As an AI engineer, I can store or reference a specific skill revision so later runs are tied to the exact version used.

Acceptance:
- A skill version ID is recorded for every run.
- Two versions of the same skill can coexist without overwriting history.
- The run record can point back to the exact version that executed.

## Epic 2 - Small-Model Runtime Execution
Run one skill with a model chosen from environment variables and record what happened.

### Story 2.1 - Resolve the runtime model from env
As an AI engineer, I can configure the runtime model from environment variables instead of code changes.

Acceptance:
- The runtime reads model selection from environment config.
- Changing the environment changes the runtime model used.
- The chosen model is written into `run.json`.

### Story 2.2 - Execute one skill run
As an AI engineer, I can run one skill against one task input through the Python runtime.

Acceptance:
- The runtime accepts a single skill and a single input case.
- The run reaches a terminal status even if it fails.
- The runtime produces a visible output artifact for the case.

### Story 2.3 - Capture a chronological trace
As an AI engineer, I can inspect turn-by-turn runtime behavior after the run finishes.

Acceptance:
- Each turn, tool action, or decision is appended to `trace.jsonl`.
- The trace preserves order.
- Failed runs still produce a trace.

## Epic 3 - Evaluation and Feedback
Judge the run and turn the judgment into actionable improvement guidance.

### Story 3.1 - Evaluate the run with checks
As an AI engineer, I can score a run using explicit tests or checks.

Acceptance:
- The system writes `eval.json`.
- The evaluation includes pass/fail or structured verdicts.
- The evaluation can report correctness, constraint adherence, efficiency, and trace quality.

### Story 3.2 - Surface concrete issues
As an AI engineer, I can see what was wrong with the run without reading the full trace manually.

Acceptance:
- The eval output names specific defects such as missing steps, extra steps, or wrong output.
- The output points to evidence in the trace or run artifacts.
- Generic advice alone is not accepted as a valid evaluation.

### Story 3.3 - Generate feedback for the next revision
As an AI engineer, I can hand the run evidence to a frontier model and get feedback that tells me how to rewrite the skill.

Acceptance:
- The system writes `feedback.json`.
- Feedback identifies concrete changes for the next skill version.
- Feedback can be regenerated from the persisted run evidence.

## Epic 4 - Revision and Comparison Loop
Use the feedback to revise the skill and compare the old and new versions.

### Story 4.1 - Produce a revised skill candidate
As an AI engineer, I can generate or update a skill version from feedback and prior run evidence.

Acceptance:
- The revised skill is stored as a new version rather than overwriting the old one.
- The revised skill can be run in the same workspace.
- The revision preserves the folder-based contract.

### Story 4.2 - Compare runs or versions
As an AI engineer, I can compare two runs or two skill versions to see whether the revision improved the outcome.

Acceptance:
- The comparison highlights at least one behavioral difference.
- The comparison can be produced from saved run files.
- Regressions are visible, not hidden.

### Story 4.3 - Complete the hero loop
As an AI engineer, I can complete the end-to-end loop from ingest to rerun in one demo.

Acceptance:
- One skill goes through ingest, run, trace capture, eval, feedback, revision, and rerun.
- The second run is attributable to the revised skill version.
- The artifact trail is enough for a human to audit the demo after the fact.

