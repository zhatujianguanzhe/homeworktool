import win32api
import win32con
import win32gui
import win32ui
from datetime import datetime
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)#1禁用,0默认
# 控件 ID
IDC_DATETIME = 1001

class DatePickerDemo:
    def __init__(self):
        self.hInstance = win32api.GetModuleHandle(None)
        self.hwnd = None
        self.hwndDate = None

        # 注册窗口类
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.WndProc
        wc.lpszClassName = "DatePickerDemoClass"
        wc.hInstance = self.hInstance
        wc.hbrBackground = win32con.COLOR_BTNFACE + 1
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        class_atom = win32gui.RegisterClass(wc)

        # 创建主窗口
        self.hwnd = win32gui.CreateWindow(
            class_atom,
            "Win32 日期选择框演示 (Python)",
            win32con.WS_OVERLAPPEDWINDOW | win32con.WS_VISIBLE,
            100, 100, 420, 250,
            0, 0, self.hInstance, None
        )

        # 创建 DateTimePicker 控件 (SysDateTimePick32)
        self.hwndDate = win32gui.CreateWindow(
            "SysDateTimePick32",          # 日期时间选择控件类名
            "",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER |
            0x0004,                      # DTS_SHORTDATEFORMAT (短日期格式)
            50, 60, 200, 28,
            self.hwnd,
            IDC_DATETIME,
            self.hInstance,
            None
        )

        # 创建按钮：获取当前选择的日期
        win32gui.CreateWindow(
            "BUTTON",
            "获取选中日期",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_PUSHBUTTON,
            50, 120, 140, 32,
            self.hwnd,
            1002,
            self.hInstance,
            None
        )

        # 创建静态文本显示结果
        self.hwndLabel = win32gui.CreateWindow(
            "STATIC",
            "当前选中日期：",
            win32con.WS_CHILD | win32con.WS_VISIBLE,
            50, 170, 300, 25,
            self.hwnd,
            1003,
            self.hInstance,
            None
        )

        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(self.hwnd)

    def get_selected_date(self):
        """从 DateTimePicker 获取选中的日期"""
        # SYSTEMTIME 结构
        class SYSTEMTIME:
            def __init__(self):
                self.wYear = 0
                self.wMonth = 0
                self.wDayOfWeek = 0
                self.wDay = 0
                self.wHour = 0
                self.wMinute = 0
                self.wSecond = 0
                self.wMilliseconds = 0

        st = SYSTEMTIME()
        # DTM_GETSYSTEMTIME = 0x1001
        win32gui.SendMessage(self.hwndDate, 0x1001, 0, st)

        return f"{st.wYear}-{st.wMonth:02d}-{st.wDay:02d}"

    def WndProc(self, hwnd, msg, wParam, lParam):
        if msg == win32con.WM_COMMAND:
            control_id = win32api.LOWORD(wParam)
            if control_id == 1002:  # 获取日期按钮
                date_str = self.get_selected_date()
                win32gui.SetWindowText(self.hwndLabel, f"当前选中日期：{date_str}")
                print(f"选中的日期: {date_str}")

        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0

        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

    def run(self):
        # 消息循环
        while True:
            try:
                msg = win32gui.GetMessage(None, 0, 0)
                if msg[0] == 0:  # WM_QUIT
                    break
                win32gui.TranslateMessage(msg[1])
                win32gui.DispatchMessage(msg[1])
            except Exception:
                break

if __name__ == "__main__":
    app = DatePickerDemo()
    app.run()