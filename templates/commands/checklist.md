---
description: Generate a reviewer-owned custom checklist that evaluates requirements quality for the current feature without testing implementation behavior.

scripts:
  sh: scripts/bash/check-prerequisites.sh --json --template checklist-template
  ps: scripts/powershell/check-prerequisites.ps1 -Json -Template checklist-template
  py: scripts/python/check_prerequisites.py --json --template checklist-template
---

## User Input

```text
{ARGS}
```

Bạn **MUST** xem xét user input trước khi tiếp tục nếu input không rỗng.

## Purpose

`__SPECKIT_COMMAND_CHECKLIST__` tạo **custom requirements-quality checklist**
(checklist tùy chỉnh để review chất lượng yêu cầu).

Checklist này kiểm tra cách requirement được viết, không kiểm tra code có chạy đúng hay không.

Think of it as:

```text
SPEC / requirements
        ↓
quality review
        ↓
custom checklist
```

Không dùng checklist này như:

```text
code
 ↓
test execution
 ↓
PASS / FAIL
```

Ví dụ đúng:

```text
Are retry limits explicitly defined? [Gap]
Is "fast response" quantified with a measurable threshold? [Clarity, NFR-001]
Are authentication requirements consistent across protected endpoints? [Consistency, FR-004]
```

Ví dụ sai:

```text
Verify the API returns 200.
Test the retry logic.
Confirm the button works.
```

## Terminology

Khi dùng các thuật ngữ sau, hiểu theo nghĩa:

- **Requirement** (yêu cầu): điều hệ thống phải làm hoặc constraint hệ thống phải tuân thủ.
- **Requirements quality** (chất lượng yêu cầu): mức độ requirement đầy đủ, rõ ràng, nhất quán và kiểm chứng được.
- **Reviewer-owned** (thuộc quyền reviewer): reviewer quyết định checklist item đã đạt hay chưa; agent không tự đánh dấu `[x]`.
- **Advisory** (mang tính khuyến nghị): hỗ trợ review nhưng không tự động chặn workflow.
- **Mandatory gate** (cổng bắt buộc): điều kiện phải đạt trước khi workflow được phép đi tiếp.
- **Traceability** (khả năng truy vết): khả năng lần từ checklist item về requirement hoặc artifact nguồn.
- **Acceptance Criteria / AC** (tiêu chí chấp nhận): điều kiện quan sát được để xác định requirement đã được đáp ứng.
- **Non-Functional Requirement / NFR** (yêu cầu phi chức năng): requirement về performance, security, reliability, accessibility, scalability, v.v.
- **Rollback** (hoàn tác): đưa hệ thống về trạng thái an toàn trước đó sau khi thay đổi thất bại.
- **Recovery flow** (luồng phục hồi): hành vi hệ thống dùng để phục hồi sau lỗi.
- **Partial failure** (lỗi một phần): một số bước thành công nhưng một số bước khác thất bại.
- **Progressive disclosure** (nạp context tăng dần): chỉ đọc thêm context khi thực sự cần thay vì tải toàn bộ artifact ngay từ đầu.

## Ownership and Lifecycle

Custom checklist do command này tạo là **review artifact**
(tài liệu phục vụ review), không phải implementation task list.

Rules:

- Item mới luôn bắt đầu bằng `[ ]`.
- `[x]` chỉ có nghĩa reviewer đã xác nhận tiêu chí về requirements quality đạt.
- `[x]` **không** có nghĩa implementation đã hoàn thành.
- Command này **MUST NOT** tự mark item `[x]`.
- Agent chỉ hỗ trợ đánh giá item khi reviewer/user yêu cầu rõ ràng.
- Custom checklist là **advisory by default**.
- Custom checklist chỉ trở thành **mandatory gate** khi Constitution, project policy, hoặc explicit user instruction yêu cầu.
- `checklists/requirements.md` là built-in requirements-quality checklist riêng, được `__SPECKIT_COMMAND_SPECIFY__` và `__SPECKIT_COMMAND_CLARIFY__` quản lý.
- `__SPECKIT_COMMAND_CHECKLIST__` **MUST NOT** tạo hoặc append vào `checklists/requirements.md`.

## Source Authority

Dùng authority order sau:

1. **Constitution** — governance constraints (quy tắc quản trị bắt buộc của project).
2. **SPEC** — source of truth cho product intent, scope, requirement, business rule và acceptance criteria.
3. **PLAN** — supporting technical context (bối cảnh kỹ thuật hỗ trợ).
4. **TASKS** — implementation decomposition context (bối cảnh cách chia nhỏ việc triển khai).
5. **AGENTS.md / project constraints** — project-wide conventions và technical baseline.

Rules:

- Không dùng PLAN hoặc TASKS để tạo product requirement mới.
- Không biến implementation detail thành business requirement.
- PLAN/TASKS chỉ được dùng để:
  - phát hiện inconsistency (không nhất quán);
  - phát hiện requirement gap (phần yêu cầu còn thiếu);
  - hiểu khu vực kỹ thuật nhạy cảm cần requirement rõ hơn.
- Nếu artifacts mâu thuẫn, checklist item phải surface conflict; không tự reconcile (tự hòa giải/chọn một phía).

## Pre-Execution Hooks

Nếu `.specify/extensions.yml` tồn tại, kiểm tra `hooks.before_checklist`.

- Ignore hook có `enabled: false`.
- Hook không có `enabled` được xem là enabled.
- Không tự evaluate non-empty `condition`.
- Hook không có condition hoặc condition rỗng:
  - optional hook → surface command/prompt;
  - mandatory hook → emit `EXECUTE_COMMAND:` và thực sự invoke trước khi tiếp tục.
- Invalid YAML → KHÔNG skip im lặng: báo cho user rằng `.specify/extensions.yml` không đọc được (kèm parser error), không hook nào được check (kể cả các hook mandatory `optional: false` đã đăng ký), sau đó tiếp tục bình thường.
- Không có hook → tiếp tục bình thường.

## Execution Steps

### 1. Setup

Run từ repository root:

```text
{SCRIPT}
```

Parse:

- `FEATURE_DIR`
- `AVAILABLE_DOCS`
- `TEMPLATE_CONTENT`

Nếu không resolve được active feature:

- **STOP**
- recommend `__SPECKIT_COMMAND_SPECIFY__`.

### 2. Load Project Context

Load nếu tồn tại:

- `.specify/memory/constitution.md`
- root-level `AGENTS.md`
- project constraint/context files được chúng tham chiếu và có liên quan

### 3. Understand Checklist Intent

Derive từ `{ARGS}`:

- checklist theme, ví dụ `security`, `ux`, `api`, `performance`, `testability`;
- focus area;
- depth mong muốn;
- reviewer/audience nếu user nêu rõ;
- explicit must-have review concerns.

Chỉ hỏi clarification khi câu trả lời **materially changes**
(thay đổi đáng kể) checklist content.

Rules:

- tối đa 3 clarification questions;
- skip câu đã rõ từ user input hoặc artifacts;
- không hỏi user lặp lại thông tin đã có;
- không ép hỏi chỉ để đủ số lượng;
- nếu không cần clarification, tiếp tục ngay.

Default khi user không chỉ định:

- depth: `Standard`;
- audience: `Reviewer`;
- focus: theme trực tiếp nhất từ user request.

### 4. Load Feature Context

Read từ `FEATURE_DIR`:

Required:

- `spec.md`

Optional:

- `plan.md`
- `tasks.md`

Dùng **progressive disclosure** (nạp context tăng dần):

- bắt đầu từ phần SPEC liên quan;
- chỉ đọc PLAN/TASKS nếu chúng giúp phát hiện inconsistency hoặc gap;
- không dump toàn bộ artifact vào output.

Nếu thiếu `spec.md`:

- **STOP**
- recommend `__SPECKIT_COMMAND_SPECIFY__`.

### 5. Select Checklist File

Create nếu chưa có:

```text
FEATURE_DIR/checklists/
```

Filename:

```text
<domain>.md
```

Examples:

```text
security.md
ux.md
api.md
performance.md
testability.md
```

Rules:

- tên ngắn, rõ domain;
- không dùng `test.md` vì dễ nhầm với implementation tests;
- không dùng `requirements.md` vì tên này reserved cho built-in checklist;
- nếu user yêu cầu tên `requirements`, dùng tên phân biệt như `requirements-review.md`.

### 6. Existing File Handling

Nếu file chưa tồn tại:

- create từ `TEMPLATE_CONTENT`;
- bắt đầu ID từ `CHK001`.

Nếu file đã tồn tại:

- preserve existing content và checkbox state;
- scan existing `CHKxxx`;
- tiếp tục từ ID lớn nhất + 1;
- detect semantic duplicate (item có cùng ý nghĩa);
- không append duplicate;
- nếu item cũ có vẻ obsolete (không còn phù hợp), report nhưng không tự xóa hoặc rewrite.

Reviewer history phải được giữ nguyên.

### 7. Generate Requirements-Quality Items

Mỗi item phải đánh giá **requirement text**, không đánh giá runtime behavior.

Quality dimensions:

- **Completeness** (độ đầy đủ): requirement cần thiết đã được ghi đủ chưa?
- **Clarity** (độ rõ ràng): wording có cụ thể, không mơ hồ không?
- **Consistency** (tính nhất quán): requirement có mâu thuẫn với requirement khác không?
- **Measurability** (khả năng đo lường): có tiêu chí khách quan để xác định đạt/chưa đạt không?
- **Coverage** (độ bao phủ): primary, alternate, error, recovery và edge cases quan trọng đã được mô tả chưa?
- **Acceptance Criteria Quality** (chất lượng AC): AC có observable và verifiable không?
- **NFR Coverage** (độ bao phủ yêu cầu phi chức năng): performance/security/reliability/accessibility liên quan đã được xác định chưa?
- **Dependencies & Assumptions**: dependency và assumption quan trọng đã được ghi rõ chưa?
- **Ambiguity & Conflict**: có điểm mơ hồ hoặc mâu thuẫn cần resolve không?

Chỉ tạo category có liên quan. Không bắt buộc output toàn bộ category trên.

### 8. Item Format

Canonical form:

```text
- [ ] CHK001 <requirements-quality question> [<quality marker>, <source ref?>]
```

Examples:

```text
- [ ] CHK001 Is the maximum retry count explicitly defined? [Gap]
- [ ] CHK002 Is "fast response" quantified with a latency threshold? [Clarity, NFR-001]
- [ ] CHK003 Are authentication rules consistent between FR-004 and FR-009? [Consistency, FR-004, FR-009]
- [ ] CHK004 Are recovery requirements defined for partial payment failure? [Coverage, Gap]
```

Rules:

- bắt đầu bằng câu hỏi về requirement quality;
- ưu tiên `Are...`, `Is...`, `Does the spec define...`, `Can ... be objectively measured...`;
- không bắt đầu bằng implementation verbs như `Verify`, `Test`, `Confirm`, `Execute`;
- không hỏi code có "works correctly" hay không;
- không biến checklist item thành test case hoặc QA procedure.

### 9. Traceability

Khi item review một requirement đã tồn tại:

- reference exact requirement ID khi có, ví dụ `FR-001`, `BR-002`, `VR-001`, `DR-001`, `AC-001`;
- nếu artifact không có ID phù hợp, reference section heading cụ thể;
- không invent source ref.

Khi item phát hiện nội dung chưa tồn tại:

```text
[Gap]
```

Khi wording có nhiều cách hiểu:

```text
[Ambiguity]
```

Khi hai nguồn mâu thuẫn:

```text
[Conflict]
```

Khi một điều đang được coi là đúng nhưng chưa xác nhận:

```text
[Assumption]
```

Không dùng percentage quota cho traceability.
Mục tiêu là reference đúng khi source tồn tại, không phải đạt một con số tùy ý.

### 10. Scenario Coverage

Chỉ khi liên quan đến feature, xem requirement đã cover:

- **Primary flow** (luồng chính);
- **Alternate flow** (luồng thay thế);
- **Exception/Error flow** (luồng lỗi);
- **Recovery flow** (luồng phục hồi sau lỗi);
- **Partial failure** (lỗi một phần);
- **Rollback** (hoàn tác về trạng thái an toàn);
- relevant **NFR**.

Không tự thêm các scenario không hợp domain.

### 11. Consolidate

Trước khi write:

- merge near-duplicates;
- prioritize high-impact gaps;
- soft cap khoảng 40 items cho một checklist;
- nếu vượt cap, giữ item có risk/impact cao hơn;
- không tạo filler item chỉ để checklist dài.

### 12. Write Checklist

Use `TEMPLATE_CONTENT` làm structural template.

Generated file phải:

- thay toàn bộ placeholder;
- bỏ sample/instruction text không còn cần;
- xóa các khối HTML comment (`<!-- ... -->`) chỉ dùng để hướng dẫn AI điền template — checklist cuối dành cho reviewer (con người);
- giữ marker definitions đủ để reviewer hiểu;
- giữ mọi item mới `[ ]`;
- không sửa built-in `requirements.md`.

### 13. Report

Report:

- full checklist path;
- created hay appended;
- số item mới;
- duplicate bị skip;
- obsolete item được report nếu có;
- focus areas;
- depth;
- checklist là `advisory` hay có mandatory gate từ policy/user;
- source artifacts đã dùng.

## Post-Execution Hooks

Nếu `.specify/extensions.yml` tồn tại, kiểm tra `hooks.after_checklist`.

Rules giống pre-hook:

- ignore disabled;
- không evaluate non-empty condition;
- mandatory executable hook → emit `EXECUTE_COMMAND:` và run;
- optional hook → surface command/prompt;
- invalid YAML → KHÔNG skip im lặng: báo cho user rằng `.specify/extensions.yml` không đọc được (kèm parser error), không hook nào được check (kể cả các hook mandatory `optional: false` đã đăng ký), sau đó tiếp tục bình thường.

## Done When

- [ ] Checklist đánh giá requirements quality, không test implementation.
- [ ] SPEC được dùng làm primary requirement source.
- [ ] PLAN/TASKS chỉ được dùng làm supporting context.
- [ ] Custom checklist không ghi vào `checklists/requirements.md`.
- [ ] Item mới giữ `[ ]`.
- [ ] Existing reviewer state được preserve.
- [ ] Duplicate item không được append.
- [ ] Existing requirement refs được trace đúng khi có.
- [ ] Gap không bị gắn source ref giả.
- [ ] Specialized terms quan trọng được định nghĩa rõ.
- [ ] Custom checklist mặc định advisory.
- [ ] Completion report được trả về.
