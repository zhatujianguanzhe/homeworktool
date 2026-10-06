import win32api
import win32con
import win32gui
import commctrl
from ctypes import windll, wintypes, WINFUNCTYPE, c_uint

# Timer 相关定义
UINT_PTR = c_uint
TIMERPROC = WINFUNCTYPE(None, wintypes.HWND, wintypes.UINT, UINT_PTR, wintypes.DWORD)
SetTimer = windll.user32.SetTimer
SetTimer.argtypes = [wintypes.HWND, UINT_PTR, wintypes.UINT, TIMERPROC]
SetTimer.restype = UINT_PTR

KillTimer = windll.user32.KillTimer
KillTimer.argtypes = [wintypes.HWND, UINT_PTR]
KillTimer.restype = wintypes.BOOL

ID_TIMER = 1
WC_BUTTON = "Button"


class ProgressBarDemo:
    def __init__(self):
        self.hwndPrgBar = None
        self.hbtn = None
        self.progress = 0
        self.wndproc = {
            win32con.WM_CREATE: self.OnCreate,
            win32con.WM_TIMER: self.OnTimer,
            win32con.WM_COMMAND: self.OnCommand,
            win32con.WM_DESTROY: self.OnDestroy,
        }

    def OnCreate(self, hwnd, msg, wparam, lparam):
        # 初始化 Common Controls（进度条）
        win32gui.InitCommonControlsEx(commctrl.ICC_PROGRESS_CLASS)

        # 创建进度条（带 PBS_SMOOTH，主题下会显示白色高光）
        self.hwndPrgBar = win32gui.CreateWindow(
            commctrl.PROGRESS_CLASS,
            None,
            win32con.WS_CHILD | win32con.WS_VISIBLE | commctrl.PBS_SMOOTH,
            30, 30, 800, 28,
            hwnd, None, None, None
        )

        # 设置范围 0~100
        win32gui.SendMessage(self.hwndPrgBar, commctrl.PBM_SETRANGE, 0, win32api.MAKELONG(0, 100))
        win32gui.SendMessage(self.hwndPrgBar, commctrl.PBM_SETPOS, 0, 0)
        win32gui.SendMessage(self.hwndPrgBar, commctrl.PBM_SETSTEP, 1, 0)

        # 创建按钮
        self.hbtn = win32gui.CreateWindow(
            WC_BUTTON, "开始进度",
            win32con.WS_CHILD | win32con.WS_VISIBLE,
            130, 80, 100, 30,
            hwnd, 1001, None, None
        )

    def OnTimer(self, hwnd, msg, wparam, lparam):
        win32gui.SendMessage(self.hwndPrgBar, commctrl.PBM_STEPIT, 0, 0)
        self.progress += 1
        if self.progress >= 100:
            KillTimer(hwnd, ID_TIMER)
            win32gui.SendMessage(self.hbtn, win32con.WM_SETTEXT, 0, "重新开始")
            self.progress = 0

    def OnCommand(self, hwnd, msg, wparam, lparam):
        if win32api.LOWORD(wparam) == 1001:
            if self.progress == 0:
                win32gui.SendMessage(self.hwndPrgBar, commctrl.PBM_SETPOS, 0, 0)
                SetTimer(hwnd, ID_TIMER, 30, TIMERPROC())  # 30ms 步进
                win32gui.SendMessage(self.hbtn, win32con.WM_SETTEXT, 0, "进行中...")
                self.progress = 1

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        KillTimer(hwnd, ID_TIMER)
        win32gui.PostQuitMessage(0)

    def __call__(self, hwnd, msg, wparam, lparam):
        if msg in self.wndproc:
            self.wndproc[msg](hwnd, msg, wparam, lparam)
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


def main():
    wc = win32gui.WNDCLASS()
    wc.lpszClassName = "PythonProgressBarGlow"
    wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
    wc.hbrBackground = win32gui.GetSysColorBrush(win32con.COLOR_3DFACE)
    wc.lpfnWndProc = ProgressBarDemo()
    wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
    win32gui.RegisterClass(wc)

    hwnd = win32gui.CreateWindow(
        wc.lpszClassName,
        "Win32 进度条 - 白色高光效果",
        win32con.WS_OVERLAPPEDWINDOW | win32con.WS_VISIBLE,
        200, 200, 400, 180,
        0, 0, 0, None
    )

    # 手动触发 WM_CREATE（pywin32 有时不会自动发）
    win32gui.SendMessage(hwnd, win32con.WM_CREATE, 0, 0)

    win32gui.PumpMessages()


if __name__ == "__main__":
    main()