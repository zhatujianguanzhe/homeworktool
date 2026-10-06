import ctypes
import time
import win32api

user32 = ctypes.WinDLL('user32', use_last_error=True)

UOI_NAME = 2
DESKTOP_ALL = 0x000F01FF

user32.GetUserObjectInformationW.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_uint,
    ctypes.POINTER(ctypes.c_uint)
]
user32.GetUserObjectInformationW.restype = ctypes.c_bool


def GetDesktopName(hdesktop):
    length = ctypes.c_uint()

    user32.GetUserObjectInformationW(
        hdesktop,
        UOI_NAME,
        None,
        0,
        ctypes.byref(length)
    )

    if length.value == 0:
        return None

    buffer = ctypes.create_unicode_buffer(length.value)

    if not user32.GetUserObjectInformationW(
        hdesktop,
        UOI_NAME,
        buffer,
        length.value,
        ctypes.byref(length)
    ):
        return None

    return buffer.value


# 获取 watchdog 启动时所在的 Desktop
original_desktop = user32.GetThreadDesktop(
    win32api.GetCurrentThreadId()
)

original_desktop_name = GetDesktopName(
    original_desktop
)

print("原始 Desktop:", original_desktop,original_desktop_name)

target_desktop_name = "PythonPasswordBoxDesktop"

start_time = None

while True:
    target_desktop = user32.OpenDesktopW(
        target_desktop_name,
        0,
        False,
        DESKTOP_ALL
    )

    if target_desktop:

        if start_time is None:
            start_time = time.time()
            print("检测到新 Desktop，开始计时")

        elif time.time() - start_time >= 10 :
            print("超过 10 秒，强制恢复原 Desktop")

            original_desktop_handle = user32.OpenDesktopW(
                original_desktop_name,
                0,
                False,
                DESKTOP_ALL
            )

            if original_desktop_handle:
                user32.SwitchDesktop(
                    original_desktop_handle
                )

                user32.CloseDesktop(
                    target_desktop
                )

                user32.CloseDesktop(
                    original_desktop_handle
                )

                print("已恢复原 Desktop")

                start_time = None

    else:
        if start_time is not None:
            print("新 Desktop 已消失")
        start_time = None

    time.sleep(1)