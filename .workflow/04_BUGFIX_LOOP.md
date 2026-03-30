# 04_BUGFIX_LOOP.md — Bug Fix Workflow
> **Vai trò:** Fix bugs từ scan, update .map diff, log tokens.
> **Input:** .bug/01_SCAN_LOG.md + .bug/02_BUG_LIST.md
> **Output:** Fixed code + .map/diff/ + Updated bug status
> **Rule:** Mỗi fix PHẢI có simulation + token log.

---

## Fix Loop Overview

```
[BUG LIST]
      │
      ▼
[Pick BUG-{id}] 
      │
      ▼
[Create .sim/dry_run_{id}.md] ──→ Log tokens
      │
      ▼
[Simulate fix impact]
      │── CASCADE_RISK?
      │── BREAKING_CHANGE?
      ▼
[Apply fix to code] ──→ Log tokens
      │
      ▼
[Validate fix]
      │── Tests pass?
      │── No regression?
      ▼
[Update .map/diff/]
      │
      ▼
[Update .bug/02_BUG_LIST.md]
      │── Status: FIXED
      ▼
[Log tokens to .token/bugfix/]
      │
      ▼
[Next bug?] ──→ Loop ─┐
      │               │
      No              │
      │               │
      ▼               │
[Transition to TEST] ←┘
```

---

## Bug Selection Strategy

```yaml
selection_order:
  1: "Critical bugs first"
  2: "Important bugs (by impact)"
  3: "Minor bugs (if time permits)"
  
priority_calculation:
  severity_weight: 0.5
  user_impact_weight: 0.3
  fix_complexity_weight: 0.2  # Lower = higher priority
```

---

## Simulation Phase (.sim/)

### Required for every fix

```yaml
simulation_requirement:
  when:
    - "Severity >= Important"
    - "Affects > 1 module"
    - "Changes API contract"
    - "Memory/resource related"
    
  output: ".sim/dry_run_{bug_id}.md"
```

### .sim/dry_run_{id}.md Format

```markdown
# Simulation — BUG-{id}

## Target
- **Bug:** BUG-001
- **File:** src/core/storage.ts:45
- **Severity:** Critical

## Current State
```typescript
// BEFORE (buggy code)
function write(data: string) {
  localStorage.setItem('key', data);  // No error handling
}
```

## Proposed Fix
```typescript
// AFTER (fixed code)
function write(data: string) {
  try {
    localStorage.setItem('key', data);
  } catch (e) {
    console.error('Storage full:', e);
    throw new StorageError('Unable to save');
  }
}
```

## Impact Analysis

### Affected Modules
- `storage.ts`: Modified ✓
- `Timeline.tsx`: Uses storage → Cần handle error
- `Settings.tsx`: Uses storage → Cần handle error

### API Changes
- `write()` giờ throw `StorageError`
- Callers cần thêm try-catch

### Risk Assessment
- **Breaking change:** YES (throws new error)
- **Regression risk:** LOW (adds safety)
- **Test required:** YES

## Token Usage
```yaml
tokens:
  analysis: 400
  sim_creation: 300
  total: 700
```

## Approval
- [ ] Reviewed by user
- [ ] Tests written
- [ ] Ready to apply
```

---

## Fix Application

### Steps

```yaml
apply_fix:
  step_1:
    action: "Read file cần sửa"
    log_tokens: "read"
    
  step_2:
    action: "Tạo fix (edit/multi_edit)"
    log_tokens: "fix_prompt + fix_response"
    
  step_3:
    action: "Verify syntax/compile"
    log_tokens: "validation"
    
  step_4:
    action: "Update .map/diff/"
    log_tokens: "diff_generation"
    
  step_5:
    action: "Update .bug/02_BUG_LIST.md"
    log_tokens: "status_update"
    
  step_6_token_log:
    action: "🔴 BẮT BUỘC: Log token usage"
    output: ".token/bugfix/BUG_{id}.yaml"
    mandatory: true
    fail_action: "KHÔNG ĐƯỢC ĐÁNH DẤU BUG FIXED"
    format:
      bug_id: "BUG-{id}"
      timestamp_start: "ISO-8601"
      timestamp_end: "ISO-8601"
      tokens:
        analysis: 600
        sim_creation: 300
        fix_implementation: 800
        map_diff: 200
        total: 3300
      result: "FIXED|FAILED|REJECTED"
```

---

## Map Diff Generation

### .map/diff/v{X}_to_v{Y}.yaml

```yaml
diff_id: "v0.1.0_to_v0.1.1"
bug_triggered: "BUG-001"
date: "2026-03-30"

changes:
  components:
    modified:
      - name: "storage"
        changes:
          - "Thêm error handling trong write()"
          - "Thêm throw StorageError"
        breaking: true
        
  contracts:
    api_changes:
      - function: "storage.write()"
        old: "write(data: string): void"
        new: "write(data: string): void | throws StorageError"
        
  impact:
    modules_affected:
      - "Timeline.tsx"
      - "Settings.tsx"
      - "NewEntryPage.tsx"
      
    action_required:
      - "Add try-catch around storage.write() calls"
      - "Add error UI for storage errors"

tokens_used:
  fix: 1200
  diff_generation: 300
  total: 1500
```

---

## Token Logging

### .token/bugfix/BUG_{id}.yaml

```yaml
bug_fix_session:
  bug_id: "BUG-001"
  timestamp_start: "2026-03-30T11:00:00Z"
  timestamp_end: "2026-03-30T11:15:00Z"
  
  tokens:
    # Phase 1: Analysis
    read_bug_report: 200
    read_source_code: 400
    analysis: 600
    
    # Phase 2: Simulation
    sim_creation: 300
    sim_review: 200
    
    # Phase 3: Fix
    fix_planning: 400
    fix_implementation: 800
    fix_validation: 300
    
    # Phase 4: Update
    map_diff: 200
    bug_list_update: 100
    
    total: 3300
    
  fix_details:
    files_modified: 1
    lines_changed: 15
    breaking_change: true
    
  result:
    status: "FIXED"
    tests_passed: true
    regression: false
```

---

## State Machine

```yaml
bug_status_flow:
  OPEN:
    - action: "Start analysis"
    - next: ANALYZING
    
  ANALYZING:
    - action: "Root cause analysis"
    - next: SIM_PENDING (nếu cần sim)
    - next: APPROVED (nếu simple fix)
    
  SIM_PENDING:
    - action: "Create .sim/dry_run"
    - next: APPROVED (nếu pass review)
    - next: REJECTED (nếu risk too high)
    
  APPROVED:
    - action: "Apply fix"
    - next: FIXING
    
  FIXING:
    - action: "Code changes"
    - next: TESTING
    
  TESTING:
    - action: "Run tests"
    - next: VERIFIED (nếu pass)
    - next: ANALYZING (nếu fail)
    
  VERIFIED:
    - action: "Update status, close bug"
    - next: CLOSED
    
  REJECTED:
    - action: "Mark won't fix"
    - next: CLOSED
```

---

## Integration with .bug/02_BUG_LIST.md

```markdown
## 🔴 Critical

### BUG-001 — Unhandled storage exception
- **File:** src/core/storage.ts:45
- **Severity:** Critical
- **Status:** VERIFIED ✅
- **Fixed:** 2026-03-30
- **Sim file:** .sim/dry_run_BUG-001.md
- **Diff:** .map/diff/v0.1.0_to_v0.1.1.yaml
- **Token used:** 3300
- **Signed:** [Claude-3.7] [2026-03-30 11:15]
```

---

*Mỗi bug fix là 1 vòng lặp hoàn chỉnh với simulation, fix, validation, và logging.*
