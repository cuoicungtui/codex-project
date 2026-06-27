---
id: SPEC-skill-runtime-eval-loop
companions:
  - workspace-contract.md
sources: []
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability only - consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Skill Runtime Evaluation Loop

## Why

This product exists to remove the runtime dependency on frontier models for skill execution without losing quality, auditability, or iteration speed. The user is an AI engineer or developer who wants to author skills with a large model, run those skills with a smaller model configured from environment variables, and then use logs, traces, evals, and feedback to make the next version better. The problem matters now because frontier-authored skills can be verbose, underspecified, and overly reliant on hidden context, while small-model runtimes need a tighter contract to run reliably.

## Capabilities

- **CAP-1**
  - **intent:** The system can ingest a skill folder and expose its instructions, metadata, examples, tests, and assets as the input package for a run.
  - **success:** Given a valid skill folder, the system lists the expected files and can identify which are present or missing without manual reformatting.

- **CAP-2**
  - **intent:** The system can execute a selected skill through a Python runtime using a small model chosen from environment configuration.
  - **success:** A run starts and completes without hardcoded model selection, and the chosen model is recorded in the run record.

- **CAP-3**
  - **intent:** The system can persist each run as a replayable filesystem record with metadata, trace, outputs, logs, and artifacts.
  - **success:** Every run writes `run.json`, `trace.jsonl`, `eval.json`, `feedback.json`, and artifact files into a stable run folder.

- **CAP-4**
  - **intent:** The system can evaluate a run against checks or test cases and compare results across skill versions.
  - **success:** An evaluation produces structured scores or findings for correctness, constraint adherence, efficiency, and trace quality.

- **CAP-5**
  - **intent:** The system can turn a run's trace and evaluation into feedback that informs a revised skill version.
  - **success:** The next skill revision can be generated or updated from prior run evidence, and a second run can be compared against the first.

## Constraints

- The v1 workspace is filesystem-first and must not depend on a production database.
- The runtime model must be configurable from environment variables, not hardcoded in the skill runtime.
- The product must support multiple skill types without fixing the workflow to one domain such as code, docs, or review.
- Every run must emit detailed trace and artifact data even when the run fails.
- The v1 scope must stay demoable in a hackathon setting with one runtime and one end-to-end loop.

## Non-goals

- A production database-backed platform.
- Multi-user auth, permissions, or team collaboration.
- A large UI or dashboard suite.
- Advanced model routing across many providers.
- Large-scale benchmark orchestration across many skill families.
- Fine-tuning or model training.

## Success signal

In a single demo, a user can author or update one skill with a frontier model, run that skill with a small model from the environment, inspect the full run trace and evaluation, then produce feedback that leads to a better second run. The replayable folder structure is enough for a human or agent to audit what happened without needing a database or a custom UI.

## Assumptions

- The first release is a developer-facing hackathon product, so traceability is more important than polished UX.
- The evaluation loop can start with rule-based checks and human-readable feedback before any advanced scoring system.
- The runtime can call an external LLM provider as long as the model name and credentials come from environment configuration.

## Open Questions

- Which small-model providers must be supported in v1?
- What is the minimum required skill metadata schema beyond `SKILL.md`?
- Should the runtime capture raw prompts and tool calls by default, or only when a debug mode is enabled?
- What is the canonical success metric for a run when a skill has no explicit tests?
- Should versioning live in the filesystem tree, in git history, or in both?
