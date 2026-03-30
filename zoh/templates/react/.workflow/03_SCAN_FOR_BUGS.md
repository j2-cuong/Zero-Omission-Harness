# 03_SCAN_FOR_BUGS.md — Bug Detection & Proof Workflow
> **Vai trò:** Quét và **CHỨNG MINH** bug bằng reproducible scenario
> **Input:** .doc/PROGRESS.md + .map/current/* + src/ code
> **Output:** .bug/01_SCAN_LOG.md + .test/scenario_bug_{id}.md + Cập nhật .bug/02_BUG_LIST.md
> **Trigger:** Sau khi coding phase hoàn thành
> **Rule:** Bug không có reproducible scenario = KHÔNG được gọi là bug

---

## Philosophy: "Prove, Don't Just Detect"

```yaml
bug_proof_requirement:
  old_workflow: "Detect → Log → List"  
  new_workflow: "Detect → Prove → Scenario → List"
  
  proof_required:
    - reproducible_scenario: ".test/scenario_bug_{id}.md"
    - deterministic: "Chạy lại 100 lần, lỗi xảy ra 100 lần"
    - minimal: "Steps tối thiểu để reproduce"
    - evidence: "Logs, screenshots, stack traces"
    
  rule: "Không reproduce được → KHÔNG PHẢI BUG → Remove khỏi list"
```

---

## Scan Trigger

```yaml
trigger:
  - "STATE.md phase = coding_complete"
  - "All tasks in 02_TASK_LIST.md done"
  - "Code exists in src/"
  - "User yêu cầu: 'scan', 'check bugs', 'review'"
  
preconditions:
  - check: ".map/current/component_tree.yaml exists"
  - check: ".map/current/data_flow.mmd exists"
  - check: ".doc/PROGRESS.md updated"
  
init_bug_dir:
  condition: ".bug/ directory chưa tồn tại"
  action: "Tạo mới .bug/ với template 02_BUG_LIST.md"
  source: ".workflow/templates/BUG_LIST_TEMPLATE.md"
```

---

## Scan Sources

### 1. Architecture Consistency Scan

```yaml
scan_architecture:
  source: ".map/current/"
  
  checks:
    - name: "Component Tree vs Code"
      method: "So sánh component_tree.yaml với thực tế src/"
      detect: "Component trong map nhưng không có code"
      
    - name: "Data Flow Validation"
      method: "Parse data_flow.mmd, kiểm tra implementation"
      detect: "Flow trong diagram nhưng không có trong code"
      
    - name: "Dependency Check"
      method: "Kiểm tra import/include dependencies"
      detect: "Circular dependencies, missing deps"
```

### 2. Code Quality Scan

```yaml
scan_code_quality:
  source: "src/"
  
  checks:
    - name: "Contract Violations"
      method: "So sánh với .agent/*CONTRACT.md"
      detect: "API signature mismatch, missing error handling"
      
    - name: "Resource Leaks"
      method: "Static analysis patterns"
      detect: "Unclosed files, memory leaks, unhandled promises"
      
    - name: "Error Handling Gaps"
      method: "Tìm functions không có try-catch"
      detect: "Missing error handlers, no validation"
      
    - name: "Concurrency Issues"
      method: "Tìm shared state, race conditions"
      detect: "Non-thread-safe operations, missing locks"
```

### 3. Documentation Sync Scan

```yaml
scan_doc_sync:
  source: ".doc/ + .map/"
  
  checks:
    - name: "Progress vs Code"
      method: "So sánh PROGRESS.md với code thực tế"
      detect: "Task đánh dấu done nhưng code không có"
      
    - name: "Map Drift"
      method: "Diff giữa map và code"
      detect: "Map outdated, missing new functions"
```

---

## Bug Classification & Proof Level

```yaml
severity_levels:
  Critical:
    examples: ["Crash/segfault", "Data corruption", "Security vulnerability"]
    proof_required: "MUST"
    scenario_format: "step-by-step reproduction"
    must_attach: ["stack trace", "input data", "environment"]
    
  Important:
    examples: ["Memory leak", "API mismatch", "Missing error handling"]
    proof_required: "MUST"
    scenario_format: "demonstration steps"
    must_attach: ["logs", "observed vs expected"]
    
  Minor:
    examples: ["Code style", "Doc mismatch", "Unused imports"]
    proof_required: "OPTIONAL"
    scenario_format: "description"
    must_attach: []

proof_requirement:
  critical_important: "BẮT BUỘC có scenario_bug_{id}.md"
  minor: "Có thể chỉ có description trong bug list"
  
not_a_bug_conditions:
  - "Không reproduce được"
  - "Non-deterministic (race condition không xác định)"
  - "Environment-specific (chỉ lỗi trên máy user)"
  - "Không có steps rõ ràng"
```

---

## Output Format

### .bug/01_SCAN_LOG.md

```markdown
# Scan Log — {timestamp}

## Session Info
- **Scanner:** AI-Agent-Base
- **Timestamp:** 2026-03-30T10:45:00Z
- **Token used:** 1500
- **Files scanned:** 25

## Scan Results

### 🔴 Critical (2)

### BUG-{id} Entry (với Proof)

```markdown
### BUG-001 — Unhandled storage exception
- **Severity:** Critical
- **File:** src/core/storage.ts:45
- **Issue:** Code không có try-catch khi ghi localStorage
- **Impact:** App crash khi storage full

#### 🔍 Proof / Reproduction
- **Reproducible:** 100% (10/10 attempts)
- **Scenario file:** `.test/scenario_bug_BUG-001.md`
- **Steps:**
  1. Fill localStorage to quota (5MB)
  2. Try to save new entry
  3. App crashes with uncaught exception

#### 📎 Evidence
```
Error: QuotaExceededError: The quota has been exceeded.
    at Storage.write (storage.ts:45)
    at NewEntryPage.save (NewEntryPage.tsx:120)
```

#### 🗺️ Map Node
- **Component:** storage
- **Function:** write()
- **Line:** 45

---

#### Reproducible Scenario Format (.test/scenario_bug_{id}.md)

```markdown
# Bug Reproduction: BUG-001

## Metadata
- **Bug ID:** BUG-001
- **Severity:** Critical
- **File:** src/core/storage.ts:45

## Reproduction Steps
1. [Setup] Clear localStorage, then fill with dummy data to 5MB
2. [Action] Navigate to NewEntryPage
3. [Action] Fill title and content
4. [Action] Click Save button
5. [Expected] Entry saved or error handled gracefully
6. [Actual] App crashes, white screen

## Environment
- Browser: Chrome 120
- OS: Windows 11
- localStorage quota: 5MB (full)

## Evidence
```
[stack trace here]
```

## Deterministic Check
- Attempt 1: ✅ Crash
- Attempt 2: ✅ Crash
- Attempt 3: ✅ Crash
- **Conclusion:** 100% reproducible
```

### 🟡 Important (3)
[...]

### ⚪ Minor (5)
[...]

## Token Usage Log
```yaml
tokens:
  read_source: 500
  analysis: 800
  report_generation: 200
  total: 1500
```
```

---

## Token Logging

```yaml
# .token/bugfix/SCAN_LOG.yaml
scan_session:
  timestamp: "2026-03-30T10:45:00Z"
  
  tokens:
    read_context: 800      # Đọc .map/, .doc/, src/
    analysis: 1200         # Phân tích
    report_write: 300      # Ghi 01_SCAN_LOG.md
    total: 2300
    
  files_scanned:
    count: 25
    total_lines: 3500
    
  bugs_detected:
    critical: 2
    important: 3
    minor: 5
    
  output:
    scan_log: ".bug/01_SCAN_LOG.md"
    bug_list_updated: ".bug/02_BUG_LIST.md"
```

---

## Workflow Integration

```
[Scan Trigger]
      │
      ▼
[Khởi tạo .bug/ nếu chưa có] ──→ Tạo 02_BUG_LIST.md template
      │
      ▼
[Load .map/, .doc/, src/] ──→ Log tokens
      │
      ▼
[Run 3 scan types]
      │
      ├── Architecture scan
      ├── Code quality scan
      └── Doc sync scan
      │
      ▼
[Classify bugs by severity]
      │
      ▼
[Write 01_SCAN_LOG.md] ──→ Log tokens
      │
      ▼
[Update 02_BUG_LIST.md] ──→ Thêm bugs phát hiện được
      │
      ▼
[Log to .token/bugfix/]
      │
      ▼
[Transition to BUGFIX phase]
```

---

## Decision Matrix

| Bugs Found | Action |
|------------|--------|
| 0 | Skip to TEST phase |
| 1-2 Minor | Ask user: Fix now or later? |
| 1+ Important | Auto-transition to BUGFIX |
| 1+ Critical | Halt, immediate fix required |

---

*Scan workflow này đảm bảo mọi vấn đề được phát hiện trước khi release.*
