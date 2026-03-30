# STATE.md — State Engine Driver
> **Vai trò:** ĐIỀU KHIỂN toàn bộ flow. Không phải log — là driver.
> **Input:** Đọc đầu tiên khi AI vào. Không có STATE → DỪNG.
> **Output:** Quyết định: phase nào? load file nào? action gì?
> **Rule CỨNG:** 
> 1. Đọc STATE trước mọi action
> 2. Không match schema → Không chạy
> 3. Transition không hợp lệ → DỪNG

---

## STATE MACHINE — Allowed Transitions

```yaml
state_machine:
  entry_point: interview
  
  states:
    interview:
      allowed_next: [planning]
      entry_condition: "INTERVIEW_OUTPUT.yaml complete"
      exit_action: "Generate .agent/, .skill/, .test/, .map/, .doc/"
      
    planning:
      allowed_next: [coding]
      entry_condition: "User approved .agent/ + .skill/ + .test/"
      exit_action: "STATE.md phase = coding"
      
    coding:
      allowed_next: [scan, testing]
      entry_condition: "Task list approved, rules loaded"
      
      sub_states:
        - read_context
        - validate_input
        - write_code
        - validate_output
        - update_map
        - update_doc
        - validate_state
        
    scan:
      allowed_next: [fix, testing]
      entry_condition: "Code hoàn thành"
      
    fix:
      allowed_next: [scan, testing]
      entry_condition: "Bug detected"
      
    testing:
      allowed_next: [release, fix, coding]
      entry_condition: "Code ready"
      
    release:
      allowed_next: [coding]
      entry_condition: "All tests pass"

  forbidden_transitions:
    - interview → coding
    - interview → scan
    - planning → testing
    - scan → release
```

---

## Required Context Loader (Theo Phase)

```yaml
context_loader:
  interview:
    required:
      - ".router/00_INTERVIEW.md"
      - ".workflow/interview/"
    
  planning:
    required:
      - ".agent/STATE.md"
      - ".agent/00_MASTER.md"
      - ".agent/01_STRUCTURE.md"
      - ".agent/02_TASK_LIST.md"
      - ".skill/{lang}.md"
    
  coding:
    required:
      - ".agent/STATE.md"
      - ".agent/02_TASK_LIST.md"
      - ".agent/05_RULES_{LANG}.md"
      - ".skill/{lang}.md"
      - ".test/scenarios/T{n}.md"
    
  scan:
    required:
      - ".agent/STATE.md"
      - ".map/current/"
      - ".doc/PROGRESS.md"
      - "src/"
    
  fix:
    required:
      - ".agent/STATE.md"
      - ".bug/02_BUG_LIST.md"
      - "src/"
    
  testing:
    required:
      - ".agent/STATE.md"
      - ".test/scenarios/"
      - "src/"
```

---

## Consistency Flags

```yaml
consistency_flags:
  interview:
    - check: "INTERVIEW_OUTPUT.yaml valid"
    
  planning:
    - check: ".agent/ files complete"
    - check: ".skill/{lang}.md exists"
    
  coding:
    - check: "Code follows rules"
    - check: "Contract validation"
    - check: ".map/ updated"
    - check: ".doc/PROGRESS.md updated"
    
  scan:
    - check: ".bug/01_SCAN_LOG.md created"
    - check: ".bug/02_BUG_LIST.md updated"
    
  fix:
    - check: ".sim/dry_run_{id}.md created"
    - check: "Code fixed"
    - check: ".map/diff/ created"
```

---

## AI Entry Procedure

```yaml
ai_entry:
  step_1: "Đọc STATE.md"
  step_2: "Validate schema version"
  step_3: "Kiểm tra phase hiện tại"
  step_4: "Load required context (theo phase)"
  step_5: "Validate transition nếu cần"
  step_6: "Chạy action"
  step_7: "Update STATE.md"
  step_8: "Log token"
```

---

## Trạng Thái Hiện Tại

```yaml
# === DRIVER CONFIG ===
state_machine:
  current: interview
  allowed_next: [planning]
  
# === RUNTIME DATA ===
phase: interview
current_task: "Khởi tạo dự án"
attempt: 0
last_action: "Tạo cấu trúc hệ thống"
last_actor: ""
next_action: "Chạy .router/00_INTERVIEW.md → Bắt đầu Tier 0"
blockers: ["INTERVIEW_OUTPUT.yaml chưa có dữ liệu"]

# === CONSISTENCY FLAGS ===
consistency_flags:
  doc: false
  map: false
  test: false
  contract: false

# === CONTEXT LOADED ===
context_loaded:
  files: []
  token_used: 0

# === SIMULATION FLAG ===
simulation_required: false

# === METADATA ===
last_updated: ""
version: "2.0"  # State schema version
```
