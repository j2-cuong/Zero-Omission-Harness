# 06_CONSISTENCY_CHECKER.md — Automated Consistency Validation
> **Vai trò:** Tự động kiểm tra tính nhất quán giữa các file hệ thống.
> **Trigger:** Trước khi chuyển phase, sau khi code, sau khi fix.
> **Output:** Consistency report + Fix suggestions.
> **Rule:** Inconsistency detected → BLOCK transition.

---

## Consistency Checks

### 1. Code vs Map Consistency

```yaml
check_code_vs_map:
  description: "Code có khớp với .map/current/ không?"
  
  checks:
    - name: "Component existence"
      method: "So sánh component_tree.yaml với src/"
      pass: "Mọi component trong tree đều có file"
      fail: "Component trong tree nhưng không có file"
      
    - name: "Function existence"
      method: "So sánh data_flow.mmd với implementation"
      pass: "Mọi function trong flow đều implemented"
      fail: "Function trong flow nhưng không có implementation"
      
    - name: "Dependency accuracy"
      method: "Kiểm tra import/require khớp với tree"
      pass: "Dependencies khớp với component_tree"
      fail: "Có dependency không được khai báo"
```

### 2. Map vs Doc Consistency

```yaml
check_map_vs_doc:
  description: ".map/ có đồng bộ với .doc/ không?"
  
  checks:
    - name: "Progress sync"
      method: "So sánh PROGRESS.md với map status"
      pass: "Task status trong doc khớp với map"
      fail: "Task đánh dấu done nhưng map chưa update"
      
    - name: "Component documentation"
      method: "Kiểm tra component trong doc"
      pass: "Mọi component đều được document"
      fail: "Component có trong map nhưng không có trong doc"
```

### 3. Contract vs Implementation Consistency

```yaml
check_contract_vs_impl:
  description: "Implementation có tuân thủ contract không?"
  condition: "Chỉ check nếu có .agent/*CONTRACT.md"
  
  checks:
    - name: "API signature"
      method: "So sánh function signatures"
      pass: "Signatures khớp với contract"
      fail: "Signature mismatch với contract"
      
    - name: "Error handling"
      method: "Kiểm tra error cases"
      pass: "Mọi error case đều handled theo contract"
      fail: "Thiếu error handling theo contract"
      
    - name: "Data types"
      method: "Kiểm tra type definitions"
      pass: "Types khớp với contract"
      fail: "Type mismatch với contract"
```

### 4. Task vs Code Consistency

```yaml
check_task_vs_code:
  description: "Code có hoàn thành task requirements?"
  
  checks:
    - name: "Task completion"
      method: "Kiểm tra task T{n} có code tương ứng"
      pass: "Task có implementation"
      fail: "Task đánh dấu done nhưng không có code"
      
    - name: "Requirements met"
      method: "So sánh code với task requirements"
      pass: "Code đáp ứng mọi requirements"
      fail: "Code thiếu requirements"
```

### 5. Bug vs Fix Consistency

```yaml
check_bug_vs_fix:
  description: "Bug fix có giải quyết vấn đề?"
  
  checks:
    - name: "Fix completeness"
      method: "Kiểm tra fix có trong code"
      pass: "Bug được fix và verified"
      fail: "Bug trong list nhưng chưa fix"
      
    - name: "Regression check"
      method: "Kiểm tra không gây regression"
      pass: "Không có regression"
      fail: "Fix gây lỗi ở chỗ khác"
```

---

## Execution Flow

```
[Trigger: Pre-transition check]
        │
        ▼
[Load all relevant files]
        │
        ▼
[Run 5 consistency checks]
        │
        ├── Code vs Map
        ├── Map vs Doc
        ├── Contract vs Impl
        ├── Task vs Code
        └── Bug vs Fix
        │
        ▼
[Generate Report]
        │
        ├── All pass? → Allow transition
        └── Any fail? → BLOCK transition
        │
        ▼
[Log to .token/consistency/]
```

---

## Output Format

### Consistency Report

```yaml
consistency_check:
  timestamp: "2026-03-30T10:30:00Z"
  trigger: "pre_transition_coding_to_scan"
  
  results:
    code_vs_map:
      status: "PASS"
      details: "All components match"
      
    map_vs_doc:
      status: "FAIL"
      details: "Task T3 marked done but not in map"
      issues:
        - "src/components/Timeline.tsx: Not in component_tree.yaml"
        
    contract_vs_impl:
      status: "PASS"
      
    task_vs_code:
      status: "PASS"
      
    bug_vs_fix:
      status: "PASS"
      
  overall: "FAIL"
  block_transition: true
  
  fix_suggestions:
    - "Update .map/current/component_tree.yaml to include Timeline"
    - "Run .router/05_ARCH.md to sync map"
```

---

## Integration with STATE.md

```yaml
state_integration:
  before_transition:
    - action: "Run consistency checker"
    - condition: "All checks PASS"
    - then: "Allow transition"
    - else: "BLOCK, show fix suggestions"
    
  update_state:
    on_pass: 
      - "Update STATE.md consistency_flags"
      - "Log to .token/consistency/PASS.yaml"
    on_fail:
      - "Update STATE.md blockers"
      - "Log to .token/consistency/FAIL.yaml"
```

---

*Consistency checker đảm bảo mọi file đồng bộ trước khi chuyển phase.*
