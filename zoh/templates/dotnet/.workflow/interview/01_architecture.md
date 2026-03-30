# .workflow/interview/01_architecture.md
> **Tier:** 1 — Components, data flow, concurrency
> **When:** Sau khi Tier 0 hoàn thành
> **Next:** Tier 2 (nếu cần contracts)
> **Token estimate:** ~500

---

## Câu 5: Components/Modules

**Hỏi:** Dự án có những module/component nào? Đặt tên và mô tả ngắn.

**Ví dụ:**
```yaml
components:
  - name: core
    description: "Xử lý logic chính"
  - name: cli
    description: "Command-line interface"
  - name: storage
    description: "Read/write file và database"
```

**Validate:**
- [ ] Ít nhất 1 component
- [ ] Tên hợp lệ `[a-z][a-z0-9_]*`
- [ ] Không trùng tên

---

## Câu 6: Data Flow

**Hỏi:** Luồng dữ liệu chính đi qua những bước nào?

**Ví dụ:**
```
User Input → CLI Parser → Core Engine → Storage → Output
                 ↓
            Validation
```

**Hỏi cụ thể:**
1. Input từ đâu? (user, file, network, sensor...)
2. Qua những bước xử lý gì?
3. Output ra đâu?

**Validate:**
- [ ] Ít nhất 2 bước xử lý
- [ ] Đề cập đến ít nhất 1 component từ Câu 5

---

## Câu 7: Concurrency Model

**Hỏi:** Dự án sử dụng mô hình concurrency nào?

- **single-threaded** — chỉ 1 thread, đơn giản
- **multi-threaded** — nhiều thread, cần đồng bộ
- **async-await** — event loop, không block
- **coroutines** — C++20 coroutines hoặc tương đương

**Nếu multi-threaded:**
- Có shared state không?
- Dùng mutex, lock-free, hay channels?

**Validate:** Phải chọn 1 trong 4

---

## Output sau Tier 1

```yaml
tier: 1
result:
  architecture:
    components: []
    data_flow: ""
    concurrency: "single-threaded|multi-threaded|async|coroutines"
next_tier: 2  # Nếu có contracts cần hỏi
```

**Quyết định tiếp theo:**
- Nếu chỉ 1 component + single-threaded → **Có thể skip Tier 2**
- Nếu multi-component hoặc IPC → **Cần Tier 2**
