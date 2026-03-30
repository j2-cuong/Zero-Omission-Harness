# API_SPEC.md — API Specification thực tế
> **Vai trò:** Response schema và key names THỰC TẾ đang chạy — không phải contract dự kiến.
> **Input:** Code đã implement (route handlers, controller actions)
> **Output:** Đối chiếu với .agent/03_API_CONTRACT.md — phát hiện drift sớm
> **Rule:** Nếu key name thực tế khác contract → BLOCK build cho đến khi đồng bộ.

## Cấu trúc

```
ENDPOINT: METHOD /path
IMPLEMENTED_IN: path/to/file.cs line X
ACTUAL_REQUEST_SCHEMA: { ... }
ACTUAL_RESPONSE_SCHEMA: { ... }
DELTA_FROM_CONTRACT: Khác gì so với 03_API_CONTRACT.md?
STATUS: IN_SYNC | DRIFT_DETECTED
LAST_UPDATED: [timestamp][AI-ID]
```

[Nội dung được build sau khi code API]
