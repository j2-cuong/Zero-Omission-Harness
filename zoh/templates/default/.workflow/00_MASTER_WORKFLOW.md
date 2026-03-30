# 00_MASTER_WORKFLOW.md — Master Orchestrator
> **Vai trò:** Điều phối toàn bộ vòng đời dự án với token tracking.
> **Input:** User intent + STATE.md
> **Output:** Quyết định phase tiếp theo + Load context tối thiểu
> **Rule:** AI PHẢI theo workflow này. Không skip steps.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AI AGENT BASE SYSTEM                     │
│              (Vòng tuần hoàn với Token Tracking)           │
└─────────────────────────────────────────────────────────────┘

    ┌──────────┐
    │  START   │
    └────┬─────┘
         │
         ▼
    ┌──────────────────────────────────────────────────┐
    │  ROUTER: Phát hiện intent + STATE.md             │
    │  - Load context tối thiểu                        │
    │  - Log token usage                               │
    └────┬─────────────────────────────────────────────┘
         │
         ├──────────────────────────────────────────────┐
         │                                              │
         ▼                                              ▼
   ┌──────────┐                                 ┌──────────┐
   │INTERVIEW │                                 │  CODING  │
   │  PHASE   │                                 │  PHASE   │
   └────┬─────┘                                 └────┬─────┘
        │                                           │
        │ Log token per question                    │ Log token per task
        │ Save to:                                │ Save to:
        │ .token/interview/                       │ .token/coding/
        │                                           │
        ▼                                           ▼
   ┌─────────────────┐                        ┌─────────────────┐
   │AUTO-GENERATE    │                        │ Update:         │
   │.agent/ files    │                        │ - .doc/PROGRESS │
   │                 │                        │ - .map/current  │
   │Log: tokens used │                        │ - .skill/       │
   │for generation   │                        │ - .test/        │
   └────────┬────────┘                        └────────┬────────┘
            │                                         │
            └──────────────────┬──────────────────────┘
                               │
                               ▼
                    ┌───────────────────┐
                    │   BUG SCAN PHASE  │
                    │  (From .doc/.map) │
                    │                   │
                    │ Log scan tokens   │
                    │ to .token/bugfix/ │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │    BUG FIX LOOP   │
                    │                   │
                    │ 1. Create .sim/   │
                    │ 2. Fix → Log      │
                    │ 3. Update .map/   │
                    │    diff/          │
                    │ 4. Log tokens     │
                    │    to .token/     │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │    TEST PHASE     │
                    │                   │
                    │ Run tests → Log   │
                    │ results → Update  │
                    │ .doc/PROGRESS     │
                    │ Log tokens to     │
                    │ .token/test/      │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │     DECISION      │
                    │                   │
                    │ Bug found? → Fix  │
                    │ Done? → Release   │
                    │ New feature? →    │
                    │ Go to CODING      │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      RELEASE      │
                    │                   │
                    │ Final token       │
                    │ summary in        │
                    │ .token/summary/   │
                    └───────────────────┘
```

---

## Token Tracking Integration

### Mọi Phase đều log token

```yaml
token_logging:
  interview:
    file: ".token/interview/INTERVIEW_LOG.yaml"
    per: "question"
    fields: [prompt_tokens, response_tokens, context_size]
    
  coding:
    file: ".token/coding/CODING_LOG.yaml"
    per: "task"
    fields: [read_tokens, plan_tokens, code_tokens, validate_tokens]
    
  bugfix:
    file: ".token/bugfix/BUGFIX_LOG.yaml"
    per: "bug"
    fields: [analysis_tokens, sim_tokens, fix_tokens, test_tokens]
    
  test:
    file: ".token/test/TEST_LOG.yaml"
    per: "test_case"
    fields: [setup_tokens, run_tokens, report_tokens]
    
  summary:
    daily: ".token/daily/{YYYY-MM-DD}.yaml"
    project: ".token/summary/{project_name}.yaml"
```

### Token Budget by Phase

```yaml
budget_allocation:
  interview: 15000      # ~50 câu hỏi
  generate_agent: 3000  # Auto-gen .agent/
  coding: 50000         # Tất cả tasks
  bug_scan: 2000        # Quét từ .doc/.map
  bugfix: 20000         # Fix bugs
  test: 10000           # Run tests
  
  total_project_budget: 100000
  emergency_reserve: 10000
```

---

## Phase Transitions (with Token Check)

### 1. Interview → Generate

```yaml
trigger:
  - "INTERVIEW_OUTPUT.yaml status = complete"
  
validation:
  - check: "Token used < budget.interview"
  - check: "All required fields filled"
  
action:
  - run: ".workflow/02_GENERATE_AGENT.md"
  - log: 
      phase: "generate"
      tokens_used: "estimate from analysis"
      output_files: [".agent/*"]
  
next_phase: "planning"
```

### 2. Generate → Coding

```yaml
trigger:
  - ".agent/ files created"
  - "STATE.md phase = planning"
  
validation:
  - check: "02_TASK_LIST.md has tasks"
  - check: "01_STRUCTURE.md valid"
  
action:
  - update: "STATE.md phase = coding"
  - notify: "Ready to start T1"
  
next_phase: "coding"
```

### 3. Coding → Bug Scan

```yaml
trigger:
  - "All tasks completed"
  - "Code exists in src/"
  
validation:
  - check: ".map/current/ up to date"
  - check: ".doc/PROGRESS.md updated"
  
action:
  - run: ".workflow/03_SCAN_FOR_BUGS.md"
  - scan_from: [".doc/", ".map/", "src/"]
  - output: ".bug/01_SCAN_LOG.md"
  - log_tokens: ".token/bugfix/SCAN_LOG.yaml"
  
next_phase: "bugfix" (if bugs found) or "test"
```

### 4. Bug Scan → Bugfix Loop

```yaml
trigger:
  - "Bugs detected in scan"
  
validation:
  - check: "Bug list not empty"
  
action:
  for_each_bug:
    - create: ".sim/dry_run_{id}.md"
    - fix: "Code change"
    - update: ".map/diff/v{x}_to_v{y}.yaml"
    - update: ".bug/02_BUG_LIST.md"
    - log_tokens: ".token/bugfix/BUG_{id}.yaml"
  
next_phase: "test"
```

### 5. Test → Decision

```yaml
trigger:
  - "Tests completed"
  
validation:
  - check: "Test results logged"
  
action:
  - update: ".doc/PROGRESS.md" with test results
  - log_tokens: ".token/test/RESULTS.yaml"
  
decision:
  - if: "New bugs found" → goto: "bugfix"
  - if: "All pass" → goto: "release"
  - if: "New feature request" → goto: "interview" (partial)
```

---

## File Linkage Matrix

| Source | Target | Link Type | Auto-Update |
|--------|--------|-----------|-------------|
| `INTERVIEW_OUTPUT.yaml` | `.agent/00_MASTER.md` | Generate | ✅ Auto |
| `INTERVIEW_OUTPUT.yaml` | `.agent/01_STRUCTURE.md` | Generate | ✅ Auto |
| `01_STRUCTURE.md` | `.agent/02_TASK_LIST.md` | Derive | ✅ Auto |
| `02_TASK_LIST.md` | `.doc/PROGRESS.md` | Dashboard | ✅ Auto |
| `02_TASK_LIST.md` | `.map/refs/TASK-{id}.yaml` | Reference | ✅ Auto |
| `architecture.components` | `.map/current/component_tree.yaml` | Generate | ✅ Auto |
| `architecture.data_flow` | `.map/current/data_flow.mmd` | Generate | ✅ Auto |
| Code changes | `.map/diff/` | Diff | ✅ On commit |
| Code + Map | `.bug/01_SCAN_LOG.md` | Scan | 🔍 Triggered |
| Bug list | `.map/refs/BUG-{id}.yaml` | Reference | ✅ Auto |
| Bug fix | `.map/diff/v{x}_to_v{y}.yaml` | Version | ✅ Auto |
| Test results | `.doc/PROGRESS.md` | Update | ✅ Auto |
| All phases | `.token/*/` | Log | ✅ Always |

---

## Router Token Optimization

```yaml
lazy_loading_rules:
  - rule: "Chỉ load file liên quan đến task hiện tại"
  - rule: "Dùng summary thay vì full file nếu >100 dòng"
  - rule: "Load diff thay vì full file khi update"
  - rule: "Cache frequently used files"
  
context_compression:
  - method: "YAML > Markdown > Plain text"
  - method: "Line numbers > Full content"
  - method: "Bullet points > Paragraphs"
  - method: "Tables > Descriptions"
  
truncation_thresholds:
  code_file: 50        # Chỉ lấy 50 dòng quanh vị trí cần sửa
  log_file: 20       # Chỉ lấy 20 entries gần nhất
  doc_file: 100      # Chỉ lấy relevant section
  map_file: full     # Map files thường ngắn
```

---

## Emergency Procedures

### Token Budget Exhausted

```yaml
emergency:
  condition: "remaining_tokens < 1000"
  
  actions:
    1: "Lưu STATE.md ngay lập tức"
    2: "Ghi checkpoint vào .token/emergency/"
    3: "Thông báo user: Token hết, cần summary"
    4: "Tạo summary ngắn gọn của progress"
    5: "Dừng gracefully"
    
  resume:
    - "Đọc .token/summary/latest.yaml"
    - "Load STATE.md"
    - "Tiếp tục từ checkpoint"
```

---

## Daily Token Report

```yaml
# .token/daily/YYYY-MM-DD.yaml
date: "2026-03-30"
project: "project_name"

summary:
  total_tokens_used: 25000
  budget_remaining: 75000
  
breakdown:
  interview: 5000
  coding: 15000
  bugfix: 3000
  test: 2000
  
files_modified: 12
bugs_fixed: 3
tests_passed: 15
```

---

*Master workflow này đảm bảo mọi interaction được track và optimize.*
