# .workflow/interview/02_contracts.md
> **Tier:** 2 — API, IPC, P/Invoke (conditional)
> **When:** Nếu multi-component hoặc có communication needs
> **Next:** Tier 3 (optional) hoặc DONE
> **Token estimate:** ~400

---

## Kiểm tra trước khi hỏi

**Nếu** `architecture.components` chỉ có 1 phần tử VÀ `concurrency=single-threaded`:
→ **Skip tier này**, không cần hỏi contracts

---

## Câu 8: Internal API

**Hỏi:** Các module có gọi API của nhau không?

- **no** — các module độc lập
- **yes** — có internal API

**Nếu yes:**
- Định nghĩa ở đâu? (header files, interface classes...)
- Có thể thay đổi API không? (breaking change policy)

---

## Câu 9: External API (Public)

**Hỏi:** Dự án có expose API ra bên ngoài không?

- **none** — không có public API
- **REST** — REST API over HTTP
- **GraphQL** — GraphQL endpoint
- **gRPC** — gRPC services

**Nếu có:**
- Authentication? (API key, OAuth, JWT)
- Rate limiting?

---

## Câu 10: IPC (Inter-Process Communication)

**Hỏi:** Có cần giao tiếp giữa các process/component?

- **none** — không cần
- **named-pipes** — Windows named pipes
- **sockets** — TCP/Unix sockets
- **shared-memory** — shared memory segments
- **gRPC** — gRPC inter-process

**Nếu có:**
- Protocol format? (JSON, Protobuf, MessagePack)
- Message ordering? (at-most-once, at-least-once, exactly-once)

---

## Câu 11: P/Invoke (Native Interop)

**Hỏi:** Có cần gọi native code (C++/C) từ managed code (C#)?

- **none** — không cần
- **csharp-to-cpp** — C# gọi C++
- **cpp-to-csharp** — C++ gọi C#
- **both** — cả hai chiều

**Nếu có:**
- Những API nào cần expose?
- Marshalling strategy?

---

## Output sau Tier 2

```yaml
tier: 2
result:
  contracts:
    internal_api: "yes|no"
    external_api: "none|REST|GraphQL|gRPC"
    ipc: "none|named-pipes|sockets|shared-memory|gRPC"
    pinvoke: "none|csharp-to-cpp|cpp-to-csharp|both"
next_tier: 3  # Nếu cần constraints
```
