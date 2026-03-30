# .workflow/interview/04_technology.md
> **Tier:** 4 — Deep technology questions
> **When:** Sau Tier 3 hoặc khi cần hiểu sâu công nghệ
> **Next:** Tier 5 hoặc DONE
> **Token estimate:** ~600

---

## 4.1 Framework & Libraries

**Hỏi:** Dùng framework/libraries nào? Tại sao chọn nó?

**Ví dụ:**
- C++: Qt, Boost, STL, fmt, spdlog, nlohmann/json...
- C#: .NET Core, ASP.NET, Entity Framework, AutoMapper...
- React: Next.js, Redux, React Query, Tailwind...

**Gợi ý thêm nếu user chưa nghĩ đến:**
- Logging library (spdlog, Serilog, winston)
- JSON/XML parsing (nlohmann/json, System.Text.Json)
- Testing framework (Catch2, xUnit, Jest)
- Async/parallel (TBB, TPL, RxJS)

---

## 4.2 Data Storage

**Hỏi:** Lưu trữ dữ liệu như thế nào?

**Các khía cạnh:**
- **Local:** File (JSON, XML, binary, SQLite), Registry, Config files
- **Remote:** Database (SQL/NoSQL), API, Cloud storage
- **Cache:** In-memory, Redis, disk cache
- **Config:** Environment variables, config files, command-line args

**Gợi ý:**
- Có cần migration strategy không?
- Backup/recovery plan?
- Data versioning?

---

## 4.3 Network & Communication

**Hỏi:** Giao tiếp network như thế nào?

**Nếu có network:**
- Protocol: HTTP/HTTPS, WebSocket, gRPC, raw TCP/UDP
- Authentication: API keys, OAuth, JWT, certificates
- Retry strategy: exponential backoff, circuit breaker
- Timeout handling: connect timeout, read timeout

**Gợi ý:**
- Rate limiting (client-side và server-side)
- Connection pooling
- Proxy support

---

## 4.4 Build & Deployment

**Hỏi:** Build và deploy như thế nào?

**Build:**
- Local build: IDE, command line, scripts
- CI/CD: GitHub Actions, Azure DevOps, Jenkins
- Artifacts: executable, library, container image

**Deployment:**
- Target: local machine, server, cloud, mobile, embedded
- Package: installer, zip, container, package manager
- Updates: auto-update, manual, rolling deployment

---

## 4.5 Development Tools

**Hỏi:** Dùng tools gì cho development?

- **IDE/Editor:** VS Code, Visual Studio, Rider, CLion, Vim
- **Debugger:** built-in, GDB, WinDbg, browser dev tools
- **Profiler:** for performance, memory, concurrency
- **Static analysis:** linter, formatter, security scanner
- **Version control:** Git workflow, branching strategy

---

## 4.6 Platform Specific

**Hỏi:** Có yêu cầu platform-specific không?

**Ví dụ:**
- Windows: COM, WinAPI, UWP, WPF
- Linux: systemd, POSIX, kernel modules
- macOS: Cocoa, Swift interoperability
- Cross-platform: abstraction layer cần gì?

---

## Output sau Tier 4

```yaml
tier: 4
result:
  technology:
    frameworks: []        # List libraries chính
    data_storage: {}      # Local/remote/cache strategy
    network: {}           # Protocol, auth, retry
    build_deploy: {}      # CI/CD, packaging
    dev_tools: {}         # IDE, debugger, profiler
    platform_specific: [] # Windows/Linux/macOS specific
next_tier: 5  # Performance
```
