# .map/diff/DIFF_FORMAT.md
> **Vai trò:** Format chuẩn để ghi lại mọi thay đổi kiến trúc — dùng cho review và rollback.
> **Input:** Map trước và sau khi thay đổi
> **Output:** Diff file YAML có cấu trúc
> **Rule:** Mọi thay đổi kiến trúc đều phải có diff log. Không diff = không track được.

---

## Diff Types

| Type | Khi nào tạo | File naming |
|------|-------------|-------------|
| **Version Diff** | Release version mới | `v1.0.0_to_v1.1.0.yaml` |
| **Feature Diff** | Hoàn thành feature | `FEAT-{task_id}.yaml` |
| **Breaking Diff** | Có breaking change | `BREAKING-{date}-{desc}.yaml` |
| **Hotfix Diff** | Sửa bug khẩn | `HOTFIX-{bug_id}.yaml` |

---

## Schema Diff File

```yaml
diff:
  id: "unique_identifier"
  type: "version|feature|breaking|hotfix"
  
  # Context
  date: "YYYY-MM-DD"
  author: "AI-ID hoặc dev"
  trigger: "TASK-001|BUG-123|PR-456"
  
  # Version info
  from:
    version: "1.0.0"
    commit: "abc123"
    map_snapshot: ".map/refs/v1.0.0/"
    
  to:
    version: "1.1.0"
    commit: "def456"
    map_snapshot: ".map/refs/v1.1.0/"
  
  # Summary
  summary: "1 dòng mô tả thay đổi chính"
  breaking: true|false
  rollback_safe: true|false
  
  # Detailed changes
  changes:
    components:
      added: []
      removed: []
      modified: []
      
    interfaces:
      added: []
      removed: []
      modified: []
      
    data_flows:
      added: []
      removed: []
      modified: []
      
    dependencies:
      added: []
      removed: []
      
  # Impact analysis
  impact:
    components_affected: []
    tests_need_update: []
    docs_need_update: []
    migration_required: true|false
    
  # Verification
  verification:
    consistency_check: true|false
    tests_passed: true|false
    reviewed_by: ""
```

---

## Breaking Change Detection

Tự động detect breaking changes:

```yaml
breaking_indicators:
  interfaces:
    - "Xóa function/interface"
    - "Thay đổi signature (không backward compatible)"
    - "Thay đổi return type"
    - "Thay đổi enum values"
    
  components:
    - "Remove component có dependents"
    - "Move component sang vị trí khác"
    
  data_flow:
    - "Bỏ step bắt buộc trong flow"
    - "Thay đổi protocol giữa components"
    
  contracts:
    - "Thay đổi API version"
    - "Thay đổi serialization format"
```

**Nếu breaking = true:**
- Bắt buộc major version bump
- Phải có migration guide
- Phải có approval từ reviewer

---

## Diff Review Template

Khi review diff:

```markdown
## Review Checklist

### Architecture Impact
- [ ] Có component nào bị ảnh hưởng không mong muốn?
- [ ] Dependencies có tạo cycle không?
- [ ] Data flow mới có logical không?

### Breaking Changes
- [ ] Có breaking không? → Cần major bump
- [ ] Migration path rõ ràng?
- [ ] Tests đã cập nhật cho breaking?

### Consistency
- [ ] Map đã cập nhật khớp code?
- [ ] Call graph đã regenerate?
- [ ] Component tree đã update?

### Rollback
- [ ] Rollback có an toàn không?
- [ ] Có state migration cần rollback?

### Verdict
- [ ] Approve
- [ ] Approve with changes
- [ ] Reject
```

---

## Rollback with Diff

Dùng diff để rollback:

```bash
# Xem diff
cat .map/diff/v1.1.0_to_v1.0.0.yaml

# Rollback architecture
# 1. Checkout code cũ
git checkout v1.0.0

# 2. Restore map snapshot
cp -r .map/refs/v1.0.0/* .map/current/

# 3. Update STATE
# Set version = 1.0.0 trong STATE.md

# 4. Verify
# Run consistency check
```

---

## Example Diff

```yaml
# .map/diff/v1.0.0_to_v1.1.0.yaml
diff:
  id: "v1.0.0_to_v1.1.0"
  type: "feature"
  date: "2026-03-30"
  author: "Claude-3.7"
  trigger: "TASK-001"
  
  from:
    version: "1.0.0"
    commit: "abc123"
    
  to:
    version: "1.1.0"
    commit: "def456"
    
  summary: "Thêm encryption layer vào storage"
  breaking: false
  rollback_safe: true
  
  changes:
    components:
      added:
        - name: "crypto"
          description: "Encryption/decryption layer"
          location: "src/crypto/"
          interfaces: ["encrypt", "decrypt"]
          
      modified:
        - name: "storage"
          changes:
            - "Thêm dependency: crypto"
            - "Thêm optional parameter trong write()"
          breaking: false
          
    interfaces:
      added:
        - component: "crypto"
          name: "encrypt"
          signature: "encrypt(data, key) -> encrypted_data"
          
        - component: "crypto"
          name: "decrypt"
          signature: "decrypt(data, key) -> decrypted_data"
          
      modified:
        - component: "storage"
          name: "write"
          old: "write(data)"
          new: "write(data, options={})"
          note: "Thêm options, default backward compatible"
          
    data_flows:
      modified:
        - old: "core → storage"
          new: "core → storage [options.encrypt] → crypto → storage"
          note: "Optional encryption path"
          
    dependencies:
      added:
        - from: "storage"
          to: "crypto"
          type: "optional"
          
  impact:
    components_affected: ["storage", "core"]
    tests_need_update: ["test_storage_write"]
    docs_need_update: ["API-ref"]
    migration_required: false
    
  verification:
    consistency_check: true
    tests_passed: true
    reviewed_by: ""
```

---

*Mọi thay đổi kiến trúc đều phải để lại dấu vết.*
