# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Ngày**: [DATE] | **Spec**: [link]  
**STATUS**: DRAFT — REVIEW  
**INPUT**: Đặc tả tính năng tại `/specs/[###-feature-name]/spec.md`

<!--
Tài liệu này mô tả CÁCH tính năng sẽ được triển khai.

Công nghệ dùng chung, quy ước, dependency đã được phê duyệt,
forbidden patterns và các ràng buộc kiến trúc của toàn dự án
được kế thừa từ:
- `AGENTS.md`
- `.specify/memory/constitution.md`
- các file constraint/context được tham chiếu bởi các tài liệu trên

KHÔNG lặp lại toàn bộ tech stack của dự án trong PLAN.

Chỉ ghi những quyết định kỹ thuật, thay đổi, ảnh hưởng,
dependency, ngoại lệ, risk và cấu trúc triển khai
liên quan trực tiếp đến tính năng này.

KHÔNG tạo `tasks.md` ở giai đoạn này.
Việc chia nhỏ task được thực hiện bởi `__SPECKIT_COMMAND_TASKS__`
sau khi PLAN được phê duyệt.
-->

## 1. Summary

[Tóm tắt ngắn gọn mục tiêu của tính năng từ SPEC và cách tiếp cận kỹ thuật dự kiến.]

## 2. Technical Context

<!--
CHỈ mô tả bối cảnh kỹ thuật riêng của tính năng này.

Nếu không có thay đổi hoặc ảnh hưởng riêng, ghi `None`.

Chỉ dùng đúng cú pháp:
`NEEDS CLARIFICATION: <câu hỏi>`
khi quyết định không thể xác định từ:
- feature spec
- `AGENTS.md`
- constitution
- project constraints
- repository context

Không lặp lại language, framework, database, testing framework
hoặc các công nghệ đã được xác định cho toàn dự án,
trừ khi tính năng này yêu cầu thay đổi hoặc mở rộng chúng.
-->

**Nền tảng dự án**: Kế thừa từ `AGENTS.md`, constitution và các project constraints liên quan.

**Dependency mới**: `None`  
HOẶC  
`[dependency + mục đích + lý do khả năng hiện tại của dự án chưa đủ]`

**Ảnh hưởng đến lưu trữ dữ liệu**: `None`  
HOẶC  
`[schema / storage / cache bị ảnh hưởng bởi tính năng]`

**Tích hợp bên ngoài (External Integration)**: `None`  
HOẶC  
`[dịch vụ / interface bên ngoài + mục đích]`

**Ảnh hưởng đến kiểm thử**: `[yêu cầu kiểm thử riêng của tính năng, loại test mới, hoặc None]`

**Ràng buộc hiệu năng / kỹ thuật**:
- `[chỉ ghi những constraint liên quan trực tiếp đến tính năng]`

**Quyết định kỹ thuật riêng của tính năng**:
- `[quyết định + lý do]`
- `NEEDS CLARIFICATION: [câu hỏi]` nếu chưa thể quyết định

## 3. Constitution Check

<!--
GATE: Phải đạt trước Phase 0 Research.
Kiểm tra lại sau Phase 1 Design.

Chỉ liệt kê những rule trong constitution
thực sự ảnh hưởng đến tính năng này.

Không sao chép toàn bộ constitution.

Nếu có violation:
1. Mô tả violation.
2. Giải thích tại sao cần thiết.
3. Ghi lại trong mục Theo dõi độ phức tạp.
4. ERROR nếu violation không có lý do hợp lệ.
-->

### Pre-Design Gate

- `[Constitution rule]`: `PASS | VIOLATION — [lý do]`

### Post-Design Re-check

- `[Constitution rule]`: `PASS | VIOLATION — [lý do]`

## 4. Architectural Approach

<!--
Mô tả cách tiếp cận kỹ thuật tổng thể cho tính năng.

Chỉ đề cập architecture pattern hoặc design pattern
khi chúng thực sự liên quan đến tính năng.

Ưu tiên các pattern đang được dự án sử dụng.

Không tự đưa architecture hoặc pattern mới vào
trừ khi tính năng thực sự cần,
và phải giải thích rõ lý do.
-->

[Mô tả cách triển khai và lý do nó phù hợp với kiến trúc hiện tại của dự án.]

## 5. Components

<!--
Chỉ liệt kê component / module / class được tạo mới
hoặc thay đổi đáng kể cho tính năng này.

Dùng bảng để so sánh ngắn gọn.

Không chia xuống mức task ở phần này.
-->

| Thành phần | Trách nhiệm | Interface / Input-Output | File |
|---|---|---|---|
| `[component]` | `[trách nhiệm]` | `[interface / input → output]` | `[đường dẫn]` |

## 6. Data Flow

<!--
Mô tả ở mức cao cách dữ liệu đi qua tính năng.

Ví dụ:

User Request
→ Controller / Router
→ Application / Service
→ Repository / External Service
→ Storage
→ Response

Không lặp lại schema chi tiết trong `data-model.md`
hoặc API contract đầy đủ trong `/contracts/`.
-->

`[Đầu vào] → [Xử lý] → [Lưu trữ / Tích hợp] → [Đầu ra]`

[Chỉ thêm luồng thay thế, async hoặc luồng lỗi khi cần.]

## 7. Dependencies

### Implementation Order

<!--
Mô tả thứ tự phụ thuộc giữa các component.

Không chia thành các bước implementation nhỏ.
Các task nguyên tử thuộc về `tasks.md`.
-->

1. `[component / prerequisite]`
2. `[component phụ thuộc vào #1]`
3. `[component phụ thuộc vào các thành phần trước]`

### External Dependencies

<!--
Chỉ liệt kê dependency hoặc integration MỚI
hoặc riêng cho tính năng.

Không lặp lại dependency thông thường của toàn dự án.
-->

- `None`

HOẶC

- `[dependency / service]`: `[mục đích và lý do sử dụng]`

## 8. Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # File hiện tại (__SPECKIT_COMMAND_PLAN__ output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output nếu có external interface
└── tasks.md             # Tạo sau bởi __SPECKIT_COMMAND_TASKS__
```

### Source Code (affected paths only)

<!--
Chỉ hiển thị đường dẫn THỰC TẾ trong repository
bị ảnh hưởng bởi tính năng.

Không đưa các project layout mẫu chung chung.

Không sao chép toàn bộ repository tree.

Chỉ giữ lại file / thư mục liên quan trực tiếp đến thay đổi.
-->

```text
[đường/dẫn/module/liên/quan]/
├── [file-hoặc-thư-mục]
└── [file-hoặc-thư-mục]

tests/
└── [đường-dẫn-test-liên-quan]
```

**Quyết định về cấu trúc**: [Giải thích tính năng được đặt ở đâu trong cấu trúc hiện tại và vì sao.]

## 9. Risks & Mitigations

<!--
Chỉ ghi các risk kỹ thuật hoặc integration risk có thật.

Không bịa thêm risk chỉ để điền đủ bảng.

Nếu tính năng đơn giản và không có risk đáng kể, ghi `None`.
-->

| Rủi ro | Khả năng | Ảnh hưởng | Cách giảm thiểu |
|---|---|---|---|
| `[risk]` | `High / Medium / Low` | `[impact]` | `[mitigation]` |

## 10. Questions for Human

<!--
Chỉ dùng phần này cho những quyết định không thể xác định an toàn từ:
- feature spec
- `AGENTS.md`
- constitution / project constraints
- repository context
- Phase 0 Research

Không tự suy đoán.

Nếu vẫn còn câu hỏi chưa được giải quyết,
planning CHƯA hoàn tất và workflow phải dừng
để chờ human input.

Sau khi được xác nhận:
- cập nhật PLAN
- thay phần này bằng `None`
  hoặc ghi lại quyết định đã được chốt
-->

- `None`

HOẶC

1. `[câu hỏi cần quyết định của con người]`

## 11. Complexity Tracking

> CHỈ điền khi Constitution Check có violation đã được giải thích và chấp nhận.

| Violation | Vì sao cần | Vì sao phương án đơn giản hơn không phù hợp |
|---|---|---|
| `[violation]` | `[nhu cầu cụ thể]` | `[lý do phương án tuân thủ đơn giản hơn là chưa đủ]` |
