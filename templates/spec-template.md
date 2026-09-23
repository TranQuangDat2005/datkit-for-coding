# Detailed Spec: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`

**Version**: `[x.x.x]`

**Owner**: `[Author Name]`

**Status**: `Draft | Review | Approved | Implemented`

**Created**: `[YYYY-MM-DD]`

**Last Updated**: `[YYYY-MM-DD]`

**Input**: User description: "$ARGUMENTS"

<!--

============================================================

LEVEL 2 — DETAILED SPECIFICATION

============================================================

This document is a Detailed Specification.

Use this level for feature/module-level work with moderate

complexity, business logic, and manageable risk.

The specification defines:

- WHAT the system must do

- UNDER WHICH CONDITIONS it must do it

- HOW success is verified

- WHAT is explicitly outside the feature boundary

The specification SHOULD provide enough information for an

AI agent to implement the feature without inventing business

rules or silently making important assumptions.

Do NOT turn this document into a Formal Specification.

Detailed Spec should remain proportional to the feature complexity.

============================================================

EARS REFERENCE

============================================================

Functional requirements SHOULD use EARS notation.

1. UBIQUITOUS

*   THE <system> SHALL <action>.*

*   Use when the behavior is always applicable.*

*   Example:*

*   THE system SHALL store timestamps in UTC.*

2. EVENT-DRIVEN

*   WHEN <event>, THE <system> SHALL <action>.*

*   Use when a specific event triggers the behavior.*

*   Example:*

*   WHEN the user submits a valid meal plan,*

*   THE system SHALL save the meal plan.*

3. STATE-DRIVEN

*   WHILE <state>, THE <system> SHALL <action>.*

*   Use when behavior applies while a state exists.*

*   Example:*

*   WHILE the order status is "processing",*

*   THE system SHALL prevent address modification.*

4. OPTIONAL

*   WHERE <feature/condition> IS ENABLED,*

*   THE <system> SHALL <action>.*

*   Use when behavior depends on a feature,*

*   configuration, or optional condition.*

*   Example:*

*   WHERE email notifications are enabled,*

*   THE system SHALL send a confirmation email.*

5. UNWANTED / ERROR

*   WHERE <error/unwanted condition>,*

*   THE <system> SHALL <response>.*

*   Use for invalid input, error conditions,*

*   failure modes, and important edge cases.*

*   Example:*

*   WHERE the submitted rating is outside the range 1–5,*

*   THE system SHALL reject the request with error code INVALID_RATING.*

Requirement keywords:

- SHALL = mandatory

- SHALL NOT = mandatory prohibition

- SHOULD = recommendation

- SHOULD NOT = recommended prohibition

- MAY = optional behavior

Avoid vague requirements such as:

- "The system should be fast."

- "The system should handle errors appropriately."

- "The interface should be user-friendly."

- "The algorithm should be optimized."

Replace vague wording with observable or measurable behavior.

============================================================

ANTI-PATTERN REFERENCE

============================================================

The specification MUST avoid these common anti-patterns.

1. MAGIC REQUIREMENT

Avoid vague adjectives without measurable criteria.

Bad:

"The system must respond quickly."

Better:

"P95 response time SHALL be below 500 ms."

2. CONTRADICTION

Do not leave conflicting requirements unresolved.

Bad:

"Session expires after 5 minutes."

"Users stay logged in for 30 days."

If requirements conflict and the correct behavior cannot be

determined, mark the requirement:

[NEEDS CLARIFICATION]

3. CONTEXT GAP

Do not invent technology, libraries, conventions,

database structures, or existing system behavior when

the required context has not been provided.

Use the existing project conventions when they are known.

4. IMPLICIT ASSUMPTION

Do not silently assume undocumented business rules.

If a behavior affects:

- business logic

- authorization

- security

- data integrity

- user-visible behavior

it SHOULD be explicitly specified.

5. MOVING TARGET

Do not silently change the specification while implementation

is in progress.

Important changes SHOULD update the version and status.

============================================================

AI IMPLEMENTATION RULES

============================================================

The AI MUST:

- implement all SHALL requirements;

- respect SHALL NOT restrictions;

- follow existing project conventions;

- use this specification as the source of truth for the feature;

- identify important ambiguity instead of silently guessing;

- respect the Out of Scope section;

- keep implementation proportional to Detailed Spec complexity.

The AI MUST NOT:

- invent new business rules;

- add unrequested features;

- expand the feature scope because a related feature seems useful;

- introduce unnecessary dependencies;

- modify unrelated modules;

- redesign existing architecture without explicit requirement;

- change existing contracts unless explicitly specified;

- turn this specification into a Formal Specification unless requested.

When information is missing but does not materially affect

implementation, use the existing project convention.

When missing information materially affects correctness,

security, data integrity, or user behavior, mark:

[NEEDS CLARIFICATION: <question>]

============================================================

SPECIFICATION FORMAT RULES

============================================================

The generated specification MUST NOT use Markdown pipe tables

or ASCII/grid tables.

Use semantic headings, bullets, numbered lists, and compact

per-item blocks instead. Keep IDs such as FR-001, BR-001,

VR-001, DR-001, ERR-001, and AC-001 so requirements remain

easy to reference and test.

Prefer the minimum structure needed to remove ambiguity. Do not

expand a simple feature merely to fill this template.

============================================================

-->

---

## 1. Context & Goal

<!--

Explain WHY this feature exists and WHAT outcome it should achieve.

Do not describe implementation details unless they are necessary

to understand an existing constraint or system dependency.

-->

### Problem

[Describe the concrete business or user problem.]

### Goal

[Describe what this feature should achieve.]

### User Intent

> As a `[user type]`, I want to `[action]`, so that `[benefit/outcome]`.

### Context

[Describe the relevant domain and existing system context.]

### Existing System Context

* Related module/service: `[module/service]`

* Existing functionality: `[related feature]`

* Existing constraints: `[relevant constraints]`

* Dependencies: `[existing dependency, if any]`

---

## 2. Actors

<!--

Identify who or what interacts with this feature.

Actors may include:

- End users

- Admins

- Staff

- External services

- Scheduled/background processes

- Internal system components

Define permissions when they matter to the feature.

Represent each actor as a short heading/bullet block; do not use tables.

-->

### Actor: `[Actor 1]`

* Description: `[Description]`

* Allowed actions: `[Actions]`

### Actor: `[Actor 2]`

* Description: `[Description]`

* Allowed actions: `[Actions]`

### Actor: `[System / Service]`

* Description: `[Description]`

* Allowed actions: `[Actions]`

### Authorization Rules

* `[Actor]` SHALL be allowed to `[action]`.

* `[Actor]` SHALL NOT be allowed to `[action]`.

* `[Condition]` SHALL be satisfied before `[action]`.

---

## 3. Functional Requirements (EARS)

<!--

Define the behavior the system must provide.

Each important requirement SHOULD:

- have a unique ID;

- use EARS when applicable;

- be testable;

- describe observable behavior;

- avoid implementation details unless required.

Do not leave important business rules implicit.

Write validation rules as ID-based bullet blocks; do not use tables.

-->

### FR-001 — [Requirement Name]

**Type**: `Ubiquitous | Event-driven | State-driven | Optional | Unwanted`

`[EARS requirement]`

### FR-002 — [Requirement Name]

**Type**: `[EARS type]`

`[EARS requirement]`

### FR-003 — [Requirement Name]

**Type**: `[EARS type]`

`[EARS requirement]`

### Business Rules

* **BR-001**: `[Business rule]`

* **BR-002**: `[Business rule]`

* **BR-003**: `[Business rule]`

### Validation Rules

* **VR-001 — `[field]`**
  * Rule: `[validation rule]`
  * Expected result: `[expected behavior]`

* **VR-002 — `[field]`**
  * Rule: `[validation rule]`
  * Expected result: `[expected behavior]`

---

## 4. Non-functional Requirements

<!--

Define quality constraints relevant to this feature.

Use measurable criteria whenever possible.

Only include applicable categories.

Do not create requirements merely to fill the template.

-->

### Performance

* **NFR-001**: `[Measurable performance requirement]`

### Security

* **NFR-002**: `[Security requirement, if applicable]`

### Reliability

* **NFR-003**: `[Reliability requirement, if applicable]`

### Availability / Scalability

* **NFR-004**: `[Availability or scalability requirement, if applicable]`

### Other Constraints

* **NFR-005**: `[Logging / accessibility / compatibility / etc.]`

---

## 5. Data Model

<!--
Describe only data relevant to this feature.
Keep this section concise.

Follow the existing schema and naming conventions.
Do not invent data that the feature does not require.

If no data model is relevant, write: None.
-->

`[entity]`:
`[relevant fields and important constraints]`

Example:

`reviews`:
`id, buyer_id, product_id, rating(1-5),
comment(text), status, created_at`

## 6. Error Handling

<!--

Define important failure modes explicitly.

For each important error, describe:

- what causes it;

- what the system does;

- what the user/system receives;

- retry/recovery behavior when relevant.

Do not use vague statements such as:

"Handle errors appropriately."

Write each important error as an ERR-ID block; do not use tables.

-->

### ERR-001 — `[Error Name]`

* Condition: `[condition]`
* System response: `[response]`
* Retry / recovery: `[behavior]`

### ERR-002 — `[Error Name]`

* Condition: `[condition]`
* System response: `[response]`
* Retry / recovery: `[behavior]`

### ERR-003 — `[Error Name]`

* Condition: `[condition]`
* System response: `[response]`
* Retry / recovery: `[behavior]`

### Error Requirements

* `WHERE [error condition], THE system SHALL [response].`

* `WHERE [error condition], THE system SHALL [response].`

---

## 7. Acceptance Criteria

<!--

Define when the feature is considered complete.

Acceptance criteria MUST be observable and testable.

Prefer Given / When / Then.

Cover:

- main/happy path;

- important validation failures;

- authorization behavior;

- important edge/error cases.

Do not describe implementation details here.

-->

### AC-001 — [Main Scenario]

**Given** `[initial state]`

**When** `[action/event]`

**Then** `[expected result]`

### AC-002 — [Secondary Scenario]

**Given** `[initial state]`

**When** `[action/event]`

**Then** `[expected result]`

### AC-003 — [Validation / Error Scenario]

**Given** `[initial state]`

**When** `[invalid input/action]`

**Then** `[expected error/result]`

### AC-004 — [Authorization / Edge Case]

**Given** `[initial state]`

**When** `[action]`

**Then** `[expected result]`

---

## 8. Out of Scope

<!--

This section is a hard boundary for the feature.

The AI MUST NOT implement or introduce functionality

that is outside this scope merely because it is commonly

associated with this feature.

-->

### Not Included (Liệt kê các tính năng không thuộc phạm vi)

* `[Feature / behavior]`

* `[Feature / behavior]`

* `[Integration]`

* `[Actor / workflow]`

### Explicit Boundaries (Chỉ thị bắt buộc cho AI dưới dạng SHALL NOT)

* The AI SHALL NOT `[unrequested change]`.

* The AI SHALL NOT `[unrelated database/schema change]`.

* The AI SHALL NOT `[new integration or dependency]`.

* The AI SHALL NOT `[behavior outside this feature]`.

---

<!--

============================================================

END OF LEVEL 2 — DETAILED SPECIFICATION

============================================================

Before implementation, verify that:

- the problem and goal are clear;

- actors and permissions are known;

- functional requirements are testable;

- important business rules are explicit;

- NFRs are measurable where applicable;

- relevant data is defined;

- important error cases are defined;

- acceptance criteria cover the required behavior;

- Out of Scope clearly defines the feature boundary.

If a critical requirement is still ambiguous,

use [NEEDS CLARIFICATION] instead of inventing behavior.

This document should remain a Detailed Spec.

State diagrams, exhaustive state machines, formal proofs,

security/legal audit sections, or other high-rigor artifacts

belong to Level 3 — Formal Specification when required.

-->