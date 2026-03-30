# 05_TEST_PHASE.md — Testing Workflow
> **Vai trò:** Chạy tests, ghi kết quả, update .doc/.
> **Input:** .agent/02_TASK_LIST.md + Code + .test/ scenarios
> **Output:** Test results + Updated .doc/PROGRESS.md
> **Trigger:** Sau coding hoặc bugfix phase

---

## Test Phase Entry

```yaml
trigger:
  - "Coding phase complete"
  - "Bugfix phase complete"
  - "User request: 'test', 'run tests'"
  - "Pre-commit hook"
  
preconditions:
  - check: "Code compiles/builds"
  - check: ".test/ directory exists"
  - check: "Test scenarios defined"
```

---

## Test Types

### 1. Unit Tests

```yaml
unit_tests:
  target: "Individual functions/components"
  location: ".test/unit/"
  
  scenarios:
    - name: "storage.write() with valid data"
      input: "{ key: 'test', value: 'data' }"
      expected: "success"
      
    - name: "storage.write() when full"
      input: "large data"
      expected: "throws StorageError"
      
    - name: "EntryCard renders with data"
      input: "entry with title, content"
      expected: "renders correctly"
```

### 2. Integration Tests

```yaml
integration_tests:
  target: "Component interactions"
  location: ".test/integration/"
  
  scenarios:
    - name: "Create entry → Save → Display in Timeline"
      flow:
        - "NewEntryPage.createEntry()"
        - "storage.save()"
        - "TimelinePage.refresh()"
      expected: "Entry appears in timeline"
      
    - name: "Full user journey"
      flow:
        - "Open app"
        - "Create 3 entries"
        - "Navigate to detail"
        - "Edit entry"
        - "Delete entry"
      expected: "All operations succeed"
```

### 3. Contract Tests

```yaml
contract_tests:
  target: "API/IPC contracts"
  location: ".test/contract/"
  
  scenarios:
    - name: "storage API respects contract"
      validate: ".agent/03_API_CONTRACT.md"
      
    - name: "Data types match Entry interface"
      validate: "types/Entry.ts"
```

### 4. Edge Case Tests

```yaml
edge_case_tests:
  target: "Boundary conditions"
  
  scenarios:
    - name: "Empty entry title"
      input: "{ title: '', content: 'test' }"
      expected: "Validation error"
      
    - name: "Very long content (> 10MB)"
      input: "10MB string"
      expected: "StorageError or truncation"
      
    - name: "Special characters in title"
      input: "{ title: '<script>alert(1)</script>' }"
      expected: "Sanitized or rejected"
```

---

## Test Execution

### Token Logging per Test

```yaml
test_execution:
  session_id: "test_{timestamp}"
  
  for_each_test:
    - load_test_file: 
        tokens: 100
        
    - setup_test_env:
        tokens: 200
        
    - run_test:
        tokens: 300
        
    - validate_result:
        tokens: 150
        
    - log_result:
        tokens: 50
        
    - total_per_test: 800
```

### Parallel vs Sequential

```yaml
execution_strategy:
  parallel:
    - "Unit tests"
    - "Independent integration tests"
    
  sequential:
    - "Tests with shared state"
    - "Contract tests (order matters)"
```

---

## Test Results Format

### .test/RESULTS_{timestamp}.md

```markdown
# Test Results — 2026-03-30T14:00:00Z

## Summary
| Category | Total | Passed | Failed | Skipped |
|----------|-------|--------|--------|---------|
| Unit | 25 | 24 | 1 | 0 |
| Integration | 8 | 7 | 1 | 0 |
| Contract | 5 | 5 | 0 | 0 |
| Edge Case | 10 | 9 | 1 | 0 |
| **Total** | **48** | **45** | **3** | **0** |

## Coverage
- **Lines:** 85%
- **Functions:** 92%
- **Branches:** 78%

## Failed Tests

### FAIL-001 — storage.write() edge case
- **Test:** storage.write() when localStorage full
- **Expected:** throw StorageError
- **Actual:** silent failure
- **Bug:** BUG-003 (newly created)
- **Severity:** Important

### FAIL-002 — Timeline rendering
- **Test:** Timeline renders 100+ entries
- **Expected:** Smooth scroll
- **Actual:** Lag, frame drops
- **Performance issue:** Needs optimization

### FAIL-003 — XSS in title
- **Test:** Entry with <script> in title
- **Expected:** Sanitized
- **Actual:** Raw HTML rendered
- **Security:** BUG-004 (Critical)

## Token Usage
```yaml
tokens:
  setup: 500
  execution: 3500
  analysis: 800
  report: 300
  total: 5100
```

## Recommendations
1. Fix BUG-003 (storage error handling)
2. Fix BUG-004 (XSS vulnerability) — Critical
3. Optimize Timeline rendering for large lists
```

---

## Update .doc/PROGRESS.md

```yaml
progress_update:
  action: "Append test results to dashboard"
  
  updates:
    - field: "Test coverage"
      value: "85%"
      
    - field: "Tests passed"
      value: "45/48"
      
    - field: "Bugs found"
      value: "3"
      
    - field: "Stability"
      value: "needs_fix"
```

---

## Token Logging

### .token/test/TEST_LOG.yaml

```yaml
test_session:
  timestamp: "2026-03-30T14:00:00Z"
  trigger: "post_coding"
  
  tokens:
    load_tests: 500
    setup_env: 800
    run_unit: 1200
    run_integration: 1500
    run_contract: 600
    run_edge: 1000
    analyze_failures: 800
    generate_report: 400
    update_progress: 200
    total: 7000
    
  results:
    total_tests: 48
    passed: 45
    failed: 3
    coverage: 85
    
  bugs_found:
    - id: "BUG-003"
      severity: "Important"
      test: "storage edge case"
    - id: "BUG-004"
      severity: "Critical"
      test: "XSS vulnerability"
      
  next_action: "bugfix_phase"
  reason: "Critical bug found"
```

---

## Decision Flow

```
[Run Tests]
      │
      ▼
[All pass?] ──YES──→ [Update .doc/]
      │                   │
      NO                  ▼
      │              [Phase: release]
      ▼
[Critical bug?] ──YES──→ [Halt → Bugfix]
      │
      NO
      │
      ▼
[Important bug?] ──YES──→ [Suggest bugfix]
      │                       │
      NO                      ▼
      │                  [Phase: bugfix]
      ▼
[Minor only?] ──YES──→ [Ask user]
                            │
                            ├── Fix now
                            └── Skip
```

---

## Integration with Other Phases

| Result | Next Phase | Action |
|--------|-----------|--------|
| All pass | Release | Update docs, prepare release |
| Critical fail | Bugfix | Immediate fix required |
| Important fail | Bugfix | Schedule fix |
| Minor only | User choice | Ask: fix now or later? |

---

*Test phase đảm bảo quality gate trước khi release.*
