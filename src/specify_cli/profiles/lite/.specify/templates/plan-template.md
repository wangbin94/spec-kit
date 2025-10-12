# Implementation Plan (Lite): [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]  
**Input**: Feature specification located at `/specs/[###-feature-name]/spec.md`

## Execution Flow (Lite)
```
1. Load the spec.md to capture the mission, core capabilities, and constraints.
2. Summarize outcomes and decisions directly in this document (no extra artifacts).
3. Record the technical snapshot: language, framework, storage, testing.
4. Outline implementation structure and the sequence of major steps.
5. List validation strategy and immediate risks or follow-ups.
6. Stop here – pass plan.md to /tasks next.
```

## Summary
- **Goal**: [1–2 sentences describing the outcome the feature delivers]
- **Users**: [Primary actors or personas]
- **Critical Behaviors**: [Key flows the feature must enable]
- **Non‑Negotiables**: [Performance, security, compliance items that cannot be skipped]

## Technical Snapshot
| Area | Decision | Notes |
|------|----------|-------|
| Language / Runtime | [e.g., Python 3.12] | |
| Primary Framework / Libraries | [e.g., FastAPI + SQLAlchemy] | |
| Storage / Data | [e.g., PostgreSQL, S3] | |
| Testing Approach | [e.g., pytest + contract tests] | |
| Deployment / Hosting | [e.g., Docker + Fly.io] | |

## Implementation Outline
- **System Shape**: [Describe the structure – monolith, client/server, service boundaries]
- **Key Components**:  
  - [Component 1] → [Responsibility / important files]  
  - [Component 2] → [Responsibility / important files]
- **Data Flow**: [One paragraph or bullet flow describing how data moves end-to-end]

## Work Breakdown (Lite)
| Phase | Objective | Key Files / Directories |
|-------|-----------|-------------------------|
| Setup | [Tooling, scaffolding, dependencies] | |
| Build | [Core feature work] | |
| Tests | [Primary validations to implement] | |
| Polish | [Docs, cleanup, operational follow-ups] | |

*Add or remove rows as needed. Keep entries short and refer to real file paths.*

## Validation Strategy
- **Automated Tests**: [Contract, integration, unit tests to write or extend]
- **Manual / Exploratory**: [Manual checklist or quickstart steps]
- **Metrics / Observability**: [Logging, monitoring, performance checks if needed]

## Risks & Follow-Ups
- **Open Questions**: [Outstanding clarifications that block work]
- **Dependencies**: [External teams, services, or approvals required]
- **Rollback Plan**: [What happens if we revert? Minimal is acceptable.]

## Status Checklist
- [ ] Summary captures desired outcomes and scope boundaries
- [ ] Technical snapshot finalized with chosen tools
- [ ] Work breakdown lists the minimal phases to ship
- [ ] Validation strategy covers tests needed to protect the change
- [ ] Risks and follow-ups logged (even if empty, confirm explicitly)

---

*Lite profile keeps artifacts lean. Keep bullets crisp, cite real files, and avoid creating additional documents unless absolutely necessary.*
