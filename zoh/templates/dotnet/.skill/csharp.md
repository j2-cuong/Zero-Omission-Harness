# csharp.md — C# Skill Base
> **Vai trò:** Rules cứng cho C# — không phụ thuộc dự án cụ thể.
> **Input:** Không có (kiến thức nền tĩnh)
> **Output:** Được copy + override vào .agent/05_RULES_CSHARP.md
> **Rule:** Đây là baseline tối thiểu. Dự án chỉ được thêm rule, không được bỏ rule.

## Memory & Interop
- Dùng Marshal.AllocHGlobal thay GCHandle.Pinned cho P/Invoke liên tục
- Luôn gọi Marshal.FreeHGlobal trong finally block
- Delegate truyền sang Native phải là biến static hoặc GCHandle.Alloc Normal

## Struct Layout
- Mọi struct qua P/Invoke: [StructLayout(LayoutKind.Sequential, Pack=1, CharSet=CharSet.Ansi)]
- Đồng bộ với #pragma pack(1) bên C++

## Threading & Safety
- Không dùng Thread.Abort → Dùng CancellationToken
- Async/await bắt buộc có ConfigureAwait(false) trong library code
- Không throw exception qua P/Invoke boundary

## TLS & Network
- Không bao giờ bypass certificate validation (ServicePointManager callback luôn trả true = BLOCK)
- HttpClient phải được inject qua DI, không new trực tiếp

## Naming Convention
- PascalCase: class, method, property, event
- camelCase: local variable, parameter
- _camelCase: private field
- IPascalCase: interface
