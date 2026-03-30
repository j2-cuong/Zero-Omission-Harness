# 00_RULES.md — Quy tắc Bug Scan
> **Vai trò:** Bộ luật tối cao điều phối AI scan bug — 7 bước bắt buộc, zero-omission.
> **Input:** Không có (rule tĩnh)
> **Output:** Protocol mà mọi AI phải tuân thủ khi scan và fix bug.
> **Rule CỨNG:** Bỏ sót bất kỳ file nào trong module cốt lõi = vi phạm nghiêm trọng.

## 7 bước bắt buộc

```
Bước 1 — SCAN: Duyệt toàn bộ file, từng hàm. Đối chiếu với .map/ và .agent/03_API_CONTRACT.md
Bước 2 — LOG: Ghi vào 01_SCAN_LOG.md theo chuẩn. Tạo BUG-ID mới trong 02_BUG_LIST.md
Bước 3 — PROPOSE: Ghi lý thuyết fix vào 03_FIX_DETAILS.md + link .sim/dry_run_{id}.md
Bước 4 — SIM: Tạo .sim/dry_run_{id}.md — đánh giá cascade risk
Bước 5 — TEST: Tạo .test/scenarios/sim_{id}.md — kịch bản kiểm thử
Bước 6 — APPROVE: Chờ user phê duyệt qua 03_FIX_DETAILS.md
Bước 7 — FIX + SIGN-OFF: Apply fix → chạy consistency check → cập nhật STATE.md + DECISION_LOG
```

## Scan format bắt buộc

```
[FILEPATH:LINE] → [FUNCTION] → [Delta so với contract/doc] → [Đề xuất fix] → [AI-ID]
```

## Phân loại severity

- 🔴 **Critical:** Logic sai, kiến trúc sai, security hole
- 🟡 **Important:** Protocol mismatch, performance issue
- ⚪ **Minor:** Optimization, style, naming
