---
description: "Dependency-ordered task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Approved design artifacts from `/specs/[###-feature-name]/`

**Required**:
- `spec.md`
- `plan.md`

**Optional**:
- `research.md`
- `data-model.md`
- `contracts/`
- `quickstart.md`


## Legend

Phần này dùng để reviewer đọc `tasks.md` mà không cần biết trước quy ước của Spec Kit.

- `- [ ]`: Task chưa hoàn thành.
- `- [x]`: Task đã hoàn thành.
- `T001`, `T002`, ...: ID tuần tự của task.
- `[P]`: Task **có thể chạy song song an toàn** với task khác khi các `Deps` của nó đã hoàn tất. `[P]` không có nghĩa là bắt buộc phải chạy song song.
- `[US1]`, `[US2]`, ...: Task được liên kết với User Story tương ứng để traceability. Ký hiệu này là optional.
- `Files`: File hoặc thư mục dự kiến được tạo/sửa bởi task.
- `Est`: Estimated effort của task. Mỗi task phải `<= 4h`.
- `Deps`: Direct dependencies. Task chỉ được bắt đầu khi các task được liệt kê ở đây đã hoàn thành.
- `Deps: -`: Task không có dependency trước đó và có thể bắt đầu ngay nếu không bị chặn bởi điều kiện khác.
- `Spec refs`: Requirement/section trong SPEC mà task triển khai, ví dụ `FR-001`, `BR-002`, `VR-001`, `DR-001`, `AC-001`.
- `N/A (PLAN: <section/component>)`: Task mang tính kỹ thuật không có direct SPEC requirement nhưng được yêu cầu bởi PLAN.
- `Done when`: Điều kiện kiểm chứng để xác nhận task thực sự hoàn thành.
- `A -> B`: `B` phụ thuộc vào `A`; `A` phải hoàn thành trước `B`.
- `Critical Path`: Chuỗi dependency quyết định thời gian hoàn thành sớm nhất của toàn feature; chậm một task trên chuỗi này sẽ làm chậm toàn feature.
- `Parallel Group`: Nhóm task có thể chạy concurrent sau khi điều kiện bắt đầu của nhóm được đáp ứng.


<!--
TASKS.md chuyển SPEC + PLAN đã được approve thành các đơn vị triển khai cụ thể.

Mỗi task phải:
- Atomic
- Independent theo declared dependencies
- Verifiable
- Estimated <= 4h

Không thêm requirement, product scope, architecture hoặc dependency mới trong TASKS.md.
Nếu phát hiện gap trong SPEC/PLAN, dừng và báo gap thay vì tự suy đoán.

Dependency order là nguồn quyết định thứ tự thực thi.
Không bắt buộc cấu trúc cố định kiểu Setup -> Foundational -> User Story -> Polish.

Có thể group task theo:
- logical component
- user story
- CORE/SHELL

nhưng grouping không được che khuất dependency thực tế.

[P] = task có thể chạy song song an toàn.
[P] không có nghĩa task bắt buộc phải chạy song song.

[USx] chỉ dùng cho traceability khi task map rõ vào user story.
Không bắt buộc mọi task phải có [USx].

Nếu PLAN có CORE/SHELL classification thì giữ lại.
Nếu PLAN không có thì không tự tạo thêm.

QUAN TRỌNG:
- Template này không chứa sample task thật.
- Lệnh __SPECKIT_COMMAND_TASKS__ phải tạo task thật từ:
  - User story trong spec.md (kèm priority P1, P2, P3...)
  - Requirement trong plan.md
  - Entity trong data-model.md
  - Endpoint trong contracts/
- Khi generate tasks.md, phải xóa toàn bộ placeholder/instructional text không còn cần thiết.
- Generated tasks.md chỉ chứa task thật và các summary section bên dưới.
-->

## Task Format

<!--
Mỗi task phải có format:

- [ ] Txxx [P?] [US?] <Action + object>
  - Files: <exact path(s)>
  - Est: <time, max 4h>
  - Deps: <task IDs or ->
  - Spec refs: <SPEC refs, or N/A with PLAN justification>
  - Done when: <specific, verifiable completion condition>

Rules:
- ID tuần tự: T001, T002, ...
- Tên task bắt đầu bằng action verb rõ ràng.
- Files dùng đường dẫn thực tế khi có thể xác định.
- Est bắt buộc và tối đa 4h.
- Deps chỉ ghi direct dependencies.
- Nếu không có dependency, ghi: -
- Spec refs dùng FR/BR/VR/DR/AC/EARS/section refs khi có.
- Technical-only task không có direct SPEC ref:
  N/A (PLAN: <section/component>)
- Done when bắt buộc và phải kiểm chứng được.
-->

## Tasks

<!--
GENERATE REAL TASKS HERE.

Sắp xếp theo dependency order.

Có thể tạo các subheading phù hợp với feature, ví dụ:
- component/module
- user story
- CORE/SHELL

Không tạo phase cố định nếu feature không cần.

Không giữ placeholder hoặc sample task trong generated tasks.md.
-->

[GENERATED TASKS]

## Dependencies & Execution Order

<!--
Tóm tắt các dependency chain quan trọng.

Chỉ ghi direct/meaningful chains, không cần lặp toàn bộ metadata của từng task.

Ví dụ biểu diễn logic:
T001, T002 -> T003 -> T004
-->

[DEPENDENCY CHAINS]

### Critical Path

<!--
Ghi critical path khi có ý nghĩa.
Nếu không có hoặc không cần xác định, ghi None.
-->

[CRITICAL PATH OR None]

## Parallel Opportunities

<!--
Chỉ liệt kê task groups thực sự an toàn để chạy concurrent.

Một nhóm parallel chỉ hợp lệ khi:
- không phụ thuộc nhau trong group
- không sửa cùng file
- không sửa cùng migration/schema/shared artifact
- không cần output chưa hoàn tất của task khác
- không tạo integration conflict

Nếu không có parallel opportunity có ý nghĩa, ghi None.
-->

[PARALLEL GROUPS OR None]

## Traceability Check

### PLAN Coverage

<!--
Mọi PLAN component cần implementation phải map tới ít nhất một task.

Format:
<PLAN component> -> Txxx, Txxx
-->

[PLAN COVERAGE]

### SPEC Coverage

<!--
Mọi requirement cần implementation phải được cover.

Format:
<FR/BR/VR/DR/AC/EARS/section> -> Txxx, Txxx
-->

[SPEC COVERAGE]

### Uncovered Items

<!--
Nếu không có gap, ghi None.

Nếu có gap khiến implementation không thể quyết định:
- mô tả gap
- chỉ ra source section
- không tự invent behavior
-->

[UNCOVERED ITEMS OR None]

## Execution Notes

- Ưu tiên `1 task = 1 focused agent session`.
- Chỉ execute task khi toàn bộ `Deps` đã complete.
- `[P]` chỉ biểu thị safe concurrency, không phải yêu cầu phải chạy song song.
- Không sửa SPEC hoặc PLAN trong lúc implementation chỉ để task dễ thực hiện hơn.
- Nếu implementation phát hiện spec/plan gap, dừng và report.
- Commit sau mỗi task hoặc logical group khi phù hợp.

<!--
VALIDATION BEFORE COMPLETION — không render thành markdown checkbox trong generated tasks.md:

- Task IDs sequential
- Every task has Files
- Every task has Est <= 4h
- Every task has Deps
- Every dependency ID exists
- No dependency cycle
- Every task has Spec refs or PLAN justification
- Every task has Done when
- Every PLAN component is covered
- No orphan task
- [P] markers are dependency-safe and file-safe
- No unresolved implementation-blocking gap
-->
