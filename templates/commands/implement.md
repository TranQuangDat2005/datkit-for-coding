---
description: Execute one ready task from tasks.md using dependency-driven, task-scoped implementation and verify its Done when condition before marking it complete.

scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
  py: scripts/python/check_prerequisites.py --json --require-tasks --include-tasks
---

## User Input

```text
{ARGS}
```

Bạn **MUST** xem xét user input trước khi tiếp tục nếu input không rỗng.

Supported input:

- Không truyền Task ID → chọn task chưa hoàn thành đầu tiên đang `READY`.
- `Txxx` → thực thi đúng task đó nếu task tồn tại và toàn bộ `Deps` đã hoàn thành.

Không tự động thực thi toàn bộ feature trong một invocation.
Ưu tiên **1 task = 1 focused implementation session**.

## Pre-Execution Checks

**Check for extension hooks (before implementation)**:

- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read entries under `hooks.before_implement`.
- If YAML is invalid, skip hook checking silently and continue normally.
- Ignore hooks with `enabled: false`.
- Hooks without `enabled` are enabled by default.
- Do not evaluate non-empty `condition` expressions here.
- If a hook has no condition, or condition is empty:
  - Optional hook: show command and prompt to the user.
  - Mandatory hook: emit `EXECUTE_COMMAND:` and actually run it before continuing.
- If no hooks are available, continue silently.

## Goal

Thực thi **một task sẵn sàng** từ `tasks.md` theo đúng:

- SPEC requirement được task tham chiếu;
- PLAN technical design được approve;
- project constraints / Constitution;
- declared `Files`;
- declared `Deps`;
- declared `Done when`.

`__SPECKIT_COMMAND_IMPLEMENT__` không phải command để tự tái thiết kế feature.

Nó chỉ:

```text
select READY task
→ load focused context
→ Plan
→ Act
→ Check
→ mark [x] only if Done when passes
→ report
```

## Operating Constraints

### Task-Scoped Execution

Trong một invocation:

- Chỉ thực thi **một** implementation task.
- Không tự chuyển sang task tiếp theo sau khi task hiện tại hoàn tất.
- Không gom nhiều task `[P]` để chạy cùng lúc trong cùng session.
- `[P]` chỉ cho biết task có thể chạy concurrent trong multi-agent/team workflow; nó không thay đổi nguyên tắc 1 task/session của command này.

### Artifact Authority

Dùng authority order:

1. Constitution — governance constraints.
2. SPEC — product behavior, rules, scope, acceptance criteria.
3. PLAN — approved technical approach, components và structure.
4. TASKS — decomposition cụ thể để triển khai.
5. `AGENTS.md` / referenced project constraints — project-wide conventions và technical baseline.

Không dùng implementation để thay đổi nghĩa của upstream artifacts.

### No Silent Scope Expansion

Không tự:

- thêm requirement;
- thay đổi business rule;
- đổi architecture;
- thêm framework/library/service mới;
- sửa SPEC;
- sửa PLAN;
- rewrite task definition;
- thêm dependency mới vào task;
- sửa task khác.

Nếu implementation yêu cầu thay đổi ngoài approved task scope, **STOP** và report artifact gap.

### Allowed `tasks.md` Mutation

`tasks.md` chỉ được thay đổi theo một cách:

```text
- [ ] Txxx ...
```

thành:

```text
- [x] Txxx ...
```

và chỉ sau khi `Done when` đã được verify.

Không rewrite:

- task name;
- `Files`;
- `Est`;
- `Deps`;
- `Spec refs`;
- `Done when`;
- task order;
- `[P]`;
- `[USx]`.

## Execution Steps

### 1. Initialize Implementation Context

Run:

```text
{SCRIPT}
```

từ repository root và parse:

- `FEATURE_DIR`
- `AVAILABLE_DOCS`

Derive absolute paths:

- `SPEC = FEATURE_DIR/spec.md`
- `PLAN = FEATURE_DIR/plan.md`
- `TASKS = FEATURE_DIR/tasks.md`

Required:

- `spec.md`
- `plan.md`
- `tasks.md`

Nếu thiếu:

- SPEC → STOP, suggest `__SPECKIT_COMMAND_SPECIFY__`
- PLAN → STOP, suggest `__SPECKIT_COMMAND_PLAN__`
- TASKS → STOP, suggest `__SPECKIT_COMMAND_TASKS__`

### 2. Load Project Context

Load nếu tồn tại:

- root-level `AGENTS.md`
- `.specify/memory/constitution.md`
- project constraint/context files được chúng tham chiếu và liên quan

Rules:

- Project-wide tech stack/conventions được inherit từ context này.
- Không yêu cầu PLAN lặp lại tech stack.
- Constitution có authority cao nhất đối với governance constraints.
- Nếu task yêu cầu thứ bị Constitution cấm, **STOP**.

### 3. Check Review Gates

#### Built-in Requirements Checklist

Nếu `FEATURE_DIR/checklists/requirements.md` tồn tại:

- scan checkbox state;
- nếu còn unchecked item có thể ảnh hưởng requirement quality:
  - **STOP**;
  - report checklist status;
  - recommend `__SPECKIT_COMMAND_CLARIFY__` hoặc review checklist trước implementation.

Không tự mark checklist item.

#### Custom Checklists

Nếu các custom checklist khác tồn tại:

- report trạng thái;
- không tự coi chúng là implementation completion;
- chỉ block khi:
  - Constitution/project policy nói checklist đó là mandatory gate; hoặc
  - user input yêu cầu checklist đó phải pass trước implementation.

### 4. Parse `tasks.md`

Chỉ parse real task line matching conceptually:

```text
- [ ] T001 ...
- [x] T001 ...
- [X] T001 ...
```

Task ID phải match:

```text
T\d{3,}
```

Cho mỗi task extract:

- completion state
- ID
- task name
- `[P]` nếu có
- `[USx]` nếu có
- `Files`
- `Est`
- `Deps`
- `Spec refs`
- `Done when`

Không dùng heading/group/phase làm execution dependency.

### 5. Minimal Task Integrity Check

Trước khi chọn task, verify task metadata đủ để executor làm việc.

Selected task phải có:

- valid ID;
- clear task name;
- `Files`;
- `Est`;
- `Deps`;
- `Spec refs`;
- `Done when`.

Ngoài ra:

- `Est <= 4h`;
- mọi `Deps` ID phải tồn tại;
- task không self-depend;
- không có obvious unresolved placeholder trong metadata.

Nếu selected task invalid:

- **STOP**;
- không implement;
- recommend `__SPECKIT_COMMAND_TASKS__`.

Không tự sửa task schema.

### 6. Select Task

#### Explicit Task ID

Nếu `{ARGS}` chứa một Task ID như `T004`:

- tìm đúng task;
- nếu không tồn tại → STOP;
- nếu đã `[x]` / `[X]` → report already completed và STOP;
- nếu còn dependency chưa complete → BLOCKED và report missing dependencies;
- nếu ready → select task.

Không tự fallback sang task khác.

#### No Task ID

Nếu không có Task ID:

1. duyệt các incomplete task theo file order;
2. với mỗi task, evaluate `Deps`;
3. task là `READY` khi mọi dependency đã `[x]` / `[X]`;
4. chọn READY task đầu tiên.

Nếu không có READY task:

- nếu tất cả task complete → report feature task list complete;
- nếu còn incomplete task → report dependency/blocker state;
- không implement task blocked.

### 7. Load Focused Task Context

Sau khi select task, chỉ load context cần thiết cho task đó.

#### From SPEC

Load:

- exact `Spec refs`;
- surrounding requirement/business-rule/validation/acceptance context cần để hiểu refs;
- referenced User Story nếu task có `[USx]`;
- relevant Out of Scope / edge-case constraints.

Nếu `Spec refs` là:

```text
N/A (PLAN: <section/component>)
```

thì không invent SPEC mapping; dùng PLAN justification.

#### From PLAN

Load:

- component/section liên quan;
- Architectural Approach có ảnh hưởng trực tiếp;
- relevant Data Flow;
- relevant Dependencies;
- affected Project Structure;
- feature-specific constraints.

#### Optional Design Artifacts

Load chỉ khi task cần:

- `data-model.md`
- relevant file(s) trong `contracts/`
- `research.md`
- `quickstart.md`

#### Repository Files

Inspect:

- files declared trong `Files`;
- directly related existing implementation cần để hiểu context;
- tests/configuration trực tiếp cần cho `Done when`.

Không load toàn repository nếu không cần.

### 8. Pre-Implementation Scope Check

Trước khi sửa code, xác nhận internally:

```text
Task:
Files:
Deps:
Spec refs:
PLAN context:
Done when:
Project constraints:
```

Check:

- task behavior nằm trong SPEC/PLAN;
- declared `Files` đủ để thực hiện task;
- không cần dependency chưa hoàn thành;
- không cần architecture/product decision mới.

Nếu implementation thực sự cần sửa thêm file chưa nằm trong `Files`:

- không tự mở rộng scope;
- **STOP** trước khi sửa file ngoài scope;
- report task decomposition gap;
- recommend `__SPECKIT_COMMAND_TASKS__`.

Ngoại lệ: generated/build artifact mà project tooling tự sinh không được coi là planned source-file expansion, nhưng không commit/edit thủ công nếu project conventions không cho phép.

## Plan-Act-Check Loop

### 9. Plan

Lập một execution plan ngắn cho **selected task only**.

Plan phải bám:

- declared Files;
- Spec refs;
- PLAN decision;
- Done when.

Không tạo feature-level re-plan.

Nếu task có nhiều sub-step nhưng vẫn nằm trong cùng atomic task, có thể dùng checklist nội bộ của session.
Không thêm các sub-step này thành task mới trong `tasks.md`.

### 10. Act

Implement selected task.

Rules:

- Follow existing code patterns and project conventions.
- Chỉ thay đổi code cần thiết cho task.
- Không refactor unrelated code.
- Không “cleanup tiện thể” ngoài task scope.
- Không introduce dependency mới nếu PLAN/task không approve.
- Không thay đổi public contract ngoài SPEC/PLAN.
- Không sửa completed dependency task chỉ để implementation hiện tại dễ hơn, trừ khi current task explicitly yêu cầu file đó và change vẫn đúng scope.

### 11. Test / Verification Behavior

Không ép TDD mặc định.

Tests-before-code chỉ áp dụng khi:

- SPEC yêu cầu TDD;
- Constitution/project constraints yêu cầu;
- selected task là test-first task;
- task/PLAN explicitly yêu cầu.

Sau implementation, chạy verification cần thiết để chứng minh `Done when`.

Có thể bao gồm:

- unit test;
- integration test;
- contract test;
- build;
- lint/typecheck;
- migration apply/rollback;
- targeted command;
- API scenario;
- file/content inspection;
- quickstart scenario;

tùy `Done when`.

Không chạy toàn bộ expensive suite nếu task không cần, trừ khi project constraint yêu cầu.

### 12. Check

Evaluate `Done when` literally.

Ví dụ:

```text
Done when:
POST /reviews returns 201 for valid input and 409 for duplicate review.
```

thì phải có evidence cho cả hai điều kiện.

Result:

#### PASS

Chỉ PASS khi toàn bộ `Done when` được verify.

Sau đó:

- mark đúng selected task `[x]` trong `tasks.md`;
- không sửa metadata khác;
- report verification evidence.

#### FAIL

Nếu `Done when` chưa đạt:

- giữ task `[ ]`;
- không mark partial completion;
- report:
  - phần nào đã làm;
  - verification nào fail;
  - blocker/error;
  - files đã thay đổi.

Không tự đổi acceptance condition để task pass.

#### BLOCKED

Nếu phát hiện:

- missing requirement;
- SPEC/PLAN contradiction;
- undeclared dependency;
- cần file ngoài task scope;
- Constitution conflict;
- external prerequisite không sẵn sàng;

thì:

- giữ `[ ]`;
- stop task;
- report blocker và artifact owner cần sửa.

### 13. Dependency State After Completion

Sau khi task PASS:

- recompute READY tasks từ remaining unchecked tasks;
- không tự execute chúng;
- report tối đa một số task READY tiếp theo để user/agent biết có thể tiếp tục.

Nếu task có `[P]`, có thể report những task READY khác cũng có thể chạy concurrent trong session/agent khác, nhưng không tự launch chúng.

## Error Handling

### Tool / Build / Test Failure

- Không mark `[x]`.
- Không che giấu failed command.
- Report concise failure evidence.
- Giữ user changes và existing unrelated changes nguyên vẹn.
- Không reset/revert repository-wide state.
- Chỉ rollback own change khi rollback đó rõ ràng, local, safe và cần để tránh leaving broken artifact.

### Existing Unrelated Changes

Nếu working tree có unrelated changes:

- không overwrite/revert chúng;
- chỉ touch declared task files;
- nếu same-file conflict khiến task không thể an toàn tiếp tục, STOP và report.

### Task Reveals Upstream Gap

Route remediation theo ownership:

- product/requirement ambiguity → `__SPECKIT_COMMAND_CLARIFY__` hoặc `__SPECKIT_COMMAND_SPECIFY__`
- technical design issue → `__SPECKIT_COMMAND_PLAN__`
- task decomposition/schema issue → `__SPECKIT_COMMAND_TASKS__`
- governance issue → adjust violating artifact, hoặc `__SPECKIT_COMMAND_CONSTITUTION__` chỉ khi user muốn thay governance

Không tự invoke các command này.

## Completion Report

Sau mỗi invocation, report:

- **Task**: selected Task ID + name
- **Result**: `COMPLETED | FAILED | BLOCKED | ALREADY COMPLETED | ALL TASKS COMPLETE`
- **Files changed**
- **Spec refs**
- **Done when**
- **Verification performed**
- **Task status in tasks.md**
- **Remaining blockers**, nếu có
- **Next READY tasks**, nếu có

Ví dụ:

```text
Task: T003 — Implement ReviewService
Result: COMPLETED

Files changed:
- src/reviews/service.py
- tests/reviews/test_service.py

Spec refs:
- FR-001
- BR-002
- AC-001

Done when:
- duplicate review rejected
- relevant tests pass

Verification:
- targeted service tests: PASS

tasks.md:
- T003 marked [x]

Next READY:
- T004
- T005 [P]
```

Không report toàn feature complete chỉ vì một task complete.

## Feature Completion

Chỉ khi tất cả real tasks trong `tasks.md` đã `[x]` / `[X]`:

- report `ALL TASKS COMPLETE`;
- không tạo thêm work;
- recommend `__SPECKIT_COMMAND_CONVERGE__` để kiểm tra codebase hiện tại so với SPEC + PLAN + TASKS.

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check `.specify/extensions.yml` for `hooks.after_implement`.

- Ignore disabled hooks.
- Do not evaluate non-empty conditions here.
- Mandatory executable hooks:
  - emit `EXECUTE_COMMAND:`
  - actually run
  - wait for completion
- Optional hooks:
  - surface command/prompt to user
- If none apply, continue silently.

Hooks phải chạy sau implementation/check state phù hợp với hook contract, nhưng trước final Completion Report.

## Done When

Một invocation `__SPECKIT_COMMAND_IMPLEMENT__` được coi là hoàn tất khi một trong các trạng thái sau được xác định rõ:

- selected task PASS và đã mark `[x]`;
- selected task FAIL và vẫn `[ ]`;
- selected task BLOCKED và vẫn `[ ]`;
- explicit task đã complete từ trước;
- toàn bộ task đã complete.

Với task PASS:

- [ ] selected task implementation nằm trong approved scope
- [ ] declared dependencies đã complete
- [ ] project constraints được tuân thủ
- [ ] `Done when` đã được verify
- [ ] chỉ selected task được mark `[x]`
- [ ] không sửa SPEC/PLAN/task metadata
- [ ] completion report đã được trả về
