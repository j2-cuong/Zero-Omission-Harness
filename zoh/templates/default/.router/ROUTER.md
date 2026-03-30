# .router/ROUTER.md
> **Vai trò:** Điều phối context — quyết định AI cần load file nào dựa trên intent và state hiện tại.
> **Input:** User request + `.agent/STATE.md` (nếu có)
> **Output:** Danh sách file cần load cho task hiện tại
> **Rule:** File này PHẢI được đọc đầu tiên trước mọi action. Không load toàn bộ hệ thống.

---

## Routing Logic

AI đọc file này → Xác định intent → Load đúng context cần thiết → Thực thi.

```
[User Request]
    │
    ▼
[ROUTER.md] ──pattern_match──► [Phase Router]
    │                              │
    │    ┌─────────────────────────┼─────────────┐
    │    │                         │             │
    ▼    ▼                         ▼             ▼
[INTERVIEW]  [CODE]  [DOC]  [BUGFIX]  [TEST]  [ARCH]
```

---

## Phase Detection

Dựa trên `STATE.md` (nếu có) hoặc user intent:

| Điều kiện | Phase Router | File cần load |
|-----------|--------------|---------------|
| `STATE.md` không tồn tại | `.router/00_INTERVIEW.md` | Chưa có dự án → bắt buộc phỏng vấn |
| `STATE.phase = interview` | `.router/00_INTERVIEW.md` | Tiếp tục phỏng vấn |
| `STATE.phase = planning` | `.router/00_INTERVIEW.md` | Hoàn thiện thông tin |
| `STATE.phase = coding` | `.router/01_CODE.md` | Task code cụ thể |
| `STATE.phase = testing` | `.router/04_TEST.md` | Task test/fix |
| `STATE.phase = bugfix` | `.router/02_BUGFIX.md` | Debug & fix |
| `STATE.phase = doc` | `.router/03_DOC.md` | Viết documentation |

---

## Intent Keywords (Override Phase)

Nếu user request chứa keywords đặc biệt → override phase detection:

| Keywords | Override Router | Priority |
|----------|-----------------|----------|
| `bug`, `crash`, `fix`, `error`, `lỗi`, `sửa` | `.router/02_BUGFIX.md` | High |
| `phỏng vấn`, `bắt đầu`, `mới`, `interview` | `.router/00_INTERVIEW.md` | High |
| `doc`, `tài liệu`, `document` | `.router/03_DOC.md` | High |
| `test`, `kiểm thử`, `scenario` | `.router/04_TEST.md` | High |
| `kiến trúc`, `arch`, `diagram` | `.router/05_ARCH.md` | Medium |

---

## Lazy Loading Rules

**Không được load toàn bộ hệ thống.** Chỉ load những gì cần:

### Rule 1: Interview Tiered
- **Tier 0** (luôn load): `.router/00_INTERVIEW.md` → `.workflow/00_INTERVIEW.md` (4 câu cơ bản)
- **Tier 1** (nếu chưa đủ): `.workflow/interview/01_architecture.md`
- **Tier 2** (conditional): `.workflow/interview/02_contracts.md`
- **Tier 3** (optional): `.workflow/interview/03_constraints.md`

### Rule 2: Skip Nếu Đã Có
- Nếu `.agent/STATE.md` tồn tại và `phase != interview` → **skip interview hoàn toàn**
- Nếu `.agent/01_STRUCTURE.md` tồn tại → **skip structural questions**
- Nếu component đã được định nghĩa → **skip component discovery**

### Rule 3: Language-Specific
- Nếu `languages.primary = cpp` → load `.skill/cpp.md` + `.agent/05_RULES_CPP.md`
- Nếu `languages.primary = csharp` → load `.skill/csharp.md` + `.agent/05_RULES_CSHARP.md`
- Nếu `languages.primary = react` → load `.skill/react.md` + `.agent/05_RULES_REACT.md`
- Nếu `multi` → load ngôn ngữ chính + `_shared.md`

---

## Token Budget

Mỗi phase router có ngân sách context riêng:

| Router | Max Tokens Estimate | Files Tối Đa |
|--------|---------------------|--------------|
| `00_INTERVIEW.md` (Tier 0) | ~500 | 3 files |
| `00_INTERVIEW.md` (Full) | ~2000 | 5 files |
| `01_CODE.md` | ~1500 | 4 files |
| `02_BUGFIX.md` | ~1000 | 3 files |
| `03_DOC.md` | ~800 | 2 files |
| `04_TEST.md` | ~1200 | 3 files |
| `05_ARCH.md` | ~1000 | 3 files |

**Nếu vượt ngân sách → báo user và đề xuất chia nhỏ task.**

---

## Decision Output Format

Sau khi routing, AI output:

```yaml
routing_decision:
  detected_phase: "interview|coding|bugfix|test|doc|arch"
  override_reason: ""  # nếu có override từ keywords
  files_to_load:
    - ".skill/cpp.md"
    - ".agent/STATE.md"
    - ".workflow/00_INTERVIEW.md"
  files_to_skip:
    - ".workflow/interview/03_constraints.md"  # chưa cần
  estimated_tokens: 1200
  next_action: "Bắt đầu interview Tier 0"
```

---

## Checklist Trước Mọi Action

- [ ] Đã đọc `ROUTER.md` này
- [ ] Đã kiểm tra `.agent/STATE.md` tồn tại không
- [ ] Đã detect phase từ STATE hoặc keywords
- [ ] Đã xác định files cần load (không load thừa)
- [ ] Đã ước tính token budget
- [ ] Nếu budget > limit → chia nhỏ task hoặc hỏi user

---

*File này là entry point của toàn hệ thống. Luôn đọc đầu tiên.*
