# .workflow/interview/00_basic.md
> **Tier:** 0 (Entry) — 4 câu hỏi tối thiểu để khởi động
> **When:** Luôn bắt đầu từ đây
> **Next:** Tier 1 sau khi có đủ thông tin
> **Token estimate:** ~300

---

## Câu 1: Tên dự án

**Hỏi:** Tên dự án là gì? (viết thường, không dấu, không khoảng trắng — dùng làm namespace)

**Ví dụ:** `my_project`, `image_processor`, `data_sync`

**Validate:**
- [ ] Không để trống
- [ ] Chỉ chứa `[a-z0-9_-]`
- [ ] 3-50 ký tự
- [ ] Không trùng reserved keywords

---

## Câu 2: Ngôn ngữ chính

**Hỏi:** Ngôn ngữ lập trình chính là gì?

- **cpp** — C++
- **csharp** — C# / .NET
- **react** — React/TypeScript (web frontend)
- **multi** — kết hợp nhiều ngôn ngữ (sẽ hỏi chi tiết sau)

**Validate:** Phải chọn 1 trong 4

---

## Câu 3: Trạng thái dự án

**Hỏi:** Hiện tại dự án đang ở trạng thái nào?

- **greenfield** — chưa có gì, bắt đầu từ đầu
- **brownfield** — đã có code sẵn, cần mở rộng
- **refactor** — cần refactor codebase cũ

**Nếu brownfield/refactor:** Cần link/path đến code hiện tại

**Validate:** Phải chọn 1 trong 3

---

## Câu 4: Mục đích

**Hỏi:** Dự án này giải quyết vấn đề gì? (1 câu ngắn gọn, rõ ràng)

**Ví dụ tốt:**
- ✅ "Tool đồng bộ file giữa local và cloud storage"
- ✅ "Library xử lý ảnh real-time cho camera"
- ✅ "CLI quản lý database migrations"

**Ví dụ không tốt:**
- ❌ "Một hệ thống" (quá vague)
- ❌ "Ứng dụng web" (chưa nói làm gì)

**Validate:** Tối thiểu 10 từ, không vague

---

## Output sau Tier 0

```yaml
tier: 0
result:
  project:
    name: ""
    state: "greenfield|brownfield|refactor"
    purpose: ""
  languages:
    primary: "cpp|csharp|react|multi"
next_tier: 1
```

**Tiếp theo:** Load `.workflow/interview/01_architecture.md`
