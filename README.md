# AI Agent Base
> **Operating System for AI-Assisted Development** — Multi-language, multi-AI, resumable at any point.

AI Agent Base là **hệ điều hành cho phát triển phần mềm có hỗ trợ AI**. Thay vì AI nhận spec tĩnh rồi code, hệ thống này thiết lập một quy trình chặt chẽ buộc AI phải:

- **Phỏng vấn** người dùng qua 7 tiers trước khi code
- **Duy trì trạng thái** liên tục — có thể dừng và resume bất kỳ lúc nào
- **Simulate** mọi thay đổi trước khi apply
- **Kiểm tra tính nhất quán** giữa code, doc, map, contract
- **Track token usage** cho mọi tương tác

---

## � Quick Start

```bash
# 1. Clone hoặc copy template này vào dự án mới
cp -r ai-agent-base/ my-new-project/

# 2. Bắt đầu với interview — AI sẽ hỏi bạn qua 7 tiers
# Tier 0-6: Từ thông tin cơ bản đến xử lý lỗi

# 3. Sau interview, AI tự động sinh:
#    - .agent/ (specs cho AI)
#    - .skill/ (language rules)
#    - .test/ (test scenarios)
#    - .map/ (architecture)

# 4. Review và approve → Bắt đầu coding

# 5. Code → Test → Bugfix → Release (tự động)
```

---

## 📁 Directory Structure

```
project/
├── .router/          # Điều phối — AI đọc đầu tiên
│   ├── ROUTER.md     # Main router
│   └── 0X_*.md       # Phase routers (interview, code, bugfix...)
│
├── .workflow/        # Workflows
│   ├── 00_MASTER_WORKFLOW.md    # Orchestrator chính
│   ├── 02_GENERATE_AGENT.md     # Sinh specs từ interview
│   ├── 03_SCAN_FOR_BUGS.md      # Quét bug
│   ├── 04_BUGFIX_LOOP.md        # Fix bugs với simulation
│   └── 0X_*.md                  # Các workflows khác
│
├── .skill/           # Language rules (bất biến)
│   ├── _shared.md    # Rules chung
│   └── {lang}.md   # Rules từng ngôn ngữ
│
├── .agent/           # Project specs (sinh động)
│   ├── STATE.md      # State engine — driver của toàn hệ thống
│   ├── 00_MASTER.md  # Vai trò AI, constraints
│   ├── 01_STRUCTURE.md
│   ├── 02_TASK_LIST.md
│   └── 0X_*.md       # Contracts, rules, build config
│
├── .sim/             # Simulations trước khi fix
│   └── dry_run_*.md  # Impact boundary control
│
├── .map/             # Architecture maps
│   ├── current/      # Current state
│   ├── diff/         # Version diffs
│   └── refs/         # Task/bug references
│
├── .test/            # Test scenarios
│   └── scenarios/    # Mỗi task có test tương ứng
│
├── .doc/             # Documentation
│   ├── PROGRESS.md   # Dashboard tiến độ
│   ├── DECISION_LOG.md  # Multi-AI coordination
│   └── GUIDE.md      # Hướng dẫn chi tiết (file này)
│
├── .bug/             # Bug tracking (tạo sau khi code)
│   ├── 01_SCAN_LOG.md
│   └── 02_BUG_LIST.md
│
└── .token/           # Token tracking
    ├── interview/
    ├── coding/
    └── bugfix/
```

| Thư mục | Mục đích | Khi nào tạo |
|---------|----------|-------------|
| `.router/` | Điều phối AI, lazy loading | Template |
| `.workflow/` | Interview, generate, scan, fix workflows | Template |
| `.skill/` | Language rules (C++, C#, React...) | Template + Auto-gen |
| `.agent/` | Project specs, state engine | Auto-gen sau interview |
| `.sim/` | Simulation trước fix | Khi fix bug |
| `.map/` | Architecture maps | Auto-gen sau interview |
| `.test/` | Test scenarios | Auto-gen sau interview |
| `.doc/` | Docs, progress, decisions | Auto-gen + Update liên tục |
| `.bug/` | Bug tracking | Tạo sau khi code xong |
| `.token/` | Token usage logs | Tạo khi bắt đầu |

---

## 🔧 How It Works

### Phase 1: Interview (7 Tiers)
AI hỏi bạn qua 7 tiers từ cơ bản đến chi tiết. Sau mỗi tier, lưu checkpoint.

### Phase 2: Auto-Generate
Từ kết quả interview, AI tự động sinh toàn bộ specs:
- `.agent/` — Project configuration
- `.skill/` — Language-specific rules
- `.test/` — Test scenarios
- `.map/` — Architecture diagrams

### Phase 3: User Approval
Bạn review và approve specs trước khi code bắt đầu.

### Phase 4: Coding Loop
- Code từng task theo specs
- Validation gates sau mỗi task
- Auto-update maps và progress

### Phase 5: Bug Scan & Fix
- Quét bug từ code, maps, docs
- Mỗi bug phải có reproducible scenario
- Fix với simulation và impact boundary control

### Phase 6: Test & Release
- Run tests
- Update progress
- Release hoặc quay lại fix

---

## 🔒 Hard Gates (Không Thể Bypass)

| Gate | Kiểm tra | Nếu Fail |
|------|----------|----------|
| **GATE-1** | Interview hoàn thành? | Không generate specs |
| **GATE-2** | STATE.md updated sau mỗi step? | Không chạy step tiếp theo |
| **GATE-3** | Có simulation cho fix? | Không apply fix |

---

## � Sign-Off Convention

Mọi thay đổi phải có chữ ký:
```
[YYYY-MM-DD HH:MM] [AI-ID] [Action]
```

Ví dụ:
```
[2026-03-29 10:00] [Claude-3.7] [Create STATE.md phase=interview]
[2026-03-29 11:30] [Claude-3.7] [Generate .agent/ from interview]
[2026-03-29 14:00] [Claude-3.7] [Complete task T1: Setup Vite]
```

---

## 📖 Documentation

- **[GUIDE.md](.doc/GUIDE.md)** — Hướng dẫn chi tiết về cách hệ thống hoạt động
- **[DECISION_LOG.md](.doc/DECISION_LOG.md)** — Log quyết định kiến trúc (Multi-AI)
- **[AI_GUIDE.md](.agent/AI_GUIDE.md)** — Hướng dẫn cho AI làm việc trong hệ thống

---

## 🎯 Key Features

- ✅ **State Machine** — Mọi phase có allowed transitions
- ✅ **Lazy Loading** — Chỉ load file cần thiết, tiết kiệm 50-80% token
- ✅ **Consistency Checker** — Auto-validate code↔map↔doc↔contract
- ✅ **Impact Boundary Control** — Biết rõ fix ảnh hưởng đến đâu
- ✅ **Token Tracking** — Log mọi interaction
- ✅ **Multi-AI Ready** — Nhiều AI có thể collaborate không conflict

---

## ⚡ Token Optimization

| Cách cũ | Cách này | Tiết kiệm |
|---------|----------|-----------|
| Load full interview (442 dòng) | Router chọn tier (~50-150 dòng) | **70-80%** |
| Load toàn bộ .agent/ | Chỉ load files liên quan task | **50-60%** |
| Bugfix load full context | Load minimal (2-3 files) | **60-70%** |

---

## 🤝 Multi-AI Collaboration

Khi nhiều AI cùng làm việc:

1. Đọc `STATE.md` trước tiên — biết phase hiện tại
2. Đọc `DECISION_LOG.md` — không override quyết định cũ
3. Chỉ bổ sung hoặc flag conflict — không xóa reasoning
4. Ký tên mọi thay đổi
5. STATE.md là single source of truth

---

*Hệ thống này là bất biến về cấu trúc. Nội dung bên trong mỗi file được sinh động theo từng dự án.*
