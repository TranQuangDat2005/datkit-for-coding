---
description: Optionally publish analyzed, incomplete tasks from tasks.md as traceable GitHub issues while preserving task metadata and dependencies.
tools: ['github/github-mcp-server/list_issues', 'github/github-mcp-server/issue_write']
handoffs:
  - label: Implement Tasks
    agent: speckit.implement
    prompt: Start implementing the next ready task
    send: true

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

Supported input có thể gồm:

- một hoặc nhiều Task ID, ví dụ `T003 T004`;
- parent feature issue, ví dụ `#42`;
- không có input → xử lý toàn bộ incomplete tasks.

## Purpose

`__SPECKIT_COMMAND_TASKS__toissues` là **optional GitHub integration skill**.

Nó không thuộc core implementation flow bắt buộc.

Recommended workflow:

```text
SPEC
 ↓
PLAN
 ↓
TASKS
 ↓
ANALYZE
 ↓ READY
 ├─→ TASKSTOISSUES   (optional, nếu dùng GitHub để tracking)
 │        ↓
 └────→ IMPLEMENT
```

Ý tưởng này tương đương phần GitHub integration trong Spec Kit:

```text
TASKS.md
  +
GitHub task issues
  +
dependency links
```

Skill này tách GitHub integration ra khỏi `__SPECKIT_COMMAND_TASKS__` để core SDD workflow không phụ thuộc GitHub.

## Goal

Chuyển các task chưa hoàn thành trong `tasks.md` thành GitHub issues có traceability.

Mỗi issue phải giữ được khi có:

- Task ID
- task name
- `Files`
- `Est`
- `Deps`
- `Spec refs`
- `Done when`
- `[P]`
- `[USx]`
- Convergence metadata:
  - `Gap`
  - `Severity`
  - `Evidence`

Default:

```text
tasks.md
   ↓
parse incomplete tasks
   ↓
validate
   ↓
deduplicate existing issues
   ↓
create prerequisite issues first
   ↓
create dependent issues
   ↓
report Task ID → GitHub Issue
```

## Operating Constraints

### Optional Integration

- Không bắt buộc project phải dùng GitHub Issues.
- Không block core Spec Kit workflow chỉ vì skill này chưa được chạy.
- Nếu project không cần GitHub tracking, skip skill này.

### Recommended Timing

Nên chạy sau khi `__SPECKIT_COMMAND_ANALYZE__` đã kết luận task set đủ sẵn sàng để implementation.

Không khuyến khích tạo issues từ task list còn đang thay đổi mạnh.

### Read-only Artifacts

Skill **MUST NOT** modify:

- `spec.md`
- `plan.md`
- `tasks.md`
- source code

Skill chỉ tạo GitHub issues.

### Task Identity

Task ID là identity ổn định:

```text
T001
T002
...
T1000
```

Match:

```text
T\d{3,}
```

Không dùng title text, heading, phase hoặc User Story làm identity.

### Repository Safety

Repository chỉ được derive từ:

```text
git config --get remote.origin.url
```

Không đoán repository từ:

- folder name;
- package metadata;
- current conversation;
- parent issue URL không khớp remote.

Nếu remote không phải GitHub hoặc không resolve chắc chắn được owner/repo:

- **STOP**
- không tạo issue.

## Pre-Execution Hooks

Check `.specify/extensions.yml` nếu tồn tại.

Read:

```text
hooks.before_taskstoissues
```

Rules:

- ignore `enabled: false`;
- enabled mặc định nếu thiếu field;
- không evaluate non-empty `condition`;
- optional hook → surface command/prompt;
- mandatory hook không có condition → emit `EXECUTE_COMMAND:` và thực sự invoke trước khi tiếp tục;
- invalid YAML → KHÔNG skip im lặng: báo cho user rằng `.specify/extensions.yml` không đọc được (kèm parser error), không hook nào được check (kể cả các hook mandatory `optional: false` đã đăng ký), sau đó tiếp tục bình thường.

## Execution

### 1. Initialize Context

Run:

```text
{SCRIPT}
```

Parse:

- `FEATURE_DIR`
- `AVAILABLE_DOCS`

Resolve:

```text
TASKS = FEATURE_DIR/tasks.md
```

Nếu `tasks.md` không tồn tại:

- **STOP**
- recommend `__SPECKIT_COMMAND_TASKS__`.

Load Constitution nếu tồn tại để tuân thủ governance/process constraints.

### 2. Resolve GitHub Repository

Run:

```text
git config --get remote.origin.url
```

Support common GitHub forms:

```text
https://github.com/<owner>/<repo>.git
git@github.com:<owner>/<repo>.git
ssh://git@github.com/<owner>/<repo>.git
```

Resolve exact:

- owner
- repository

Strip trailing `.git` khi cần.

Nếu không chắc chắn:

- **STOP**.

### 3. Parse Real Task Blocks

Chỉ parse task có header dạng:

```text
- [ ] T001 ...
- [x] T001 ...
- [X] T001 ...
```

Task ID:

```text
T\d{3,}
```

Không coi checkbox khác trong file là task.

Extract:

- status
- ID
- name
- `[P]` nếu có
- `[USx]` nếu có
- `Files`
- `Est`
- `Deps`
- `Spec refs`
- `Done when`

Nếu task đến từ Convergence Pass, extract thêm nếu có:

- `Gap`
- `Severity`
- `Evidence`

### 4. Select Tasks

Default:

```text
[ ]  → selected
[x]  → skip
[X]  → skip
```

Nếu `{ARGS}` chứa Task ID:

- chỉ xử lý các ID được yêu cầu;
- ID phải tồn tại;
- completed task vẫn skip mặc định.

Nếu không có incomplete task:

```text
NO OPEN TASKS TO CONVERT
```

và không gọi issue creation.

### 5. Validate Selected Tasks

Mỗi selected task phải có:

- valid unique Task ID;
- clear task name;
- `Files`;
- `Est`;
- `Deps`;
- `Spec refs`;
- `Done when`.

Validate:

- `Est <= 4h`;
- every dependency ID exists trong `tasks.md`;
- no self-dependency;
- no dependency cycle;
- no unresolved placeholder.

Invalid task:

- không tạo issue;
- report `INVALID`;
- recommend `__SPECKIT_COMMAND_ANALYZE__` hoặc `__SPECKIT_COMMAND_TASKS__`.

Không tự sửa task.

## Existing Issue Deduplication

### 6. Build Target ID Set

Ví dụ:

```text
T004
T005
T006
```

### 7. Fetch Existing Issues

Use GitHub `list_issues` trên exact repository.

Requirements:

- include open + closed issues nếu tool hỗ trợ bằng cách omit state;
- paginate;
- prefer page size `100`;
- stop khi:
  - mọi target ID đã match; hoặc
  - không còn page.

Match issue titles bằng:

```text
\bT\d{3,}\b
```

Recognize:

```text
T001: Create entity
T001 Create entity
[T001] Create entity
```

Task ID là dedup key.

### 8. Skip Existing

Nếu task đã có issue:

- không tạo duplicate;
- preserve existing issue;
- record mapping;
- report `SKIPPED_EXISTING`.

Không rewrite issue chỉ để body giống format mới.

## Dependency-aware Creation

### 9. Determine Creation Order

Create issue theo dependency order.

Rules:

- prerequisite issue trước dependent issue;
- file order dùng làm deterministic tie-breaker;
- không dùng section/group order như dependency.

Nếu dependency task đã completed nhưng không có GitHub issue:

- coi dependency là satisfied;
- không tạo historical issue chỉ để lấy link.

### 10. Canonical Issue Title

Use:

```text
T001: <task name>
```

Không đưa vào title:

- `[P]`
- `[USx]`
- `Est`
- `Deps`
- `Severity`
- `Gap`

## Issue Body

### 11. Build Body

Use:

```md
## Task

<task name>

## Files

- `<path>`

## Estimate

`<Est>`

## Dependencies

<dependency list or None>

## Spec Refs

<spec refs>

## Done When

<exact Done when>

## Metadata

- Parallelizable: Yes | No
- User Story: US1 | None
- Source: `tasks.md`
```

### 12. Dependencies

Nếu:

```text
Deps: -
```

render:

```md
## Dependencies

None
```

Nếu dependency có GitHub issue:

```text
- T001 — #43
```

Nếu dependency đã completed nhưng không có issue:

```text
- T001 — completed in tasks.md
```

Nếu chưa resolve được GitHub mapping:

```text
- T001 — task dependency
```

Không invent issue number.

### 13. Spec Refs

Preserve refs từ task.

Examples:

```text
FR-001, BR-002, AC-001
```

hoặc:

```text
N/A (PLAN: Components > ReviewService)
```

Không tự infer/rewrite refs trong skill này.

### 14. Parallel Marker

`[P]`:

```text
Parallelizable: Yes
```

Không có `[P]`:

```text
Parallelizable: No
```

`[P]` không tạo GitHub dependency và không bắt buộc concurrent execution.

### 15. User Story Marker

`[US1]`:

```text
User Story: US1
```

Không có marker:

```text
User Story: None
```

Không infer từ heading.

### 16. Convergence Context

Nếu có:

```text
Gap
Severity
Evidence
```

append:

```md
## Convergence Context

- Gap: `<gap>`
- Severity: `<severity>`
- Evidence: <evidence>
```

Không đưa các field này vào issue title.

## Parent Feature Issue

### 17. Optional Parent Issue

Nếu `{ARGS}` cung cấp parent issue, ví dụ:

```text
#42
```

thì:

- verify issue thuộc exact repository;
- nếu GitHub tool hỗ trợ parent/sub-issue relationship, attach task issue làm sub-issue;
- nếu tool không hỗ trợ relationship:
  - không giả lập capability;
  - ghi parent reference trong issue body khi phù hợp.

Không tự đoán parent issue.

## Create Issues

### 18. Create Missing Issues

For each selected task chưa có existing issue:

- create trong exact remote repository;
- use canonical title;
- use full body;
- process dependency-first;
- record returned issue number/URL.

Maintain:

```text
issue_by_task_id[Txxx]
```

để dependent task có thể reference prerequisite issue.

### 19. Failure Handling

Nếu create issue fail:

- record `FAILED`;
- không retry vô hạn;
- không sửa `tasks.md`.

Dependent issue vẫn có thể được tạo nếu task dependency trong `tasks.md` hợp lệ, nhưng dependency body chỉ dùng Task ID nếu GitHub issue link chưa resolve được.

Không thay đổi dependency semantics chỉ vì GitHub API/tool failure.

## Post-Execution Hooks

Check:

```text
hooks.after_taskstoissues
```

Rules giống pre-hook:

- ignore disabled;
- do not evaluate non-empty conditions;
- mandatory executable hook → emit `EXECUTE_COMMAND:` và run;
- optional hook → surface;
- invalid YAML → KHÔNG skip im lặng: báo cho user rằng `.specify/extensions.yml` không đọc được (kèm parser error), không hook nào được check (kể cả các hook mandatory `optional: false` đã đăng ký), sau đó tiếp tục sang Completion Report.

## Completion Report

Report:

```text
## Tasks to Issues Report
```

Include:

- repository
- parent feature issue nếu có
- incomplete tasks discovered
- issues created
- existing issues skipped
- completed tasks skipped
- invalid tasks
- failures
- Task ID → Issue mapping
- unresolved dependency links
- convergence tasks included nếu có

Example:

```text
Repository: owner/repo
Parent: #42

Created:
- T003 → #43
- T004 → #44

Skipped existing:
- T002 → #41

Skipped completed:
- T001

Invalid:
- None

Failed:
- None

Unresolved dependency links:
- None
```

## Next Action

Sau khi sync issues:

Recommended:

```text
__SPECKIT_COMMAND_IMPLEMENT__
```

để thực thi task READY tiếp theo.

Skill này **không** tự implement và **không** mark task complete.

## Done When

- [ ] repository được resolve an toàn từ git remote
- [ ] chỉ real incomplete tasks được selected
- [ ] selected tasks được validate
- [ ] duplicate issues không được tạo
- [ ] issues được tạo dependency-first
- [ ] issue title theo `Txxx: <task name>`
- [ ] issue body giữ `Files`, `Est`, `Deps`, `Spec refs`, `Done when`
- [ ] `[P]` và `[USx]` được preserve
- [ ] Convergence metadata được preserve khi có
- [ ] parent/sub-issue chỉ dùng khi tool hỗ trợ
- [ ] `tasks.md` không bị sửa
- [ ] completion report được trả về
