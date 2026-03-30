# .workflow/02_GENERATE_AGENT.md
> **Vai trò:** Quy trình tự động sinh toàn bộ .agent/ từ INTERVIEW_OUTPUT.yaml
> **Input:** INTERVIEW_OUTPUT.yaml hoàn thành
> **Output:** Tất cả file trong .agent/ được tự động populate
> **Trigger:** Sau khi interview hoàn thành và validate

---

## Quy trình tự động

```
INTERVIEW_OUTPUT.yaml (đã xong)
        ↓
[Phân tích nội dung]
        ↓
Tự động sinh:
├── .agent/00_MASTER.md (vai trò AI, constraint)
├── .agent/01_STRUCTURE.md (cây thư mục project)
├── .agent/02_TASK_LIST.md (danh sách task từ structure)
├── .agent/03_API_CONTRACT.md (N/A nếu không có API)
├── .agent/03_IPC_CONTRACT.md (N/A nếu không có IPC)
├── .agent/04_PINVOKE_CONTRACT.md (N/A nếu không có P/Invoke)
├── .agent/05_RULES_{LANG}.md (kế thừa + override từ .skill/)
├── .agent/06_BUILD_CONFIG.md (build flags từ tech stack)
├── .skill/{lang}.md (TẠO MỚI từ interview nếu chưa có)
│   └── Kế thừa _shared.md + thêm rules từ technology.*
└── .agent/STATE.md (cập nhật phase → planning)
        ↓
[USER APPROVAL REQUIRED]
        ↓
Review .agent/ + .skill/ → Approve → Chuyển sang coding

---

## Step 1: Phân tích INTERVIEW_OUTPUT.yaml

```yaml
analysis:
  read_fields:
    - project.name
    - project.purpose
    - architecture.components
    - architecture.data_flow
    - technology.frameworks.primary
    - technology.data_storage
    - contracts (API/IPC/PInvoke có hay không)
```

---

## Step 2: Sinh 00_MASTER.md

**Template:**
```markdown
# Dự án: {project.name}

**Mô tả:** {project.purpose}

## Vai trò của AI
- {vai trò từ purpose}

## Constraints
{liệt kê từ constraints + architecture}

## Tech Stack
{from technology.frameworks}
```

---

## Step 3: Sinh 01_STRUCTURE.md

**Từ:** `architecture.components`

- Map mỗi component → thư mục/file
- Tạo cây thư mục chi tiết
- Định nghĩa data model từ storage type

---

## Step 4: Sinh 02_TASK_LIST.md

**Từ:** `01_STRUCTURE.md` + component list

- Mỗi file trong structure → 1 task
- Sắp xếp theo dependency
- Đánh độ khó: Dễ/Trung bình/Khó

---

## Step 5: Sinh .test/ Scenarios (Từ Task List)

**Từ:** `02_TASK_LIST.md` + `01_STRUCTURE.md`

**Logic:**
```yaml
test_generation:
  input:
    - "02_TASK_LIST.md: Danh sách tasks"
    - "01_STRUCTURE.md: Cấu trúc components"
    - "technology.frameworks: Tech stack"
    
  output: ".test/scenarios/"
  
  for_each_task:
    - task_id: "T{n}"
      test_file: ".test/scenarios/T{n}_{task_name}.md"
      
  test_types:
    - name: "Unit Tests"
      target: "Individual functions"
      scenarios_per_task: 3-5
      
    - name: "Integration Tests"  
      target: "Component interactions"
      scenarios_per_flow: 2-3
      
    - name: "Edge Cases"
      target: "Boundary conditions"
      scenarios_per_task: 2
```

**Format test scenario:**
```markdown
# Test: T1 - Khởi tạo Vite project

## Scenario 1: Basic setup
**Given:** Clean directory  
**When:** Run `npm create vite@latest`  
**Then:**
- package.json exists
- vite.config.ts exists
- Can run `npm install` successfully

## Scenario 2: TypeScript config
**Given:** Vite project created  
**When:** Check tsconfig.json  
**Then:**
- strict mode enabled
- React types included
- No compiler errors
```

---

## Step 6: Sinh Contracts (Conditional)

**Nếu `contracts.external_api != none`:**
→ Tạo 03_API_CONTRACT.md

**Nếu `contracts.ipc != none`:**
→ Tạo 03_IPC_CONTRACT.md

**Nếu `contracts.pinvoke != none`:**
→ Tạo 04_PINVOKE_CONTRACT.md

**Else:**
→ Ghi "N/A — No contracts required" vào file

---

## Step 6: Sinh .skill/{lang}.md (Nếu chưa có)

**Từ:** `technology.frameworks.primary`

**Logic:**
```yaml
detect_language:
  input: "technology.frameworks.primary"
  
  if_file_exists: ".skill/{lang}.md"
    action: "Skip (đã có)"
    
  else:
    action: "Tạo mới .skill/{lang}.md"
    template: "Kế thừa _shared.md + thêm rules riêng"
    
    sections:
      - header: "Vai trò, Input, Output, Rule"
      - shared_inherit: "Kế thừa toàn bộ _shared.md"
      - language_specific:
          - "Syntax rules"
          - "Best practices"
          - "Common patterns"
          - "Error handling"
      - project_overrides: "Từ interview (nếu có)"
      - examples: "Code examples"
```

**Nội dung .skill/{lang}.md mới:**
```markdown
# {lang}.md — Rules cho {Language}
> **Vai trò:** Rules coding cho {Language}
> **Input:** Project requirements + _shared.md
> **Output:** Constraint khi viết code {Language}
> **Rule:** Override bằng .agent/05_RULES_{LANG}.md

## Kế thừa từ _shared.md
- File size: Max 300 dòng
- Naming convention
- Sign-off requirement
- Doc language rules
- No God object
- Zero omission

## {Language} Specific Rules

### Syntax & Style
- Indent: 2 spaces / 4 spaces / tabs
- Quote: single / double
- Semicolon: required / optional

### Patterns
- Error handling pattern
- Async pattern
- Module structure

### Anti-patterns
- Những gì KHÔNG được làm

## Examples
```

---

## Step 7: Sinh .agent/05_RULES_{LANG}.md

**Từ:** `.skill/{lang}.md` + `INTERVIEW_OUTPUT.yaml`

**Logic:**
```yaml
rules_agent_generation:
  base: ".skill/{lang}.md"  # Kế thừa toàn bộ
  override:  # Từ interview
    - project_specific_constraints
    - framework_version_lock
    - additional_patterns
```

**Nội dung:**
- Kế thừa toàn bộ từ `.skill/{lang}.md`
- Override project-specific từ interview

---

## Step 7: Sinh 06_BUILD_CONFIG.md

**Từ:** `technology.build_deploy`

- Build tool (Vite/CMake/MSBuild...)
- Target platform
- Output format

---

## Step 10: Cập nhật STATE.md + USER APPROVAL

```yaml
update_state:
  phase: planning
  current_task: "Review .agent/ + .skill/ files"
  next_action: "[PENDING USER APPROVAL]"
  blockers: ["Chờ user approve .agent/ và .skill/"]
  
user_approval_step:
  required: true
  message: |
    ✅ Đã tự động tạo:
    - .agent/ (00_MASTER → 06_BUILD_CONFIG)
    - .skill/{lang}.md (nếu chưa có)
    - .map/ (component_tree, data_flow)
    - .doc/ (PROGRESS.md)
    - .bug/ (template)
    
    👤 Yêu cầu user:
    1. Review .agent/00_MASTER.md
    2. Review .agent/01_STRUCTURE.md
    3. Review .agent/02_TASK_LIST.md
    4. Review .skill/{lang}.md (nếu mới tạo)
    5. Nói "approve" hoặc yêu cầu sửa đổi
    
  on_approve:
    - update: "STATE.md phase = coding"
    - update: "STATE.md current_task = T1"
    - update: "STATE.md next_action = Bắt đầu task T1"
    - notify: "Sẵn sàng coding"
    
  on_reject:
    - action: "Chỉnh sửa theo yêu cầu"
    - loop: "Generate lại → Approval"
```

---

## Step 12: Khởi tạo .map/

## Step 13: Khởi tạo .doc/

---

## Step 14: Final Validation

```yaml
validate_all:
  .agent/:
    - "00_MASTER.md: Vai trò, constraints"
    - "01_STRUCTURE.md: Cấu trúc đầy đủ"
    - "02_TASK_LIST.md: Tasks rõ ràng"
    - "05_RULES_{LANG}.md: Rules hợp lệ"
    - "STATE.md: Phase = planning"
    
  .skill/:
    - "{lang}.md: Kế thừa _shared.md, có language rules"
    
  .test/:
    - "scenarios/: Mỗi task có ít nhất 1 test file"
    - "Test format: Given/When/Then đúng chuẩn"
    
  .map/:
    - "current/: component_tree.yaml, data_flow.mmd"
    - "diff/: Initialized"
    - "refs/: Sẵn sàng cho task/bug links"
    
  .doc/:
    - "PROGRESS.md: Dashboard với tasks"
    - "DECISION_LOG.md: Template ready"
    
  .bug/:
    - "02_BUG_LIST.md: Template ready"
    
  cross_reference:
    - "Task list khớp với test scenarios"
    - "Components khớp với component_tree"
```

---

## User Approval Gate (BẮT BUỘC)

```yaml
approval_gate:
  location: "Sau Step 10, trước khi vào Coding"
  
  required_approvals:
    - file: ".agent/00_MASTER.md"
      reason: "Vai trò AI, constraints"
      
    - file: ".agent/01_STRUCTURE.md"
      reason: "Cấu trúc thư mục"
      
    - file: ".agent/02_TASK_LIST.md"
      reason: "Danh sách task"
      
    - file: ".test/scenarios/T{n}_{name}.md"
      reason: "Test cases cho mỗi task (BẮT BUỘC trước coding)"
      
    - file: ".skill/{lang}.md"
      reason: "Language rules cho project"
      
    - file: ".map/current/component_tree.yaml"
      reason: "Architecture map hiện tại"
      
    - file: ".doc/PROGRESS.md"
      reason: "Dashboard tiến độ dự án"
      
  user_actions:
    - option: "approve"
      result: "Chuyển sang phase coding"
      
    - option: "sửa [file]"
      result: "Chỉnh sửa file đó → Generate lại"
      
    - option: "thêm task"
      result: "Cập nhật 02_TASK_LIST.md"
      
    - option: "bỏ qua [task]"
      result: "Đánh dấu skip, regenerate"

  token_usage_during_approval:
    log: ".token/interview/APPROVAL.yaml"
    per_iteration: 500  # Nếu cần regenerate
```

---

## Validation

Sau khi tự động sinh:

```yaml
validate:
  .agent/:
    - check: "00_MASTER.md: Vai trò, constraints"
    - check: "01_STRUCTURE.md: Cấu trúc đầy đủ"
    - check: "02_TASK_LIST.md: Tasks rõ ràng"
    - check: "05_RULES_{LANG}.md: Rules hợp lệ"
    - check: "STATE.md: Phase = planning"
    
  .skill/:
    - check: "{lang}.md: Kế thừa _shared.md, có language rules"
    
  .test/:
    - check: "scenarios/: Mỗi task có ít nhất 1 test file"
    - check: "Test format: Given/When/Then đúng chuẩn"
    
  .map/:
    - check: "current/: component_tree.yaml, data_flow.mmd"
    - check: "diff/: Initialized (.gitkeep)"
    - check: "refs/: Initialized (.gitkeep)"
    
  .doc/:
    - check: "PROGRESS.md: Dashboard với tasks từ 02_TASK_LIST.md"
    - check: "DECISION_LOG.md: Template sẵn sàng"
    
  cross_reference:
    - check: "Task list trong 02_TASK_LIST.md khớp với scenarios trong .test/"
    - check: "Components trong 01_STRUCTURE.md khớp với component_tree.yaml"
```

---

## Step 5: Token Logging

```yaml
step_5_token_log:
  name: " BẮT BUỘC: Log Token Usage"
  action: "Ghi token sau mỗi câu hỏi"
  output: ".token/interview/INTERVIEW_LOG.yaml"
  format:
    entry_id: "Q1-Tier0"  # {question_num}-Tier{tier_num}
    timestamp: "ISO-8601"
    tier: 0
    question_num: 1
    question_text: "Tóm tắt"
    answer_summary: "Tóm tắt câu trả lời"
    tokens:
      prompt_tokens: 350      # Context + question
      response_tokens: 200    # User answer
      total_tokens: 550
      cumulative: 550       # Running total
    budget:
      remaining: 14450
      percentage_used: 3.7%
    file_path: ".token/interview/INTERVIEW_LOG.yaml"
  fail_action: "KHÔNG ĐƯỢC TIẾP TỤC nếu chưa log token"
```

## Step 6: Checkpoint

```yaml
step_6_checkpoint:
  name: "Lưu Checkpoint"
  action: "Ghi INTERVIEW_OUTPUT.yaml sau mỗi tier"
  if: "tier hoàn thành"
```

*Quy trình này tự động chạy sau khi INTERVIEW_OUTPUT.yaml hoàn thành.*
