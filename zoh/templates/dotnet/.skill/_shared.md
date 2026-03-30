# _shared.md
> **Vai trò:** Rules bất biến chung cho mọi ngôn ngữ trong dự án.
> **Input:** Không có (kiến thức nền tĩnh)
> **Output:** Constraint áp dụng cho tất cả .agent/RULES_*.md
> **Rule:** Không được override file này ở cấp dự án. Muốn thay đổi → đề xuất cập nhật .skill/ gốc.

## Các quy tắc chung bất biến
- File size: Mỗi file tối đa 300 dòng code
- Naming: Tuân thủ convention của từng ngôn ngữ (xem file ngôn ngữ tương ứng)
- Sign-off: Mọi thay đổi phải có [timestamp][AI-ID][action][reason]
- Doc language: Tiếng Việt cho comment nghiệp vụ, tiếng Anh cho technical term
- No God object: Mỗi module có input rõ, output rõ, log riêng
- Zero omission: Không được bỏ sót file nào khi scan
