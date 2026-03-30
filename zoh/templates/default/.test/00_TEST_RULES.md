# 00_TEST_RULES.md — Quy tắc Test Gate
> **Vai trò:** Định nghĩa điều kiện bắt buộc test — gate cứng không thể bypass.
> **Input:** Không có (rule tĩnh)
> **Output:** Checklist AI phải hoàn thành trước khi đánh dấu task DONE.
> **Rule CỨNG:** Không có test → không được merge. Không có memory trace → không được đánh dấu "no leak".

## Test gate theo loại task

| Loại task | Unit test | Integration test | Memory trace | Sim scenario |
|-----------|-----------|-----------------|--------------|--------------|
| Hàm utility | BẮT BUỘC | Không cần | Nếu alloc | Không cần |
| Module mới | BẮT BUỘC | BẮT BUỘC | BẮT BUỘC | Không cần |
| API endpoint | BẮT BUỘC | BẮT BUỘC | Không cần | Không cần |
| Fix bug | Có test cover bug | BẮT BUỘC | Nếu liên quan leak | BẮT BUỘC |
| Refactor | Existing test vẫn pass | BẮT BUỘC | Nếu thay đổi alloc | BẮT BUỘC |

## Format test result

```
TEST_ID: test-{task_id}-{short-desc}
TYPE: unit | integration | memory | scenario
TARGET: path/to/tested/file
STATUS: PASS | FAIL | PENDING
COVERAGE: list các function được cover
NOTES: ghi chú nếu có exception
SIGNED: [AI-ID] [timestamp]
```
