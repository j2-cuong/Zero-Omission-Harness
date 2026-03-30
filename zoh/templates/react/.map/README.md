# README.md — Hướng dẫn đọc .map/
> **Vai trò:** Giải thích hệ thống sơ đồ logic text-based — cách đọc, cách cập nhật, quy ước.
> **Input:** Không có (hướng dẫn tĩnh)
> **Output:** Context cho AI và human khi đọc architecture diagrams.

## Text-Based Architecture

Hệ thống `.map/` sử dụng text formats (Mermaid, YAML, ASCII) thay vì binary (SVG/PNG).

**Ưu điểm:**
- Diff được trong Git
- Dễ sửa bằng text editor
- Source of truth rõ ràng
- Export SVG/PNG khi cần (derived output)

## Các File Format

| Format | Extension | Dùng cho |
|--------|-----------|----------|
| Mermaid | `.mmd` | Data flow, sequence diagrams |
| YAML | `.yaml` | Component tree, dependencies |
| ASCII | `.txt` | Call graphs, hierarchy |

## Quy ước trong Mermaid

```mermaid
graph TD
    A[Module/File — Rectangle] --> B{Decision — Diamond}
    B -->|Pass| C[Success]
    B -->|Fail| D[Error]
    
    style C fill:#90EE90    %% Xanh lá = OK
    style D fill:#FFB6C1    %% Hồng nhạt = Error
```

## Cách cập nhật

Mỗi khi code thay đổi, AI phải:
1. Cập nhật `.map/current/*.mmd`, `*.yaml`, `*.txt` tương ứng
2. Nếu thay đổi contract → tạo `.map/diff/v{n}_to_v{n+1}.yaml`
3. Nếu có bug → tạo `.map/refs/BUG-{id}.yaml`

## Rendering (Xuất SVG/PNG khi cần)

```bash
# Mermaid CLI — SVG là OUTPUT, không phải source
mermaid -i .map/current/data_flow.mmd -o docs/diagrams/data_flow.svg
```

**Nguyên tắc:** Text là source of truth. SVG/PNG chỉ là derived output cho presentation.

---

*Xem STRUCTURE.md cho chi tiết về formats và workflow.*
