# DECISION_LOG.md — Multi-AI Coordination Log
> **Vai trò:** Ghi lại mọi quyết định kiến trúc để nhiều AI có thể collaborate mà không conflict.
> **Input:** Mọi quyết định kiến trúc, breaking change, hoặc design choice.
> **Output:** Lịch sử quyết định để AI tiếp theo biết context.
> **Rule:** Mọi AI PHẢI đọc và ghi vào đây trước khi làm breaking change.

---

## Format Entry

```yaml
decision:
  id: "D{nnn}"                    # Decision ID
  timestamp: "2026-03-30T10:15:00Z"
  ai_id: "Claude-3.7"             # AI thực hiện
  phase: "coding" | "planning" | "bugfix" | "refactor"
  
  decision_type:
    - "architecture"               # Thay đổi kiến trúc
    - "breaking_change"          # Breaking change
    - "api_contract"             # Thay đổi API
    - "data_model"               # Thay đổi data model
    - "refactor"                 # Refactor lớn
    - "dependency"             # Thay đổi dependency
    - "performance"              # Optimization
    
  context:
    problem: "Mô tả vấn đề cần giải quyết"
    constraints: ["Ràng buộc", "Yêu cầu"]
    
  options_considered:
    - option: "Option A"
      pros: ["Ưu điểm"]
      cons: ["Nhược điểm"]
      
    - option: "Option B"
      pros: []
      cons: []
      
  decision_made: "Chọn Option A"
  rationale: "Lý do chọn"
  
  impact:
    files_affected: ["src/file1.ts", "src/file2.ts"]
    modules_affected: ["Module A", "Module B"]
    breaking_change: true | false
    migration_required: true | false
    
  related_docs:
    - ".map/diff/v{X}_to_v{Y}.yaml"
    - ".sim/dry_run_{id}.md"
    - ".bug/BUG-{id}.md" (nếu liên quan)
    
  sign_off:
    ai_id: "Claude-3.7"
    timestamp: "2026-03-30T10:20:00Z"
    approved: true | false
    
  follow_up:
    - "Task T{n} cần update"
    - "Document cần cập nhật"
```

---

## Entry Template

```markdown
## D001 — Chuyển từ localStorage sang IndexedDB

**Timestamp:** 2026-03-30T10:15:00Z  
**AI:** Claude-3.7  
**Phase:** planning

### Context
- **Problem:** localStorage giới hạn 5MB, không đủ cho app journal
- **Constraints:** Phải giữ compatibility với data cũ

### Options Considered

#### Option A: Giữ localStorage + Compression
- **Pros:** Đơn giản, không breaking change
- **Cons:** Vẫn giới hạn 5MB, phức tạp

#### Option B: Chuyển sang IndexedDB
- **Pros:** Giới hạn lớn hơn (50MB+), async API
- **Cons:** Breaking change, cần migration

### Decision
**Chọn Option B** — Chuyển sang IndexedDB với migration script

### Impact
- **Files affected:** `src/storage.ts`, `src/migration.ts`
- **Breaking change:** YES
- **Migration required:** YES — tự động chạy khi app update

### Related
- `.map/diff/v0.1_to_v0.2.yaml`
- `.sim/dry_run_storage_migration.md`

### Sign-off
- [Claude-3.7] [2026-03-30T10:20:00Z] ✅ Approved

### Follow-up
- [ ] Update `.agent/03_API_CONTRACT.md`
- [ ] Test migration on large datasets
- [ ] Document cho user
```

---

## Multi-AI Read Protocol

```yaml
ai_entry_protocol:
  step_1: "Đọc STATE.md → biết phase"
  step_2: "Đọc DECISION_LOG.md → biết quyết định gần nhất"
  step_3: "Kiểm tra có quyết định liên quan không?"
  step_4: "Nếu có → Hiểu context trước khi code"
  step_5: "Nếu làm breaking change → GHI vào DECISION_LOG.md"
```

---

## Conflict Prevention Rules

```yaml
conflict_rules:
  before_architecture_change:
    - "Đọc 5 entry gần nhất trong DECISION_LOG.md"
    - "Kiểm tra có AI khác đang làm thay đổi liên quan"
    - "Nếu có → Chờ hoặc coordinate"
    
  before_breaking_change:
    - "BẮT BUỘC ghi vào DECISION_LOG.md trước"
    - "BẮT BUỘC có .sim/dry_run_{id}.md"
    - "Notify nếu có AI khác active"
    
  concurrent_work:
    - "Không sửa cùng file với AI khác cùng lúc"
    - "Không làm breaking change khi AI khác đang code"
    - "Sync qua STATE.md liên tục"
```

---

## Index

```yaml
# Index nhanh để tìm quyết định
index:
  by_type:
    architecture: [D001, D003]
    breaking_change: [D001, D005]
    api_contract: [D002]
    
  by_file:
    "src/storage.ts": [D001]
    "src/api.ts": [D002]
    
  by_module:
    "storage": [D001]
    "api": [D002]
```

---

*Mọi AI phải đọc và ghi vào đây để tránh conflict.*
