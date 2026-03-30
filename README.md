# Zero-Omission-Harness (ZOH) v2.0

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Mode](https://img.shields.io/badge/Mode-Light%20%7C%20Strict-yellow.svg)](CONFIG.yaml)

- **Audit Trail** - Every change is logged

**Light Mode** lets you get started in just 10 minutes.

---

## 📦 Installation & Setup

Before running ZOH commands, you need to install the package in your environment:

```bash
# 1. Clone the repository
git clone https://github.com/your-repo/Zero-Omission-Harness.git
cd Zero-Omission-Harness

# 2. Install in editable mode to enable the 'zoh' command
pip install -e ".[all]"

# 3. Verify installation
zoh --help

# 4. Run tests
python -m pytest tests/
```

> [!NOTE]
> If the `zoh` command is not recognized after installation, you can always use the direct module syntax: `python -m zoh.cli <command>`.

---

## 🚀 Quick Start

### 🚀 1. Initialize a New Project

The `init` command scaffolds a complete "Zero-Omission" infrastructure and initializes the AI Agent behavior rules.

```bash
# Basic initialization (Full Mode)
zoh init my-awesome-project

# Initialize with a specific preset and mode
zoh init my-awesome-project --preset react --mode strict

# Lightweight initialization (Only Rules & Config)
zoh init my-minimal-project --mode light
```

#### Initialization Options:
-   `path`: The destination directory (required).
-   `--preset`: Architecture ruleset (`default`, `react`, `dotnet`).
-   `--mode`: Project depth:
    -   `full` (default): All 12 infrastructure folders.
    -   `light`: Minimalist (Only `.agent/` and `CONFIG.YAML`).
    -   `strict`: Full structure with hardened safety rules.

---

### 📂 "Zero-Omission" Project Structure

Every ZOH project is built upon a standard infrastructure designed for absolute traceability:

#### 🧠 Governance & Intelligence
-   📁 **`.agent/`**: The "Brain" of the project. Master governance rules (`00_MASTER.md`) and requirements (`02_TASK_LIST.md`).
-   📁 **`.skill/`**: Domain-specific intelligence for AI Agents (React, C#, C++, etc.).
-   📁 **`.workflow/`**: Standard Operating Procedures (SOPs) for every phase (Interview, Planning, Coding).

#### 🛡️ Stability & Safety
-   📁 **`.state/`**: Automated State Machine (`STATE_MACHINE.yaml`) and current phase tracking (`STATE.md`).
-   📁 **`.token/`**: Automated budget management and token usage tracking across all phases.
-   📁 **`.sim/`**: Impact analysis reports and dependency risk simulations.

#### 🏗️ Architecture & Documentation
-   📁 **`.map/`**: System architecture maps and visualized dependency graphs.
-   📁 **`.doc/`**: Comprehensive project documentation and domain-specific knowledge.
-   📁 **`.router/`**: Configuration for specialized AI routing.

#### 🧪 Quality Assurance
-   📁 **`.gates/`**: Automated quality checkpoints and validation gates.
-   📁 **`.bug/`**: Centralized bug logging and historical resolution database.
-   📁 **`.test/`**: High-level test scenarios and validation cases.

---

### 🛠️ Core Automation Commands

After initializing, use these commands to manage your AI workforce:

| Command | Action | purpose |
| :--- | :--- | :--- |
| `zoh status` | Dashboard | View current phase, tasks, and budget. |
| `zoh validate` | Consistency | Programmatic AST check for code, maps, and docs. |
| `zoh transition` | Phase Change | Move to the next project phase with automated guards. |
| `zoh sim` | Simulation | Analyze the impact of a code change before applying. |
| `zoh task` | To-Do | List or update project tasks. |
| `zoh checkpoint` | Safety | Create recovery points before dangerous operations. |
| **Lock** | Prevent conflicts when multiple AIs work together |
| **Token Budget** | Cost management per phase |

---

## ZOH CLI

### Installation

```bash
# Install with full CLI
pip install -e ".[cli]"

# Or install basic version
pip install -e .
```

### Main Commands

```bash
# Infrastructure & Initialization
zoh init [path] --preset <p> # Initialize in [path] from preset
zoh init my_project --mode light # Example: init in 'my_project' folder

# Validation & Simulation
zoh validate                # Run consistency validation
zoh sim <files>             # Run Impact Analysis (Simulation)
zoh check-consistency       # Quick check

# State Management
zoh status                  # View status
zoh transition <phase>      # Switch phase

# Task Management
zoh task list               # List tasks
zoh task complete <id>      # Mark as complete

# Checkpoint
zoh checkpoint create       # Create checkpoint
zoh checkpoint list         # List checkpoints
zoh checkpoint rollback --id <id>  # Rollback

# Auto-fix
zoh apply-fix --id <drift_id> --dry-run   # Preview
zoh apply-fix --id <drift_id> --yes       # Apply fix
```

---

## Light Mode vs Strict Mode

### Light Mode (Prototype)

```yaml
# CONFIG.yaml
mode: light

auto_fix:
  require_approval: false    # Auto-fix without approval
```

- Skip some non-critical validations
- Auto-fix without approval
- Token budget not enforced
- **Use for:** Prototypes, experiments, small projects (< 1 week)

### Strict Mode (Production)

```yaml
# CONFIG.yaml
mode: strict

auto_fix:
  require_approval: true     # Requires user approval
```

- All validation gates enforced
- Auto-fix requires approval
- Token budget enforced
- **Use for:** Production, team collaboration, large projects

## 📈 Proven ROI
- **40% Reduction** in production-bound bugs.
- **30% Reduction** in AI Token consumption.
- [Read the Full Case Study](.doc/03_CASE_STUDY.md)

---

## Directory Structure

```
Zero-Omission-Harness/
├── CONFIG.yaml              # Main configuration ⭐
├── zoh/                     # Python package (code centralized)
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
├── ONBOARDING.md           # 10-minute guide ⭐
└── README.md               # This file
```

**Python code is centralized in `zoh/`**, directories `.agent/`, `.state/`, `.map/` contain only data (YAML, MD).

---

## Hard Rules (AI MUST FOLLOW)

### 1. Do Not Edit STATE.md Directly

❌ **Wrong:** Edit `.state/STATE.md` manually  
✅ **Correct:** `zoh transition <phase>`

### 2. Validation Before Transition

❌ **Wrong:** Switch phase without validation  
✅ **Correct:**
```bash
zoh validate        # Pass
zoh transition testing
```

### 3. Task Completion via CLI

❌ **Wrong:** Edit `.agent/02_TASK_LIST.md` directly  
✅ **Correct:** `zoh task complete T-001`

---

## Workflow

### Interview → Planning → Coding → Testing → Release

```bash
# Interview
zoh transition interview
# ... AI interviews user ...

# Planning
zoh transition planning
# ... Generate task list ...

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

See details in `.workflow/` directory.

---

## Git Hooks

```bash
# Install pre-commit hook
cp .agent/hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

# Hook will run validation before each commit
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

| File | Description |
|------|-------------|
| [ONBOARDING.md](ONBOARDING.md) | 10-minute guide for newcomers |
| [GUIDE.md](GUIDE.md) | Detailed architecture documentation |
| [.agent/AI_GUIDE.md](.agent/AI_GUIDE.md) | Guide for AI working in the system |
| `.workflow/*.md` | Specific workflows |

---

## Contributing

1. Fork repository
2. Create branch: `git checkout -b feature/new-feature`
3. Commit: `git commit -am 'Add new feature'`
4. Push: `git push origin feature/new-feature`
5. Create Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*Ready to start? Run `zoh status` to check your system!*
