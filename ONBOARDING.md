# Zero-Omission-Harness Onboarding Guide

> **Thời gian:** 10 phút  
> **Mục tiêu:** Hiểu và chạy được ZOH cơ bản  
> **Đối tượng:** Developer mới hoặc AI Assistant

---

## Quick Start (5 phút)

### 1. Cài Đặt

```bash
# Clone repository
git clone <repo-url>
cd Zero-Omission-Harness

# Cài dependencies
pip install -r requirements.txt

# Hoặc cài với extras
pip install -e ".[dev]"
```

### 2. Cấu Hình Mode

Chỉnh sửa `CONFIG.yaml`:

```yaml
# Light mode - prototype
mode: light

# Hoặc Strict mode - production
mode: strict
```

**Light mode bỏ qua:**
- Một số validation gates
- Token budget enforcement
- Strict approval cho auto-fix

### 3. Chạy Validation

```bash
# Kiểm tra hệ thống
zoh check-consistency

# Hoặc chi tiết hơn
zoh validate --verbose
```

---

## ZOH CLI Commands

### Core Commands

| Command | Mô tả | Ví dụ |
|---------|-------|-------|
| `zoh validate` | Chạy validation | `zoh validate --output report.md` |
| `zoh transition` | Chuyển phase | `zoh transition coding` |
| `zoh status` | Xem trạng thái | `zoh status` |
| `zoh task` | Quản lý task | `zoh task complete T-001` |
| `zoh apply-fix` | Fix drift | `zoh apply-fix --id drift_001 --dry-run` |
| `zoh checkpoint` | Quản lý checkpoint | `zoh checkpoint create` |

### Transition Flow

```bash
# 1. Kiểm tra phase hiện tại
zoh status

# 2. Chạy validation
zoh validate

# 3. Chuyển phase (nếu validation pass)
zoh transition coding

# 4. Kiểm tra lại
zoh status
```

---

## Cấu Trúc Thư Mục

```
Zero-Omission-Harness/
├── CONFIG.yaml              # Cấu hình chính ⭐
├── .agent/                  # AI Agent files
│   ├── consistency/         # Validators & CLI
│   │   ├── cli.py          # Entry point ⭐
│   │   ├── validator.py    # Main validator
│   │   ├── checkpoint_manager.py
│   │   ├── lock_manager.py
│   │   └── validators/      # Individual validators
│   ├── 02_TASK_LIST.md     # Task list ⭐
│   └── contracts/           # API contracts
├── .state/                  # State management
│   ├── STATE.md            # Current state ⭐
│   ├── STATE_MACHINE.yaml  # State definitions
│   └── history/             # Audit logs
├── .map/                    # Architecture maps
├── .doc/                    # Documentation
├── .bug/                    # Bug tracking
├── .token/                  # Token logs
├── .gates/                  # Validation gates
└── .workflow/               # Workflow definitions
```

**Files quan trọng (⭐):** AI và developer cần biết

---

## Workflow Cơ Bản

### 1. Interview Phase

- AI đọc `.router/00_INTERVIEW.md`
- Output: `.agent/00_INTERVIEW_OUTPUT.yaml`

### 2. Planning Phase

```bash
# Chuyển sang planning
zoh transition planning

# Sinh task list
# (AI sẽ tự động sinh .agent/02_TASK_LIST.md)
```

### 3. Coding Phase

```bash
# Chuyển sang coding
zoh transition coding

# Code implementation...

# Complete task
zoh task complete T-001
```

### 4. Testing Phase

```bash
# Chuyển sang testing
zoh transition testing

# Chạy tests
# Validation
zoh validate
```

---

## Light Mode vs Strict Mode

### Light Mode

```yaml
# CONFIG.yaml
mode: light

auto_fix:
  require_approval: false  # Auto-fix không cần approve
  
validation:
  # Một số gates optional
```

**Khi nào dùng:**
- Prototype nhanh
- Experiment
- Small project (< 1 week)

### Strict Mode

```yaml
# CONFIG.yaml
mode: strict

auto_fix:
  require_approval: true   # Cần user approve
  
validation:
  # Tất cả gates bắt buộc
```

**Khi nào dùng:**
- Production code
- Team collaboration
- Large project (> 1 week)

---

## Hard Rules (AI PHẢI TUÂN THỦ)

### Rule 1: Không Sửa STATE.md Trực Tiếp

❌ **Sai:**
```
AI edit file .state/STATE.md
  phase: coding -> testing
```

✅ **Đúng:**
```bash
zoh transition testing
```

### Rule 2: Validation Trước Transition

❌ **Sai:**
```
Chuyển phase không validation
```

✅ **Đúng:**
```bash
zoh validate        # Pass
zoh transition testing
```

### Rule 3: Task Completion Qua CLI

❌ **Sai:**
```
AI edit .agent/02_TASK_LIST.md
  - [ ] Task -> - [x] Task
```

✅ **Đúng:**
```bash
zoh task complete T-001
```

---

## Troubleshooting

### Lỗi: "Cannot acquire lock"

```bash
# Kiểm tra lock status
zoh status

# Hoặc force unlock (cẩn thận!)
zoh force-unlock --reason "stale_lock"
```

### Lỗi: "Validation FAIL"

```bash
# Xem chi tiết lỗi
zoh validate --verbose

# Hoặc xem report
ls .agent/consistency/reports/
cat .agent/consistency/reports/consistency_*.md
```

### Lỗi: "Transition not allowed"

```bash
# Kiểm tra allowed transitions
zoh status
# Xem cột "Allowed Transitions"
```

---

## Git Hooks

```bash
# Copy pre-commit hook
cp .agent/hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

# Hook sẽ tự động chạy validation trước mỗi commit
```

---

## CI/CD Integration

```yaml
# .github/workflows/consistency.yml
name: Consistency Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run consistency check
        run: zoh validate --strict
```

---

## Resources

- **CLI Help:** `zoh --help`
- **Workflow:** Xem `.workflow/` directory
- **Config:** `CONFIG.yaml`
- **State:** `.state/STATE.md`

---

*Sẵn sàng để bắt đầu? Chạy `zoh status` để kiểm tra!*
