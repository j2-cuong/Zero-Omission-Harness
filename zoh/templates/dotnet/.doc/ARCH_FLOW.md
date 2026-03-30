# ARCH_FLOW.md — Luồng kiến trúc thực tế
> **Vai trò:** Ghi lại luồng dữ liệu và logic thực tế sau khi code — không phải dự định.
> **Input:** Code đã implement + .agent/03_API_CONTRACT.md để đối chiếu
> **Output:** Source of truth về "hệ thống đang chạy như thế nào" — input cho .map/ và .bug/
> **Rule:** Update sau mỗi task hoàn thành. Nếu thực tế khác .agent/ → ghi delta rõ + flag để review.

## Cấu trúc

```
FLOW_ID: flow-{module}-{action}
TRIGGER: Điều gì kích hoạt flow này
STEPS:
  1. Module A làm gì
  2. Gọi Module B với data gì
  3. Module B trả về gì
  4. ...
ACTUAL_VS_PLANNED: Khác gì so với .agent/?
LAST_UPDATED: [timestamp][AI-ID]
```

[Nội dung được build dần sau khi code]
