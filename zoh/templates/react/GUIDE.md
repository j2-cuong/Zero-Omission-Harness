# AI Agent Base — Hướng Dẫn Chi Tiết
> **File:** `.doc/GUIDE.md`  
> **Mục đích:** Tài liệu chi tiết về cách hệ thống hoạt động bên trong.

---

## 🧠 Triết Lý Cốt Lõi

Đây không phải template. Đây là **hệ điều hành cho AI development**.

Thay vì AI nhận spec tĩnh rồi code, hệ thống này buộc AI phải:
1. **Phỏng vấn** người dùng và validate đầu vào trước khi làm bất cứ điều gì
2. **Duy trì trạng thái** liên tục — có thể dừng và resume bất kỳ lúc nào
3. **Simulate** mọi thay đổi trước khi áp dụng thực tế
4. **Kiểm tra tính nhất quán** giữa code, doc, map, contract sau mỗi bước
5. **Không bao giờ đoán** — mọi quyết định đều có log, mọi bug đều có trace

---

## 🔒 Ba Gate Cứng

| Gate | Điều kiện | Hành động nếu vi phạm |
|------|-----------|----------------------|
| **GATE-1** | `.workflow/SEED.md` chưa được validate đầy đủ | Không generate `.agent/` |
| **GATE-2** | `.agent/STATE.md` chưa được update sau mỗi step | Không chạy step tiếp theo |
| **GATE-3** | Chưa có `.sim/` + `.test/` cho fix | Không được apply fix |

---

## 📁 Chi Tiết Từng Thư Mục

### `.router/` — Tầng điều phối
AI đọc đây đầu tiên để quyết định:
- Phát hiện intent từ user request
- Xác định phase hiện tại (từ STATE.md)
- Chọn đúng files cần load (không load toàn bộ)
- Quản lý token budget

**Files:**
- `ROUTER.md` — Main router
- `00_INTERVIEW.md` — Điều phối phỏng vấn tiered
- `01_CODE.md` — Điều phối coding tasks
- `02_BUGFIX.md` — Điều phối bug fixing
- `03_DOC.md` — Điều phối documentation
- `04_TEST.md` — Điều phối testing
- `05_ARCH.md` — Điều phối architecture tasks
- `06_CONSISTENCY_CHECKER.md` — Kiểm tra tính nhất quán
- `07_CONTEXT_LOADER.md` — Load context theo phase

### `.workflow/` — Phỏng vấn và workflow
AI hỏi người dùng qua **7 tiers** (0-6), validate toàn bộ trước khi sinh bất kỳ file nào.

**7 Tiers:**
| Tier | Nội dung |
|------|----------|
| 0 | Tên, ngôn ngữ, trạng thái, mục đích |
| 1 | Components, data flow, concurrency |
| 2 | API, IPC, P/Invoke |
| 3 | Performance, memory, security (optional) |
| 4 | Frameworks, storage, network, build, tools |
| 5 | Hiệu năng chi tiết, bottleneck, profiling |
| 6 | Error handling, edge cases, logging |

**Workflow files:**
- `00_MASTER_WORKFLOW.md` — Orchestrator chính
- `02_GENERATE_AGENT.md` — Sinh `.agent/` từ interview
- `03_SCAN_FOR_BUGS.md` — Quét và chứng minh bug
- `04_BUGFIX_LOOP.md` — Vòng lặp fix với simulation
- `05_TEST_PHASE.md` — Testing workflow

### `.skill/` — Kiến thức nền bất biến
Rules cứng cho từng ngôn ngữ (C++, C#, React). Không phụ thuộc vào dự án cụ thể.

**Files:**
- `_shared.md` — Rules chung cho mọi ngôn ngữ
- `{lang}.md` — Rules cụ thể cho từng ngôn ngữ

### `.agent/` — Đặc tả dự án + State engine
Toàn bộ context để AI code đúng. STATE.md là **driver** — không có state → không chạy.

**Files:**
- `STATE.md` — State machine, context loader, validation gates
- `00_MASTER.md` — Vai trò AI, constraints
- `01_STRUCTURE.md` — Cây thư mục project
- `02_TASK_LIST.md` — Danh sách task
- `03_API_CONTRACT.md` — API contract (nếu có)
- `03_IPC_CONTRACT.md` — IPC contract (nếu có)
- `04_PINVOKE_CONTRACT.md` — P/Invoke contract (nếu có)
- `05_RULES_{LANG}.md` — Rules coding cho project
- `06_BUILD_CONFIG.md` — Build configuration
- `AI_GUIDE.md` — Hướng dẫn cho AI

### `.sim/` — Simulation trước khi fix
Mọi fix phải dry-run ở đây trước. Impact boundary control cho biết fix X sẽ ảnh hưởng đến Y, Z.

**Format:** `dry_run_{id}.md` với:
- Impact scope (blast radius level 1-3)
- Risk assessment
- Cascade risk
- Change detail
- Approval status

### `.map/` — Sơ đồ logic (Text-based)
Text-based architecture diagrams: Mermaid, YAML, ASCII. Dễ diff, dễ cập nhật khi code thay đổi.

**Cấu trúc:**
```
.map/
├── STRUCTURE.md              # Guide cho text-based maps
├── SYSTEM_DIAGRAM.mmd        # Sơ đồ tổng thể hệ thống
├── current/                  # State hiện tại
│   ├── component_tree.yaml   # Component hierarchy
│   ├── data_flow.mmd         # Mermaid diagram
├── diff/                     # Lịch sử thay đổi
│   └── DIFF_FORMAT.md        # Schema ghi diff
└── refs/                     # References cho tasks/bugs
```

### `.test/` — Test scenarios
Test cases được sinh từ task list. Mỗi task có scenarios tương ứng.

**Cấu trúc:**
```
.test/
└── scenarios/
    ├── T1_{task_name}.md     # Test cho task 1
    ├── T2_{task_name}.md     # Test cho task 2
    └── scenario_bug_{id}.md  # Reproducible bug scenarios
```

### `.doc/` — Documentation
Kiến trúc sau khi code. Ghi lại luồng thực tế (không phải dự định).

**Files:**
- `PROGRESS.md` — Dashboard tiến độ
- `DECISION_LOG.md` — Log quyết định kiến trúc (Multi-AI)

### `.bug/` — Bug tracking
Zero-omission: không được bỏ sót file nào. Mọi bug link đến node trong `.map/`.

**Files:**
- `01_SCAN_LOG.md` — Kết quả quét bug
- `02_BUG_LIST.md` — Danh sách bug với proof

### `.token/` — Token tracking
Theo dõi token usage cho mọi phase.

**Cấu trúc:**
```
.token/
├── TOKEN_TRACKING.md         # Guide
├── interview/                # Log phỏng vấn
├── coding/                   # Log coding
├── bugfix/                   # Log bug fix
└── test/                     # Log testing
```

---

## 🔄 Luồng Hoạt Động Chi Tiết

```
[Bắt đầu]
    │
    ▼
.router/ ──► Đọc STATE.md ──► Xác định phase
    │
    ├── interview ──► .workflow/00_INTERVIEW.md
    │                     │
    │                     ▼
    │                 7 tiers interview
    │                     │
    │                     ▼
    │                 INTERVIEW_OUTPUT.yaml
    │                     │
    │                     ▼
    │                 Auto-generate:
    │                 ├── .agent/*
    │                 ├── .skill/{lang}.md
    │                 ├── .test/scenarios/
    │                 ├── .map/current/
    │                 └── .doc/PROGRESS.md
    │                     │
    │                     ▼
    │                 [USER APPROVAL GATE]
    │
    ├── planning ──► Review .agent/ + .skill/
    │
    ├── coding ──► .router/01_CODE.md
    │               ├── Load context (lazy)
    │               ├── GATE 1: Pre-code validation
    │               ├── Write code
    │               ├── GATE 2: Code validation
    │               ├── GATE 3: Post-code validation
    │               ├── Update .map/
    │               ├── Update .doc/PROGRESS.md
    │               └── Log token
    │
    ├── scan ──► .workflow/03_SCAN_FOR_BUGS.md
    │             ├── Khởi tạo .bug/ (nếu chưa có)
    │             ├── Scan .map/, .doc/, src/
    │             ├── Tạo .test/scenario_bug_{id}.md (proof)
    │             ├── Ghi .bug/01_SCAN_LOG.md
    │             └── Update .bug/02_BUG_LIST.md
    │
    ├── fix ──► .workflow/04_BUGFIX_LOOP.md
    │            ├── Tạo .sim/dry_run_{id}.md
    │            ├── Impact boundary analysis
    │            ├── Apply fix
    │            ├── Tạo .map/diff/v{X}_to_v{Y}.yaml
    │            └── Update .bug/02_BUG_LIST.md
    │
    └── testing ──► .workflow/05_TEST_PHASE.md
                   ├── Run tests
                   ├── Update .doc/PROGRESS.md
                   └── Decision: release | fix | coding
```

---

## 🤝 Quy Tắc Multi-AI

Khi nhiều AI (Claude, Gemini, GPT...) cùng làm việc:

1. **Đọc `.router/ROUTER.md` trước tiên** — xác định context cần load
2. **Đọc `DECISION_LOG.md` nếu có quyết định kiến trúc** — không được override
3. **Chỉ được bổ sung hoặc flag conflict** — không được xóa reasoning cũ
4. **Ký tên mọi thay đổi** — format: `[timestamp] [AI-name] [action] [reason]`
5. **STATE.md là single source of truth** — conflict về state → dừng, báo user

---

## 📊 Tiết Kiệm Token

| Trước | Sau | Tiết kiệm |
|-------|-----|-----------|
| Load full 00_INTERVIEW.md (442 dòng) | Router chọn tier phù hợp (~50-150 dòng) | 70-80% |
| Load toàn bộ .agent/ | Chỉ load files liên quan đến task | 50-60% |
| Bugfix load full context | Load minimal (2-3 files) | 60-70% |
| Code task load tất cả contracts | Chỉ load nếu thực sự cần | 30-40% |

---

## 📌 Quy Ước Ký Tên

Mọi nội dung trong hệ thống này phải có chữ ký:
```
[YYYY-MM-DD HH:MM] [AI-ID] [Hành động]
Ví dụ: [2026-03-29 10:00] [Claude-3.7] [Khởi tạo STATE.md phase=interview]
```

---

*Hệ thống này là bất biến về cấu trúc. Nội dung bên trong mỗi file được sinh động theo từng dự án.*
