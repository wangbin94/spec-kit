---
description: Rehydrate project context and surface actionable next steps when starting a fresh agent session (works with or without Spec Kit artifacts).
scripts:
  sh: scripts/bash/check-prerequisites.sh --paths-only --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

Goal: Quickly rebuild the working context after opening a new session so the user can pick up where the last conversation ended. Command must gracefully handle repositories that do not use Spec Kit; when Spec Kit files are present, include them for richer context. Supports overrides like `context=my-app` or `feature=003-photo-albums`.

STRICTLY READ-ONLY: Do **not** modify any files. Summaries and recommendations live in the response only.

Execution steps:

1. Determine repository context:
   - Try running `{SCRIPT}` from the repository root to discover `REPO_ROOT` and `BRANCH`. If it fails, fall back to:
     * `REPO_ROOT` = `git rev-parse --show-toplevel` (if Git available) or the current working directory.
     * `BRANCH` = current Git branch or `"N/A"` when Git is not detected.
   - Record environment hints such as `SPECIFY_FEATURE`, `SPECIFY_CONTEXT`, or `SPECIFY_FEATURE_DIR` if set.

2. Resolve the active context label (`context_label`) by checking, in order:
   1. `context=<value>` or `feature=<value>` arguments extracted from `$ARGUMENTS`.
   2. `SPECIFY_FEATURE` / `SPECIFY_CONTEXT` environment variables.
   3. Current Git branch (excluding detached HEAD).
   4. Default to `"session"`.
   Normalize by lowercasing and replacing whitespace with hyphens. This label is used to select handoff logs and optional Spec Kit directories.

3. Build context catalogs:
   - Handoff files: look for `$REPO_ROOT/.specify/session/handoffs` and `$REPO_ROOT/.session/handoffs`; list `.md` files in each with their timestamps. Select the file matching `context_label` if present, and identify the latest entry headed by `## Handoff Summary - ...`.
   - Spec Kit artifacts (optional): if `$REPO_ROOT/specs` exists, gather directories and see whether one matches `context_label`. Record available files (`spec.md`, `plan.md`, `tasks.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/`). If none exist, skip gracefully.

4. Collect working state:
   - Capture `git status --short` (limit to top 10 entries) and `git log -1 --oneline` when Git is available.
   - For Spec Kit artifacts (when present):
     * Extract feature name, top functional requirements, and `[NEEDS CLARIFICATION]` markers from `spec.md`.
     * Pull key-value pairs from `## Technical Context`, `Structure Decision`, and outstanding gates in `plan.md`.
     * Parse `tasks.md` to compute total/completed/remaining tasks and list the next 3 unchecked items.
     * Summarize notable insights from `research.md`, `data-model.md`, `quickstart.md`, or `contracts/` (1–2 bullets each).
   - For general repositories (when Spec Kit artifacts absent), scan for helpful reference files such as `TODO.md`, `CHANGELOG.md`, or `docs/` summaries and include high-level reminders if detected.

5. Assemble the warm-up report with Markdown sections:
   - `### Session Snapshot`: include branch, context label, repository path, and quick counts (e.g., modified files).
   - `### Latest Handoff`: summarize the newest handoff entry (timestamp, key notes, next actions) or state that no handoff exists yet.
   - `### Work Status`: highlight git status, recent commit info, and—if available—task completion metrics.
   - `### Spec Kit Insights` (only when relevant): bullets from spec/plan/research/tasks with clarification markers.
   - `### Outstanding Clarifications`: consolidate unresolved questions from handoff notes or `[NEEDS CLARIFICATION]` markers; otherwise say "None".
   - `### Suggested Next Actions`: recommend up to 3 concrete follow-ups, incorporating `{ARGS}` hints when prioritizing. Reference commands (`/handoff`, `/clarify`, `/plan`, `/tasks`, `/implement`, etc.) or manual steps as appropriate.

6. Close by asking the user what they’d like to tackle next (e.g., "Ready to continue with task XYZ or adjust priorities?").

Context for prioritization: {ARGS}
