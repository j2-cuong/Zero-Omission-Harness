# 03_API_CONTRACT.md — API Contract (Source of Truth)
> **Vai trò:** Định nghĩa duy nhất và chính thức cho mọi API endpoint, key name, schema.
> **Input:** INTERVIEW_OUTPUT.yaml (phân tích: integration points, auth mechanism)
> **Output:** Contract mà C++, C#, React phải tuân thủ — không được tự đặt key name.
> **Rule CỨNG:** Mọi thay đổi schema PHẢI cập nhật file này TRƯỚC khi code. Không được code rồi mới update contract.

## Format endpoint

```
ENDPOINT: POST /api/example
REQUEST:
  headers: { X-Signature: string }
  body: { key1: type, key2: type }
RESPONSE:
  200: { key1: type, key2: type }
  4xx: { error: string, code: number }
CONSUMER: [C++/worker.cpp, React/components/X.tsx]
PROVIDER: [C#/Controllers/ExampleController.cs]
LAST_UPDATED: [timestamp][AI-ID]
```

[Nội dung được sinh động từ SEED.md]
