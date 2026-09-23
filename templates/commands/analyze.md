---
description: Perform a read-only cross-artifact consistency and task-quality analysis across spec.md, plan.md, and tasks.md before implementation.

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

**Check for extension hooks (before analysis)**:

- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read entries under `hooks.before_analyze`.
- If YAML is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally.
- Ignore hooks with `enabled: false`.
- Hooks without `enabled` are enabled by default.
- Do not evaluate non-empty `condition` expressions here.
- If a hook has no condition, or condition is empty:
  - Optional hook: show command and prompt to the user.
  - Mandatory hook: emit `EXECUTE_COMMAND:` and actually run it before continuing.
- If no hooks are available, continue silently.

## Goal

Kiểm tra tính nhất quán và mức sẵn sàng để implementation của:

- `spec.md`
- `plan.md`
- `tasks.md`
- project Constitution / constraints có liên quan

`__SPECKIT_COMMAND_ANALYZE__` là **read-only gate** chạy sau `__SPECKIT_COMMAND_TASKS__` và trước `__SPECKIT_COMMAND_IMPLEMENT__`.

Mục tiêu không phải viết lại artifact, mà là phát hiện:

- requirement bị thiếu hoặc mâu thuẫn;
- PLAN không phản ánh SPEC;
- TASKS không cover PLAN/SPEC;
- task không đúng schema;
- task quá lớn hoặc không verifiable;
- dependency sai hoặc có cycle;
- `[P]` được gắn sai;
- orphan task;
- constitution violation;
- unresolved ambiguity có thể làm implementation phải đoán.

## Operating Constraints

### Read-only

**STRICTLY READ-ONLY**:

- Không sửa `spec.md`.
- Không sửa `plan.md`.
- Không sửa `tasks.md`.
- Không sửa source code.
- Không tự “fix” artifact trong quá trình analyze.
- Chỉ output analysis report và hướng remediation.

### Source Authority

Dùng authority order sau:

1. Constitution cho governance constraints.
2. SPEC cho product intent, scope, requirement, business rule và acceptance criteria.
3. PLAN cho approved technical approach, components, dependencies và affected structure.
4. TASKS cho implementation decomposition của SPEC + PLAN.
5. `AGENTS.md` / referenced project constraints cho project-wide conventions và technical baseline.

Không được dùng TASKS để thay đổi nghĩa của SPEC hoặc PLAN.

Nếu artifacts mâu thuẫn, report conflict thay vì tự reconcile.

## Execution Steps

### 1. Initialize Analysis Context

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

Nếu thiếu artifact:

- missing SPEC → hướng dẫn chạy `__SPECKIT_COMMAND_SPECIFY__`
- missing PLAN → hướng dẫn chạy `__SPECKIT_COMMAND_PLAN__`
- missing TASKS → hướng dẫn chạy `__SPECKIT_COMMAND_TASKS__`

Không produce partial readiness result nếu thiếu core artifact.

### 2. Load Project Context

Load nếu tồn tại:

- root-level `AGENTS.md`
- `.specify/memory/constitution.md`
- project constraint/context files được chúng tham chiếu và liên quan tới feature

Rules:

- Không yêu cầu PLAN lặp lại project-wide tech stack đã nằm trong project context.
- Nếu project context conflict, Constitution có authority cao hơn.
- Nếu conflict không thể resolve theo authority trên, report.

### 3. Load Core Artifacts

Load đủ nội dung cần thiết để kiểm tra, nhưng tránh dump raw artifact vào output.

#### From `spec.md`

Extract nếu có:

- Context / Goal
- Actors / Roles
- User Stories
- Functional Requirements (`FR-*`)
- Business Rules (`BR-*`)
- Validation Rules (`VR-*`)
- Data Requirements / Data Rules (`DR-*`)
- Error Handling (`ERR-*`)
- Acceptance Criteria (`AC-*`)
- Success Criteria (`SC-*`) nếu template có
- Edge Cases
- Out of Scope
- unresolved clarification / placeholder

Chỉ coi Success Criteria là implementation obligation khi nó thực sự yêu cầu buildable work.
Không biến business KPI hoặc post-launch outcome thành task requirement nếu SPEC không yêu cầu implementation tương ứng.

#### From `plan.md`

Extract nếu có:

- Summary
- Technical Context
- Constitution Check
- Architectural Approach
- Components
- Data Flow
- Dependencies
- Project Structure / affected paths
- Risks & Mitigations
- Questions for Human
- Complexity Tracking
- `NEEDS CLARIFICATION`
- Status / approval state nếu có

Không giả định PLAN phải chứa toàn bộ tech stack.

#### From `tasks.md`

Parse **mỗi real task** theo schema:

```text
- [ ] T001 [P?] [US?] <Action + object>
  - Files: ...
  - Est: ...
  - Deps: ...
  - Spec refs: ...
  - Done when: ...
```

Extract:

- completion state: `[ ]` / `[x]` / `[X]`
- Task ID
- task name / description
- `[P]`
- `[USx]`
- `Files`
- `Est`
- `Deps`
- `Spec refs`
- `Done when`
- group/subheading nếu có

Ngoài task, đọc:

- Dependencies & Execution Order
- Critical Path
- Parallel Opportunities
- Traceability Check
- Uncovered Items

Không coi checkbox ngoài real task syntax `T\d{3,}` là implementation task.

### 4. Build Internal Models

Build internal representations; không output raw model trừ khi cần giải thích finding.

#### Requirements Inventory

Tạo stable key cho các implementation-relevant item:

- `FR-*`
- `BR-*`
- `VR-*`
- `DR-*`
- `ERR-*`
- `AC-*`
- buildable `SC-*`
- user-story acceptance scenarios nếu không có ID riêng

#### PLAN Inventory

Record:

- component name
- responsibility
- interface / input-output
- affected files/modules
- implementation dependency
- architecture decision
- storage/integration impact

Chỉ những PLAN item tạo implementation obligation mới cần task coverage.

#### Task Inventory

Cho mỗi task record:

- ID
- status
- name
- files
- estimate
- dependencies
- spec refs
- PLAN justification nếu `Spec refs: N/A`
- done criteria
- parallel marker
- user-story marker

#### Dependency Graph

Build directed graph:

```text
A -> B
```

nghĩa là `B` phụ thuộc `A`.

#### Traceability Maps

Build:

```text
SPEC item -> task IDs
PLAN component -> task IDs
task ID -> SPEC refs / PLAN justification
```

Ưu tiên explicit `Spec refs`.

Chỉ dùng semantic/keyword inference như fallback khi explicit reference thiếu hoặc sai, và phải đánh dấu mapping đó là **inferred**, không coi là authoritative.

## Detection Passes

Tập trung high-signal findings. Tối đa 50 findings; phần dư aggregate trong overflow summary.

### A. Artifact Readiness

Flag:

- unresolved `NEEDS CLARIFICATION`
- unresolved `Questions for Human`
- important placeholder còn sót
- PLAN status chưa approved nếu status field tồn tại
- unjustified Constitution violation
- `Uncovered Items` trong tasks.md khác `None`

Không flag các marker hợp lệ như:

- `[P]`
- `[US1]`
- `[ ]`
- `[x]`

### B. SPEC ↔ PLAN Consistency

Check:

- mỗi PLAN component có justification từ SPEC hoặc project constraints;
- PLAN không introduce product behavior ngoài SPEC;
- data/entity naming nhất quán;
- external integration không xuất hiện vô căn cứ;
- architecture decision không conflict requirement;
- Out of Scope không bị PLAN đưa trở lại scope;
- technical decision không conflict Constitution / AGENTS constraints.

### C. Task Schema Quality

Mỗi real task phải có:

- sequential Task ID;
- clear action-oriented task name;
- `Files`;
- `Est`;
- `Deps`;
- `Spec refs`;
- `Done when`.

Flag:

- duplicate Task ID;
- skipped/non-sequential ID khi không có lý do;
- missing field;
- placeholder field;
- invalid `Est`;
- `Est > 4h`;
- vague task name;
- file path quá mơ hồ khi PLAN/repository cho phép xác định cụ thể.

### D. Atomic / Independent / Verifiable Quality

#### Atomic

Flag task có dấu hiệu quá rộng, ví dụ:

- `Est > 4h`;
- gom nhiều component không liên quan;
- task description chứa nhiều deliverable độc lập có thể tách;
- sửa nhiều layer không cần thiết trong cùng task mà không có lý do.

Không tự khẳng định task “không atomic” chỉ vì sửa nhiều file; dùng evidence cụ thể.

#### Independent

Check:

- mọi dependency cần thiết được khai báo;
- task không ngầm yêu cầu output của task khác nhưng `Deps` lại thiếu;
- direct dependencies đủ để task có thể bắt đầu;
- không dùng phase/group order như dependency ngầm.

#### Verifiable

`Done when` phải observable/testable.

Flag các dạng mơ hồ như:

- "works"
- "completed"
- "done"
- "looks good"
- "implemented successfully"

nếu không có điều kiện kiểm chứng cụ thể.

### E. Dependency Graph Validation

Check:

- mọi `Deps` ID tồn tại;
- không self-dependency;
- không duplicate dependency;
- prerequisite xuất hiện hợp lý trước dependent;
- không dependency cycle;
- dependency summary không conflict metadata trong từng task;
- Critical Path nếu được ghi phải phù hợp graph;
- không có artificial dependency chỉ để ép phase order nếu task thực sự independent.

Cycle là **CRITICAL** vì implementation order không thể resolve.

### F. Parallel Safety

Với task có `[P]`, validate:

- không phụ thuộc trực tiếp hoặc gián tiếp vào task khác trong cùng parallel group;
- không sửa cùng file;
- không sửa cùng migration;
- không sửa cùng schema/shared artifact có ordering requirement;
- không cần output chưa hoàn tất của task khác trong group;
- không có integration conflict rõ ràng.

Nếu `[P]` sai:

- report task ID;
- chỉ ra conflict;
- recommend bỏ `[P]` hoặc thêm dependency phù hợp.

Không yêu cầu task phải có `[P]` chỉ vì nó có thể parallelize; `[P]` là optimization marker.

### G. SPEC Coverage

Check:

- mọi implementation-relevant SPEC item có ít nhất một task;
- acceptance criterion cần code/test work được cover;
- requirement security/performance/reliability có buildable obligation được phản ánh trong task;
- không silently bỏ edge case bắt buộc.

Requirement không có task là:

- CRITICAL nếu block baseline/core behavior;
- HIGH nếu requirement bắt buộc nhưng không block toàn feature;
- MEDIUM nếu supporting/non-core concern.

### H. PLAN Coverage

Check:

- mọi PLAN component cần implementation có ít nhất một task;
- PLAN dependency/integration/storage impact có task tương ứng nếu cần code/config/schema work;
- affected structure không chứa planned change hoàn toàn không xuất hiện trong tasks.

Điều này là independent với SPEC coverage:

```text
SPEC -> PLAN
PLAN -> TASKS
```

Cả hai chain đều phải hợp lệ.

### I. Orphan Task Detection

Task là orphan nếu:

- không map tới SPEC requirement; và
- không có valid `N/A (PLAN: <section/component>)` justification; và
- không được project constraint yêu cầu.

Flag task thêm scope, architecture hoặc dependency mới.

Technical prerequisite hợp lệ **không phải orphan** nếu PLAN justification tồn tại và đúng.

### J. Traceability Reference Validation

Check explicit `Spec refs`:

- referenced ID tồn tại;
- referenced section đúng ý nghĩa task;
- không reference requirement không liên quan chỉ để tránh orphan;
- `[USx]` nếu có phải tồn tại trong SPEC;
- `N/A (PLAN: ...)` phải trỏ đến section/component tồn tại trong PLAN.

Nếu explicit ref sai, không silently thay bằng inferred mapping; report mismatch.

### K. Duplication & Ambiguity

Check high-impact cases:

- duplicate requirements;
- contradictory requirements;
- terminology drift;
- vague security/performance/reliability requirement;
- contradictory task descriptions;
- duplicate tasks thực hiện cùng deliverable;
- same output file/task responsibility bị chia chồng lấn mà không có dependency rõ.

Không ưu tiên style-only findings nếu có execution-blocking issue quan trọng hơn.

### L. Constitution Alignment

Check:

- SPEC, PLAN hoặc TASKS conflict với Constitution MUST;
- required quality/security/process gate bị thiếu;
- task yêu cầu thực hiện forbidden pattern;
- PLAN-approved exception không có justification nếu Constitution yêu cầu.

Constitution MUST violation luôn **CRITICAL**.

## Severity Assignment

Use:

### CRITICAL

- Constitution MUST violation
- unresolved blocker khiến implementation phải đoán
- dependency cycle
- missing core requirement coverage
- SPEC ↔ PLAN contradiction làm thay đổi expected behavior
- task làm ngoài scope theo cách có thể gây breaking/security/data issue

### HIGH

- required task missing
- PLAN component không được cover
- orphan task thêm behavior/dependency mới
- `Est > 4h`
- invalid dependency làm task không thể chạy đúng
- `[P]` tạo file/schema/resource conflict
- `Done when` không đủ để verify task quan trọng
- explicit `Spec refs` sai

### MEDIUM

- missing metadata không block execution hoàn toàn
- weak traceability có thể infer nhưng chưa explicit
- terminology drift
- non-core requirement coverage gap
- likely non-atomic task nhưng chưa vượt 4h
- unnecessary dependency làm mất parallel opportunity

### LOW

- wording/style issue
- minor redundancy
- optional optimization
- cosmetic organization issue không ảnh hưởng correctness

## Implementation Readiness Gate

Sau detection, derive một trong hai trạng thái:

### READY

Chỉ khi:

- không có CRITICAL;
- không có HIGH issue làm implementation unsafe hoặc ambiguous;
- dependency graph valid;
- core SPEC coverage complete;
- PLAN implementation coverage complete;
- task schema đủ để executor hiểu;
- không còn unresolved blocker.

### BLOCKED

Nếu bất kỳ điều kiện READY nào không đạt.

`READY` không có nghĩa code chắc chắn đúng; chỉ nghĩa artifacts đủ nhất quán để bắt đầu implementation mà không phải đoán các quyết định quan trọng.

## Analysis Report

Output report theo structure:

```text
## Spec Kit Analysis Report

**Implementation Readiness**: READY | BLOCKED

### Findings
...

### SPEC Coverage
...

### PLAN Coverage
...

### Task Quality
...

### Dependency Graph
...

### Parallel Safety
...

### Constitution Alignment
...

### Metrics
...

### Next Actions
...
```

### Findings Table

Use:

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|---|---|---|---|---|---|

Finding IDs phải deterministic theo category, ví dụ:

- `AR-*` Artifact Readiness
- `SP-*` SPEC/PLAN
- `TS-*` Task Schema
- `AQ-*` Atomic/Quality
- `DG-*` Dependency Graph
- `PA-*` Parallel
- `SC-*` SPEC Coverage
- `PC-*` PLAN Coverage
- `OR-*` Orphan
- `TR-*` Traceability
- `CA-*` Constitution
- `DA-*` Duplication/Ambiguity

### SPEC Coverage Table

| Requirement | Covered? | Task IDs | Mapping |
|---|---:|---|---|

`Mapping`:

- `explicit`
- `inferred`
- `none`

### PLAN Coverage Table

| PLAN Component / Obligation | Covered? | Task IDs | Notes |
|---|---:|---|---|

### Task Quality Table

Chỉ include task có issue hoặc khi user yêu cầu full matrix.

| Task | Est | Deps Valid | Spec Ref Valid | Done When | Parallel Safe | Status |
|---|---:|---:|---:|---:|---:|---|

### Dependency Graph Summary

Report:

- total nodes
- total dependency edges
- root/ready tasks
- cycle status
- invalid/missing refs
- critical path consistency nếu applicable

Không cần render graph lớn trừ khi user yêu cầu.

### Metrics

Include:

- Total SPEC obligations
- SPEC obligations covered
- SPEC Coverage %
- Total PLAN implementation obligations
- PLAN obligations covered
- PLAN Coverage %
- Total tasks
- Tasks > 4h
- Tasks missing required metadata
- Orphan tasks
- Invalid dependency refs
- Dependency cycles
- `[P]` tasks
- Unsafe `[P]` tasks
- Invalid explicit Spec refs
- Critical findings
- High findings

## Next Actions

Đưa recommendation theo **artifact ownership**:

- SPEC issue → `__SPECKIT_COMMAND_CLARIFY__` hoặc `__SPECKIT_COMMAND_SPECIFY__` tùy loại thay đổi.
- PLAN issue → `__SPECKIT_COMMAND_PLAN__`.
- TASK decomposition/schema issue nhưng SPEC/PLAN đúng → `__SPECKIT_COMMAND_TASKS__`.
- Constitution issue → `__SPECKIT_COMMAND_CONSTITUTION__` chỉ khi user thực sự muốn thay governance; nếu không thì sửa artifact vi phạm.
- Nếu READY → `__SPECKIT_COMMAND_IMPLEMENT__`.

Không mặc định recommend “manually edit tasks.md” vì task list phải được regenerate từ approved upstream artifacts khi decomposition sai.

Không tự invoke remediation command.

## Post-Execution Hooks

Sau khi report:

- Check `.specify/extensions.yml` for `hooks.after_analyze`.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue.
- Ignore disabled hooks.
- Do not evaluate non-empty conditions here.
- Mandatory executable hooks:
  - emit `EXECUTE_COMMAND:`
  - actually run
  - wait for completion
- Optional hooks:
  - surface command/prompt to user
- If none apply, continue silently.

## Operating Principles

### Deterministic Analysis

- Cùng artifacts → cùng inventory/counts/finding IDs khi có thể.
- Ưu tiên explicit IDs và direct metadata.
- Inference chỉ là fallback và phải được label.

### High Signal

- Ưu tiên blocker, coverage gap, dependency issue và traceability issue.
- Không flood report bằng style-only findings.
- Limit 50 findings; aggregate overflow.

### No Silent Repair

- Không tự thay ref sai.
- Không tự thêm missing dependency.
- Không tự split task.
- Không tự đổi `[P]`.
- Không tự sửa SPEC/PLAN/TASKS.
- Chỉ report recommendation.

### Respect Task Semantics

Task tốt phải được đánh giá theo:

- Atomic
- Independent
- Verifiable
- `Est <= 4h`
- explicit dependencies
- traceability
- observable completion condition

## Context

{ARGS}
