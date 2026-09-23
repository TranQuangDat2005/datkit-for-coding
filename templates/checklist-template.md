# [CHECKLIST TYPE] Checklist: [FEATURE NAME]

**Purpose**: [Requirements-quality focus of this checklist]  
**Created**: [DATE]  
**Feature**: [Link/path to spec.md]

**Ownership**: Reviewer-owned
(`reviewer-owned` = reviewer quyết định item đã đạt hay chưa; agent không tự mark `[x]`).

**Marker Semantics**:
`[x]` nghĩa là tiêu chí về **requirements quality** đã được reviewer xác nhận đạt.
Nó **không** có nghĩa implementation đã hoàn thành.

**Gate Behavior**:
Custom checklist là **advisory** mặc định
(`advisory` = hỗ trợ review, không tự động chặn workflow).
Nó chỉ trở thành **mandatory gate**
(`mandatory gate` = điều kiện bắt buộc phải đạt trước khi workflow đi tiếp)
khi Constitution, project policy, hoặc explicit user instruction yêu cầu.

## Marker Definitions

- `Completeness` (độ đầy đủ): requirement cần thiết đã được ghi đủ.
- `Clarity` (độ rõ ràng): wording cụ thể và không mơ hồ.
- `Consistency` (tính nhất quán): requirement không mâu thuẫn với requirement khác.
- `Measurability` (khả năng đo lường): có tiêu chí khách quan để xác định đạt/chưa đạt.
- `Coverage` (độ bao phủ): các flow, scenario và edge case quan trọng đã được mô tả.
- `Gap` (phần thiếu): nội dung cần có nhưng chưa được specification mô tả.
- `Ambiguity` (điểm mơ hồ): có nhiều cách hiểu hợp lý khác nhau.
- `Conflict` (mâu thuẫn): hai hoặc nhiều requirement/artifact yêu cầu điều không tương thích.
- `Assumption` (giả định): điều đang được coi là đúng nhưng chưa được xác nhận.
- `Traceability` (khả năng truy vết): có thể lần từ checklist item về requirement hoặc artifact nguồn.
- `NFR` — Non-Functional Requirement (yêu cầu phi chức năng): performance, security, reliability, accessibility, scalability, v.v.
- `AC` — Acceptance Criteria (tiêu chí chấp nhận): điều kiện quan sát được để xác định requirement đã được đáp ứng.

<!--
IMPORTANT

- __SPECKIT_COMMAND_CHECKLIST__ MUST replace every placeholder below with real checklist content.
- Do not keep sample items in the generated checklist.
- SPEC is the primary source for product requirements.
- PLAN and TASKS are supporting context only.
- Do not promote PLAN/TASKS implementation details into product requirements.
- Newly generated items MUST remain unchecked.
- Do not create or modify checklists/requirements.md from this template.
-->

## [Relevant Category]

- [ ] CHK001 [Requirements-quality question] [Clarity, FR-001]
- [ ] CHK002 [Requirements-quality question for missing content] [Gap]

## Notes

- Mark an item `[x]` only after reviewer evaluation confirms the requirements-quality criterion is satisfied.
- Leave an item `[ ]` when it still needs clarification, correction, or review.
- `__SPECKIT_COMMAND_IMPLEMENT__` MUST NOT modify checklist markers.
- Custom checklists only block implementation when Constitution, project policy, or explicit user instruction makes them a mandatory gate.
- `checklists/requirements.md` has a separate built-in lifecycle maintained by `__SPECKIT_COMMAND_SPECIFY__` and `__SPECKIT_COMMAND_CLARIFY__`.
- Reference exact requirement IDs (`FR-*`, `BR-*`, `VR-*`, `DR-*`, `AC-*`) when they exist.
- Use `[Gap]` when no source requirement exists; never invent a source reference.
