---
description: Create a new feature specification using one shared feature name for the Git branch and specs directory.
handoffs:
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: speckit.clarify
    prompt: Clarify specification requirements
    send: true

scripts:
  sh: scripts/bash/create-new-feature.sh --json
  ps: scripts/powershell/create-new-feature.ps1 -Json
  py: scripts/python/create_new_feature.py --json
---

## User Input

```text
{ARGS}
```

You **MUST** consider the user input before proceeding.

## Feature Identity

Spec Kit dùng **tên Git branch hiện tại** làm tên feature.

Ví dụ:

```text
Current Git branch = 003-user-auth

FEATURE_NAME = 003-user-auth
BRANCH_NAME  = 003-user-auth
FEATURE_DIR  = specs/003-user-auth
```

Rules:

- Spec Kit **không quản lý Git branch** trong `__SPECKIT_COMMAND_SPECIFY__`.
- Spec Kit không tạo, switch, rename, merge hoặc delete branch.
- User hoặc công cụ bên ngoài phải checkout đúng feature branch trước.
- Tên branch hiện tại là nguồn dùng để đặt `FEATURE_NAME`.
- `basename(FEATURE_DIR)` phải giống chính xác `BRANCH_NAME`.
- `.specify/feature.json` vẫn là nơi các command phía sau dùng để tìm feature hiện tại.
- Feature branch nên có dạng:
  - `003-user-auth`, hoặc
  - `20260923-134500-user-auth`.
- Không dùng dạng `feature/003-user-auth`, vì `/` làm branch name và feature directory basename không còn giống nhau.

## Outline

The text the user typed after `__SPECKIT_COMMAND_SPECIFY__` is the feature description.
Do not ask the user to repeat it unless the command was invoked without a description.

### 1. Pre-Execution Hooks

Nếu `.specify/extensions.yml` tồn tại, kiểm tra `hooks.before_specify`.

Rules:

- ignore hook có `enabled: false`;
- hook không có `enabled` được xem là enabled;
- không evaluate non-empty `condition`;
- hook không có condition hoặc condition rỗng:
  - optional hook -> surface command/prompt;
  - mandatory hook -> emit `EXECUTE_COMMAND:` và thực sự invoke;
- invalid YAML -> KHÔNG skip im lặng: báo cho user rằng `.specify/extensions.yml` không đọc được (kèm parser error), không hook nào được check (kể cả các hook mandatory `optional: false` đã đăng ký), sau đó tiếp tục bình thường.

Một hook có thể chuẩn bị hoặc checkout Git branch nếu project muốn.
Core `__SPECKIT_COMMAND_SPECIFY__` và script `create-new-feature` **không tự quản lý branch**.

Sau hooks, Git branch hiện tại phải là feature branch cần làm.

### 2. Resolve Current Feature From Git Branch

Run từ repository root:

```text
{SCRIPT}
```

Script chỉ **đọc tên branch hiện tại** rồi tạo feature files tương ứng.

Nó không được:

- `git switch`;
- `git checkout`;
- `git branch`;
- tạo branch;
- đổi branch;
- xóa branch.

Parse JSON:

- `FEATURE_NAME`
- `BRANCH_NAME`
- `FEATURE_NUM`
- `FEATURE_DIR`
- `SPEC_FILE`
- `NUMBERING_MODE`

Required invariant:

```text
FEATURE_NAME == BRANCH_NAME == basename(FEATURE_DIR)
```

Nếu script fail:

- **STOP**;
- không tự tạo branch;
- không tự đoán feature name;
- không fallback sang logic tạo folder bằng AI;
- report lỗi và yêu cầu user checkout đúng feature branch.

Nếu feature directory đã tồn tại và user đang cố mở lại đúng feature,
có thể chạy:

```text
{SCRIPT} -AllowExistingFeature
```

Flag tương đương theo loại script: `-AllowExistingFeature` (PowerShell),
`--allow-existing-feature` (bash/python).

Chỉ dùng flag này khi việc reuse feature cũ là có chủ đích.

### 3. Load Starting Documents

Load:

- `SPEC_FILE` vừa được script tạo từ active `spec-template`;
- `.specify/memory/constitution.md` nếu tồn tại;
- root-level `AGENTS.md` nếu tồn tại và có rule liên quan đến specification.

Không resolve/copy `spec-template` lần thứ hai trong command này.

### 4. Feature Update Rule

Nếu user đang thay đổi requirement của một feature đã tồn tại:

- giữ nguyên feature branch/name;
- mở lại đúng `FEATURE_DIR`;
- sửa `spec.md`;
- sau đó chạy lại các bước downstream cần thiết.

Nếu code sai nhưng SPEC vẫn đúng:

- không sửa SPEC chỉ để khớp code;
- tạo task sửa code ở bước thích hợp.

### 5. Write the Specification

Follow this execution flow:

1. Parse the feature description.
   - If empty: `ERROR "No feature description provided"`.

2. Extract:
   - actors;
   - actions;
   - data;
   - constraints.

3. Resolve unclear aspects.
   - Make informed guesses only when a safe, ordinary default exists.
   - Use `[NEEDS CLARIFICATION: specific question]` only when:
     - the choice significantly changes scope or user experience;
     - multiple reasonable interpretations have different consequences;
     - no reasonable default exists.
   - Maximum 3 clarification markers.
   - Priority: scope > security/privacy > user experience > technical detail.

4. Fill User Scenarios & Testing.
   - If no clear user flow can be determined: **ERROR**.

5. Generate Functional Requirements.
   - Every mandatory requirement must be testable.
   - Record reasonable defaults in Assumptions.

6. Define measurable, technology-agnostic Success Criteria.

7. Identify Key Entities when data is involved.

8. Write the completed specification to `SPEC_FILE`.

   Template compliance (MUST):

   - `SPEC_FILE` is an exact copy of the active `spec-template`; keep that structure.
   - Do not add, remove, rename, or reorder section headings from the template.
   - Fill placeholders in place; never rewrite the template's own instructional text.
   - If a section does not apply, keep the heading and write "N/A" with a one-line reason.
   - Match the template's formatting for status markers, lists, and tables.
   - Remove HTML comment blocks (`<!-- ... -->`) that only guide how to fill the template (yours or copied from the template). The delivered spec is read by humans; keep only comments that carry real content.

### 6. Specification Quality Validation

After writing the initial spec, validate it against these quality criteria:

   a. **Create Spec Quality Checklist**: Generate a checklist file at `SPECIFY_FEATURE_DIRECTORY/checklists/requirements.md` using the checklist template structure with these validation items:

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]

      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]

      ## Content Quality

      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed

      ## Template Structure

      - [ ] All spec-template section headings present, unchanged, in order
      - [ ] No extra top-level sections beyond the template
      - [ ] Placeholders filled in place (template text not rewritten)

      ## Requirement Completeness

      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified

      ## Feature Readiness

      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification

      ## Notes

      - Items marked incomplete require spec updates before `__SPECKIT_COMMAND_CLARIFY__` or `__SPECKIT_COMMAND_PLAN__`
      ```

   b. **Run Validation Check**: Review the spec against each checklist item:
      - For each item, determine if it passes or fails
      - Document specific issues found (quote relevant spec sections)

   c. **Handle Validation Results**:

      - **If all items pass**: Mark checklist complete and proceed to the Mandatory Post-Execution Hooks section

      - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List the failing items and specific issues
        2. Update the spec to address each issue
        3. Re-run validation until all items pass (max 3 iterations)
        4. If still failing after 3 iterations, document remaining issues in checklist notes and warn user

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. **LIMIT CHECK**: If more than 3 markers exist, keep only the 3 most critical (by scope/security/UX impact) and make informed guesses for the rest
        3. For each clarification needed (max 3), present options to user in this format:

           ```markdown
           ## Question [N]: [Topic]

           **Context**: [Quote relevant spec section]

           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

           **Suggested Answers**:

           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |

           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - Table Formatting**: Ensure markdown tables are properly formatted:
           - Use consistent spacing with pipes aligned
           - Each cell should have spaces around content: `| Content |` not `|Content|`
           - Header separator must have at least 3 dashes: `|--------|`
           - Test that the table renders correctly in markdown preview
        5. Number questions sequentially (Q1, Q2, Q3 - max 3 total)
        6. Present all questions together before waiting for responses
        7. Wait for user to respond with their choices for all questions (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
        8. Update the spec by replacing each [NEEDS CLARIFICATION] marker with the user's selected or provided answer
        9. Re-run validation after all clarifications are resolved

   d. **Update Checklist**: After each validation iteration, update the checklist file with current pass/fail status


## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check `.specify/extensions.yml` for `hooks.after_specify`.

- If it does not exist, or no hooks are registered, continue to Completion Report.
- Ignore hooks with `enabled: false`.
- Hooks without `enabled` are enabled by default.
- Do not evaluate non-empty `condition` expressions here.
- Mandatory executable hook:
  - emit `EXECUTE_COMMAND:`;
  - actually invoke it;
  - wait for completion.
- Optional hook:
  - surface command/prompt to the user.
- Invalid YAML -> KHÔNG skip im lặng: báo cho user rằng `.specify/extensions.yml` không đọc được (kèm parser error), không hook nào được check (kể cả các hook mandatory `optional: false` đã đăng ký), sau đó tiếp tục sang Completion Report.

## Completion Report

Report:

- `FEATURE_NAME`
- `BRANCH_NAME`
- `FEATURE_DIR`
- `SPEC_FILE`
- `NUMBERING_MODE` lấy từ format của branch hiện tại
- specification checklist result
- unresolved clarification count
- readiness for `__SPECKIT_COMMAND_CLARIFY__` or `__SPECKIT_COMMAND_PLAN__`

Confirm:

```text
branch name == feature name == feature directory basename
```

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, frameworks, code structure, or database choice unless the requirement itself explicitly depends on them).
- Write for product/business understanding first.
- Do not create custom `__SPECKIT_COMMAND_CHECKLIST__` artifacts here.
- `checklists/requirements.md` is the built-in specification-quality checklist owned by this command and `__SPECKIT_COMMAND_CLARIFY__`.

### Section Requirements

- Mandatory sections: complete for every feature.
- Optional sections: include only when relevant.
- Remove non-applicable optional sections instead of leaving placeholder content.

### For AI Generation

1. Make informed guesses only when a safe, ordinary default exists.
2. Record meaningful assumptions.
3. Use maximum 3 `[NEEDS CLARIFICATION: ...]` markers.
4. Prioritize clarification by scope > security/privacy > user experience > technical detail.
5. Every mandatory requirement must be testable and unambiguous.

## Done When

- [ ] Git branch hiện tại đã tồn tại trước khi Spec Kit chạy.
- [ ] Spec Kit không tạo/switch/rename/delete Git branch.
- [ ] `FEATURE_NAME == BRANCH_NAME == basename(FEATURE_DIR)`.
- [ ] `SPEC_FILE` tồn tại trong đúng feature directory.
- [ ] `.specify/feature.json` trỏ tới feature directory hiện tại.
- [ ] Specification được viết và kiểm tra bằng `checklists/requirements.md`.
- [ ] Extension hooks được xử lý theo rule.
- [ ] Completion report được trả về.
