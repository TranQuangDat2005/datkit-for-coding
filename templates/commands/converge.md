---
description: Assess the implemented feature against approved SPEC.md, PLAN.md, and completed TASKS.md, then append atomic remediation tasks only for verified remaining gaps.

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

## Pre-Execution Checks

**Check for extension hooks (before convergence)**:

- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read entries under `hooks.before_converge`.
- If YAML is invalid, skip hook checking silently and continue normally.
- Ignore hooks with `enabled: false`.
- Hooks without `enabled` are enabled by default.
- Do not evaluate non-empty `condition` expressions here.
- If a hook has no condition, or condition is empty:
  - Optional hook: show command and prompt to the user.
  - Mandatory hook: emit `EXECUTE_COMMAND:` and actually run it before continuing.
- If no hooks are available, continue silently.

## Goal

`__SPECKIT_COMMAND_CONVERGE__` chạy **sau khi toàn bộ task hiện tại đã được implementation hoàn tất**.

Nhiệm vụ:

```text
approved SPEC + PLAN
        +
completed TASKS
        ↓
inspect current codebase
        ↓
compare implementation with approved intent
        ↓
remaining gap?
   ├─ no  → CONVERGED
   └─ yes → append atomic remediation tasks
```

Converge không phải diff tool và không dùng git history để suy luận intent.

Nó đánh giá **current state** của codebase so với approved artifacts.

## Operating Constraints

### Append-only

Converge là read-only đối với:

- `spec.md`
- `plan.md`
- source code
- existing task definitions

Write duy nhất được phép:

- append một `## Convergence Pass N` mới ở cuối `tasks.md` khi có actionable findings.

Không được:

- rewrite existing task;
- renumber task;
- reorder task;
- đổi `[x]` thành `[ ]`;
- thay metadata của task cũ;
- sửa code;
- tự sửa SPEC/PLAN.

Nếu không có actionable finding:

- `tasks.md` phải **byte-for-byte unchanged**.

### Artifact Authority

Dùng authority order:

1. Constitution — governance constraints.
2. SPEC — product intent, scope, requirements, business rules, acceptance criteria.
3. PLAN — approved technical approach, components, dependencies, structure.
4. TASKS — implementation decomposition và verification intent.
5. `AGENTS.md` / referenced project constraints — project-wide conventions.

TASKS không được thay đổi nghĩa của SPEC hoặc PLAN.

### No Silent Design

Nếu remaining gap chỉ có thể giải quyết bằng:

- product decision mới;
- architecture decision mới;
- dependency/service mới;
- thay đổi scope;
- requirement clarification;

thì **không append implementation task đoán mò**.

Report upstream gap và route về artifact owner phù hợp.

## Execution Steps

### 1. Initialize Convergence Context

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

- Constitution có authority cao nhất đối với governance constraints.
- Không yêu cầu PLAN lặp project-wide tech stack.
- Nếu project context conflict mà authority order không giải quyết được, report blocker.

### 3. Completion Gate

Parse **real tasks** trong `tasks.md`.

Real task line conceptually match:

```text
- [ ] T001 ...
- [x] T001 ...
- [X] T001 ...
```

Task ID:

```text
T\d{3,}
```

Before convergence:

- mọi current real task phải `[x]` hoặc `[X]`;
- không được còn incomplete remediation task từ Convergence Pass trước;
- task metadata có thể được đọc để tìm scope/evidence, nhưng không sửa.

Nếu còn bất kỳ task `[ ]`:

- **STOP**;
- không inspect code để tạo remediation work;
- không append Convergence section;
- report incomplete task IDs;
- recommend tiếp tục `__SPECKIT_COMMAND_IMPLEMENT__`.

Lý do: work chưa implement không được coi là convergence gap.

### 4. Load Approved Intent

#### From `spec.md`

Extract implementation-relevant intent:

- Context / Goal
- Functional Requirements (`FR-*`)
- Business Rules (`BR-*`)
- Validation Rules (`VR-*`)
- Data Requirements / Data Rules (`DR-*`)
- Error Handling (`ERR-*`)
- Acceptance Criteria (`AC-*`)
- buildable Success Criteria (`SC-*`) nếu có
- User Stories / acceptance scenarios
- Edge Cases
- Out of Scope

Không biến business KPI hoặc post-launch outcome thành implementation obligation nếu SPEC không yêu cầu buildable work.

#### From `plan.md`

Extract:

- Summary
- Technical Context
- Constitution Check
- Architectural Approach
- Components
- Data Flow
- Dependencies
- Project Structure / affected paths
- feature-specific technical decisions
- storage impact
- external integrations
- relevant Risks & Mitigations
- resolved Questions for Human / decisions

Không giả định PLAN có fixed phases hoặc full project tech stack.

#### From `tasks.md`

Parse each completed task:

- ID
- task name
- `[P]`
- `[USx]`
- `Files`
- `Est`
- `Deps`
- `Spec refs`
- `Done when`

Use TASKS for:

- file-scope hints;
- traceability;
- expected verification;
- locating implementation produced by completed tasks.

TASKS không phải authority để thêm product behavior ngoài SPEC/PLAN.

### 5. Build Intent Inventory

Build internal inventories.

#### SPEC Obligations

Stable keys for implementation-relevant:

- `FR-*`
- `BR-*`
- `VR-*`
- `DR-*`
- `ERR-*`
- `AC-*`
- buildable `SC-*`
- user-story acceptance scenario nếu không có ID riêng

#### PLAN Obligations

Record implementation-relevant:

- components;
- interfaces;
- architecture decisions;
- data/storage changes;
- external integrations;
- affected modules/files;
- technical constraints.

#### Task Traceability

Build:

```text
SPEC item -> completed task IDs
PLAN obligation -> completed task IDs
task ID -> files + Done when
```

Use explicit refs first.

### 6. Build Code Scope

Derive code scope from:

- PLAN affected paths/components;
- completed task `Files`;
- relevant contract/data-model paths;
- targeted repository search for requirement/component names.

Do not expand scope to unrelated repository areas without evidence.

Inspect current code, configuration, schema/migrations, and tests relevant to the inventory.

### 7. Assess Current Implementation

For each approved obligation, compare current code with expected intent.

Create a finding only when there is evidence of a remaining gap.

Gap types:

#### `missing`

Required behavior/artifact does not exist.

#### `partial`

Implementation exists but does not fully satisfy requirement / acceptance criterion / PLAN decision.

#### `contradicts`

Implementation conflicts with:

- SPEC;
- PLAN;
- Constitution MUST;
- explicit Out of Scope.

#### `unrequested`

Code exists without support from SPEC/PLAN.

`unrequested` handling is special:

- Nếu nó contradict explicit Out of Scope, Constitution, requirement hoặc PLAN decision → actionable.
- Nếu nó chỉ là extra code nhưng không conflict explicit intent → report informationally; **do not automatically append a removal task**.

Không dùng absence of a requirement làm đủ bằng chứng để tự quyết định xóa behavior.

### 8. Verify Finding Evidence

Mỗi actionable finding phải có:

- stable finding ID;
- gap type;
- severity;
- source ref;
- concrete evidence;
- affected file(s);
- remaining work;
- objective completion condition.

Không append task nếu:

- source ref không xác định được;
- affected scope không đủ rõ;
- remediation cần product/architecture decision mới;
- `Done when` không thể viết objectively.

Những trường hợp đó là upstream blocker, không phải implementation task.

## Severity

### CRITICAL

- Constitution MUST violation;
- contradiction gây security/data-integrity/baseline failure;
- missing core behavior làm feature không đáp ứng approved baseline.

### HIGH

- missing/partial core functional requirement;
- acceptance criterion bắt buộc chưa đạt;
- PLAN component/contract quan trọng chưa được thực hiện đúng.

### MEDIUM

- partial secondary requirement;
- non-core technical obligation;
- actionable consistency gap không block baseline.

### LOW

- minor verified gap;
- low-risk cleanup trực tiếp cần để đạt approved intent.

Không tạo remediation task chỉ để xử lý cosmetic style issue không thuộc approved intent.

## Convergence Findings Report

Trước khi write `tasks.md`, output compact report:

```text
## Convergence Findings

| ID | Gap Type | Severity | Source | Evidence | Remaining Work |
|----|----------|----------|--------|----------|----------------|
```

Summary:

- SPEC obligations checked
- PLAN obligations checked
- completed tasks inspected
- Constitution rules checked
- actionable findings
- informational `unrequested` findings
- findings by severity

Nếu có upstream blockers, liệt kê riêng:

```text
### Upstream Blockers
```

Không append task cho blocker cần clarification/design decision.

## Remediation Task Generation

### 9. Decide Outcome

Có ba outcome:

#### `CONVERGED`

Không có actionable finding và không có upstream blocker.

#### `TASKS_APPENDED`

Có actionable implementation findings đủ rõ để tạo remediation task.

#### `BLOCKED`

Có gap nhưng remediation cần thay đổi/clarify upstream artifact.

Có thể vừa có actionable findings vừa có upstream blockers:

- append chỉ những remediation task độc lập, đủ rõ;
- report blockers riêng;
- overall outcome phải nêu cả `TASKS_APPENDED + BLOCKED`.

### 10. Generate Atomic Remediation Tasks

Mỗi actionable finding phải được chuyển thành một hoặc nhiều task thỏa:

- Atomic
- Independent theo declared dependencies
- Verifiable
- `Est <= 4h`

Nếu remediation >4h:

- split thành nhiều task trước khi append.

Task name:

- action verb + object rõ ràng;
- không nhét severity/gap type/source ref vào title.

### 11. Assign Task IDs

Scan all existing task IDs.

Let:

```text
M = maximum existing numeric task ID
```

Assign:

```text
T{M+1:03d}
T{M+2:03d}
...
```

Không reuse ID.

`03d` là minimum width, không phải maximum:

```text
T999
T1000
T1001
```

đều hợp lệ.

### 12. Determine Remediation Dependencies

Cho mỗi new task:

- identify direct dependencies;
- dependency có thể trỏ tới completed existing task nếu thực sự là prerequisite;
- dependency có thể trỏ tới task mới trong cùng Convergence Pass;
- không thêm dependency chỉ để tạo thứ tự giả;
- không tạo cycle.

Nếu không có direct prerequisite:

```text
Deps: -
```

### 13. Determine Parallel Marker

`[P]` optional.

Chỉ mark `[P]` nếu remediation task:

- không phụ thuộc task khác trong same ready group;
- không sửa cùng file;
- không sửa cùng migration/schema/shared artifact có ordering;
- không có integration conflict.

Không cần `[P]` chỉ vì task có thể độc lập về logic.

### 14. Build `Spec refs`

Priority:

1. explicit SPEC requirement/criterion causing finding;
2. explicit PLAN justification cho technical-only remediation;
3. Constitution source khi remediation trực tiếp sửa violation.

Examples:

```text
Spec refs: FR-003, AC-002
```

```text
Spec refs: N/A (PLAN: Components > ReviewService)
```

```text
Spec refs: N/A (Constitution: Security II)
```

Đối với `unrequested` behavior:

- nếu contradict explicit Out of Scope → reference Out of Scope section;
- nếu không có explicit source để justify removal/review → informational only, không append task.

### 15. Build `Done when`

`Done when` phải observable và specific.

Good:

```text
Done when: duplicate review requests return 409 and the regression test passes
```

Bad:

```text
Done when: issue fixed
```

Verification có thể là:

- test pass;
- API result;
- migration behavior;
- build/lint/typecheck;
- configuration state;
- observable code path;
- contract behavior.

### 16. Append `Convergence Pass`

Nếu có remediation tasks:

Determine pass number:

- scan headings `## Convergence Pass N`;
- next pass = max N + 1;
- nếu chưa có → `1`;
- legacy headings `## Phase N: Convergence` có thể được nhận diện khi tính lịch sử, nhưng không tạo mới theo format đó.

Append:

```md
## Convergence Pass N

<!--
Generated by __SPECKIT_COMMAND_CONVERGE__ from verified remaining implementation gaps.
Existing tasks above are immutable.
-->

- [ ] T042 Fix duplicate review validation
  - Files: `src/reviews/service.py`, `tests/reviews/test_service.py`
  - Est: 2h
  - Deps: -
  - Spec refs: BR-002, AC-004
  - Done when: duplicate review is rejected and the regression test passes
  - Gap: partial
  - Severity: HIGH
  - Evidence: `src/reviews/service.py` does not enforce one-review-per-order

- [ ] T043 Add transaction boundary to ReviewService
  - Files: `src/reviews/service.py`, `tests/reviews/test_service.py`
  - Est: 2h
  - Deps: T042
  - Spec refs: N/A (PLAN: Components > ReviewService)
  - Done when: review creation is atomic and rollback behavior is covered by a passing test
  - Gap: missing
  - Severity: MEDIUM
  - Evidence: review write operations are currently performed without the planned transaction boundary
```

Required task fields remain:

- `Files`
- `Est`
- `Deps`
- `Spec refs`
- `Done when`

Convergence-specific fields are optional metadata:

- `Gap`
- `Severity`
- `Evidence`

Không append empty Convergence Pass.

## Validation Before Append

Trước khi write:

- all new IDs unique và sequential;
- every task has Files;
- every task has `Est <= 4h`;
- every task has valid Deps;
- no dependency cycle;
- every task has valid Spec ref / PLAN / Constitution justification;
- every task has objective Done when;
- no new task requires unresolved product/design decision;
- no duplicate remediation task already exists;
- task does not overlap an incomplete task — Completion Gate phải đảm bảo không có incomplete existing task;
- `[P]` markers safe.

Nếu validation fail:

- không append invalid task;
- report blocker/finding.

## After Append

Không sửa existing task summaries chỉ để reflect new pass.

Không rewrite:

- existing Dependencies section;
- existing Critical Path;
- existing Parallel Opportunities;
- existing Traceability Check.

Convergence Pass tự chứa đủ metadata để `__SPECKIT_COMMAND_ANALYZE__` và `__SPECKIT_COMMAND_IMPLEMENT__` xử lý.

## Next Actions

### On `CONVERGED`

Report:

```text
CONVERGED
```

và recommend:

- human/code review;
- PR;
- release workflow phù hợp.

Không cần `__SPECKIT_COMMAND_IMPLEMENT__` thêm cho approved scope.

### On `TASKS_APPENDED`

Report:

- Convergence Pass number;
- task IDs appended;
- total estimated remediation effort;
- dependencies;
- parallel opportunities;
- remaining upstream blockers nếu có.

Next workflow:

```text
__SPECKIT_COMMAND_ANALYZE__
    ↓ READY
__SPECKIT_COMMAND_IMPLEMENT__
    ↓
implement remediation tasks one-by-one
    ↓
all tasks complete
    ↓
__SPECKIT_COMMAND_CONVERGE__
```

Không recommend skip Analyze.

### On `BLOCKED`

Route theo artifact ownership:

- requirement/product ambiguity → `__SPECKIT_COMMAND_CLARIFY__` hoặc `__SPECKIT_COMMAND_SPECIFY__`
- technical design gap → `__SPECKIT_COMMAND_PLAN__`
- task decomposition problem → `__SPECKIT_COMMAND_TASKS__`
- Constitution issue → sửa violating artifact; chỉ dùng `__SPECKIT_COMMAND_CONSTITUTION__` nếu user thực sự muốn thay governance

Không tự invoke remediation command.

## Post-Execution Hooks

Sau khi convergence outcome đã được xác định:

- Check `.specify/extensions.yml` for `hooks.after_converge`.
- Ignore disabled hooks.
- Do not evaluate non-empty conditions here.
- Report convergence outcome trước optional hook suggestions.
- Mandatory executable hooks:
  - emit `EXECUTE_COMMAND:`
  - actually run
  - wait for completion
- Optional hooks:
  - surface command/prompt to user
- If none apply, continue silently.

## Completion Report

Report:

- outcome:
  - `CONVERGED`
  - `TASKS_APPENDED`
  - `BLOCKED`
  - `TASKS_APPENDED + BLOCKED`
- obligations checked
- actionable finding count
- informational finding count
- appended task IDs
- Convergence Pass number nếu có
- estimated remediation effort
- upstream blockers
- recommended next command

## Done When

Converge hoàn tất khi:

- current tasks được xác nhận all complete trước assessment;
- current code được so với approved SPEC + PLAN;
- findings có concrete evidence;
- no-gap case không sửa `tasks.md`;
- actionable gaps được chuyển thành valid atomic remediation tasks;
- remediation tasks có `Files`, `Est`, `Deps`, `Spec refs`, `Done when`;
- task <=4h;
- existing tasks không bị rewrite;
- unresolved design/product gaps không bị biến thành guessed implementation task;
- next workflow được report rõ ràng.
