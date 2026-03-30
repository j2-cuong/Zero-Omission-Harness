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

## Post-Code Actions

Sau khi code xong, AI phải:

```yaml
post_code_actions:
  - update: ".agent/STATE.md"
    fields: ["current_task", "last_action", "last_actor", "consistency_flags"]
  - append: ".agent/DECISION_LOG.md"
    if: "có quyết định kiến trúc"
  - update_map:
      if: "thay đổi component/function/data flow"
      strategy: "incremental"  # Chỉ update phần thay đổi
      files:
        - ".map/current/component_tree.yaml"  # Nếu thêm/xóa component
        - ".map/current/callgraph_{comp}.txt"   # Nếu thay đổi functions
        - ".map/current/data_flow.mmd"          # Nếu thay đổi luồng
  - create_ref:
      if: "task có linked map nodes"
      file: ".map/refs/TASK-{id}.yaml"
  - trigger: "consistency_check"
    verify: ["doc", "map", "test", "contract"]
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
