# 03_FIX_DETAILS.md — Chi tiết phương án fix
> **Vai trò:** Lý thuyết fix cho từng bug + link simulation và test scenario.
> **Input:** 02_BUG_LIST.md + .sim/dry_run_{id}.md + .test/scenarios/
> **Output:** Kế hoạch fix chi tiết để user phê duyệt trước khi thực thi.
> **Rule:** Không được fix bất kỳ bug nào mà không có entry ở đây được user approve.

## Format mỗi fix plan

```
BUG-ID: BUG-{nn}
ROOT_CAUSE: Nguyên nhân gốc rễ
FIX_APPROACH: Phương án fix chi tiết
CODE_CHANGE: Mô tả thay đổi code cụ thể
SIM_LINK: .sim/dry_run_{id}.md
TEST_LINK: .test/scenarios/sim_{id}.md
CASCADE_RISK: Rủi ro ảnh hưởng đến module khác (từ cascade_map.md)
APPROVAL_STATUS: PENDING | APPROVED | REJECTED
APPROVED_BY: [user/AI-ID] [timestamp]
```

[Chưa có fix plan]
