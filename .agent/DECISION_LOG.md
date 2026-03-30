# DECISION_LOG.md — Nhật ký quyết định kiến trúc
> **Vai trò:** Ghi lại mọi quyết định thiết kế quan trọng. Bảo vệ reasoning trước multi-AI drift.
> **Input:** Được ghi bởi AI khi ra quyết định kiến trúc, chọn approach, hoặc giải quyết conflict.
> **Output:** Context cho AI tiếp theo — không được override quyết định đã có mà không ghi lý do.
> **Rule:** Chỉ được APPEND. Không được xóa entry cũ. Conflict → ghi entry mới + flag CONFLICT.

## Format mỗi entry

```
[YYYY-MM-DD HH:MM] [AI-ID]
DECISION: <tên quyết định>
CONTEXT: <tại sao phải quyết định>
CHOSEN: <phương án được chọn>
REJECTED: <phương án bị loại + lý do>
IMPACT: <file/module nào bị ảnh hưởng>
RISK: <rủi ro nếu quyết định này sai>
```

## Log

[Chưa có entry — sẽ được ghi trong quá trình phát triển]
