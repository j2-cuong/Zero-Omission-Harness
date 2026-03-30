# 00_SIM_RULES.md — Quy tắc Simulation
> **Vai trò:** Định nghĩa điều kiện bắt buộc chạy simulation và format kết quả.
> **Input:** Không có (rule tĩnh)
> **Output:** Gate trước mọi fix — không có sim → không có fix.
> **Rule CỨNG:** Mọi thay đổi code (fix/refactor) PHẢI có dry_run_{id}.md trước khi apply.

## Khi nào bắt buộc chạy sim
- Bất kỳ thay đổi nào ảnh hưởng đến API contract
- Bất kỳ thay đổi nào ảnh hưởng đến IPC/Pipe protocol  
- Sửa logic trong file có dependency > 2 module khác
- Thay đổi memory allocation / handle management
- Thay đổi build flags hoặc linker config

## Format dry_run_{id}.md (Có Impact Boundary Control)

```yaml
simulation:
  metadata:
    SIM_ID: "fix-{timestamp}-{short-desc}"
    BUG_ID: "BUG-{nn}"
    TARGET_FILE: "path/to/file.cpp"
    
  # === IMPACT BOUNDARY CONTROL ===
  impact_scope:
    blast_radius:
      - level: 1  # Direct file being modified
        files: ["storage.ts"]
        
      - level: 2  # Files calling the modified function
        files: ["NewEntryPage.tsx", "SettingsPage.tsx", "Timeline.tsx"]
        
      - level: 3  # Indirect dependencies
        modules: ["EntryStore", "SettingsStore"]
        
    risk_assessment:
      breaking_change: true | false
      api_signature_change: true | false
      data_format_change: true | false
      requires_migration: true | false
      
    affected_contracts:
      - contract: "03_API_CONTRACT.md"
        impact: "function signature changed"
        requires_update: true
        
    risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    
    rollback_complexity: "EASY" | "MEDIUM" | "HARD"
    estimated_fix_time: "30 minutes"
    
  # === CHANGE DETAIL ===
  change:
    summary: "Mô tả thay đổi"
    PRE_STATE: "Trạng thái trước khi fix"
    POST_STATE: "Trạng thái dự kiến sau fix"
    
  # === CASCADE RISK (Detailed) ===
  cascade_risk:
    modules_affected:
      - name: "Module A"
        impact: "Phải thêm try-catch khi gọi storage.write()"
        effort: "2 files cần sửa"
        
      - name: "Module B"
        impact: "Cần update error handling UI"
        effort: "1 component"
        
  # === VALIDATION ===
  test_required: "path/to/.test/scenarios/sim_{id}.md"
  
  approval:
    APPROVED_BY: "[user/AI-ID] [timestamp]"
    STATUS: "PENDING | APPROVED | REJECTED"
```

---

## Impact Boundary Analysis Steps

```yaml
step_1_find_direct:
  action: "Identify file(s) being modified"
  output: "Level 1 blast radius"
  
step_2_find_callers:
  action: "Find all files importing/using the modified function"
  output: "Level 2 blast radius"
  
step_3_find_indirect:
  action: "Identify modules/components that depend on affected modules"
  output: "Level 3 blast radius"
  
step_4_assess_contracts:
  action: "Check if any API/IPC contracts affected"
  output: "Contract update requirements"
  
step_5_calculate_risk:
  action: "Calculate risk_level dựa trên:"
  formula:
    - "Level 2 files > 5 → risk tăng"
    - "Breaking change = true → risk tăng"
    - "Requires migration = true → risk cao"
    - "Rollback complexity = HARD → risk cao"
```
