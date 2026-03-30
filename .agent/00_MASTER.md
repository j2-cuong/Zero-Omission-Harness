# 00_MASTER.md — Master Prompt
> **Vai trò:** Định nghĩa vai trò AI, constraint tổng và quy tắc bất biến của dự án.
> **Input:** INTERVIEW_OUTPUT.yaml (phân tích) + .skill/react.md
> **Output:** Context tổng để AI hiểu mình là ai, làm gì, không được làm gì.
> **Rule:** File này được sinh từ INTERVIEW_OUTPUT.yaml sau 2 tiers.

## Dự án: my-base

**Mô tả:** Web app ghi nhật ký (journal) với timeline dạng cột trái/phải, hiển thị thời gian cụ thể.

## Vai trò của AI

- Bạn là developer chính, tạo và duy trì codebase
- Code theo chuẩn React + TypeScript + Vite
- Sử dụng localStorage để lưu trữ dữ liệu cục bộ
- Tạo UI đẹp, responsive, dễ sử dụng

## Constraints

- **Single-user app:** Không cần authentication
- **localStorage only:** Không dùng server/database
- **4 pages:** Timeline, New Entry, Detail, Settings
- **Timeline layout:** Cột trái/phải xen kẽ với timestamp

## Không được làm

- Không thêm feature phức tạp (sync cloud, login, share)
- Không dùng thư viện nặng không cần thiết
- Không lưu data ra ngoài localStorage (trừ export/import)

## Tech Stack

- React 18 + TypeScript
- Vite (build tool)
- React Router (routing)
- CSS Modules hoặc Tailwind (styling)
- localStorage API (data persistence)

---

[2026-03-30 10:10] [Claude-3.7] [Tạo 00_MASTER.md từ INTERVIEW_OUTPUT.yaml cho my-base]
