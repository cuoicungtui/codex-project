---
baseline_commit: 22af596298611882b557d7b7d2ea9aa83f496e46
---

# Story 1.1: Create the workspace contract

Status: review

## Story

As an AI engineer,
I want a predictable folder structure for skills, runs, datasets, logs, and artifacts,
so that both humans and agents can inspect, run, and audit the system without a database.

## Acceptance Criteria

1. The workspace contains `skills/`, `runs/`, `datasets/`, and `logs/`.
2. The contract is documented in the repository and does not depend on a database.
3. A human can inspect the folders and understand where inputs, outputs, and traces live.

## Tasks / Subtasks

- [x] Create the filesystem bootstrap for the v1 workspace (AC: 1)
  - [x] Add code or a script entry point that creates `skills/`, `runs/`, `datasets/`, and `logs/` under a configured workspace root.
  - [x] Ensure bootstrap is idempotent so re-running it does not corrupt an existing workspace.
- [x] Define the workspace contract in machine-readable and human-readable form (AC: 2, 3)
  - [x] Introduce a domain model or schema object that names the canonical roots and expected subpaths.
  - [x] Keep the contract aligned with the product docs so later runtime stages use the same path rules.
- [x] Add verification for the contract bootstrap (AC: 1, 3)
  - [x] Add tests that assert the required directories exist after bootstrap.
  - [x] Add tests that assert path resolution remains inside the workspace root.

## Dev Notes

- This story is the bootstrap for all later work. Do not treat folder creation as an incidental utility; the workspace contract is a core domain invariant.
- The architecture spine fixes the paradigm as `filesystem-first ports-and-adapters pipeline`. The workspace layout is therefore a first-class interface, not an implementation detail.
- Keep the first implementation local and simple. Do not add a database abstraction, background worker, or remote storage hook here.

### Technical Requirements

- Workspace artifacts are the system of record. Every later stage depends on these directories existing and staying stable.
- File I/O must be workspace-bounded by policy. Path helpers created in this story should make path escape hard or impossible by default.
- Durable artifact formats later will be JSON/JSONL with explicit schemas. This story does not need to generate those files yet, but it must not choose a directory layout that conflicts with them.

### Architecture Compliance

- Follow AD-1: workspace artifacts are the system of record.
- Follow AD-6: artifact locations and names must be stable and parseable by small agents.
- Follow AD-7: write paths must resolve under configured workspace roots only.

### File Structure Requirements

- Target application structure from the architecture seed:
  - `src/skill_runtime/domain/`
  - `src/skill_runtime/application/`
  - `src/skill_runtime/ports/`
  - `src/skill_runtime/adapters/`
  - `src/skill_runtime/cli/`
  - `tests/unit/`
- This story should at minimum establish the workspace-facing pieces, likely in `domain/skills.py`, `domain/runs.py`, and a filesystem adapter or bootstrap module.
- If the repo still has no application code, create only the minimum skeleton needed for the workspace contract and its tests. Do not scaffold unrelated runtime features yet.

### Testing Requirements

- Add unit tests for workspace bootstrap and path resolution.
- Test re-running bootstrap on an existing workspace.
- Test that invalid or escaping paths are rejected.

### Project Structure Notes

- Current repository state is documentation-first. There is no existing runtime code to preserve, so this story should establish the initial source tree in a way that matches the architecture spine.
- Keep naming in `snake_case` for Python modules and JSON field names, per architecture conventions.

### References

- [SPEC.md](/F:/codex-project/_bmad-output/specs/spec-skill-runtime-eval-loop/SPEC.md)
- [workspace-contract.md](/F:/codex-project/_bmad-output/specs/spec-skill-runtime-eval-loop/workspace-contract.md)
- [prd.md](/F:/codex-project/_bmad-output/planning-artifacts/prd-skill-runtime-eval-loop/prd.md)
- [epics-and-stories.md](/F:/codex-project/_bmad-output/planning-artifacts/prd-skill-runtime-eval-loop/epics-and-stories.md)
- [ARCHITECTURE-SPINE.md](/F:/codex-project/_bmad-output/planning-artifacts/architecture/architecture-skill-runtime-eval-loop-2026-06-27/ARCHITECTURE-SPINE.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Sprint status updated for Story 1.1 in `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Implemented the workspace bootstrap, contract model, CLI entry point, and root-bounded path resolution.
- Validated with unit tests and a CLI smoke run against a temporary workspace.

### Completion Notes List

- Workspace bootstrap now creates `skills/`, `runs/`, `datasets/`, and `logs/` under a configured workspace root.
- `WorkspaceContract` centralizes the canonical workspace roots and rejects path escapes outside the workspace root.
- Added a `bootstrap-workspace` CLI and unit tests covering bootstrap, idempotency, and path resolution.
- Verified with `python -m unittest discover -s tests` and a CLI smoke run.

### File List

- `_bmad-output/implementation-artifacts/1-1-create-the-workspace-contract.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `pyproject.toml`
- `src/skill_runtime/__init__.py`
- `src/skill_runtime/application/__init__.py`
- `src/skill_runtime/application/bootstrap_workspace.py`
- `src/skill_runtime/adapters/__init__.py`
- `src/skill_runtime/adapters/filesystem_workspace.py`
- `src/skill_runtime/cli/__init__.py`
- `src/skill_runtime/cli/main.py`
- `src/skill_runtime/domain/__init__.py`
- `src/skill_runtime/domain/workspace.py`
- `src/skill_runtime/ports/__init__.py`
- `tests/__init__.py`
- `tests/unit/__init__.py`
- `tests/unit/test_workspace_contract.py`

## Change Log

- 2026-06-27: Implemented the workspace contract, bootstrap CLI, and validation tests for Story 1.1.
