# 00_MEMORY_TRACE_RULES.md — Quy tắc Memory Trace
> **Vai trò:** Định nghĩa cách trace memory lifecycle — không đoán, chạy rồi trace.
> **Input:** Code C++ / C# có alloc/free
> **Output:** Lifecycle rõ ràng: alloc → use → free → leak? cho từng object
> **Rule:** Không được ghi "no leak" mà không có trace file. Đây là zero-omission cho memory.

## Lifecycle template

```
OBJECT: HandleGuard / IntPtr / malloc block
ALLOCATED_AT: file.cpp:line trong function X
USED_BY: list các function đọc/ghi object này
FREED_AT: file.cpp:line hoặc "destructor" hoặc "MISSING"
LEAK_RISK: LOW | MEDIUM | HIGH
EXCEPTION_PATH: Nếu exception xảy ra ở Y, có free không?
TRACE_VERIFIED: true | false
```
