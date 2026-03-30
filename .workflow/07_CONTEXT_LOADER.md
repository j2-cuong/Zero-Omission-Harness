# 07_CONTEXT_LOADER.md — Smart Context Loading
> **Vai trò:** Load đúng file cần thiết cho từng phase + target, tránh context explosion.
> **Input:** STATE.md (phase hiện tại) + Task target.
> **Output:** Danh sách file cần load + Lazy loading strategy.
> **Rule:** Không load full .agent/ — chỉ load phần cần thiết.

---

## Loading Strategy

```yaml
loading_strategy:
  principle: "Lazy Loading — chỉ load khi cần"
  
  rules:
    - "Truncate file dài >100 dòng, chỉ lấy relevant sections"
    - "Dùng summary thay vì full content"
    - "Cache frequently accessed files"
    - "Unload files không cần nữa"
    
  priority:
    1: "STATE.md (bắt buộc)"
    2: "Files cho phase hiện tại"
    3: "Files cho task cụ thể"
    4: "Reference files (on demand)"
```

---

## Phase-Based Loading

### Phase: interview

```yaml
load_interview:
  required:
    - ".agent/STATE.md"           # 200 tokens
    - ".router/00_INTERVIEW.md"   # 500 tokens
    
  tier_specific:
    tier_0: ".workflow/interview/00_basic.md"      # 300 tokens
    tier_1: ".workflow/interview/01_architecture.md"  # 400 tokens
    tier_2: ".workflow/interview/02_contracts.md"   # 400 tokens
    # ...
    
  optional:
    - ".workflow/interview/INTERVIEW_OUTPUT.yaml"  # Nếu resume
    
  total_budget: 2000 tokens
```

### Phase: planning

```yaml
load_planning:
  required:
    - ".agent/STATE.md"              # 200 tokens
    - ".agent/00_MASTER.md"          # 400 tokens (truncate)
    - ".agent/01_STRUCTURE.md"      # 500 tokens
    - ".agent/02_TASK_LIST.md"      # 400 tokens
    - ".skill/{lang}.md"             # 600 tokens
    
  optional:
    - ".agent/05_RULES_{LANG}.md"    # Nếu cần chi tiết
    
  exclude:
    - ".map/current/*"               # Chưa cần
    - ".doc/*"                     # Chưa cần
    
  total_budget: 2500 tokens
```

### Phase: coding

```yaml
load_coding:
  required:
    - ".agent/STATE.md"              # 200 tokens
    - ".agent/02_TASK_LIST.md"      # Chỉ T{n} hiện tại: 300 tokens
    - ".agent/05_RULES_{LANG}.md"    # 500 tokens
    - ".skill/{lang}.md"             # 600 tokens
    - ".test/scenarios/T{n}.md"     # 400 tokens
    
  on_demand:
    - ".agent/03_*_CONTRACT.md"      # Chỉ nếu task liên quan API
    - "src/*"                        # Chỉ files liên quan task
    
  exclude:
    - ".agent/01_STRUCTURE.md"       # Đã có context từ task
    - "Các tasks khác trong 02_TASK_LIST.md"
    
  total_budget: 2500 tokens
  with_source: 4000 tokens
```

### Phase: scan

```yaml
load_scan:
  required:
    - ".agent/STATE.md"              # 200 tokens
    - ".map/current/component_tree.yaml"  # 300 tokens
    - ".map/current/data_flow.mmd"   # 300 tokens
    - ".doc/PROGRESS.md"             # 400 tokens (recent entries)
    
  on_demand:
    - "src/*"                        # Từng file khi scan
    
  total_budget: 1500 tokens
  with_source: 3500 tokens
```

### Phase: fix

```yaml
load_fix:
  required:
    - ".agent/STATE.md"              # 200 tokens
    - ".bug/02_BUG_LIST.md"          # Chỉ BUG-{id}: 300 tokens
    - ".sim/dry_run_{id}.md"         # 500 tokens (nếu có)
    
  on_demand:
    - "src/{target_file}"            # File cần fix
    - ".test/scenarios/bug_{id}.md"  # Nếu có
    
  total_budget: 1500 tokens
```

### Phase: testing

```yaml
load_testing:
  required:
    - ".agent/STATE.md"              # 200 tokens
    - ".test/scenarios/"             # Từng scenario khi chạy
    
  on_demand:
    - "src/*"                        # Files cần test
    
  total_budget: 1500 tokens
```

---

## File Truncation Rules

```yaml
truncation_rules:
  large_files:
    threshold: 100  # Dòng
    strategy: "Lấy 50 dòng đầu + 50 dòng relevant"
    
  very_large_files:
    threshold: 500  # Dòng
    strategy: "Chỉ lấy summary + index"
    
  log_files:
    strategy: "Chỉ lấy 20 entries gần nhất"
    
  code_files:
    strategy: "Lấy 30 dòng quanh vị trí cần sửa"
```

---

## Token Budget Management

```yaml
token_budget:
  per_phase:
    interview: 2000
    planning: 2500
    coding: 4000
    scan: 3500
    fix: 2000
    testing: 2500
    
  reserve: 1000  # Dành cho response
  
  overflow_strategy:
    - "Truncate context đã load"
    - "Unload files không cần"
    - "Dùng summary thay vì detail"
    - "Yêu cầu user approval nếu vẫn không đủ"
```

---

## Caching Strategy

```yaml
cache:
  hot_files:  # Giữ trong context
    - ".agent/STATE.md"
    - ".skill/{lang}.md"
    - ".agent/05_RULES_{LANG}.md"
    
  warm_files:  # Giữ reference, reload nếu cần
    - ".agent/02_TASK_LIST.md"
    - ".map/current/*"
    
  cold_files:  # Load on demand, unload sau dùng
    - ".doc/PROGRESS.md"
    - ".bug/02_BUG_LIST.md"
    - "src/*"
```

---

## Multi-AI Context Sharing

```yaml
multi_ai_context:
  shared:
    - ".agent/STATE.md"              # Mọi AI đều đọc
    - ".doc/DECISION_LOG.md"        # Mọi AI đều đọc
    
  partitioned:
    - "src/*"                        # Mỗi AI làm file khác
    - ".test/scenarios/*"            # Mỗi AI test khác nhau
    
  coordination:
    - "Update STATE.md liên tục"
    - "Ghi DECISION_LOG.md khi conflict risk"
```

---

*Context loader đảm bảo optimal token usage trong mọi phase.*
