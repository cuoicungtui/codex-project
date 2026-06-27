---
title: Skill Runtime Evaluation Loop
created: 2026-06-27
updated: 2026-06-27
status: draft
---

# PRD: Skill Runtime Evaluation Loop
*Working title - confirm.*

## 0. Document Purpose
This PRD is for the PM, builder, and downstream architecture/story workflows. It defines a filesystem-first skill workspace that lets a frontier model author or revise a skill, lets a Python runtime execute that skill with a small model from environment config, and turns each run into logs, traces, evals, and feedback. The detailed workspace contract lives in `addendum.md` and the spec companion `workspace-contract.md`; this PRD focuses on the product shape, the MVP cut, and the acceptance bar.

## 1. Vision
The product is a skill workbench and runtime loop, not a generic agent platform. It exists because skills written by a large model are often too implicit for a smaller runtime model to execute reliably. The system makes the skill contract explicit, runs it with a configurable small model, records everything that happened, and uses that evidence to improve the next version.

The core promise is simple: write a skill once, run it many times with a smaller model, and know exactly why it failed or succeeded. The output should be auditable by a human and consumable by an agent without depending on a database or a heavyweight UI.

## 2. Target User

### 2.1 Jobs To Be Done
- Author a skill with a frontier model, then make it runnable by a smaller model.
- Inspect what the runtime actually did, not just the final answer.
- Compare skill revisions using concrete run evidence.
- Keep skill work organized in folders that agents can read directly.
- Build a demoable loop quickly, without platform engineering first.

### 2.2 Non-Users (v1)
- End consumers who only want to use a finished product.
- Teams that need multi-user permissions, shared workspaces, or enterprise governance on day one.
- Users who need a polished web app before trusting the workflow.

### 2.3 Key User Journeys
- **UJ-1. Maya closes the loop on one skill.**
  - **Persona + context:** Maya is an AI engineer who wants to prove that a frontier-authored skill can run on a smaller runtime model.
  - **Entry state:** She has a skill folder, a task input, and environment variables for the runtime model.
  - **Path:** She drops the skill into the workspace, runs one case, inspects the trace and eval, then asks the frontier model to revise the skill from the feedback.
  - **Climax:** She sees a second run improve on the issue that the first run exposed.
  - **Resolution:** The revised skill stays in versioned storage with a complete audit trail.

## 3. Glossary
- **Skill package** - A folder containing the skill contract and any supporting files the runtime needs.
- **Skill version** - A versioned snapshot of a skill package.
- **Run** - One execution of one skill against one input or test case.
- **Trace** - Chronological record of turns, tool actions, decisions, and outputs during a run.
- **Eval** - Structured judgment of a run against checks, tests, or scoring rules.
- **Feedback** - Actionable findings that explain how the skill should change next.
- **Workspace** - The folder tree that stores skills, runs, datasets, logs, and artifacts.
- **Artifact** - Any output file produced or preserved by the runtime during a run.

## 4. Constraints and Guardrails

### 4.1 Cross-cutting NFRs
- The system must be reproducible from the filesystem alone for any completed run.
- The runtime must always record enough detail to audit the behavior after the fact.
- The model choice must come from environment configuration, not from hardcoded runtime logic.
- The product must stay generic across skill types instead of hardcoding one domain workflow.

### 4.2 Safety and Containment
- The runtime must not write outside the workspace contract unless explicitly configured.
- The runtime must preserve failures, not hide them behind a successful wrapper output.
- Trace capture must be complete enough to explain missing steps, extra steps, and malformed outputs.

## 5. Features

### 5.1 Skill Ingestion and Versioning
**Description:** The system reads a skill folder, recognizes the skill contract, and prepares it for execution or revision. It treats the skill as a folder-based package rather than a database record. [ASSUMPTION: v1 accepts a single canonical skill folder layout and does not need a migration layer for legacy layouts.]

**Functional Requirements:**

#### FR-1: Ingest a skill package
The system can load a skill folder and surface the files that define the skill. Realizes UJ-1.

**Consequences (testable):**
- The system identifies at minimum `SKILL.md` and any available metadata, examples, tests, and assets.
- Missing optional files do not block ingestion.

#### FR-2: Preserve skill versions
The system can store or reference versioned skill snapshots so a run can be tied to an exact revision. Realizes UJ-1.

**Consequences (testable):**
- A run record names the skill version it executed.
- Two skill versions can be compared without overwriting history.

### 5.2 Runtime Execution
**Description:** The system executes one skill against one input using a Python runtime and a small model resolved from the environment. The runtime is the operational core of the product, so it must make the model, input, and execution state visible. [ASSUMPTION: v1 runs one task at a time, not a batch queue.]

**Functional Requirements:**

#### FR-3: Resolve the runtime model from environment
The system can select the runtime model from environment variables at execution time. Realizes UJ-1.

**Consequences (testable):**
- Changing the environment changes the model used without code changes.
- The selected model is written into the run record.

#### FR-4: Execute a skill with traceable turns
The system can run the skill and record the observable execution steps. Realizes UJ-1.

**Consequences (testable):**
- Each turn or tool action is appended to trace output in chronological order.
- Failed runs still produce a trace and a terminal status.

### 5.3 Run Storage, Trace, and Replay
**Description:** Every run is persisted in a folder so the human or agent can replay what happened later. This is the audit backbone of the product and the place where debugability lives. Realizes UJ-1.

**Functional Requirements:**

#### FR-5: Persist a complete run folder
The system can write the run metadata, trace, evaluation, feedback, and artifacts into the run workspace. Realizes UJ-1.

**Consequences (testable):**
- Every run writes `run.json`, `trace.jsonl`, `eval.json`, and `feedback.json`.
- Artifact files live under the run folder and are discoverable from the run record.

#### FR-6: Support audit and replay
The system can reconstruct what happened in a run from the saved files alone. Realizes UJ-1.

**Consequences (testable):**
- A reviewer can inspect a run without needing a database or hidden server state.
- The run record explains what input, model, and skill version were used.

### 5.4 Evaluation and Comparison
**Description:** The system evaluates each run against checks or test cases and can compare one skill version against another. The product should surface quality defects such as extra steps, missing steps, wrong output, and inefficient context usage. Realizes UJ-1.

**Functional Requirements:**

#### FR-7: Evaluate a run with checks or tests
The system can score or classify a run using explicit checks or test cases. Realizes UJ-1.

**Consequences (testable):**
- Eval output distinguishes pass/fail or equivalent structured outcomes.
- Eval output can include correctness, constraint adherence, efficiency, and trace quality.

#### FR-8: Compare runs or versions
The system can compare two runs, or two skill versions, and highlight regressions or improvements. Realizes UJ-1.

**Consequences (testable):**
- The comparison calls out at least one concrete difference in behavior or score.
- The comparison can be produced from the persisted run records.

### 5.5 Feedback and Revision Loop
**Description:** The system turns evaluation evidence into feedback that a frontier model can use to rewrite the skill. This is the improvement loop, and it is the main reason the product exists. Realizes UJ-1.

**Functional Requirements:**

#### FR-9: Generate actionable feedback
The system can summarize what was wrong with the run and what the next skill revision should change. Realizes UJ-1.

**Consequences (testable):**
- Feedback names concrete defects instead of generic advice.
- Feedback points to trace or eval evidence.

#### FR-10: Produce a revised skill candidate
The system can create or update a skill version from feedback and prior run evidence. Realizes UJ-1.

**Consequences (testable):**
- The revised skill can be run in the same workspace.
- A second run can be compared against the first run.

## 6. Non-Goals (Explicit)
- Production-scale orchestration or queue management.
- Multi-user permissions, collaboration, or auth.
- A polished web dashboard in v1.
- Fine-tuning or training the model.
- Hardcoding the product around one skill type.
- Database-first storage.

## 7. MVP Scope

### 7.1 In Scope
- One filesystem workspace with clear folders for skills, runs, datasets, logs, and artifacts.
- One Python runtime.
- One small model resolved from environment variables.
- One canonical skill package layout.
- One end-to-end hero loop: ingest skill -> run skill -> capture trace -> evaluate -> generate feedback -> revise skill -> run again.
- One sample skill that proves the loop works.
- Text or JSON artifacts that a human can inspect directly.

### 7.2 Out of Scope for MVP
- Multi-user accounts, access control, or team features.
- A broad UI, analytics dashboard, or visual run explorer.
- More than one runtime backend.
- Model routing, fallback policies, or provider abstraction layers.
- Benchmarking across many unrelated skill families.
- Fine-tuning, preference learning, or training data pipelines.

## 8. Success Metrics

**Primary**
- **SM-1:** A demo completes the full loop for one skill and produces `run.json`, `trace.jsonl`, `eval.json`, and `feedback.json` every time. Validates FR-1 through FR-10.
- **SM-2:** A reviewer can explain a run outcome from the filesystem alone without hidden state. Validates FR-5 and FR-6.

**Secondary**
- **SM-3:** A revised skill version improves or fixes at least one issue surfaced by the first run. Validates FR-8, FR-9, and FR-10.

**Counter-metrics (do not optimize)**
- **SM-C1:** Trace detail should not be reduced just to save storage or simplify implementation. Completeness matters more than minimal files.

## 9. Open Questions
- What exact environment variables define the runtime model configuration?
- Which small-model provider(s) must v1 support?
- What is the minimal required skill metadata schema beyond `SKILL.md`?
- Should raw prompts and tool calls be captured by default or behind a debug flag?
- What is the canonical success signal for a run when a skill has no tests?
- Should version history live only in folders, only in git, or in both?

## 10. Assumptions Index
- [ASSUMPTION] v1 is a developer-facing hackathon product, so traceability matters more than polished UX.
- [ASSUMPTION] v1 evaluates one skill at a time, not batch workloads.
- [ASSUMPTION] The runtime can call an external model provider as long as credentials and model name come from environment config.
- [ASSUMPTION] Rule-based checks plus human-readable feedback are enough for the first evaluation loop.

