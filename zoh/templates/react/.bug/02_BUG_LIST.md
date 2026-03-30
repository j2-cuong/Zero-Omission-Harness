# 02_BUG_LIST.md — Danh sách bug
> **Vai trò:** Registry tập trung tất cả bug — phân nhóm theo severity.
> **Input:** 01_SCAN_LOG.md
> **Output:** Danh sách ưu tiên để fix — input cho 03_FIX_DETAILS.md và .sim/
> **Rule:** Mỗi bug có ID duy nhất. Status phải sync với 03_FIX_DETAILS.md và STATE.md.

## Format mỗi bug

```
BUG-ID: BUG-{nn}
SEVERITY: Critical | Important | Minor
TITLE: Tên ngắn
FILE: path/to/file:line
FUNCTION: tên_hàm
DELTA: Sai lệch so với contract/doc là gì
MAP_NODE: Link đến node trong cross_lang.svg
STATUS: OPEN | SIM_PENDING | APPROVED | FIXED | VERIFIED
LINKED_SIM: .sim/dry_run_{id}.md
SIGNED: [AI-ID] [timestamp]
```

## 🔴 Critical

[Chưa có]

## 🟡 Important

[Chưa có]

## ⚪ Minor

[Chưa có]
