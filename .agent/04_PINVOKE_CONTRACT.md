# 04_PINVOKE_CONTRACT.md — P/Invoke & Cross-Language Contract
> **Vai trò:** Mapping type, marshal rule, ownership, constraint cho mọi điểm giao giữa ngôn ngữ.
> **Input:** INTERVIEW_OUTPUT.yaml (phân tích: ngôn ngữ, integration points) + .skill/cpp.md + .skill/csharp.md
> **Output:** Bảng contract cho từng hàm cross-language — lưu vào `.map/current/cross_language.mmd` hoặc `.map/refs/` dạng YAML
> **Rule:** Chỉ tạo nếu có ít nhất 2 ngôn ngữ giao tiếp trực tiếp. Mọi thay đổi → update .map/diff/.

## Format mỗi entry

```
FUNCTION: NativeFunctionName
C++ signature: HRESULT __cdecl Fn(const char* in, int* out)
C# signature:  [DllImport] static extern int Fn(IntPtr in, out int out)
Type mapping:  const char* → IntPtr (Marshal.AllocHGlobal)
Ownership:     Caller allocates, callee reads only, caller frees
Constraint:    Must call on same thread as allocation
Risk:          HIGH — memory leak if FreeHGlobal skipped in exception path
```

[Nội dung được sinh động từ SEED.md]
