# Zero-Omission-Harness (ZOH)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Mode](https://img.shields.io/badge/Mode-Light%20%7C%20Strict-yellow.svg)](CONFIG.yaml)

> **AI-driven software development framework** with state machine, consistency validation, and drift detection.

---

## TL;DR

**Zero-Omission-Harness** is an operating system for AI-assisted software development. Instead of AI receiving a static spec and then coding, ZOH establishes a strict workflow with:

- **State Machine** - Clear phases (interview → planning → coding → testing → release)
- **Validation Gates** - Check before phase transition
- **Consistency Check** - Code, Map, Doc always in sync
- **Token Budget** - Manage AI costs
- **Audit Trail** - Every change is logged

**Light Mode** lets you get started in just 10 minutes.

---

## Quick Start (Light Mode)

### 1. Clone & Install (2 minutes)

```bash
git clone <repo-url>
cd Zero-Omission-Harness
pip install -e ".[cli]"
```

### 2. Initialize (1 minute)

```bash
# Initialize from preset (react, dotnet, default)
zoh init --preset react --mode light

# View current status
zoh status
```

### 3. Verification & Simulation

```bash
# Run consistency check
zoh validate

# Simulate impact of changes (Impact Analysis)
zoh sim src/utils.ts
```

### 3. Start Interview (5 minutes)

```bash
# Switch to interview phase
zoh transition interview

# After interview, switch to planning
zoh transition planning
```

Done! See [ONBOARDING.md](ONBOARDING.md) for more details.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **State Machine** | Clear phases with allowed transitions and guards |
| **Validation Gates** | Automated checks before each phase transition |
| **Consistency Check** | Code ↔ Map ↔ Doc always in sync |
| **Auto-fix** | Automatic fix for small issues (with approval) |
| **Checkpoint** | Backup before major changes |
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
zoh init --preset <p>      # Initialize from preset (default, react, dotnet)
zoh init --mode light      # Light mode (only .agent/ and CONFIG.yaml)

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
