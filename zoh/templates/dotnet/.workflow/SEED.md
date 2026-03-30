# SEED.md
> **Vai trò:** Output của phỏng vấn — chìa khóa unlock toàn hệ thống. **(Legacy: thay bằng INTERVIEW_OUTPUT.yaml)**
> **Input:** `INTERVIEW_OUTPUT.yaml` hoàn thành → Phân tích → Sinh SEED
> **Output:** Context đầy đủ để sinh .agent/, .skill/ overrides, khởi tạo STATE.md
> **Rule:** File này được sinh từ INTERVIEW_OUTPUT.yaml sau khi 7 tiers hoàn thành. Không chỉnh tay — mọi thay đổi phải qua lại interview.
> **Status:** LEGACY — Nội dung được chuyển từ INTERVIEW_OUTPUT.yaml

## Workflow mới (7 Tiers)

```
7 Tiers Interview (00_basic → 06_exceptions)
        ↓
INTERVIEW_OUTPUT.yaml (checkpoint sau mỗi tier)
        ↓
Phân tích → Sinh SEED.md + .agent/
```

**Ghi chú:** Hệ thống mới dùng `INTERVIEW_OUTPUT.yaml` làm checkpoint chính. SEED.md là derived output.

---

[Nội dung được sinh từ INTERVIEW_OUTPUT.yaml sau khi 7 tiers hoàn thành]
