# cascade_map.md — Bản đồ ảnh hưởng
> **Vai trò:** Ghi lại mối quan hệ "nếu sửa X thì Y, Z bị ảnh hưởng". Update sau mỗi fix.
> **Input:** .agent/01_STRUCTURE.md + .agent/03_API_CONTRACT.md + lịch sử fix
> **Output:** Input cho dry_run_{id}.md — AI đọc trước khi đánh giá cascade risk.
> **Rule:** Update bắt buộc sau mỗi fix hoàn thành. Không được để stale quá 1 task.

## Format

```
MODULE: path/to/module
DEPENDS_ON: [list các module mà module này phụ thuộc]
DEPENDED_BY: [list các module phụ thuộc vào module này]
SHARED_CONTRACT: [API/IPC contract liên quan]
LAST_UPDATED: [timestamp][AI-ID]
```

[Nội dung được build dần trong quá trình phát triển]
