# CHANGELOG.md — Nhật ký thay đổi
> **Vai trò:** Lịch sử mọi thay đổi có nghĩa — ai sửa gì, lúc nào, tại sao.
> **Input:** Mọi action của AI và người dùng
> **Output:** Audit trail đầy đủ — không bao giờ "không biết tại sao lại như vậy"
> **Rule:** Chỉ APPEND. Không được xóa entry cũ. Format chuẩn bắt buộc.

## Format

```
[YYYY-MM-DD HH:MM] [AI-ID / User]
ACTION: CREATE | MODIFY | FIX | REFACTOR | REVERT
TARGET: path/to/file
SUMMARY: Mô tả ngắn
REASON: Tại sao cần thay đổi
LINKED_BUG: BUG-ID hoặc N/A
LINKED_TASK: TASK-ID
```

[Chưa có entry]
