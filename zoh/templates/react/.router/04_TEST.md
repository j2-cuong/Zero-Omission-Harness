# .router/04_TEST.md
> **Vai trò:** Điều phối testing tasks — unit, integration, e2e, special scenarios.
> **Input:** Test request hoặc post-code validation
> **Output:** Load test framework + generate/run tests
> **Rule:** Không code mà không test. Không test mà không scenario rõ ràng.

---

## Test Task Detection

| User Request | Test Type | Files Load |
|--------------|-----------|------------|
| `unit test`, `test hàm` | **Unit Test** | Component code + RULES |
| `integration test`, `test luồng` | **Integration** | Multiple components + API contracts |
| `e2e test`, `end-to-end` | **E2E** | Full system + test environment |
| `memory leak`, `leak check` | **Memory** | `.test/memory/` config |
| `race condition`, `concurrency` | **Concurrency** | Threading code + test scenarios |
| `load test`, `performance` | **Load** | Performance requirements + metrics |
| `coverage`, `đo coverage` | **Coverage** | All tests + coverage config |

---

## Required Context

**Mọi test đều cần:**
1. **`.agent/STATE.md`** — biết phase và test requirements
2. **`.agent/01_STRUCTURE.md`** — biết components và dependencies
3. **`.agent/06_BUILD_CONFIG.md`** — biết test framework và build config

**Theo test type:**

| Test Type | Files bổ sung |
|-----------|---------------|
| Unit | Component implementation files |
| Integration | `.agent/03_API_CONTRACT.md`, `.agent/03_IPC_CONTRACT.md` |
| E2E | `.doc/USER_GUIDE.md` (hiểu use cases) |
| Memory | `.test/memory/TRACE_CONFIG.md` |
| Concurrency | `.test/concurrency/SCENARIOS.md` |
| Load | `.constraints/performance.md` hoặc từ SEED |

---

## Test Gate (GATE-3)

Quy tắc cứng của hệ thống:

```yaml
gate_3_requirements:
  - "Test phải có trước khi merge code"
  - "Test phải có scenario rõ ràng (input → expected output)"
  - "Memory leak test cho long-running code"
  - "Race condition test cho multi-threaded code"
  - "Test phải chạy được tự động (không manual steps)"
```

**Vi phạm GATE-3:** Không cho phép apply fix/feature.

---

## Test Writing Flow

```
[Yêu cầu test hoặc post-code]
    │
    ▼
[Phân loại test cần]
    │
    ▼
Load test framework context
    │
    ▼
Kiểm tra existing tests
    │── Có → Extend
    │── Không → Tạo mới theo template
    ▼
Generate test code
    │
    ▼
Run test → [Pass?]
    │── FAIL → Debug và sửa (code hoặc test)
    │ PASS
    ▼
Update .test/ + STATE.md
```

---

## Memory Testing

Nếu `.test/memory/` tồn tại:
1. Đọc `TRACE_CONFIG.md`
2. Chạy scenario với memory tracing enabled
3. Phân tích alloc/free patterns
4. Flag leak nếu có

**Nếu chưa có:** Setup memory trace cho scenario quan trọng.

---

## Token Budget: Testing

| Test Type | Est. Tokens | Notes |
|-----------|-------------|-------|
| Unit test (1 hàm) | ~400 | Simple input/output |
| Unit test (complex) | ~600 | Mocks, dependencies |
| Integration test | ~800 | Multi-component |
| E2E test | ~1000 | Full flow setup |
| Memory test setup | ~500 | Trace config |
| Concurrency test | ~700 | Race scenarios |

---

## Post-Test Actions

```yaml
post_test:
  - update: ".agent/STATE.md"
    field: "consistency_flags.test"
    value: true
    
  - write: ".test/{component}/{test_name}.md"
    content: "Test scenario + results"
    
  - if_memory_test: 
    write: ".test/memory/{scenario}_trace.md"
    
  - verify: "GATE-3 PASS"
```

---

## Special Test Scenarios

| Scenario | Khi nào cần | Files |
|----------|-------------|-------|
| **Race Condition** | `concurrency=multi-threaded` | `.test/concurrency/race_{component}.md` |
| **Memory Leak** | `state=long-running` hoặc embedded | `.test/memory/leak_{component}.md` |
| **Load Test** | `constraints.performance` có yêu cầu | `.test/load/{metric}_{threshold}.md` |
| **Fuzzing** | Security-critical input | `.test/fuzz/{input_type}.md` |

---

*Router này đảm bảo mọi code đều có test, mọi test đều có scenario.*
