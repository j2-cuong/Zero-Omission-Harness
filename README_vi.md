# Zero-Omission-Harness (ZOH)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Mode](https://img.shields.io/badge/Mode-Light%20%7C%20Strict-yellow.svg)](CONFIG.yaml)

> **AI-driven software development framework** with state machine, consistency validation, and drift detection.

---

## TL;DR

**Zero-Omission-Harness** là hệ điều hành cho phát triển phần mềm có hỗ trợ AI. Thay vì AI nhận spec tĩnh rồi code, ZOH thiết lập quy trình chặt chẽ với:

- **State Machine** - Các phase rõ ràng (interview → planning → coding → testing → release)
- **Validation Gates** - Kiểm tra trước khi chuyển phase
- **Consistency Check** - Code, Map, Doc luôn đồng bộ
- **Token Budget** - Quản lý chi phí AI
- **Audit Trail** - Mọi thay đổi đều được ghi lại

**Light Mode** cho phép bạn bắt đầu ngay trong 10 phút.

---

## Quick Start (Light Mode)

### 1. Clone & Install (2 phút)

```bash
git clone <repo-url>
cd Zero-Omission-Harness
pip install -e ".[cli]"
```

### 2. Khởi tạo (1 phút)

```bash
# Khởi tạo từ preset (react, dotnet, default)
zoh init --preset react --mode light

# Xem trạng thái hiện tại
zoh status
```

### 3. Kiểm tra & Mô phỏng

```bash
# Chạy kiểm tra tính nhất quán
zoh validate

# Mô phỏng ảnh hưởng của thay đổi (Impact Analysis)
zoh sim src/utils.ts
```

### 3. Bắt đầu Interview (5 phút)

```bash
# Chuyển sang phase interview
zoh transition interview

# Sau khi interview xong, chuyển sang planning
zoh transition planning
```

Hoàn tất! Xem [ONBOARDING.md](ONBOARDING.md) để biết thêm chi tiết.

---

## Key Features

| Feature | Mô tả |
|---------|-------|
| **State Machine** | Các phase rõ ràng với allowed transitions và guards |
| **Validation Gates** | Kiểm tra tự động trước mỗi chuyển phase |
| **Consistency Check** | Code ↔ Map ↔ Doc luôn đồng bộ |
| **Auto-fix** | Sửa lỗi nhỏ tự động (có approval) |
| **Checkpoint** | Backup trước mỗi thay đổi lớn |
| **Lock** | Ngăn xung đột khi nhiều AI cùng làm việc |
| **Token Budget** | Quản lý chi phí theo phase |

---

## ZOH CLI

### Cài đặt

```bash
# Cài đặt với CLI đầy đủ
pip install -e ".[cli]"

# Hoặc cài đặt cơ bản
pip install -e .
```

### Các lệnh chính

```bash
# Infrastructure & Initialization
zoh init --preset <p>      # Khởi tạo từ preset (default, react, dotnet)
zoh init --mode light      # Chế độ Light (chỉ .agent/ và CONFIG.yaml)

# Validation & Simulation
zoh validate                # Chạy kiểm tra tính nhất quán
zoh sim <files>             # Phân tích vùng ảnh hưởng (Simulation)
zoh check-consistency       # Kiểm tra nhanh các file chính

# State Management
zoh status                  # Xem trạng thái hiện tại
zoh transition <phase>      # Chuyển đổi phase

# Task Management
zoh task list               # Liệt kê danh sách task
zoh task complete <id>      # Đánh dấu hoàn thành task

# Checkpoint
zoh checkpoint create           # Tạo checkpoint
zoh checkpoint list             # Liệt kê checkpoints
zoh checkpoint rollback --id <id>  # Rollback

# Auto-fix
zoh apply-fix --id <drift_id> --dry-run   # Xem trước
zoh apply-fix --id <drift_id> --yes       # Áp dụng fix
```

---

## Light Mode vs Strict Mode

### Light Mode (Prototype)

```yaml
# CONFIG.yaml
mode: light

auto_fix:
  require_approval: false    # Auto-fix không cần approve
```

- Bỏ qua một số validation không quan trọng
- Auto-fix không cần approval
- Token budget không bắt buộc
- **Dùng cho:** Prototype, experiment, project nhỏ (< 1 tuần)

### Strict Mode (Production)

```yaml
# CONFIG.yaml
mode: strict

auto_fix:
  require_approval: true     # Cần user approve
```

- Tất cả validation gates bắt buộc
- Auto-fix cần approval
- Token budget enforced
- **Dùng cho:** Production, team collaboration, project lớn

---

## Directory Structure

```
Zero-Omission-Harness/
├── CONFIG.yaml              # Cấu hình chính ⭐
├── zoh/                     # Python package (code tập trung)
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── validator.py        # Main validator
│   ├── core/               # Core modules
│   │   ├── config.py       # Config loader
│   │   ├── state.py        # State validator
│   │   ├── checkpoint.py   # Checkpoint manager
│   │   └── lock.py         # Lock manager
│   └── validators/         # Validation modules
│       ├── code_contract.py
│       ├── map_code.py
│       ├── doc_reality.py
│       └── state_transition.py
├── .agent/                  # AI Agent files (data)
│   ├── 02_TASK_LIST.md     # Task list ⭐
│   └── contracts/           # API contracts
├── .state/                  # State management (data)
│   ├── STATE.md            # Current state ⭐
│   └── STATE_MACHINE.yaml  # State definitions
├── .map/                    # Architecture maps (data)
├── .doc/                    # Documentation (data)
├── .workflow/               # Workflow definitions
│   └── *.md                # Process documentation
├── .router/                 # AI routers
├── ONBOARDING.md           # Hướng dẫn 10 phút ⭐
└── README.md               # This file
```

**Code Python tập trung trong `zoh/`**, các thư mục `.agent/`, `.state/`, `.map/` chỉ chứa dữ liệu (YAML, MD).

---

## Hard Rules (AI PHẢI TUÂN THỦ)

### 1. Không Sửa STATE.md Trực Tiếp

❌ **Sai:** Edit `.state/STATE.md` bằng tay  
✅ **Đúng:** `zoh transition <phase>`

### 2. Validation Trước Transition

❌ **Sai:** Chuyển phase không validation  
✅ **Đúng:**
```bash
zoh validate        # Pass
zoh transition testing
```

### 3. Task Completion Qua CLI

❌ **Sai:** Edit `.agent/02_TASK_LIST.md` trực tiếp  
✅ **Đúng:** `zoh task complete T-001`

---

## Workflow

### Interview → Planning → Coding → Testing → Release

```bash
# Interview
zoh transition interview
# ... AI phỏng vấn user ...

# Planning
zoh transition planning
# ... Sinh task list ...

# Coding
zoh transition coding
# ... Code implementation ...
zoh task complete T-001

# Testing
zoh transition testing
zoh validate

# Release
zoh transition release
```

Xem chi tiết trong `.workflow/` directory.

---

## Git Hooks

```bash
# Cài đặt pre-commit hook
cp .agent/hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

# Hook sẽ chạy validation trước mỗi commit
```

---

## CI/CD

```yaml
# .github/workflows/consistency.yml
name: Consistency Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: zoh validate --strict
```

---

## Documentation

| File | Mô tả |
|------|-------|
| [ONBOARDING.md](ONBOARDING.md) | Hướng dẫn 10 phút cho người mới |
| [GUIDE.md](GUIDE.md) | Tài liệu chi tiết về kiến trúc |
| [.agent/AI_GUIDE.md](.agent/AI_GUIDE.md) | Hướng dẫn cho AI làm việc trong hệ thống |
| `.workflow/*.md` | Các workflow cụ thể |

---

## Contributing

1. Fork repository
2. Tạo branch: `git checkout -b feature/new-feature`
3. Commit: `git commit -am 'Add new feature'`
4. Push: `git push origin feature/new-feature`
5. Tạo Pull Request

---

## License

MIT License - xem [LICENSE](LICENSE) để biết thêm chi tiết.

---

*Ready to start? Run `zoh status` to check your system!*
