# [PROJECT_NAME] Constitution

<!--
Naming Guide

Project title:
- Prefer: "<Product/Project Name> Constitution"
- Examples:
  - "Campus Portal Constitution"
  - "Order Management Constitution"
  - "BPA Workflow Platform Constitution"

Core Principle names:
- Use short noun phrases that describe enduring project values.
- Prefer names such as:
  - Security by Default
  - Architecture Integrity
  - Testable Behaviour
  - Observability
  - Simplicity
  - API-First
  - Data Integrity
- Avoid vague names such as:
  - Good Code
  - Best Practice
  - Quality
  - Rule 1

Rule IDs:
- Use a stable CATEGORY-NNN format.
- Recommended categories:
  - SEC-NNN   Security
  - DATA-NNN  Data integrity / privacy
  - ARCH-NNN  Architecture
  - API-NNN   API / contracts
  - TEST-NNN  Testing
  - ENG-NNN   Engineering standards
  - PERF-NNN  Performance
  - OPS-NNN   Operations / deployment
  - OBS-NNN   Observability
  - DOC-NNN   Documentation
  - AI-NNN    AI agent behaviour

Rule names:
- Use a concise noun phrase after the rule ID.
- Examples:
  - SEC-001: Secrets Management
  - DATA-001: Sensitive Data Handling
  - ARCH-001: Dependency Direction
  - API-001: Contract-First Changes
  - TEST-001: Business Logic Tests
  - ENG-001: Dependency Management
  - PERF-001: API Latency Budget
  - OPS-001: Production Deployment
  - AI-001: Constitution Self-Check

Numbering:
- Keep rule IDs stable after creation.
- Do not renumber existing rules just to make the sequence prettier.
- New rules should receive the next available number in their category.
-->

<!-- Example: Order Management Platform Constitution, Campus Portal Constitution, etc. -->

## Core Principles

### I. [PRINCIPLE_1_NAME]

[PRINCIPLE_1_DESCRIPTION]

**Rationale**: [PRINCIPLE_1_RATIONALE]

<!--
Example:
### I. Security by Default

Security MUST be considered in every specification, plan, task, and implementation.
Secrets MUST NOT be committed to source control. User input MUST be validated before
being processed or persisted.

Rationale: Security defects are expensive to fix late and may compromise user or
business data.
-->

### II. [PRINCIPLE_2_NAME]

[PRINCIPLE_2_DESCRIPTION]

**Rationale**: [PRINCIPLE_2_RATIONALE]

<!--
Example:
### II. Architecture Integrity

Dependencies MUST follow the approved architectural direction.
Presentation MUST NOT access persistence directly. Cross-module communication MUST
use approved contracts or interfaces.

Rationale: Explicit boundaries reduce coupling and prevent architecture drift.
-->

### III. [PRINCIPLE_3_NAME]

[PRINCIPLE_3_DESCRIPTION]

**Rationale**: [PRINCIPLE_3_RATIONALE]

<!--
Example:
### III. Testable Behaviour

Business-critical behaviour MUST be verifiable through automated tests.
Tests SHOULD validate observable behaviour rather than implementation details.

Rationale: Behaviour-focused tests make refactoring safer and provide executable
evidence that requirements are satisfied.
-->

### IV. [PRINCIPLE_4_NAME]

[PRINCIPLE_4_DESCRIPTION]

**Rationale**: [PRINCIPLE_4_RATIONALE]

<!--
Example:
### IV. Observability

Production-relevant operations MUST emit structured, actionable logs.
Errors MUST include enough context for diagnosis without exposing secrets or
sensitive information.

Rationale: A system that cannot be observed cannot be reliably operated or debugged.
-->

### V. [PRINCIPLE_5_NAME]

[PRINCIPLE_5_DESCRIPTION]

**Rationale**: [PRINCIPLE_5_RATIONALE]

<!--
Example:
### V. Simplicity

Implementations MUST prefer the simplest design that satisfies the approved
requirements. New abstractions, dependencies, and infrastructure MUST be justified.

Rationale: Unnecessary complexity increases maintenance cost and makes AI-generated
changes harder to review safely.
-->

<!--
Other possible principles:
- API-First
- Data Integrity
- Privacy by Design
- Strict TDD
- Backward Compatibility
- Accessibility
- Domain-Driven Boundaries

Only keep principles that are genuinely project-wide and important enough to govern
all specifications, plans, and implementation work.
-->

## Additional Constraints

### Layer 1 — Hard Rules

[HARD_RULES]

<!--
Purpose:
Rules that MUST NEVER be violated during normal project work.

Suggested rule format:

#### SEC-001: Secrets Management

THE system MUST NOT store API keys, passwords, tokens, private keys, or other
credentials in source code, committed configuration, logs, or test fixtures.

Verification:
- Secret scanning in CI
- Code review
- Environment-variable/configuration inspection

Naming examples:
- SEC-001: Secrets Management
- SEC-002: Password Protection
- SEC-003: Input Validation
- DATA-001: Sensitive Data Handling
- OPS-001: Destructive Production Operations

Example rules:
- SEC-001: No hardcoded secrets
- SEC-002: Passwords MUST be securely hashed
- SEC-003: Input MUST be validated and sanitized
- DATA-001: Sensitive data MUST NOT be exposed in logs
- OPS-001: Production data MUST NOT be destructively modified without an approved
  operational procedure
-->

Rules in this layer are non-negotiable. Specifications, plans, tasks,
implementation, reviews, and AI-generated output MUST NOT violate them.

If a Layer 1 violation is detected, work MUST stop and the violation MUST
be corrected before progress continues. A Layer 1 rule can only change
through a Constitution amendment; it cannot be bypassed by an ad-hoc
exception.

### Layer 2 — Architectural Constraints

[ARCHITECTURAL_CONSTRAINTS]

<!--
Purpose:
Rules that preserve architectural boundaries and approved technical direction.

Suggested rule format:

#### ARCH-001: Dependency Direction

Presentation MAY depend on Application.
Application MAY depend on Domain.
Domain MUST NOT depend on Infrastructure or Presentation.

Verification:
- Dependency tests
- Architecture tests
- Static analysis
- Code review

Naming examples:
- ARCH-001: Dependency Direction
- ARCH-002: Layer Boundaries
- ARCH-003: Module Communication
- ARCH-004: External Integration Isolation
- ARCH-005: Schema Migration Policy

Example rules:
- ARCH-001: Controller MUST NOT access the database directly
- ARCH-002: Application layer MUST NOT depend on Infrastructure
- ARCH-003: Cross-module communication MUST use defined contracts
- ARCH-004: External integrations MUST be isolated behind adapters/interfaces
- ARCH-005: Database schema changes require an approved migration
-->

Rules in this layer define approved system boundaries, architectural
patterns, integration constraints, data-flow constraints, and technology
boundaries.

A deviation from Layer 2 MUST be explicitly identified before
implementation continues. The deviation MUST include its rationale,
impact, risks, and approval from an authorized human reviewer. Silent
architectural exceptions are prohibited.

### Layer 3 — Engineering Standards

[ENGINEERING_STANDARDS]

<!--
Purpose:
Rules that define expected engineering quality and consistency.

Suggested rule format:

#### TEST-001: Business Logic Tests

Business-critical application and domain logic MUST have automated tests covering
the primary success path and relevant failure/edge cases.

Verification:
- Test suite
- Coverage report where applicable
- Pull request review

Naming examples:
- TEST-001: Business Logic Tests
- TEST-002: API Contract Tests
- ENG-001: Structured Logging
- ENG-002: Public Interface Documentation
- ENG-003: Dependency Management
- PERF-001: Performance Budget

Example rules:
- TEST-001: Business logic MUST have unit tests
- TEST-002: Public APIs MUST have integration/contract tests
- ENG-001: Structured logging MUST be used for operational events
- ENG-002: Public interfaces MUST be documented
- ENG-003: New dependencies MUST be justified and version-pinned
- PERF-001: Critical operations MUST satisfy defined performance budgets
-->

Rules in this layer define engineering quality expectations such as
testing, documentation, observability, code quality, dependency
management, performance, and delivery standards.

A Layer 3 deviation MUST be reported and justified. The project MAY
continue with a documented deviation only when it does not violate Layer
1 or an unapproved Layer 2 constraint.

## Development Workflow & Quality Gates

### Constitution Compliance

Every specification, implementation plan, task set, code change, and
review MUST be evaluated against the applicable Constitution rules.

Constitution checks MUST use the following enforcement semantics:

- Layer 1 violation: BLOCK until fixed.
- Layer 2 deviation: BLOCK until explicitly approved and documented.
- Layer 3 deviation: REPORT and justify; continue only when allowed by the
  applicable project quality gate.

<!--
Example:

Before approving a plan:
- Verify no task conflicts with Layer 1.
- Identify Layer 2 exceptions before implementation.
- Record Layer 3 deviations and mitigations.

Before merge:
- Re-run automated checks.
- Confirm approved architectural exceptions are documented.
- Confirm unresolved Layer 1 violations = 0.
-->

### AI Agent Self-Check Protocol

Before submitting implementation output, an AI agent MUST evaluate all
applicable Constitution rules against the work it produced.

The agent MUST:

1. Check every applicable Layer 1 rule. If a violation exists, fix it
   before submitting output.
2. Check every applicable Layer 2 rule. If a deviation exists, stop,
   report the conflicting rule, and request explicit human approval.
3. Check every applicable Layer 3 rule. If a deviation exists, report the
   deviation, rationale, impact, and proposed mitigation.
4. Never silently ignore or downgrade a Constitution violation.
5. Report the result of the self-check in a concise compliance summary.

[PROJECT_SPECIFIC_AGENT_RULES]

<!--
Naming examples for AI-specific rules:
- AI-001: Required Context Loading
- AI-002: Schema Change Approval
- AI-003: Dependency Addition Approval
- AI-004: Protected Branch Safety
- AI-005: Ambiguity Reporting

Example project-specific AI rules:
- AI MUST read the approved spec and implementation plan before editing code.
- AI MUST NOT modify database schema without explicit human confirmation.
- AI MUST NOT add a new package/dependency without approval.
- AI MUST NOT push directly to protected branches.
- AI MUST report assumptions when requirements are ambiguous.

Example self-check output:

=== CONSTITUTION SELF-CHECK ===
Layer 1: PASS
- SEC-001: No hardcoded secrets detected
- SEC-003: Input validation present

Layer 2: PASS
- ARCH-001: Dependency direction preserved

Layer 3: DEVIATION
- TEST-001: One edge case is not yet automated
- Rationale: external sandbox unavailable
- Mitigation: manual validation documented; automated test tracked as follow-up
================================
-->

### Quality Gates

[QUALITY_GATES]

<!--
Example:
- All required tests MUST pass.
- Lint/static-analysis errors MUST be zero.
- Secret/security scan MUST pass.
- API contract MUST be updated when an API changes.
- Database migration MUST be reviewed before merge.
- Constitution Layer 1 compliance MUST be blocking in CI where automation is
  practical.
- Pull requests require at least one reviewer approval.
-->

Quality gates SHOULD be automated where practical through tests, linters,
static analysis, security scanning, contract validation, CI checks, or
other reproducible mechanisms.

A passing tool result does not override a Constitution violation.

## Governance

This Constitution is the highest-level project governance artifact for
software development practices covered by this document.

When this Constitution conflicts with a feature specification,
implementation plan, task list, prompt, local convention, or ad-hoc
development practice, the Constitution takes precedence. The conflicting
artifact MUST be corrected or an allowed exception MUST be documented
according to the applicable enforcement layer.

Amendments MUST be explicit. Every amendment MUST:

1. State the motivation for the change.
2. Identify affected principles, constraints, workflows, and dependent
   artifacts.
3. Record any required migration or follow-up work.
4. Receive approval from the project's authorized maintainers or owners.
5. Update the Constitution version and amendment date.

Constitution versioning follows Semantic Versioning:

- MAJOR: backward-incompatible governance changes, or removal/redefinition
  of an existing principle.
- MINOR: a new principle or section, or materially expanded governance.
- PATCH: clarification, wording, typo, or other non-semantic refinement.

Compliance with this Constitution MUST be reviewed during planning and
code review. Unjustified violations MUST block approval when the
applicable enforcement layer requires blocking.

[GOVERNANCE_RULES]

<!--
Example governance rules:
- Constitution amendments require approval from the Tech Lead and at least one
  additional maintainer.
- Architecture exceptions MUST be recorded in docs/adr/ or an RFC directory.
- Temporary Layer 3 deviations MUST include an owner and remediation deadline.
- Every pull request MUST confirm Constitution compliance.
- The Constitution MUST be reviewed at major architectural milestones.

Example version changes:
- 1.0.0 -> 1.0.1: clarify wording without changing meaning
- 1.0.0 -> 1.1.0: add a new engineering principle
- 1.2.0 -> 2.0.0: remove or redefine a fundamental governance rule
-->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
