# .router/02_BUGFIX.md
> **Vai trò:** Điều phối bug fixing — nhanh, tập trung, ít context.
> **Input:** Bug report từ user
> **Output:** Load context cần thiết để reproduce & fix
> **Rule:** Bugfix cần tốc độ — load tối thiểu, focus vào repro + fix.

---

## Bug Report Analysis

Phân loại bug dựa trên mô tả:

| Indicator | Bug Type | Priority |
|-----------|----------|----------|
| `crash`, `segfault`, `exception`, `abort` | **Crash** | Critical |
| `hang`, `freeze`, `infinite loop`, `stuck` | **Hang** | Critical |
| `wrong result`, `incorrect`, `not working` | **Logic** | High |
| `slow`, `lag`, `performance` | **Performance** | Medium |
| `memory leak`, `OOM`, `growing` | **Memory** | High |
| `race condition`, `deadlock`, `thread` | **Concurrency** | Critical |

---

## Minimal Context Loading

**Luôn load (2-3 files):**
1. **`.agent/STATE.md`** — biết phase hiện tại
2. **`.skill/{language}.md`** — ngôn ngữ specific debugging
3. **`.agent/05_RULES_{LANG}.md`** — project conventions

**Conditional load:**

| Điều kiện | File bổ sung |
|-----------|--------------|
| Bug liên quan API | `.agent/03_API_CONTRACT.md` |
| Bug liên quan IPC | `.agent/03_IPC_CONTRACT.md` |
| Bug liên quan P/Invoke | `.agent/04_PINVOKE_CONTRACT.md` |
| Crash/Leak/Memory | `.test/memory/` traces nếu có |
| Đã có `.sim/` | `.sim/{bug_id}/` reproduction |
| Bug phức tạp | `.agent/DECISION_LOG.md` |

---

## Bugfix Flow

```
[Nhận bug report]
    │
    ▼
[Phân loại bug] → [Xác định files cần load]
    │
    ▼
Load minimal context → [Reproduce?]
    │── Không repro được → Yêu cầu thêm info
    │
    ▼
[Simulate fix] → .sim/{bug_id}/
    │── Nếu có .sim/ sẵn → dùng luôn
    │
    ▼
[Apply fix] → Test → [Pass?]
    │── FAIL → Quay lại simulate
    │ PASS
    ▼
Update STATE.md + .bug/ trace
```

---

## Simulation First (Nếu có .sim/)

Nếu `.sim/` đã được setup:
1. Đọc `.sim/{bug_id}/SCENARIO.md`
2. Chạy simulation để reproduce
3. Test fix trong simulation
4. User approve → apply vào code thật

**Nếu chưa có .sim/:**
- Tạo nhanh `.sim/bug_{timestamp}/`
- Viết SCENARIO.md minimal
- Reproduce và fix trong đó

---

## Token Budget: Bugfix

| Bug Type | Files | Est. Tokens | Max Time |
|----------|-------|-------------|----------|
| Simple (1 file) | 2-3 | ~500 | 10 phút |
| Medium (multi-file) | 3-4 | ~800 | 20 phút |
| Complex (root cause khó tìm) | 4-5 | ~1000 | 30 phút |
| Critical (crash/hang) | 3-5 | ~1000 | ASAP |

**Quy tắc:** Bugfix không được ngốn >1000 tokens. Nếu cần nhiều hơn → chia thành investigation + fix phases.

---

## Post-Fix Actions

```yaml
post_fix:
  - update: ".agent/STATE.md"
    field: "last_action"
    value: "Fixed {bug_description}"
  
  - append: ".bug/BUG_LOG.md"
    entry:
      bug_id: "{timestamp}"
      type: "crash|hang|logic|perf|memory|concurrency"
      root_cause: ""
      fix_location: ""
      test_added: true|false
      
  - update_map:
      if: "fix thay đổi code structure / function"
      strategy: "minimal"
      note: "Bugfix thường không đổi architecture, chỉ cập nhật nếu cần"
      
  - create_ref:
      if: "bug liên quan đến component cụ thể"
      file: ".map/refs/BUG-{id}.yaml"
      content:
        bug_id: "{id}"
        affected_nodes:
          component: ""
          function: ""
        map_snapshot: "v{X.Y.Z}"
        
  - trigger: "consistency_check"
    verify: ["test", "contract"]
```

---

## Map Update After Bugfix

Bugfix thường **không cần** cập nhật map nếu:
- Chỉ sửa logic implementation (không đổi interface)
- Sửa bug trong function body (không đổi call graph)
- Không thêm/xóa component

**Cần update map nếu:**
- Fix thêm function mới (ví dụ: thêm `validate_input()`)
- Fix đổi API signature (breaking change)
- Fix thêm error handling path mới

### Minimal Update Strategy

```
Phân tích fix:
    ↓
Chỉ sửa implementation? → Skip map update
Thêm function? → Append vào callgraph_{comp}.txt
Đổi signature? → Update component_tree.yaml
    ↓
Ghi nhận trong BUG_LOG
```

---

## Emergency Bugfix (Crash/Hang)

Khi có critical bug:
1. **Bỏ qua** phần lớn context files
2. **Focus:** stack trace, log, code location
3. **Quick fix** → test → commit
4. **Ghi nợ** documentation cho sau

---

*Router này đảm bảo bugfix nhanh gọn, không bị ngập context.*
