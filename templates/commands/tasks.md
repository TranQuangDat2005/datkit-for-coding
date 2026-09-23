---
description: Generate an actionable, dependency-ordered tasks.md from an approved SPEC.md and PLAN.md using atomic, independent, and verifiable tasks.
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Start the implementation task-by-task
    send: true

scripts:
  sh: scripts/bash/setup-tasks.sh --json
  ps: scripts/powershell/setup-tasks.ps1 -Json
  py: scripts/python/setup_tasks.py --json
---

## User Input

```text
{ARGS}
```

Bạn **MUST** xem xét user input trước khi tiếp tục nếu input không rỗng.

## Pre-Execution Checks

**Check for extension hooks (before tasks generation)**:

- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_tasks` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable.
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation.
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):

    ```text
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

  - **Mandatory hook** (`optional: false`):

    ```text
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```

    Sau khi emit block trên, bạn **MUST** thực sự invoke hook và chờ hoàn tất trước khi tiếp tục. Cách invoke có thể khác literal `{command}` tùy agent/session.

- Nếu không có hooks hoặc `.specify/extensions.yml` không tồn tại, tiếp tục silently.

## Outline

### 1. Setup

Run `{SCRIPT}` từ repository root và parse:

- `FEATURE_DIR`
- `TASKS_TEMPLATE_CONTENT`
- `TASKS_TEMPLATE`
- `AVAILABLE_DOCS`

Rules:

- `FEATURE_DIR` và `TASKS_TEMPLATE` phải dùng absolute path khi được cung cấp.
- `AVAILABLE_DOCS` là danh sách tài liệu khả dụng bên trong `FEATURE_DIR`.
- Với single quote trong argument, escape đúng theo shell đang sử dụng.

### 2. Load Context

Read từ `FEATURE_DIR`:

**Required**

- `spec.md`
- `plan.md`

**Optional**

- `data-model.md`
- `contracts/`
- `research.md`
- `quickstart.md`

**Project-level context, if present**

- `AGENTS.md`
- `.specify/memory/constitution.md`
- các project constraint/context files được `AGENTS.md` hoặc constitution tham chiếu và có liên quan

Authority:

- `SPEC.md` là source of truth cho intent, requirement, business rule, acceptance criteria và scope.
- `PLAN.md` là source of truth cho technical approach, components, data flow, implementation dependencies, technical decisions và affected structure.
- `AGENTS.md` / project constraints cung cấp conventions và project-wide technical context.
- Constitution có authority cao nhất đối với governance constraints.
- Không tự quyết định lại architecture, tech stack hoặc dependency đã được approve.
- Nếu SPEC và PLAN mâu thuẫn, **STOP** và report inconsistency. Không tự chọn một phía.

### 3. Plan Readiness Gate

Trước khi decomposition, PLAN phải sẵn sàng để implement.

Kiểm tra:

- `plan.md` tồn tại và không còn placeholder quan trọng.
- Không còn unresolved `NEEDS CLARIFICATION`.
- `Questions for Human` phải là `None` hoặc mọi câu hỏi đã có quyết định rõ ràng.
- `Constitution Check` không còn unjustified violation.
- Nếu PLAN có trường `Status`, status phải là `APPROVED`.
- Nếu SPEC vẫn có unresolved clarification ảnh hưởng implementation, **STOP**.

Nếu bất kỳ điều kiện nào không đạt:

- **STOP**.
- Không generate hoặc overwrite `tasks.md`.
- Report chính xác blocking item và file/section liên quan.

### 4. Build Traceability Map

Trước khi tạo task, build internal traceability map:

- Extract các requirement cần implementation từ SPEC:
  - Functional Requirements
  - Business Rules
  - Validation Rules
  - Acceptance Criteria
  - EARS requirement refs nếu có
- Extract từ PLAN:
  - Components
  - Architectural decisions có tạo implementation work
  - Data flow touchpoints
  - Implementation dependencies
  - Affected files/modules
- Map mỗi PLAN component cần implement tới ít nhất một candidate task.
- Map mỗi candidate task về SPEC requirement/section tương ứng khi có.
- Không tạo orphan task không có justification từ SPEC hoặc PLAN.

Không output raw internal map trừ khi cần report gap.

### 5. Generate Candidate Tasks

Decompose approved PLAN thành các task cụ thể.

Mỗi task **MUST** thỏa:

- **Atomic**: một đơn vị công việc tập trung; nếu còn có thể tách thành các task độc lập có ý nghĩa thì phải cân nhắc tách.
- **Independent**: có thể thực hiện khi các dependency được khai báo đã hoàn tất; không phụ thuộc ngầm vào task chưa xong.
- **Verifiable**: có điều kiện `Done when` cụ thể để xác nhận hoàn thành.
- **Time-bounded**: estimate tối đa **4 giờ**.
- Nếu estimate > 4h, **MUST split** task trước khi ghi vào `tasks.md`.

Tên task:

- Bắt đầu bằng action verb rõ ràng.
- Nói rõ object/component được tạo hoặc sửa.
- Không dùng tên mơ hồ như `Handle backend`, `Fix stuff`, `Complete API`.

### 6. Determine Dependencies

Với mỗi task:

- Ghi direct dependencies bằng task ID.
- Dùng `Deps: -` nếu task không cần task nào hoàn tất trước.
- Chỉ ghi direct dependency, không lặp transitive dependency nếu không cần.
- Mọi dependency ID phải tồn tại.
- Task prerequisite phải xuất hiện trước task phụ thuộc.
- Dependency graph không được có cycle.

Dependency order quan trọng hơn cách group task.

### 7. Determine Parallel Opportunities

Mark `[P]` **ONLY** khi task an toàn để thực thi concurrent.

Một task chỉ được mark `[P]` khi:

- không phụ thuộc vào task chưa hoàn tất trong cùng execution group;
- không sửa cùng file, migration, schema artifact hoặc shared artifact với task chạy song song;
- không tạo ordering conflict trên cùng resource;
- không yêu cầu output chưa tồn tại từ task khác trong nhóm;
- concurrent execution không tạo integration conflict rõ ràng.

Rules:

- `[P]` = **can run in parallel**, không phải must run in parallel.
- Không mark `[P]` chỉ vì task thuộc user story khác.
- Nếu không chắc task có an toàn để chạy song song hay không, không mark `[P]`.

### 8. Generate `tasks.md`

Use:

1. `TASKS_TEMPLATE_CONTENT` nếu setup script trả về nội dung này.
2. Nếu không có, read `TASKS_TEMPLATE`.

Generate `tasks.md` theo template đã resolve.

Rules:

- Tuân thủ tuyệt đối cấu trúc template: giữ nguyên mọi heading, không thêm/bỏ/đổi tên/đảo thứ tự section, không viết lại phần chữ định sẵn của template.
- Section không áp dụng: giữ heading và ghi "N/A" kèm lý do ngắn.
- Không force fixed phases như Setup → Foundational → User Story → Polish.
- Tổ chức task theo dependency order rõ nhất.
- Có thể group theo logical component, user story hoặc CORE/SHELL nếu điều đó giúp đọc dễ hơn.
- Grouping không được che khuất dependency thực tế.
- Nếu SPEC có user stories:
  - `[US1]`, `[US2]`, ... **MAY** được dùng để traceability.
  - Không bắt buộc mọi task phải có `[USx]`.
- Nếu PLAN có CORE/SHELL classification:
  - preserve classification.
  - Không tự invent CORE/SHELL nếu PLAN không sử dụng.
- Xóa toàn bộ sample task, placeholder, instructional example và các khối HTML comment (`<!-- ... -->`) chỉ dùng để hướng dẫn AI điền template khỏi generated `tasks.md`.
- Generated `tasks.md` chỉ chứa task thật của feature và các summary section cần thiết; người đọc là con người, không cần guidance comment.

### 9. Validate Tasks

Trước khi ghi completion report, verify:

- Task IDs tuần tự: `T001`, `T002`, ...
- Mọi task có task name rõ ràng.
- Mọi task có file path cụ thể khi có thể xác định.
- Mọi task có `Est`.
- Không task nào > 4h.
- Mọi task có `Deps`.
- Mọi dependency ID tồn tại.
- Không có dependency cycle.
- Mọi task có `Spec refs` khi có requirement trực tiếp.
- Với technical prerequisite không có direct SPEC ref, trường `Spec refs` phải ghi `N/A` kèm PLAN section/component justification.
- Mọi task có `Done when`.
- Mọi PLAN component cần implementation được cover bởi ít nhất một task.
- Không có orphan task ngoài SPEC/PLAN.
- `[P]` tasks thực sự dependency-safe và file-safe.
- Không còn unresolved gap làm implementation không thể quyết định.

Nếu validation fail:

- Không report success.
- Sửa task decomposition nếu có thể sửa mà không thay đổi intent.
- Nếu lỗi đến từ SPEC/PLAN gap, **STOP** và report gap thay vì invent behavior.

## Task Format

Mọi task **MUST** dùng structure sau:

```text
- [ ] T001 [P?] [US?] <Action + object>
  - Files: <exact path(s)>
  - Est: <time, max 4h>
  - Deps: <task IDs or ->
  - Spec refs: <SPEC refs, or N/A with PLAN justification>
  - Done when: <specific, verifiable completion condition>
```

Rules:

- Checkbox `- [ ]` là bắt buộc.
- Task ID là bắt buộc và sequential.
- `[P]` là optional.
- `[USx]` là optional.
- `Files` là bắt buộc khi có thể xác định path từ PLAN/repository.
- `Est` là bắt buộc và tối đa 4h.
- `Deps` là bắt buộc.
- `Spec refs` là bắt buộc:
  - dùng requirement/section IDs khi có;
  - nếu technical-only task không có direct requirement, dùng `N/A (PLAN: <section/component>)`.
- `Done when` là bắt buộc và phải kiểm chứng được.

### Example

```text
- [ ] T001 [P] Create reviews table migration
  - Files: migrations/001_create_reviews.sql
  - Est: 1h
  - Deps: -
  - Spec refs: DR-001, §5 Data
  - Done when: migration applies successfully and rollback restores the previous schema

- [ ] T002 [P] Implement BlacklistService
  - Files: src/shared/blacklist.py, tests/shared/test_blacklist.py
  - Est: 2h
  - Deps: -
  - Spec refs: FR-004
  - Done when: blacklist rules are implemented and referenced tests pass

- [ ] T003 Implement ReviewService
  - Files: src/reviews/service.py, tests/reviews/test_service.py
  - Est: 4h
  - Deps: T001, T002
  - Spec refs: FR-001, FR-002, AC-001
  - Done when: all referenced business rules are enforced and the service acceptance tests pass
```

## Test Task Rules

Standalone test tasks là **OPTIONAL**, trừ khi:

- SPEC yêu cầu test artifact riêng;
- user yêu cầu TDD;
- contract hoặc acceptance criterion cần test task độc lập;
- test setup là một implementation dependency riêng.

Tuy nhiên verification **không optional**:

- mọi task phải có `Done when`;
- `Done when` phải đủ cụ thể để agent hoặc reviewer biết task đã hoàn thành hay chưa.

Không tự tạo một phase test riêng nếu PLAN/SPEC không yêu cầu.

## Dependencies & Parallelism Output

Generated `tasks.md` **MUST** có section:

### Dependencies & Execution Order

- summarize các dependency chain quan trọng;
- cho biết task nào block task nào;
- ghi critical path khi có ý nghĩa.

### Parallel Opportunities

- chỉ liệt kê các nhóm thực sự có thể chạy concurrent;
- ghi điều kiện để nhóm có thể bắt đầu;
- nếu không có parallel opportunity có ý nghĩa, ghi `None`.

Ví dụ:

```text
T001 ──┐
T002 ──┼── can run in parallel
T003 ──┘
       ↓
      T004
       ↓
      T005
```

## Consistency Rules

Trước khi completion:

- Mọi PLAN component cần implementation phải map tới ít nhất một task.
- Mọi implementation task phải có justification từ SPEC hoặc PLAN.
- Mọi requirement cần implementation phải được cover bởi một hoặc nhiều task.
- Không chuyển requirement giữa SPEC, PLAN và TASKS.
- Không thêm product scope mới trong TASKS.
- Không thêm architecture hoặc dependency mới trong TASKS.
- Nếu decomposition phát hiện gap trong SPEC/PLAN, report gap thay vì tự điền giả định.

## Execution Guidance

Đưa các note sau vào `tasks.md` khi template có section phù hợp:

- Ưu tiên `1 task = 1 focused agent session`.
- Chỉ execute task khi toàn bộ `Deps` đã complete.
- `[P]` chỉ biểu thị safe concurrency.
- Không sửa SPEC hoặc PLAN trong lúc implementation chỉ để task dễ làm hơn.
- Nếu implementation phát hiện spec/plan gap, dừng và report.

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check if `.specify/extensions.yml` exists in the project root.

- If it does not exist, or no hooks are registered under `hooks.after_tasks`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_tasks` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue to the Completion Report.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable.
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation.
- For each executable hook, output the following based on its `optional` flag:
  - **Mandatory hook** (`optional: false`) — **You MUST emit `EXECUTE_COMMAND:` for each mandatory hook**:

    ```text
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```

    Sau khi emit block trên, bạn **MUST** thực sự invoke hook và chờ hoàn tất trước khi tiếp tục.

  - **Optional hook** (`optional: true`):

    ```text
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## Completion Report

Report:

- output path tới generated `tasks.md`;
- total task count;
- total estimated effort;
- dependency chains / critical path nếu có ý nghĩa;
- parallel opportunities;
- số task có `[P]`;
- uncovered SPEC/PLAN items nếu có;
- xác nhận:
  - mọi task Atomic;
  - mọi task Independent theo declared dependencies;
  - mọi task Verifiable;
  - mọi task <= 4h;
  - PLAN coverage complete;
  - không có orphan task.

Không report success nếu Plan Readiness Gate hoặc task validation chưa pass.

## Done When

- [ ] PLAN readiness gate passed
- [ ] `tasks.md` generated from approved SPEC + PLAN
- [ ] Every task has ID, Files, Est, Deps, Spec refs, and Done when
- [ ] Every task is <= 4h
- [ ] Dependency graph has no cycle
- [ ] PLAN components are covered
- [ ] No orphan tasks
- [ ] Parallel markers are dependency-safe and file-safe
- [ ] Extension hooks dispatched or skipped correctly
- [ ] Completion report returned to the user
