# Addendum

## Workspace and Data Model

The product is folder-first. The folder contract is intentionally stable so both humans and agents can inspect it without a database.

### Workspace Roots
- `skills/<skill_id>/`
- `runs/<skill_id>/<run_id>/`
- `datasets/<dataset_id>/`
- `logs/`

### Skill Package
- `skills/<skill_id>/skill.md`
- `skills/<skill_id>/metadata.json`
- `skills/<skill_id>/examples/`
- `skills/<skill_id>/tests/`
- `skills/<skill_id>/assets/`
- `skills/<skill_id>/versions/<version_id>/`

### Run Folder
- `runs/<skill_id>/<run_id>/run.json`
- `runs/<skill_id>/<run_id>/trace.jsonl`
- `runs/<skill_id>/<run_id>/eval.json`
- `runs/<skill_id>/<run_id>/feedback.json`
- `runs/<skill_id>/<run_id>/artifacts/`

### Required File Semantics
- `run.json` stores the skill version, model config, input, timestamps, and status.
- `trace.jsonl` stores one chronological event per line.
- `eval.json` stores checks, scores, or verdicts.
- `feedback.json` stores defect descriptions and next-step guidance.

### Runtime Lifecycle
1. Ingest a skill folder.
2. Resolve the runtime model from environment variables.
3. Execute one task or test case.
4. Append trace entries for each turn, tool action, and decision.
5. Persist outputs and artifacts in the run folder.
6. Evaluate the run.
7. Write feedback for the next skill revision.

## Hero Feature

The hero feature for the hackathon is the single-skill round trip: one skill, one input, one runtime run, one evaluation, one feedback pass, one revised run. If this loop works cleanly, the rest of the product can grow around it.

## Notes for Architecture

- The system should treat the workspace as the source of truth.
- The runtime should be able to run with no database and no UI.
- Artifact schemas should stay simple enough for an agent to read and rewrite them.

