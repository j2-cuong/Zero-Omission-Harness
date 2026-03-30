# .router/03_DOC.md
> **Vai trò:** Điều phối viết documentation — đồng bộ với code, không trùng lặp.
> **Input:** Doc request từ user
> **Output:** Load đúng loại doc cần viết
> **Rule:** Doc không được drift khỏi code — luôn verify với implementation.

---

## Doc Type Detection

| User Request | Doc Type | Output File |
|--------------|----------|-------------|
| `API doc`, `API reference`, `document hàm` | **API Reference** | `.doc/API.md` hoặc auto-generated |
| `kiến trúc`, `architecture`, `sơ đồ` | **Architecture** | `.doc/ARCH.md` + `.map/` |
| `hướng dẫn`, `user guide`, `cách dùng` | **User Guide** | `.doc/USER_GUIDE.md` |
| `dev guide`, `contribute`, `developer` | **Dev Guide** | `.doc/DEV_GUIDE.md` |
| `README`, `overview`, `giới thiệu` | **Overview** | Root `README.md` hoặc `.doc/README.md` |

---

## Context Loading

**Tất cả doc types đều cần:**
1. **`.agent/STATE.md`** — biết phase và current task
2. **`.agent/01_STRUCTURE.md`** — hiểu architecture

**Theo doc type:**

| Doc Type | Files bổ sung |
|----------|---------------|
| API Reference | `.agent/03_API_CONTRACT.md`, `.agent/03_IPC_CONTRACT.md` |
| Architecture | `.agent/01_STRUCTURE.md`, `.map/` (nếu có) |
| User Guide | `.doc/USER_GUIDE.md` skeleton (nếu có) |
| Dev Guide | `.agent/06_BUILD_CONFIG.md`, `.agent/07_COMMON_MISTAKES.md` |

---

## Doc Consistency Rules

Viết doc phải verify:

```yaml
doc_consistency_check:
  - "Mọi API documented phải tồn tại trong code"
  - "Mọi component trong doc phải match .agent/01_STRUCTURE.md"
  - "Mọi code example trong doc phải compile được"
  - "Version trong doc phải match project.version"
  - "Không document feature chưa implement"
```

**Nếu phát hiện drift:** Flag và hỏi user có muốn cập nhật code hay sửa doc.

---

## Doc Generation Flow

```
[Nhận doc request]
    │
    ▼
[Phân loại doc type]
    │
    ▼
Load relevant context
    │
    ▼
Kiểm tra doc hiện tại (nếu có)
    │── Có → Append/Update
    │── Không → Tạo mới
    ▼
Generate doc content
    │
    ▼
Consistency check với code
    │── FAIL → Sửa lại
    │ PASS
    ▼
Ghi vào .doc/ + Update STATE.md
```

---

## Token Budget: Documentation

| Doc Type | Est. Tokens | Notes |
|----------|-------------|-------|
| API Reference (auto-gen) | ~400 | Đọc contracts, generate markdown |
| Architecture Doc | ~600 | Đọc structure, mô tả flow |
| User Guide | ~800 | Cần hiểu use cases |
| Dev Guide | ~600 | Build config + conventions |
| Full doc suite | ~1500 | Tất cả các loại |

---

## Post-Doc Actions

```yaml
post_doc:
  - update: ".agent/STATE.md"
    field: "consistency_flags.doc"
    value: true
    
  - verify: ".doc/" sync với code
    method: "grep check hoặc consistency script"
    
  - append: ".agent/DECISION_LOG.md"
    if: "có quyết định về doc structure"
```

---

## Auto-Generated vs Manual

| Loại | Auto-Generated? | File |
|------|-----------------|------|
| API Reference | Yes (từ contracts) | `.doc/API.md` |
| Architecture Diagram | Yes (từ .map/) | `.doc/ARCH.svg` |
| Build Instructions | Yes (từ BUILD_CONFIG) | `.doc/BUILD.md` |
| User Guide | Manual | `.doc/USER_GUIDE.md` |
| Troubleshooting | Semi-auto | `.doc/TROUBLESHOOTING.md` |

---

*Router này đảm bảo documentation luôn sync với code reality.*
