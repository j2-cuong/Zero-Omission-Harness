# 04_MEMORY_TRACE.md — Memory Trace System
> **Vai trò:** Trace memory lifecycle thực tế — không đoán leak, chạy từ .test/memory/ rồi trace.
> **Input:** .test/memory/ trace results + code C++/C# có alloc/free
> **Output:** Danh sách object với lifecycle rõ ràng — xác định leak có evidence, không phỏng đoán.
> **Rule:** Không được ghi "no memory leak" mà không có trace evidence từ .test/memory/.

## Trace summary

| Object | Allocated at | Freed at | Exception path safe? | Leak risk | Verified |
|--------|-------------|----------|----------------------|-----------|---------|
| — | — | — | — | — | — |

[Nội dung được build từ .test/memory/ trace results]
