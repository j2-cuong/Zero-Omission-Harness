# react.md — React / Next.js Skill Base
> **Vai trò:** Rules cứng cho React/Next.js — không phụ thuộc dự án cụ thể.
> **Input:** Không có (kiến thức nền tĩnh)
> **Output:** Được copy + override vào .agent/05_RULES_REACT.md
> **Rule:** Đây là baseline tối thiểu. Dự án chỉ được thêm rule, không được bỏ rule.

## API Contract
- Mọi response schema phải được định nghĩa bằng Zod trước khi code
- Key names phải khớp 100% với .agent/03_API_CONTRACT.md — không được tự đặt
- Endpoint path phải khớp với config của Native layer (C++/C#)

## Security
- Không để secret trong client-side code
- Mọi API route có side-effect phải validate HMAC hoặc auth token
- Environment variable: NEXT_PUBLIC_ chỉ cho giá trị thực sự public

## Route Convention
- App Router: mỗi route là folder với page.tsx / route.ts
- API route: validate input bằng Zod, trả về typed response
- Middleware: auth check trước khi vào route handler

## State & Data
- Server Component mặc định, Client Component chỉ khi cần interactivity
- Không fetch trong useEffect nếu có thể dùng Server Component
- Error boundary bắt buộc cho mọi async component
