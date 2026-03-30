# Zero-Omission-Harness (ZOH)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Mode](https://img.shields.io/badge/Mode-Light%20%7C%20Strict-yellow.svg)](CONFIG.yaml)

> **AI-driven software development framework** with state machine, consistency validation, and drift detection.

---

## TL;DR

**Zero-Omission-Harness** là hệ điều hành cho phát triển phần mềm có hỗ trợ AI. Thay vì AI nhận spec tĩnh rồi code, ZOH thiết lập quy trình chặt chẽ với:

- **State Machine** - Các phase rõ ràng (interview → planning → coding → testing → release)
- **Programmatic Enforcement** - Xác thực tuân thủ rule qua phân tích AST (LibCST/TypeScript)
- **Consistency Check** - Code, Map, Doc luôn đồng bộ
- **Token Budget** - Quản lý chi phí AI
- **Audit Trail** - Mọi thay đổi đều được ghi lại

**Light Mode** cho phép bạn bắt đầu ngay trong 10 phút.

---

## 📦 Cài đặt & Thiết lập

Trước khi chạy các lệnh ZOH, bạn cần cài đặt gói vào môi trường của mình:

```bash
# 1. Clone repository
git clone https://github.com/your-repo/Zero-Omission-Harness.git
cd Zero-Omission-Harness

# 2. Cài đặt ở chế độ editable để kích hoạt lệnh 'zoh'
pip install -e ".[all]"

# 3. Kiểm tra cài đặt
zoh --help

# 4. Chạy test suite
python -m pytest tests/
```

> [!NOTE]
> Nếu lệnh `zoh` không được nhận diện sau khi cài đặt, bạn luôn có thể sử dụng cú pháp module trực tiếp: `python -m zoh.cli <lệnh>`.

---

## 🚀 Khởi động nhanh

### 🚀 1. Khởi tạo dự án (Initialize)

Lệnh `init` sẽ tự động sinh ra toàn bộ hạ tầng "Zero-Omission" và thiết lập các quy tắc ứng xử cho AI Agent.

```bash
# Khởi tạo mặc định (Full Mode)
zoh init my-awesome-project

# Khởi tạo với preset và mode cụ thể
zoh init my-awesome-project --preset react --mode strict

# Khởi tạo tối giản (Chỉ lấy Rule & Config)
zoh init my-minimal-project --mode light
```

#### Các tùy chọn khởi tạo:
-   `path`: Đường dẫn thư mục đích (Bắt buộc).
-   `--preset`: Tập quy tắc kiến trúc (`default`, `react`, `dotnet`).
-   `--mode`: Độ sâu của hạ tầng:
    -   `full` (Mặc định): Đầy đủ 12 thư mục hạ tầng ZOH.
    -   `light`: Tối giản (Chỉ `.agent/` và `CONFIG.YAML`).
    -   `strict`: Bộ khung đầy đủ với các quy tắc an toàn nghiêm ngặt hơn.

---

### 📂 Bản đồ Hạ tầng "Zero-Omission"

Mọi dự án ZOH đều được xây dựng trên một cấu trúc hạ tầng chuẩn nhằm đảm bảo tính minh bạch tuyệt đối:

#### 🧠 Quản trị & Trí tuệ (Governance)
-   📁 **`.agent/`**: "Bộ não" của dự án. Chứa các quy tắc quản trị Master (`00_MASTER.md`) và danh sách Task (`02_TASK_LIST.md`).
-   📁 **`.skill/`**: Nơi lưu trữ "Trí tuệ chuyên biệt" cho AI Agent (React, C#, C++, v.v.).
-   📁 **`.workflow/`**: Các quy trình vận hành chuẩn (SOPs) cho từng giai đoạn (Phỏng vấn, Lập kế hoạch, Cài đặt).

#### 🛡️ Tính Ổn định & An toàn (Safety)
-   📁 **`.state/`**: Máy trạng thái tự động (`STATE_MACHINE.yaml`) và theo dõi giai đoạn hiện tại (`STATE.md`).
-   📁 **`.token/`**: Quản lý ngân sách tự động và theo dõi mức độ tiêu thụ AI Token.
-   📁 **`.sim/`**: Lưu trữ kết quả phân tích ảnh hưởng và mô phỏng rủi ro khi thay đổi code.

#### 🏗️ Kiến trúc & Tài liệu (Architecture)
-   📁 **`.map/`**: Sơ đồ kiến trúc hạ tầng và các biểu đồ phụ thuộc (Dependency Graph).
-   📁 **`.doc/`**: Toàn bộ tài liệu kỹ thuật và kiến thức chuyên sâu về dự án.
-   📁 **`.router/`**: Cấu hình điều phối các Agent chuyên biệt (AI Routing).

#### 🧪 Kiểm soát Chất lượng (Quality)
-   📁 **`.gates/`**: Các chốt chặn chất lượng tự động và cổng xác thực (Validation Gates).
-   📁 **`.bug/`**: Nhật ký quản lý lỗi và lịch sử giải quyết bug tập trung.
-   📁 **`.test/`**: Các kịch bản kiểm thử (Test Scenarios) và trường hợp xác thực.

---

### 🛠️ Các lệnh tự động hóa cốt lõi

Sau khi khởi tạo, hãy sử dụng các lệnh này để điều hành "Đội ngũ AI" của bạn:

| Lệnh | Hành động | Mục đích |
| :--- | :--- | :--- |
| `zoh status` | Dashboard | Xem giai đoạn hiện tại, task đang làm và ngân sách. |
| `zoh validate` | Consistency | Kiểm tra programmatic AST cho Code, Sơ đồ và Tài liệu. |
| `zoh transition` | Phase Change | Chuyển giai đoạn dự án với các chốt chặn tự động. |
| `zoh sim` | Simulation | Phân tích ảnh hưởng của một file trước khi thực hiện code. |
| `zoh task` | To-Do | Liệt kê hoặc cập nhật trạng thái công việc. |
| `zoh checkpoint` | Safety | Tạo điểm phục hồi an toàn trước khi thực hiện thay đổi lớn. |
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
zoh init [path] --preset <p> # Khởi tạo trong [path] từ preset
zoh init my_project --mode light # Ví dụ: khởi tạo trong thư mục 'my_project'

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

## 📈 ROI đã được chứng minh
- **Giảm 40%** số lỗi lọt vào production.
- **Tiết kiệm 30%** tiêu thụ Token AI.
- [Đọc Toàn bộ Case Study (Nguồn Template)](https://github.com/your-repo/Zero-Omission-Harness/blob/main/zoh/templates/default/.doc/03_CASE_STUDY.md)

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
