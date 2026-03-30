# .workflow/interview/06_exceptions.md
> **Tier:** 6 — Error handling & edge cases
> **When:** Khi cần robustness cao hoặc critical systems
> **Next:** DONE → Sinh INTERVIEW_OUTPUT.yaml
> **Token estimate:** ~600

---

## 6.1 Error Handling Strategy

**Hỏi:** Chiến lược xử lý lỗi tổng thể?

**Approach:**
- **Exceptions:** throw/catch (C++, C#, Python-style)
- **Error codes:** return codes, result types (Rust-style)
- **Hybrid:** exceptions cho fatal, error codes cho expected
- **Logging & continue:** log và tiếp tục (batch processing)
- **Fail-fast:** crash ngay để detect sớm (development)

**Recovery strategy:**
- Retry: immediate, exponential backoff
- Fallback: default value, cached value, degraded mode
- Circuit breaker: ngừng gọi service đang lỗi
- Checkpoint/restart: save state, restart từ điểm an toàn

---

## 6.2 Expected Failures (Known Errors)

**Hỏi:** Những lỗi nào là "bình thường" và cần handle gracefully?

**Ví dụ thường gặp:**
- **I/O:** File not found, permission denied, disk full
- **Network:** Timeout, connection reset, DNS failure
- **Input:** Invalid format, out of range, encoding error
- **Resource:** Out of memory, too many open files
- **External:** Service unavailable, API rate limited

**Per-component:**
```yaml
cli:
  expected_errors: ["invalid_args", "file_not_found"]
  
core:
  expected_errors: ["validation_failed", "timeout"]
  
network:
  expected_errors: ["connection_failed", "timeout", "retry_exhausted"]
```

---

## 6.3 Unexpected Failures (Bugs/Crashes)

**Hỏi:** Xử lý thế nào khi gặp bug/crash không mong đợi?

**Crash handling:**
- **Dump:** core dump, minidump, crash report
- **Restart:** auto-restart service, supervisor
- **Report:** telemetry, error tracking (Sentry, etc.)
- **Graceful degradation:** tắt feature lỗi, giữ app chạy

**Data integrity:**
- Transactions: rollback on failure
- Idempotency: gọi lại không làm hỏng data
- Validation: checksum, sanity checks
- Backup/recovery: restore từ backup

---

## 6.4 Edge Cases & Boundary Conditions

**Hỏi:** Những edge cases cần xử lý?

**Input boundaries:**
- Empty input
- Maximum size (huge file, long string)
- Special characters (unicode, null bytes, escape sequences)
- Concurrent modification (file bị xóa khi đang đọc)

**Resource exhaustion:**
- Out of memory
- Disk full
- Network unavailable
- Too many connections

**Timing issues:**
- Race conditions
- Timeouts
- Clock skew
- Leap seconds/timezone

**External changes:**
- Config file bị sửa khi đang chạy
- Database schema thay đổi
- API version update
- OS shutdown/restart

---

## 6.5 Logging & Observability

**Hỏi:** Log như thế nào để debug được?

**Log levels:**
- ERROR: failures cần action
- WARN: có thể là vấn đề
- INFO: significant events
- DEBUG: chi tiết cho debugging
- TRACE: rất chi tiết (performance impact)

**Log content:**
- Timestamp, correlation ID
- Component, function, line number
- Context: input, state, environment
- Stack trace cho exceptions

**Observability:**
- Distributed tracing (jaeger, zipkin)
- Metrics (prometheus, statsd)
- Alerting (pagerduty, slack)

---

## Output sau Tier 6

```yaml
tier: 6
result:
  exceptions:
    error_handling_strategy: ""
    recovery_strategy: []
    
  expected_failures:
    by_component: {}
    global: []
    
  unexpected_failures:
    crash_handling: {}
    data_integrity: {}
    
  edge_cases:
    input_boundaries: []
    resource_exhaustion: []
    timing_issues: []
    external_changes: []
    
  logging:
    levels: []
    content: {}
    observability: {}

next_tier: DONE
```

---

## Sau khi hoàn thành tất cả tiers

**Sinh file:** `.workflow/interview/INTERVIEW_OUTPUT.yaml`

File này chứa toàn bộ kết quả phỏng vấn từ Tier 0-6, là input để phân tích và tạo `.agent/`.
