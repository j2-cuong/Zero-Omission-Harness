# AI_GUIDE.md — Hướng Dẫn AI Làm Việc Trong Hệ Thống
> **Vai trò:** Hướng dẫn cho AI (Claude, GPT, v.v.) khi làm việc trong AI Agent Base.
> **Đọc khi:** Bắt đầu session, chuyển phase, hoặc cần nhắc lại workflow.
> **Rule:** AI PHẢI tuân thủ workflow này. Không làm tự do.

---

## 1. Tổng Quan Hệ Thống

### Cấu Trúc Thư Mục

```
ai-agent-base/
├── .router/           ← Điều phối intent → file cần load
│   ├── ROUTER.md
│   ├── 00_INTERVIEW.md
│   ├── 01_CODE.md
│   ├── 02_BUGFIX.md
│   ├── 03_DOC.md
│   ├── 04_TEST.md
│   └── 05_ARCH.md
│
├── .workflow/         ← Quy trình từng phase
│   ├── 00_MASTER_WORKFLOW.md      ← Đọc đầu tiên!
│   ├── 02_GENERATE_AGENT.md
│   ├── 03_SCAN_FOR_BUGS.md
│   ├── 04_BUGFIX_LOOP.md
│   └── 05_TEST_PHASE.md
│
├── .agent/            ← Context cho AI
│   ├── 00_MASTER.md               ← Vai trò, constraint
│   ├── 01_STRUCTURE.md            ← Cây thư mục
│   ├── 02_TASK_LIST.md            ← Danh sách task
│   ├── 03_API_CONTRACT.md         ← API nếu có
│   ├── 03_IPC_CONTRACT.md         ← IPC nếu có
│   ├── 04_PINVOKE_CONTRACT.md     ← P/Invoke nếu có
│   ├── 05_RULES_{LANG}.md         ← Rules coding
│   ├── 06_BUILD_CONFIG.md         ← Build config
│   └── STATE.md                   ← Trạng thái hiện tại
│
├── .map/              ← Architecture tracking
│   ├── current/                   ← State hiện tại
│   ├── diff/                      ← Version diffs
│   └── refs/                      ← Bug/task references
│
├── .doc/              ← Documentation
│   ├── PROGRESS.md                ← Dashboard
│   └── DECISION_LOG.md            ← Quyết định kiến trúc
│
├── .bug/              ← Bug tracking
│   ├── 01_SCAN_LOG.md             ← Kết quả quét
│   ├── 02_BUG_LIST.md             ← Danh sách bug
│   └── 03_FIX_DETAILS.md          ← Chi tiết fix
│
├── .sim/              ← Simulations
│   └── dry_run_{id}.md            ← Pre-fix simulation
│
├── .test/             ← Test scenarios
│   └── scenarios/                 ← Test cases
│
├── .skill/            ← Language rules
│   ├── react.md
│   ├── cpp.md
│   └── csharp.md
│
└── .token/            ← Token tracking ← QUAN TRỌNG!
    ├── TOKEN_TRACKING.md
    ├── interview/
    ├── coding/
    ├── bugfix/
    ├── test/
    └── daily/
```

---

## 2. Workflow Tuần Hoàn

### Vòng Đời Dự Án

```
┌─────────────────────────────────────────────────────┐
│                    START                            │
└──────────┬──────────────────────────────────────────┘
           │
           ▼
    ┌──────────────┐
    │   INTERVIEW  │ ← Phỏng vấn user, log token
    │   (.router/) │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   GENERATE   │ ← Auto-sinh .agent/ files
    │  (.workflow/)│   Log token
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │    CODING    │ ← Code từng task
    │   (.router/) │   Update .map/, .doc/
    └──────┬───────┘   Log token per task
           │
           ▼
    ┌──────────────┐
    │    SCAN      │ ← Quét bug từ .map/, .doc/
    │  (.workflow/)│   Log token
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │    FIX       │ ← Fix bugs
    │  (.workflow/)│   .sim/ → fix → .map/diff/
    └──────┬───────┘   Log token per bug
           │
           ▼
    ┌──────────────┐
    │    TEST      │ ← Chạy tests
    │  (.workflow/)│   Update .doc/PROGRESS.md
    └──────┬───────┘   Log token
           │
           ▼
    ┌──────────────┐
    │   DECISION   │ ← Bug? → Fix
    │              │ ← Pass? → Release
    └──────────────┘ ← Feature? → Interview (partial)
```

---

## 3. Token Tracking (BẮT BUỘC!)

### Mọi Interaction Đều Log

```yaml
rule_mandatory:
  - "Sau mỗi câu hỏi interview → log token"
  - "Sau mỗi task code → log token"
  - "Sau mỗi bug fix → log token"
  - "Sau mỗi test run → log token"
  - "Cuối ngày → summary"
```

### Format Log

```yaml
# .token/interview/INTERVIEW_LOG.yaml
entry:
  question_id: "Q1"
  timestamp: "2026-03-30T10:35:00Z"
  tokens:
    input: 500      # Prompt gửi đi
    output: 300     # Response nhận về
    total: 800
  budget_remaining: 14200
```

```yaml
# .token/coding/CODING_LOG.yaml
entry:
  task_id: "T1"
  timestamp: "2026-03-30T11:00:00Z"
  tokens:
    read: 400       # Đọc context
    plan: 300       # Lập kế hoạch
    code: 800       # Viết code
    validate: 200   # Kiểm tra
    total: 1700
```

---

## 4. Lazy Loading (Tiết Kiệm Token)

### Nguyên Tắc

```yaml
lazy_loading:
  - "Chỉ load file cần cho task HIỆN TẠI"
  - "Không load toàn bộ .agent/"
  - "Dùng STATE.md để biết phase hiện tại"
  - "Truncate file dài (>100 dòng)"
```

### Ví Dụ

| Task | Files Load | Không Load |
|------|-----------|------------|
| Interview Tier 0 | 00_INTERVIEW.md, 00_basic.md | Các tier khác |
| Code task T1 | 02_TASK_LIST.md (T1 only), 01_STRUCTURE.md (relevant) | Toàn bộ tasks |
| Fix bug BUG-001 | Bug report, file cần sửa, .sim/ | Các bug khác |

---

## 5. State-Driven Actions

### Luôn Kiểm Tra STATE.md

```yaml
action_rules:
  - rule: "Đọc STATE.md đầu tiên khi vào"
  - rule: "Kiểm tra phase trước mọi action"
  - rule: "Chỉ làm task trong current_task"
  - rule: "Update STATE.md sau mỗi action"
```

### STATE.md Schema

```yaml
phase: interview | planning | coding | bugfix | testing | release
current_task: "Tên task cụ thể"
next_action: "Task tiếp theo"
blockers: []  # Nếu có blocker, DỪNG và hỏi user
consistency_flags:
  doc: true | false
  map: true | false
  test: true | false
```

---

## 6. Cross-Reference Updates

### Khi Code Thay Đổi

```yaml
on_code_change:
  immediate:
    - "Update file code"
    - "Log token"
    
  post_action:
    - "Update .map/current/ nếu thêm component"
    - "Update .doc/PROGRESS.md status"
    - "Update .agent/STATE.md"
    
  if_new_feature:
    - "Update .map/current/component_tree.yaml"
    - "Update .map/current/data_flow.mmd"
```

### Khi Fix Bug

```yaml
on_bug_fix:
  immediate:
    - "Fix code"
    - "Update .bug/02_BUG_LIST.md status"
    - "Log token"
    
  post_action:
    - "Create .map/diff/v{X}_to_v{Y}.yaml"
    - "Update .map/refs/BUG-{id}.yaml"
    - "Run regression tests"
```

---

## 7. Gate Checks

### Không Được Bỏ Qua

```yaml
gate_checks:
  gate_1_interview:
    check: "INTERVIEW_OUTPUT.yaml complete?"
    fail_action: "Không được generate .agent/"
    
  gate_2_planning:
    check: "02_TASK_LIST.md đã review?"
    fail_action: "Không được code"
    
  gate_3_before_fix:
    check: ".sim/dry_run_{id}.md tồn tại?"
    fail_action: "Phải tạo simulation trước"
    
  gate_4_before_release:
    check: "All tests pass?"
    fail_action: "Phải fix bugs trước"
```

---

## 8. Emergency Procedures

### Token Hết

```yaml
emergency_token_exhausted:
  1: "Lưu STATE.md ngay lập tức"
  2: "Ghi checkpoint vào .token/emergency/"
  3: "Thông báo user chi tiết"
  4: "Tạo progress summary"
  5: "Dừng gracefully"
```

### Mất Context

```yaml
emergency_context_lost:
  1: "Đọc STATE.md để biết phase"
  2: "Đọc checkpoint file (.token/interview/INTERVIEW_LOG.yaml)"
  3: "Resume từ điểm dừng"
  4: "Không bắt đầu lại từ đầu"
```

---

## 9. AI Sign-Off

### Mỗi Action Phải Ký Tên

```yaml
sign_off_format:
  file_header: "[timestamp] [AI-ID] [action description]"
  inline: "// [AI-ID]: change reason"
  
examples:
  - "[2026-03-30 10:15] [Claude-3.7] [Tạo 01_STRUCTURE.md từ INTERVIEW_OUTPUT.yaml]"
  - "[2026-03-30 11:20] [Claude-3.7] [Fix BUG-001: thêm error handling]"
```

---

## 10. Checklist Khi Bắt Đầu

```yaml
startup_checklist:
  - "Đọc .agent/STATE.md"
  - "Xác định phase hiện tại"
  - "Đọc .token/TOKEN_TRACKING.md"
  - "Kiểm tra budget còn lại"
  - "Load file cần thiết (lazy load)"
  - "Bắt đầu task"
```

---

## 11. Checklist Khi Kết Thúc

```yaml
shutdown_checklist:
  - "Update STATE.md"
  - "Log token usage"
  - "Cập nhật .doc/PROGRESS.md"
  - "Kiểm tra consistency flags"
  - "Thông báo user next action"
```

---

*Hệ thống này đảm bảo AI làm việc có tổ chức, track được, và optimize token usage.*
