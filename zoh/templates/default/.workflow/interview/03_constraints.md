# .workflow/interview/03_constraints.md
> **Tier:** 3 — Performance, Memory, Security (optional)
> **When:** Chỉ khi user có yêu cầu đặc biệt hoặc project rõ ràng cần
> **Next:** DONE → Generate SEED.md
> **Token estimate:** ~400

---

## Kiểm tra trước khi hỏi

**Mặc định:** Skip tier này, để constraints = none

**Chỉ hỏi nếu:**
- User explicit mention performance/memory/security
- Loại project rõ ràng cần (embedded, finance, real-time...)
- Yêu cầu compliance (GDPR, HIPAA...)

---

## Câu 12: Performance Requirements

**Hỏi:** Có yêu cầu performance cụ thể không?

**Ví dụ:**
- Latency: < 100ms cho request X
- Throughput: 10,000 requests/giây
- Startup time: < 2 giây

**Nếu không có cụ thể → để trống**

---

## Câu 13: Memory Constraints

**Hỏi:** Có giới hạn memory không?

- **none** — không giới hạn
- **embedded** — device có RAM hạn chế (bao nhiêu MB?)
- **server** — giới hạn trên server (bao nhiêu GB?)

**Nếu có giới hạn:**
- Giới hạn cụ thể là gì? (ví dụ: 512MB, 2GB)
- Cần custom allocator/memory pool không?

---

## Câu 14: Security Requirements

**Hỏi:** Có xử lý sensitive data không?

**Nếu có:**
- Loại dữ liệu? (PII, credentials, payment info, health data)
- Encryption at-rest? Encryption in-transit?
- Compliance cần đáp ứng? (GDPR, HIPAA, PCI-DSS)

---

## Output sau Tier 3

```yaml
tier: 3
result:
  constraints:
    performance: ""  # hoặc số liệu cụ thể
    memory: "none|embedded|server"
    memory_limit: ""  # nếu có
    security: "none|yes"
    security_compliance: "none|GDPR|HIPAA|PCI-DSS"
next_tier: DONE
```

**Kế tiếp:** Sinh SEED.md từ tất cả các tier
