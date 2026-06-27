# Workspace Contract

## Workspace Roots

- `skills/<skill_id>/`
- `runs/<skill_id>/<run_id>/`
- `datasets/<dataset_id>/`
- `logs/`

## Skill Package

- `skills/<skill_id>/skill.md`
- `skills/<skill_id>/metadata.json`
- `skills/<skill_id>/examples/`
- `skills/<skill_id>/tests/`
- `skills/<skill_id>/assets/`
- `skills/<skill_id>/versions/<version_id>/`

## Run Record

- `runs/<skill_id>/<run_id>/run.json`
- `runs/<skill_id>/<run_id>/trace.jsonl`
- `runs/<skill_id>/<run_id>/eval.json`
- `runs/<skill_id>/<run_id>/feedback.json`
- `runs/<skill_id>/<run_id>/artifacts/`

## Runtime Flow

1. Ingest a skill folder.
2. Resolve the runtime model from environment variables.
3. Execute one task or test case against the skill.
4. Append trace entries for each turn, tool action, and decision.
5. Persist outputs and artifacts in the run folder.
6. Evaluate the run.
7. Write feedback for the next skill revision.

## Required Records

- `run.json` must identify the skill version, model config, inputs, timestamps, and status.
- `trace.jsonl` must preserve chronological execution detail.
- `eval.json` must store the scoring or checks used to judge the run.
- `feedback.json` must name the failure modes or improvement targets.

