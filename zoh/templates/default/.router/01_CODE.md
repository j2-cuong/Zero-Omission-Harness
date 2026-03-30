# .router/01_CODE.md
> **Vai trò:** Điều phối coding tasks — load đúng skill files + context cần thiết.
> **Input:** `ROUTER.md` đã xác định phase = coding
> **Output:** Danh sách files để implement task cụ thể
> **Rule:** Không load toàn bộ `.agent/` — chỉ load liên quan đến task.

---

## Task Detection

Phân tích user request để xác định loại code task:

| Pattern | Task Type | Files Load |
|---------|-----------|------------|
| `implement`, `viết`, `tạo`, `add`, `thêm` | **New Feature** | STRUCTURE + RULES + STATE |
| `refactor`, `tái cấu trúc`, `clean` | **Refactor** | STRUCTURE + RULES + STATE + DECISION_LOG |
| `update`, `sửa đổi`, `modify` | **Modify** | API_CONTRACT + RULES + STATE |
| `delete`, `xóa`, `remove` | **Remove** | STRUCTURE + DEPENDENCY_MAP |

---

## Core Files (Luôn Load)

1. **`.agent/STATE.md`** — biết current phase và task
2. **`.skill/{language}.md`** — rules ngôn ngữ (chọn đúng ngôn ngữ)
3. **`.agent/05_RULES_{LANG}.md`** — rules dự án cụ thể

---

## Conditional Files

| Điều kiện | File bổ sung | Lý do |
|-----------|--------------|-------|
| Task liên quan API | `.agent/03_API_CONTRACT.md` | Biết interface |
| Task có IPC | `.agent/03_IPC_CONTRACT.md` | Protocol format |
| Task có P/Invoke | `.agent/04_PINVOKE_CONTRACT.md` | Marshaling |
| Task đụng nhiều component | `.agent/01_STRUCTURE.md` | Dependencies |
| Task cần breaking change | `.agent/DECISION_LOG.md` | Không override quyết định cũ |
| Task phức tạp | `.agent/06_BUILD_CONFIG.md` | Build implications |

---

## Code Review Checklist

Trước khi generate code:

```yaml
pre_code_check:
  - "Đọc STATE.md → biết đang ở phase nào"
  - "Đọc SKILL file → biết constraint ngôn ngữ"
  - "Đọc RULES file → biết convention dự án"
  - "Kiểm tra CONTRACT nếu có API"
  - "Xác định component nào bị ảnh hưởng"
```

---

## VALIDATION GATES (BẮT BUỘC)

### Gate 1: Pre-Code Validation

```yaml
gate_1_pre_code:
  required_checks:
    - name: "State Check"
      verify: "STATE.md phase = coding"
      fail_action: "DỪNG - Chuyển phase trước"
      
    - name: "Rule Load Check"
      verify: ".skill/{lang}.md loaded"
      verify: ".agent/05_RULES_{LANG}.md loaded"
      fail_action: "DỪNG - Load rules trước"
      
    - name: "Contract Check"
      verify: "Nếu có API/IPC/PInvoke → CONTRACT.md loaded"
      fail_action: "DỪNG - Load contract trước"
      
    - name: "Test Scenario Check"
      verify: ".test/scenarios/T{n}.md loaded"
      fail_action: "Cảnh báo - Code mà không có test scenario"
```

### Gate 2: Code Validation

```yaml
gate_2_code_validation:
  during_coding:
    - name: "Syntax Check"
      tool: "Linter/Language server"
      
    - name: "Rule Compliance"
      verify: "Code follows .skill/{lang}.md"
      verify: "Code follows .agent/05_RULES_{LANG}.md"
      
    - name: "Contract Compliance"
      verify: "API signatures match CONTRACT.md"
      verify: "Data types match contracts"
      verify: "Error handling follows contract"
```

### Gate 3: Post-Code Validation

```yaml
gate_3_post_code:
  required_checks:
    - name: "Output Validation"
      verify: "Output types match expected"
      verify: "Error cases handled"
      
    - name: "Rule Re-Check"
      verify: "Final code follows all rules"
      
    - name: "Test Alignment"
      verify: "Code có thể pass .test/scenarios/T{n}.md"
      
    - name: "Doc & Map Update Check"
      verify: ".doc/PROGRESS.md cập nhật progress task"
      verify: ".map/current/ cập nhật nếu có thay đổi structure"
      verify: ".map/diff/ tạo version diff nếu breaking change"
      fail_action: "Cập nhật doc/map trước khi đánh dấu done"
```

---

## Coding Workflow với Gates

```
[Load Context]
    ↓
[GATE 1: Pre-Code]
    ├── State check ✅
    ├── Rule load check ✅
    ├── Contract check ✅
    └── Test scenario check ✅
    ↓
[Write Code]
    ↓
[GATE 2: Code Validation]
    ├── Syntax check ✅
    ├── Rule compliance ✅
    └── Contract compliance ✅
    ↓
[GATE 3: Post-Code]
    ├── Output validation ✅
    ├── Rule re-check ✅
    └── Test alignment ✅
    ↓
[Update Map]
    ↓
[Update Progress]
    ↓
[Log Token]
```

---

## Post-Code Actions (BẮT BUỘC)

Sau khi code xong, AI phải thực hiện:

### 1. Update Documentation
```yaml
update_doc:
  file: ".doc/PROGRESS.md"
  action: "append"
  content:
    - task_id: "T{n}"
    - status: "completed"
    - timestamp: "YYYY-MM-DD HH:MM"
    - actor: "[AI-ID]"
    - files_modified: ["list files đã đổi"]
    - breaking_change: true/false
    - map_updated: true/false
```

### 2. Update Map Files (Incremental)
```yaml
update_map:
  strategy: "incremental"
  
  if_new_component:
    file: ".map/current/component_tree.yaml"
    action: "append node"
    
  if_new_function:
    file: ".map/current/callgraph_{comp}.txt"
    action: "append function signature"
    
  if_data_flow_change:
    file: ".map/current/data_flow.mmd"
    action: "update mermaid diagram"
    
  create_ref:
    if: "task có linked map nodes"
    file: ".map/refs/TASK-{id}.yaml"
    content:
      task_id: "T{n}"
      map_nodes: ["list nodes"]
      timestamp: "YYYY-MM-DD HH:MM"
```

### 3. Create Diff Version (Nếu Breaking Change)
```yaml
create_diff:
  condition: "breaking_change OR major refactor"
  
  steps:
    1: "Xác định version trước và sau"
    2: "So sánh diff giữa các file thay đổi"
    3: "Ghi vào .map/diff/"
    
  output:
    file: ".map/diff/v{old}_to_v{new}.yaml"
    content:
      old_version: "x.y.z"
      new_version: "x.y.z"
      timestamp: "YYYY-MM-DD HH:MM"
      changed_files:
        - file: "path"
          change_type: "add|modify|delete"
          impact: "api|internal|docs"
      breaking_changes:
        - description: "what changed"
          migration: "how to migrate"
      affected_contracts: ["list if any"]
```

### 4. Update State
```yaml
update_state:
  file: ".agent/STATE.md"
  fields:
    - "current_task"
    - "last_action"
    - "last_actor"
    - "consistency_flags.code_map = true"
    - "consistency_flags.map_doc = true"
    - "version: nếu có breaking change"
```

### 5. Trigger Consistency Check
```yaml
consistency_check:
  verify:
    - "code_vs_map: Code changes reflected in map"
    - "map_vs_doc: Map updates documented"
    - "task_vs_progress: Task marked complete in PROGRESS.md"
    - "ref_created: TASK-{id}.yaml exists if needed"
    - "diff_created: Version diff exists if breaking change"
    - "token_logged: Token usage recorded in .token/coding/"
```

### 6. Token Logging (BẮT BUỘC)
```yaml
token_log:
  file: ".token/coding/TASK_{id}.yaml"
  mandatory: true
  fail_action: "KHÔNG ĐƯỢC ĐÁNH DẤU TASK COMPLETE"
  
  content:
    task_id: "T{n}"
    timestamp_start: "ISO-8601"
    timestamp_end: "ISO-8601"
    actor: "[AI-ID]"
    
    phases:
      - name: "pre_code"
        tokens: 500
        action: "Load context + validation"
        
      - name: "code_generation"
        tokens: 2000
        action: "Write implementation"
        
      - name: "validation"
        tokens: 300
        action: "Run 3 gates"
        
      - name: "map_update"
        tokens: 400
        action: "Update .map/current/"
        
      - name: "doc_update"
        tokens: 200
        action: "Update PROGRESS.md"
        
    total_tokens: 3400
    files_modified: 3
    
    budget:
      allocated: 5000
      used: 3400
      remaining: 1600
      percentage: 68%
```

---

## Map Update Strategy (Tiết kiệm token)

Cập nhật `.map/` sau code có thể tốn token. Dùng chiến lược:

### 1. Incremental Update (Khuyến nghị)
Chỉ cập nhật phần thay đổi, không load toàn bộ map:

```
Code thay đổi
    ↓
Xác định ảnh hưởng:
- Thêm component? → Chỉ thêm node vào component_tree.yaml
- Thêm function? → Chỉ thêm vào callgraph_{comp}.txt
- Đổi data flow? → Chỉ sửa data_flow.mmd
    ↓
Append/Patch (không regenerate)
```

### 2. Deferred Update (Nếu token hết)
Nếu context đã nặng sau coding:

```yaml
deferred_update:
  - ghi_nhớ: "List các map changes cần làm"
  - vào_STATE: "consistency_flags.map = false (pending update)"
  - next_task: "Map update only"
  - user_notify: "Cần separate step để cập nhật map"
```

### 3. Minimal Load Pattern
Chỉ load map file liên quan:

| Code Change | Map File Cần Load |
|-------------|-------------------|
| Thêm component mới | `component_tree.yaml` |
| Thêm function trong component | `callgraph_{comp}.txt` |
| Đổi API interface | `component_tree.yaml` (interfaces) |
| Đổi luồng dữ liệu | `data_flow.mmd` |
| Refactor cross-component | Nhiều file (báo complex) |

---

## Token Budget: Code Tasks

| Task Complexity | Files | Est. Tokens | Map Update? |
|-----------------|-------|-------------|-------------|
| Simple (1 file) | 3 | ~800 | No / Append only |
| Medium (multi-file) | 4-5 | ~1200 | Incremental |
| Complex (cross-component) | 6 | ~1500 | May need deferred |

**Nếu >1500 tokens:** Đề xuất chia thành: 1) Code 2) Map update

---

## Example: Code + Map Update

**User request:** *"Thêm hàm xử lý JSON vào Core module"*

**Phase 1: Coding**
```yaml
files_to_load:
  - ".agent/STATE.md"
  - ".skill/cpp.md"
  - ".agent/05_RULES_CPP.md"
  - ".agent/01_STRUCTURE.md"
estimated_tokens: 900
action: "Implement JSON handler"
```

**Phase 2: Map Update (Incremental)**
```yaml
files_to_load:
  - ".map/current/callgraph_core.txt"  # Chỉ load callgraph của Core
estimated_tokens: 300
action: "Append new function to callgraph"
```

Total: ~1200 tokens (thay vì 1500+ nếu load full map)

---

## Example Routing

**User request:** *"Thêm hàm xử lý JSON vào Core module"*

```yaml
routing_decision:
  detected_phase: "coding"
  task_type: "New Feature"
  files_to_load:
    - ".agent/STATE.md"
    - ".skill/cpp.md"           # giả sử language=cpp
    - ".agent/05_RULES_CPP.md"
    - ".agent/01_STRUCTURE.md"  # biết Core module ở đâu
  files_to_skip:
    - ".agent/03_IPC_CONTRACT.md"   # không liên quan
    - ".agent/04_PINVOKE_CONTRACT.md" # không liên quan
  estimated_tokens: 900
  next_action: "Implement JSON handler in Core"
```

---

*Router này đảm bảo code task không load thừa context.*
