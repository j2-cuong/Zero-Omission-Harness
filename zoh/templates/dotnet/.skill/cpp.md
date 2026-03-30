# cpp.md — C++ Skill Base
> **Vai trò:** Rules cứng cho C++ — không phụ thuộc dự án cụ thể.
> **Input:** Không có (kiến thức nền tĩnh)
> **Output:** Được copy + override vào .agent/05_RULES_CPP.md
> **Rule:** Đây là baseline tối thiểu. Dự án chỉ được thêm rule, không được bỏ rule.

## Memory & Handle
- Bắt buộc dùng HandleGuard (RAII) cho mọi HANDLE
- Cấm: strcpy, strcat, sprintf, memcpy → Dùng: StringCchCopyA, memcpy_s
- SecureZeroMemory cho mọi buffer chứa secret sau khi dùng xong

## Threading
- Cấm std::mutex → Dùng CRITICAL_SECTION hoặc SRWLOCK
- Cấm ExitProcess từ thread phụ → Dùng SetEvent báo hiệu
- std::atomic cho flags đơn giản, không trộn với InterlockedExchange

## DLL Safety
- Không thực hiện Network/File/UI trong DllMain
- DLL_PROCESS_DETACH: set running=false → WaitForSingleObject
- Naked function: bảo vệ ECX/EDX trước jmp, dùng pushad/popad

## Build flags bắt buộc
- /GS /MT /O1 /DYNAMICBASE /NXCOMPAT
- Static linking, không phụ thuộc VCRUNTIME.dll

## Interop
- Mọi struct qua P/Invoke: #pragma pack(push, 1)
- Mọi hàm export trả về HRESULT hoặc int error_code
- Cấm ném C++ Exception qua biên giới DLL
