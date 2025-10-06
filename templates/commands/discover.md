---
description: Explore a new idea, capture structured context, and decide readiness for specification.
scripts:
  sh: scripts/bash/discover.sh --json "{ARGS}"
  ps: scripts/powershell/discover.ps1 -Json "{ARGS}"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

Goal: Collaboratively flesh out the idea, gather essential context, and populate the backlog intake file so the team can decide whether to proceed to `/specify`.

Execution steps:

1. Run `{SCRIPT}` once from the repository root. Parse the JSON for:
   - `IDEA_ID`
   - `IDEA_DIR`
   - `INTAKE_FILE`
   Confirm the file path exists before continuing.

2. Load the intake template structure (`INTAKE_FILE`). Use it as the canonical outline—do not reorder sections.

3. Facilitate up to **five** high-impact discovery questions to clarify the idea. Focus on:
   - Problem / opportunity definition
   - Target users and success metrics
   - Scope boundaries and constraints
   - Risks, unknowns, and required research
   - Desired next step (proceed, research, or drop)
   Ask one question at a time, capture succinct answers, and stop early if sufficient clarity emerges.

4. Populate `INTAKE_FILE` in place after each accepted answer:
   - Fill bullet lists with concrete statements derived from the conversation
   - Capture risks / open questions explicitly
   - Note recommended follow-ups or owners in the Next Steps section
   - Prepend the idea metadata (`Idea ID`, working title inferred from conversation) under Overview
   Save after each update to avoid context loss.

5. Summarise the session back to the user:
   - Idea ID and intake file path
   - Key takeaways (problem, goals, constraints, next step)
   - Recommendation: proceed to `/specify`, run more discovery later, or archive
   - Suggested follow-up commands (`/specify`, `/portfolio --json`, etc.)

Behavior rules:
- Never create multiple intake files per idea—re-run the script only once per `/discover` invocation
- Avoid speculative implementation details; stay at problem/opportunity level
- Keep tone collaborative and inquisitive; acknowledge when further research is needed
- If the idea is not viable, document why under Risks / Next Steps
- When users already provided structured answers, skip unnecessary questioning and commit the details directly
