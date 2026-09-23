# So sánh `spec-datkit` (local) vs `github/spec-kit` (upstream)

> Ngày so sánh: 2026-09-23
> Nguồn upstream: clone `--depth 1` từ `https://github.com/github/spec-kit` (branch `main`, commit tại thời điểm so sánh)

## 1. Tổng quan

| Hạng mục | Local (`spec-datkit`) | Upstream (`spec-kit`) |
|---|---|---|
| Tên package (`pyproject.toml`) | `spec-datkit` | `spec-kit` |
| Version | `1.0.1` (2026-08-21) | `1.0.11.dev0` (release mới nhất `1.0.10`, 2026-09-22) |
| Bản chất | Fork của spec-kit ~v1.0.1, **đổi tên + tùy biến sâu** | Repo gốc, tiến hóa ~10 release sau thời điểm fork |
| Kiến trúc tổng thể | Giống gốc: `templates/`, `scripts/`, `extensions/`, `workflows/`, `presets/`, `bundles/`, `src/specify_cli/` | Giống, nhưng đã **refactor module CLI theo domain** |
| Ngôn ngữ trong template | **Song ngữ Việt–Anh** (chú thích tiếng Việt) | Tiếng Anh thuần |
| Số file test | 158 | 302 |

**Kết luận nhanh:** local không phải bản "cũ hơn đơn thuần" của upstream — mà là một **nhánh phát triển độc lập** với triết khác biệt lớn nhất nằm ở workflow `specify` (xem mục 3), trong khi upstream chạy theo hướng refactor nội bộ, bổ sung agent/workflow mới và tinh gọn template.

---

## 2. Khác biệt kiến trúc cốt lõi

### 2.1 Placeholder tham số

| | Local | Upstream |
|---|---|---|
| Trong template | `{ARGS}` | `$ARGUMENTS` |
| Cơ chế | Rewrite lúc install: `agents.py` / `integrations/base.py` thay `{ARGS}` → `$ARGUMENTS` hoặc placeholder riêng của từng agent (`{{args}}`, `{{parameters}}`…) | Dùng `$ARGUMENTS` trực tiếp; chỉ thay bằng placeholder agent khi cần |

### 2.2 Đường dẫn constitution

| | Local | Upstream |
|---|---|---|
| Trong template | Hard-code `.specify/memory/constitution.md` | Viết `/memory/constitution.md`, **rewrite bằng regex lúc install** (`agents.py`: `memory/` → `.specify/memory/`) |
| Vị trí thực tế sau install | `.specify/memory/constitution.md` | `.specify/memory/constitution.md` (giống nhau) |

### 2.3 `scripts:` frontmatter trong lệnh specify

- **Local** `templates/commands/specify.md` **có** khối `scripts:` (sh/ps/py → `create-new-feature`) và dùng `{SCRIPT}`.
- **Upstream** `templates/commands/specify.md` **không có** khối `scripts:` — specify hoàn toàn do agent tự thực hiện (xem 3.1). Riêng bản preset scaffold `presets/scaffold/commands/speckit.specify.md` của upstream vẫn gọi script kèm `"{ARGS}"`.

---

## 3. Input / Output của workflow `specify` — khác biệt lớn nhất

### 3.1 Local: mô hình **branch-driven** (branch là danh tính feature)

```text
User checkout branch trước (bắt buộc)
   ví dụ: 003-user-auth  hoặc  20260923-134500-user-auth
        │
        ▼
specify → chạy create_new_feature.{sh|ps1|py} --json
   • ĐỌC branch hiện tại, KHÔNG tạo/switch/rename/merge/delete branch
   • Branch phải khớp: NNN-short-name | YYYYMMDD-HHMMSS-short-name
   • Từ chối branch có '/' hoặc '\'
        │
        ▼
Tạo specs/<branch>/spec.md (copy spec-template) + .specify/feature.json
```

**Input:**
- Tên Git branch hiện tại (bắt buộc, là nguồn danh tính feature)
- `{ARGS}` (tuỳ chọn — mô tả bổ sung cho agent điền spec)

**Output JSON của script** (`create_new_feature.py`):

```json
{
  "FEATURE_NAME": "...", "BRANCH_NAME": "...", "FEATURE_NUM": "...",
  "FEATURE_DIR": "...", "SPEC_FILE": "...", "NUMBERING_MODE": "sequential|timestamp"
}
```

### 3.2 Upstream: mô hình **description-driven** (branch và spec dir độc lập)

```text
User gõ mô tả tự nhiên (natural language)
   ví dụ: "I want to add user authentication"
        │
        ▼
specify (agent tự làm toàn bộ):
   1. Sinh short-name 2–4 từ từ mô tả (action-noun, giữ thuật ngữ kỹ thuật)
   2. (Tuỳ chọn) before_specify hook của extension git tạo branch
      → JSON: BRANCH_NAME, FEATURE_NUM
   3. Agent tự mkdir specs/<prefix>-<short-name>/
      • prefix: NNN (sequential) hoặc YYYYMMDD-HHMMSS (timestamp)
        đọc từ .specify/init-options.json → feature_numbering
        (branch_numbering đã deprecated, sẽ gỡ trong tương lai)
   4. Copy spec-template → spec.md, ghi .specify/feature.json
```

**Input:**
- Mô tả feature bằng ngôn ngữ tự nhiên (bắt buộc — rỗng thì ERROR)
- `GIT_BRANCH_NAME` (tuỳ chọn — ép tên branch, bypass sinh prefix/suffix)
- `SPECIFY_FEATURE_DIRECTORY` (tuỳ chọn — ghi đè thư mục spec)

**Output:** branch và spec dir **độc lập** — "may be the same but that is the user's choice". Script `create_new_feature.py` upstream vẫn tồn tại nhưng hợp đồng JSON nhỏ hơn:

```json
{ "BRANCH_NAME": "...", "SPEC_FILE": "...", "FEATURE_NUM": "..." }
```

(kèm gợi ý `# To persist:` để export biến môi trường `SPECIFY_FEATURE`)

### 3.3 Hệ quả thực tiễn

| Tình huống | Local | Upstream |
|---|---|---|
| Quên tạo branch hợp lệ | specify FAIL ngay (script exit 1) | vẫn chạy — spec dir tự sinh, branch là tuỳ chọn |
| Đổi mô tả sau khi specify | Phải đổi branch (hoặc chấp nhận tên cũ) | Chỉ cần chỉnh spec.md |
| Tên spec dir ≠ tên branch | Không thể (bắt buộc đồng nhất) | Được (độc lập) |
| Automation/CI | Dễ — chỉ cần `git checkout NNN-x` trước | Cần truyền mô tả, dựa agent suy luận tên |

---

## 4. So sánh từng command template (`templates/commands/`)

Đây là "bộ skill" nguồn — khi install sẽ sinh skill `speckit-<tên>/SKILL.md` (hoặc command theo format agent). Số dòng diff là `diff local upstream | wc -l`.

| Command | Diff lines | Local (dòng) | Upstream (dòng) | Mức độ khác biệt |
|---|---|---|---|---|
| specify.md | 475 | 367 | 345 | 🔴 Viết lại — khác triết học (mục 3) |
| plan.md | 79 | 186 | 170 | 🟡 Vừa — context loading khác nhau |
| analyze.md | 947 | 739 | 255 | 🔴 Viết lại |
| checklist.md | 771 | 410 | 379 | 🔴 Viết lại |
| clarify.md | 26 | 292 | 291 | 🟢 Nhẹ |
| constitution.md | 20 | 178 | 179 | 🟢 Nhẹ |
| converge.md | 1013 | 773 | 279 | 🔴 Viết lại |
| implement.md | 808 | 623 | 222 | 🔴 Viết lại — khác scope thực thi |
| tasks.md | 537 | 447 | 220 | 🔴 Viết lại |
| taskstoissues.md | 787 | 704 | 106 | 🔴 Viết lại |

Xu hướng chung: **local phình to template với hướng dẫn chi tiết + chú thích tiếng Việt; upstream giữ template ngắn gọn** (triết lý "lean template", đẩy chi tiết ra ngoài).

### 4.1 `specify.md`
- Local: branch-driven (mục 3.1); có mục "Feature Identity" giải thích bằng tiếng Việt; quy tắc "Spec Kit không quản lý Git branch".
- Upstream: description-driven (mục 3.2); sinh short-name, tự tạo thư mục, hỗ trợ `GIT_BRANCH_NAME` / `SPECIFY_FEATURE_DIRECTORY`; giới hạn `[NEEDS CLARIFICATION]` tối đa 3 marker, ưu tiên theo tác động.

### 4.2 `plan.md`
| | Local | Upstream |
|---|---|---|
| Parse JSON setup | `FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH` | `FEATURE_SPEC, IMPL_PLAN, FEATURE_DIR, BRANCH` |
| Load context | Đọc `AGENTS.md` + các file constraint được tham chiếu; kế thừa tech stack/quy ước dự án; constitution là **authoritative** khi xung đột | Chỉ FEATURE_SPEC + constitution + IMPL_PLAN template |
| Điền template | Bắt buộc giữ nguyên mọi heading của `plan-template`; mục không áp dụng ghi "N/A" + lý do; không lặp tech stack dự án; chỉ đánh dấu `NEEDS CLARIFICATION` cho quyết định **đặc thù feature** | Hướng dẫn chung, tự do hơn |
| Phase | Phase 0 research.md → Phase 1 data-model.md, contracts/, quickstart.md → re-evaluate Constitution Check | Không mô tả phase chi tiết trong command |
| extensions.yml lỗi | Bỏ qua im lặng, tiếp tục | **Báo lỗi cho user** (kèm parser error), nêu hooks nào chưa check |

### 4.3 `analyze.md`
| | Local | Upstream |
|---|---|---|
| Mô tả | "read-only cross-artifact consistency and task-quality analysis … **before implementation**" | "non-destructive … analysis **after task generation**" |
| Cờ check-prerequisites | `--require-tasks --include-tasks` | `--require-spec --require-tasks --include-tasks` |
| Constitution | Nêu đường dẫn `.specify/memory/constitution.md` | "Constitution Authority" — conflict constitution tự động CRITICAL |

### 4.4 `checklist.md` / `checklist-template.md`
- Local đưa khái niệm **"reviewer-owned"** (reviewer quyết định item đạt; agent không tự đánh dấu `[x]`), semantics marker `[x]` = yêu cầu chất lượng đã được xác nhận (không phải implementation xong), checklist **advisory** mặc định — kèm chú thích tiếng Việt.
- Upstream: mô tả đơn giản "custom checklist based on user requirements", khái niệm "Unit Tests for English".

### 4.5 `clarify.md` & `constitution.md` (khác nhẹ)
- Giống nhau về cấu trúc; khác ở: placeholder `{ARGS}`/`$ARGUMENTS`, đường dẫn constitution (mục 2.2), và xử lý lỗi `extensions.yml` (local bỏ qua im lặng — upstream báo lỗi).
- Local constitution có "Sync Impact Report" prepend HTML comment sau update; upstream tương đương.

### 4.6 `converge.md`
| | Local | Upstream |
|---|---|---|
| Mô tả | Đánh giá feature đã implement theo SPEC/PLAN/TASKS, **chỉ append task remediation nguyên tử cho gap còn lại đã verify** | Đánh giá codebase, append **mọi work chưa build** vào tasks.md để implement tiếp |
| Cờ check-prerequisites | `--require-tasks --include-tasks` | `--require-spec --require-tasks --include-tasks` |

### 4.7 `implement.md` — khác biệt scope quan trọng
| | Local | Upstream |
|---|---|---|
| Mô tả | "**Execute one ready task** … verify its Done-when condition before marking complete" — một task mỗi lần gọi, dependency-driven | "**processing and executing all tasks** defined in tasks.md" — chạy toàn bộ plan |
| Ngôn ngữ | Mở đầu tiếng Việt: "Bạn MUST xem xét user input…" | Tiếng Anh |
| Handoff (tasks.md) | "Start the implementation **task-by-task**" | "Start the implementation **in phases**" |

### 4.8 `tasks.md`
- Local: yêu cầu `spec.md` + `plan.md` là **bắt buộc**, artifacts khác tuỳ chọn; task "atomic, independent, verifiable"; handoff task-by-task.
- Upstream: sinh tasks "based on available design artifacts" (linh hoạt hơn về artifact nguồn).

### 4.9 `taskstoissues.md`
- Local: giữ khối `handoffs:` (label "Implement Tasks", gọi `speckit.implement`); nhấn mạnh "optionally publish **analyzed, incomplete** tasks", preserve metadata + dependencies. 704 dòng.
- Upstream: gọn (106 dòng), không có handoffs; "Convert existing tasks into actionable, dependency-ordered GitHub issues".

---

## 5. So sánh document templates (`templates/*.md`)

| Template | Diff | Local (dòng) | Upstream (dòng) | Khác biệt chính |
|---|---|---|---|---|
| spec-template.md | 789 | 695 | 131 | Local: metadata mở rộng `Version`/`Owner`/`Status` (`Draft|Review|Approved|Implemented`), heading "Detailed Spec", hướng dẫn chi tiết. Upstream: "Feature Specification", chỉ `Created`, cực gọn |
| plan-template.md | 363 | 272 | 113 | Local: header tiếng Việt (`Ngày`, `INPUT`), comment khối giải thích kế thừa context từ `AGENTS.md` + constitution; upstream gọn |
| tasks-template.md | 468 | 227 | 252 | Local: phân biệt rõ Required (`spec.md`, `plan.md`) vs Optional artifacts; upstream mô tả chung |
| checklist-template.md | 96 | 61 | 45 | Local: mục Purpose/Ownership (reviewer-owned)/Marker Semantics/Gate Behavior (advisory) + tiếng Việt |
| constitution-template.md | 488 | 452 | 50 | Local: khối "Naming Guide" hướng dẫn đặt tên project & core principle (ví dụ Campus Portal Constitution…); upstream chỉ khung trống |
| vscode-settings.json | ~0 | = | = | Giống nhau |

---

## 6. So sánh scripts (`scripts/`) — hợp đồng I/O

12/12 file diff (bash + powershell + python của 4 script: check-prerequisites, common, create-new-feature, setup-plan).

### 6.1 `create_new_feature` — khác biệt lớn nhất

| | Local | Upstream |
|---|---|---|
| Triết lý | Đọc **branch hiện tại** làm feature name; không đụng git | Sinh tên từ **`--description`**/`--short-name`**; tách slug (bỏ STOP_WORDS), `_fit_branch_name` giới hạn 244 bytes, feature number ≤ int64 |
| Dùng git | Chỉ ĐỌC trạng thái repo/branch | Không thao tác git |
| Output JSON | FEATURE_NAME, BRANCH_NAME, FEATURE_NUM, FEATURE_DIR, SPEC_FILE, NUMBERING_MODE | BRANCH_NAME, SPEC_FILE, FEATURE_NUM (+ gợi ý persist env shell) |
| Số dòng (py) | 284 | 448 |

### 6.2 `setup_plan`
| | Local | Upstream |
|---|---|---|
| Args lạ | **Chấp nhận và bỏ qua im lặng** | **ERROR** `Unknown option` và exit 1 |
| Key JSON | `SPECS_DIR` | `FEATURE_DIR` (đổi tên — khớp plan.md mới) |

### 6.3 `check_prerequisites`
- Upstream **thêm cờ `--require-spec`** (yêu cầu `spec.md` tồn tại — dùng cho analysis phase: analyze/converge). Local chưa có cờ này.

### 6.4 `common` (bash/ps1/py)
- Cập nhật theo các thay đổi trên (hỗ trợ cờ mới, key mới).

---

## 7. So sánh extensions (`extensions/`)

Cả hai có **cùng 6 extension**: `agent-context`, `assess`, `bug`, `git`, `selftest`, `template`.

| Extension | Version local | Version upstream | Ghi chú |
|---|---|---|---|
| agent-context | 1.0.0 | **1.0.1** | `agent-context-defaults.json` upstream thêm agent `muse` → `AGENTS.md` |
| assess | 1.0.0 | **1.0.1** | |
| bug | 1.0.0 | 1.0.0 | |
| git | 1.0.0 | **1.0.1** | Upstream fix parity locale trong `create-new-feature-branch.*`: `LC_ALL=C` (tránh collation UTF-8 giữ ký tự có dấu), sed POSIX `--*` thay `\+`, `printf` thay `echo` — để output sh/ps/py **byte-identical** |
| selftest | 1.0.0 | 1.0.0 | |

- **Tất cả `commands/` của extension giống hệt nhau** (0 diff) — phần lớn thay đổi nằm ở script và metadata.
- Catalog (`catalog.json`, `catalog.community.json`) khác nhau (version + mục mới của upstream).

---

## 8. So sánh workflows (`workflows/`)

| | Local | Upstream |
|---|---|---|
| `speckit/workflow.yml` | `version: 1.0.0`; **thêm input `scope`** (`full` \| `backend-only` \| `frontend-only`, default `full`) | `version: 1.0.1`; **không có** `scope` |
| Workflow khác | Chỉ có `speckit` | **Thêm `workflows/assess` + `workflows/bugfix`** |
| Bundles | — | **Thêm `bundles/assess`, `bundles/bugfix`, `bundles/catalog.json`** |

→ Đây là **tính năng riêng của local** (param `scope` hạn chế phạm vi generate theo backend/frontend) mà upstream chưa có; ngược lại upstream đã ship 2 workflow mới (assess, bugfix) mà local chưa có.

---

## 9. So sánh integrations / agents (`src/specify_cli/integrations/`)

- **Chung (37):** agy, alquimia, amp, auggie, bob, claude, cline, codebuddy, codex, command_code, copilot, cursor_agent, devin, droid, firebender, forge, gemini, generic, goose, grok, hermes, junie, kilocode, kimi, kiro_cli, lingma, omp, opencode, pi, qodercli, qwen, rovodev, shai, tabnine, trae, vibe, zcode, zed *(38 keys, trừ `generic` là 37 agent thực)*
- **Chỉ upstream:** `docker_agent`, `dsh`, `muse` (+ module `catalog`)
- **Chỉ local:** không có agent nào riêng — mọi tùy biến nằm ở template/workflow.

Cơ chế sinh skill từ template **giống nhau** về layout (ví dụ codex: `.agents/skills/speckit-<tên>/SKILL.md`, claude: `.claude/skills/…`), vì code integration của 37 agent chung hầu như không đổi.

---

## 10. So sánh CLI (`src/specify_cli/`)

| | Local | Upstream |
|---|---|---|
| Cấu trúc | `commands/` (bundle, event.py, init.py) + module phẳng | Đã **refactor theo domain**: `command_init.py`, `command_check.py`, `command_version.py`, `artifacts/`, `authentication/`, `events/`, `extensions/`, `integrations/`, `presets/`, `selfs/`, `workflows/`, `bundles/` |
| Flags `specify init` | Giống hệt nhau: `--debug --extension --force --github-token --here --ignore-agent-tools --integration --integration-options --non-interactive --offline --preset --script --skills --skip-tls --trust-extension-urls` | (như cột trái) |
| `specify version` | — | Bổ sung báo cáo runtime OpenSSL |

Refactor domain của upstream (thấy trong CHANGELOG 1.0.2–1.0.10: #4685, #4683, #4678, #4673, #4671…) là **nội bộ**, không đổi UX chính.

---

## 11. Summarize bảng một trang (cheatsheet)

| Khía cạnh | Local `spec-datkit` 1.0.1 | Upstream `spec-kit` 1.0.10 |
|---|---|---|
| Danh tính feature | = tên Git branch hiện tại | Sinh từ mô tả tự nhiên; độc lập với branch |
| specify tạo branch? | Không (user tự tạo trước) | Qua hook git extension (tuỳ chọn) |
| Ai mkdir + copy template | Script `create_new_feature` | Agent (hoặc script trong preset scaffold) |
| Key JSON specify | + `FEATURE_NAME`, `FEATURE_DIR`, `NUMBERING_MODE` | + persistence hints; nhỏ gọn hơn |
| Placeholder | `{ARGS}` (rewrite lúc install) | `$ARGUMENTS` |
| Constitution path | Hard-code `.specify/memory/…` | `/memory/…` → rewrite lúc install |
| implement | 1 task/lần gọi | Toàn bộ tasks |
| analyze/converge gate | Không require spec | `--require-spec` |
| extensions.yml lỗi | Skip im lặng | Báo lỗi rõ ràng |
| Template command | Dài, chi tiết, song ngữ Việt | Ngắn, gọn, tiếng Anh |
| Workflow riêng | `scope` (full/backend/frontend) | `assess`, `bugfix` workflows + bundles |
| Agent mới | — | docker_agent, dsh, muse |
| Tests | 158 file | 302 file |

---

## 12. Đánh giá & khuyến nghị

**Điểm mạnh của local (spec-datkit):**
1. `specify` branch-driven rất hợp automation/CI và team đã quản lý branch bằng quy ước (`NNN-…`): danh tính feature tường minh ngay từ git.
2. `implement` one-task-at-a-time + handoff "task-by-task": kiểm soát tốt hơn, dễ review từng bước, giảm rủi ro agent chạy tràn.
3. Template chi tiết (plan giữ nguyên heading, kế thừa `AGENTS.md`, phân quyền constitution) — tốt cho chất lượng artifact ổn định giữa các agent.
4. `scope` trong workflow (backend-only/frontend-only) — tính năng upstream chưa có.
5. Checklist "reviewer-owned" + semantics marker rõ ràng — chống agent tự đánh dấu hoàn thành sai.

**Điểm mạnh của upstream (nên cân nhắc port về):**
1. Fix parity byte sh/ps/py trong git extension (`LC_ALL=C`, sed POSIX, printf) — tránh bug ký tự có dấu trên macOS/UTF-8 locale, **liên quan trực tiếp khi làm việc với tiếng Việt**.
2. `--require-spec` cho analyze/converge; báo lỗi `extensions.yml` thay vì im lặng — phát hiện cấu hình hỏng sớm hơn.
3. `setup_plan` từ chối args lạ — phát hiện lỗi gọi script sai.
4. Key `FEATURE_DIR` thống nhất (local đang lệch: template dùng `SPECS_DIR`).
5. Agent mới (docker_agent, dsh, muse), workflows assess/bugfix, số lượng test phủ ~gấp đôi.

**Rủi ro khi merge/upgrade từ upstream:** xung đột gần như **toàn bộ** `templates/` (10/10 command + 5/5 document template đều diff, nhiều file diff hàng trăm–nghìn dòng). Nên merge chọn lọc theo từng file thay vì merge nhánh nguyên khối; ưu tiên port bug-fix (mục 6–7) trước, giữ triết lý template của local.

---

*Tệp này được sinh ra bằng cách diff trực tiếp cây thư mục local với bản clone `--depth 1` của `github/spec-kit` tại thời điểm 2026-09-23; số liệu "diff lines" tính bằng `diff | wc -l`.*
