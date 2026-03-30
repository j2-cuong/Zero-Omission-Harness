# .router/00_INTERVIEW.md
> **Vai trò:** Điều phối phỏng vấn — 7 tiers (0-6), checkpoint + token tracking.
> **Input:** `ROUTER.md` đã xác định phase = interview
> **Output:** Load đúng tier câu hỏi → Sinh INTERVIEW_OUTPUT.yaml + Token log
> **Rule:** Không load full interview. Chỉ load tier phù hợp. Log token sau mỗi câu.

---

## Interview + Token Tracking Philosophy

```
Interview dài (7 tiers, ~50 câu)
        ↓
Sau mỗi CÂU → Log token usage
        ↓
Lưu INTERVIEW_OUTPUT.yaml (checkpoint)
        ↓
AI có thể dừng → Resume sau
        ↓
Khi xong → Phân tích → Sinh .agent/
```

**Lợi ích:**
- Tránh mất context khi phỏng vấn dài
- Track token budget theo thời gian thực
- Optimize: Skip tiers nếu budget thấp
- Resume từ checkpoint

---

## Token Budget Management

```yaml
token_budget:
  interview_total: 15000      # Tổng budget cho phỏng vấn
  per_question_max: 800     # Tối đa mỗi câu (prompt + response)
  checkpoint_cost: 200      # Cost lưu checkpoint
  
  # Theo tier
  tier_allocation:
    tier_0_basic: 2000        # 8 câu × ~250 tokens
    tier_1_architecture: 2500 # 8 câu × ~300 tokens
    tier_2_contracts: 1500    # 5 câu × ~300 tokens
    tier_3_constraints: 1500  # 5 câu × ~300 tokens
    tier_4_technology: 3000   # 10 câu × ~300 tokens
    tier_5_performance: 2500  # 7 câu × ~350 tokens
    tier_6_exceptions: 2000  # 7 câu × ~280 tokens
```

### Token Logging (Sau mỗi câu)

```yaml
log_entry:
  question_id: "Q1-Tier0"
  timestamp: "2026-03-30T10:35:00Z"
  
  tokens:
    prompt: 350       # Context + question
    response: 200     # User answer
    total: 550
    
  budget:
    remaining: 14450
    used_percentage: 3.7%
    
  file: ".token/interview/INTERVIEW_LOG.yaml"
```

---

## Tier Detection

Kiểm tra những gì đã có để quyết định tier:

```yaml
# Đọc từ INTERVIEW_OUTPUT.yaml nếu tồn tại
check_existing:
  interview_output: ".workflow/interview/INTERVIEW_OUTPUT.yaml có không?"
  last_completed_tier: "tiers_completed: [0,1,2...]"
  status: "complete|partial|needs_review"
```

| Điều kiện | Tier | Files Load |
|-----------|------|------------|
| Chưa có INTERVIEW_OUTPUT.yaml | **Tier 0** | `.workflow/interview/00_basic.md` |
| Có basic info | **Tier 1** | `.workflow/interview/01_architecture.md` |
| Có architecture | **Tier 2** | `.workflow/interview/02_contracts.md` |
| Có contracts | **Tier 3** | `.workflow/interview/03_constraints.md` (optional) |
| Có constraints | **Tier 4** | `.workflow/interview/04_technology.md` |
| Có technology | **Tier 5** | `.workflow/interview/05_performance.md` |
| Có performance | **Tier 6** | `.workflow/interview/06_exceptions.md` |
| Đã đủ hết | **DONE** | Validate → Sinh .agent/ |

---

## Các Tiers (7 tiers tổng cộng)

### Tier 0: Basic Info (Bắt buộc, ~300 tokens)
**File:** `.workflow/interview/00_basic.md`
4 câu: tên, ngôn ngữ, trạng thái, mục đích

### Tier 1: Architecture (~500 tokens)
**File:** `.workflow/interview/01_architecture.md`
3 câu: components, data flow, concurrency

### Tier 2: Contracts (~400 tokens, conditional)
**File:** `.workflow/interview/02_contracts.md`
4 câu: internal API, external API, IPC, P/Invoke

### Tier 3: Constraints (~400 tokens, optional)
**File:** `.workflow/interview/03_constraints.md`
3 câu: performance, memory, security

### Tier 4: Technology Deep Dive (~600 tokens)
**File:** `.workflow/interview/04_technology.md`
6 câu: frameworks, data storage, network, build/deploy, dev tools, platform

### Tier 5: Performance Deep Dive (~700 tokens)
**File:** `.workflow/interview/05_performance.md`
5 câu: quantified requirements, resource constraints, bottleneck prediction, profiling, trade-offs

### Tier 6: Exceptions & Edge Cases (~600 tokens)
**File:** `.workflow/interview/06_exceptions.md`
5 câu: error handling, expected failures, unexpected failures, edge cases, logging

**Tổng:** ~29 câu hỏi across 7 tiers (~3500 tokens nếu làm 1 lần)

---

## Checkpoint Strategy (Chống mất context)

### Sau mỗi tier:
```yaml
checkpoint:
  - update: ".workflow/interview/INTERVIEW_OUTPUT.yaml"
    with: "kết quả tier vừa hoàn thành"
  - verify: "File có thể đọc lại không?"
  - notify_user: "Đã lưu checkpoint sau Tier X"
```

### Nếu token sắp hết:
```yaml
emergency_checkpoint:
  - save_immediately: "INTERVIEW_OUTPUT.yaml"
  - mark_status: "partial"
  - notify: "AI sẽ dừng, có thể resume sau"
  - next_session: "Đọc INTERVIEW_OUTPUT.yaml → Tiếp tục tier chưa xong"
```

### Resume workflow:
```yaml
resume:
  - read: ".workflow/interview/INTERVIEW_OUTPUT.yaml"
  - check: "metadata.tiers_completed"
  - determine: "Tier tiếp theo cần làm"
  - load: "Tier file tương ứng"
  - continue: "Từ đâu dừng lại"
```

---

## Execution Flow (with Checkpoint + Auto-Generate)

```
[AI bắt đầu]
    │
    ▼
Kiểm tra INTERVIEW_OUTPUT.yaml tồn tại?
    │── Có → Đọc tiers_completed → Xác định tier tiếp
    │── Không → Bắt đầu từ Tier 0
    ▼
Load tier file → Hỏi user
    │
    ▼
User trả lời → Validate
    │── FAIL → Hỏi lại (vẫn trong tier)
    │── PASS → Ghi vào INTERVIEW_OUTPUT.yaml
    ▼
Checkpoint saved? → Thông báo user
    │
    ▼
Tier xong? → Chuyển tier tiếp hoặc DONE
    │
    ▼
[DONE]
    │
    ▼
[TỰ ĐỘNG] Chạy .workflow/02_GENERATE_AGENT.md
    │
    ├── Phân tích INTERVIEW_OUTPUT.yaml
    ├── Sinh 00_MASTER.md
    ├── Sinh 01_STRUCTURE.md
    ├── Sinh 02_TASK_LIST.md
    ├── Sinh .test/scenarios/ (từ task list)
    ├── Sinh .skill/{lang}.md (nếu chưa có)
    ├── Sinh Contracts (N/A nếu không cần)
    ├── Sinh 05_RULES_{LANG}.md
    ├── Sinh 06_BUILD_CONFIG.md
    ├── Khởi tạo .map/current/, .map/diff/, .map/refs/
    ├── Khởi tạo .doc/PROGRESS.md, .doc/DECISION_LOG.md
    └── Cập nhật STATE.md (phase = planning)
    │
    ▼
Thông báo: ".agent/ đã tự động tạo xong"
    │
    ▼
User review → Approve → Chuyển sang coding
```

## Auto-Generate Trigger

**Khi nào kích hoạt:**
```yaml
trigger_conditions:
  - "Interview status = complete"
  - "INTERVIEW_OUTPUT.yaml tồn tại và valid"
  - "Chưa có .agent/00_MASTER.md HOẶC đã cũ"
  - "User nói 'xong', 'hoàn tất', 'bắt đầu code'"
```

**Quy trình tự động:**

```yaml
auto_generate_workflow:
  file: ".workflow/02_GENERATE_AGENT.md"
  
  step_1_analyze:
    input: "INTERVIEW_OUTPUT.yaml"
    output: "Phân tích project type, tech stack, components"
  
  step_2_generate_master:
    template: "00_MASTER template"
    fill: "project name, purpose, constraints, tech stack"
    output: ".agent/00_MASTER.md"
  
  step_3_generate_structure:
    from: "architecture.components"
    create: "Cây thư mục chi tiết"
    output: ".agent/01_STRUCTURE.md"
  
  step_4_generate_tasks:
    from: "01_STRUCTURE.md"
    create: "Task list với dependency"
    output: ".agent/02_TASK_LIST.md"
  
  step_5_generate_tests:
    from: "02_TASK_LIST.md"
    create: "Test scenarios cho mỗi task"
    output: ".test/scenarios/T{n}_{task_name}.md"
    format:
      - "Given/When/Then scenarios"
      - "Unit test cases"
      - "Integration test flows"
      - "Edge cases"
    mandatory: true
    fail_action: "KHÔNG ĐƯỢC CHUYỂN SANG CODING NẾU THIẾU .test/"

  step_6_generate_skill:
    from: "technology.frameworks.primary"
    detect_language: "react|cpp|csharp|python|go|rust|..."
    check_existing: ".skill/{lang}.md đã tồn tại?"
    if_not_exists:
      action: "Tạo mới .skill/{lang}.md"
      template: "Kế thừa _shared.md + language specific rules"
      sections:
        - "Vai trò, Input, Output, Rule"
        - "Kế thừa _shared.md"
        - "Language specific rules (syntax, patterns, anti-patterns)"
        - "Examples"
    output: ".skill/{lang}.md"

  step_7_generate_rules_agent:
    from: ".skill/{lang}.md" + "INTERVIEW_OUTPUT.yaml constraints"
    create: "Project-specific rules"
    output: ".agent/05_RULES_{LANG}.md"

  step_8_generate_contracts:
    condition: "IF contracts.external_api != none"
    files: ["03_API_CONTRACT.md", "03_IPC_CONTRACT.md", "04_PINVOKE_CONTRACT.md"]
    else: "Đánh dấu N/A"

  step_9_generate_build_config:
    from: "technology.build_deploy"
    create: "Build configuration"
    output: ".agent/06_BUILD_CONFIG.md"
  
  step_10_init_map:
    name: "Khởi tạo .map/ structure"
    create:
      - ".map/current/component_tree.yaml"
      - ".map/current/data_flow.mmd"
      - ".map/diff/.gitkeep"
      - ".map/refs/.gitkeep"
    from: "architecture.components + architecture.data_flow"

  step_11_init_doc:
    name: "Khởi tạo .doc/ structure"
    create:
      - ".doc/PROGRESS.md (dashboard từ task list)"
      - ".doc/DECISION_LOG.md (template)"
      - ".doc/ARCH_FLOW.md (nếu cần)"

  step_12_update_state:
    update: ".agent/STATE.md"
    set:
      phase: "planning"
      current_task: "Review .agent/ files"
      next_action: "Approve and start coding"
      last_action: "Auto-generated .agent/ from INTERVIEW_OUTPUT.yaml"
      
  step_13_token_log:
    name: "🔴 BẮT BUỘC: Log token tổng kết interview"
    action: "Ghi tổng token usage cho toàn bộ interview"
    output: ".token/interview/INTERVIEW_LOG.yaml"
    mandatory: true
    fail_action: "KHÔNG ĐƯỢC CHUYỂN SANG PHASE PLANNING"
    format:
      phase: "interview"
      timestamp_start: "ISO-8601"
      timestamp_end: "ISO-8601"
      tiers_completed: [0, 1, 2, 3, 4, 5, 6]
      total_questions: 29
      tokens:
        total: 14500
        by_tier:
          tier_0: 2000
          tier_1: 2500
          tier_2: 1500
          tier_3: 1500
          tier_4: 3000
          tier_5: 2500
          tier_6: 2000
      budget:
        allocated: 15000
        used: 14500
        remaining: 500
        percentage: 96.7%
  
  notify_user: "✅ .agent/ đã tự động tạo xong. Token logged. Sẵn sàng review."
```

---

## Tier Skipping Strategy

Không phải lúc nào cũng cần đủ 7 tiers:

| Scenario | Skip tiers |
|----------|------------|
| Simple CLI tool | Skip 3, 5, 6 (constraints, performance, exceptions) |
| Prototype/MVP | Skip 4, 5, 6 (technology deep dive) |
| Embedded system | Không skip gì (cần đầy đủ) |
| Web API đơn giản | Skip 6 (exceptions) nếu framework handle |

## Output Files (Sau Auto-Generate)

### INTERVIEW_OUTPUT.yaml (Checkpoint)
```yaml
interview:
  metadata:
    tiers_completed: [0, 1, 2, 3, 4, 5, 6]
    tiers_skipped: []
    status: "complete"
  
  # Tier 0-6 content here...
  project: {}
  architecture: {}
  contracts: {}
  constraints: {}
  technology: {}
  performance: {}
  exceptions: {}
  
  analysis:
    open_questions: []
    assumptions: []
    risks: []
```

### Sau khi interview xong (TỰ ĐỘNG):
**Chạy** `.workflow/02_GENERATE_AGENT.md` → Sinh:
- `.agent/00_MASTER.md`
- `.agent/01_STRUCTURE.md`
- `.agent/02_TASK_LIST.md` (skeleton)
- `.test/scenarios/T{n}_{name}.md` (cho mỗi task)
- `.skill/{lang}.md` (nếu chưa có)
- `.map/current/` (component_tree, data_flow)
- `.map/diff/`, `.map/refs/` (initialized)
- `.doc/PROGRESS.md`, `.doc/DECISION_LOG.md`
- `.agent/STATE.md` (phase = planning)

**KHÔNG cần user intervention** — AI tự động chạy.

---

## Review Before Proceeding

Trước khi sinh .agent/, user có thể review:
```yaml
review_checklist:
  - "Đọc INTERVIEW_OUTPUT.yaml"
  - "Xem có thiếu gì không?"
  - "Sửa trực tiếp nếu cần"
  - "Approve → Tiếp tục"
```

**Nếu user muốn sửa:**
- Sửa INTERVIEW_OUTPUT.yaml
- Không cần phỏng vấn lại

---

*Router này cho phép interview dài (7 tiers, 29 câu) mà không mất context.*
