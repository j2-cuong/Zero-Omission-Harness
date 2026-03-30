# TOKEN_TRACKING.md — Token Budget & Logging System
> **Vai trò:** Theo dõi và quản lý token usage trong toàn bộ hệ thống AI Agent Base.
> **Input:** Mọi interaction AI ↔ User
> **Output:** Chi tiết token đi/về cho mọi phase.

## Directory Structure

```
.token/
├── TOKEN_TRACKING.md         # (file này) Guide & format
├── BUDGET.yaml               # Token budget cho từng phase
├── interview/
│   ├── INTERVIEW_LOG.yaml    # Log từng câu hỏi
│   └── SESSION_{timestamp}.yaml
├── coding/
│   ├── CODING_LOG.yaml       # Log từng task code
│   └── TASK_{id}.yaml
├── bugfix/
│   ├── BUGFIX_LOG.yaml       # Log từng bug fix
│   └── BUG_{id}.yaml
├── test/
│   └── TEST_LOG.yaml
└── daily/
    └── {YYYY-MM-DD}.yaml     # Daily summary
```

## Format Log Entry

```yaml
entry:
  timestamp: "2026-03-30T10:35:00Z"
  phase: "interview" | "coding" | "bugfix" | "test"
  task_id: "T1" | "BUG-001" | "Q1-Tier0"
  
  # Token counts (ước tính/actual)
  tokens:
    input: 1500      # Prompt gửi đi (system + context + question)
    output: 800      # Response nhận về
    total: 2300
    
  # Context loaded
  context:
    files_loaded: 3
    lines_loaded: 450
    
  # Content
  action: "Hỏi về project architecture"
  result: "User trả lời: web app với React"
  
  # Efficiency
  efficiency_score: 0.85  # (useful_output / total_tokens)
```

## Budget Allocation

```yaml
budget:
  interview:
    total: 10000
    per_question: 1500
    max_questions: 20
    
  coding:
    total: 50000
    per_task: 5000
    buffer: 10000
    
  bugfix:
    total: 20000
    per_bug: 5000
    
  test:
    total: 10000
    per_test: 2000
    
  daily_limit: 80000
```

## Router Token Management

```yaml
router_rules:
  lazy_loading:
    - "Chỉ load file cần thiết cho task hiện tại"
    - "Truncate file dài, chỉ lấy relevant sections"
    - "Dùng summary thay vì full content"
    
  context_window:
    max_tokens: 64000
    reserve: 4000  # Dành cho response
    effective_limit: 60000
    
  compression:
    - "YAML > Markdown > Plain text (cho cùng info)"
    - "Ghi line numbers thay vì copy code"
    - "Dùng bullet points thay vì paragraphs"
```

---

*Mọi interaction PHẢI ghi lại token usage.*
