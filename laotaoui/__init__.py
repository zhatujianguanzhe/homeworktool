#2026-04-30 23:20

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import ctypes,winreg,win32api,win32con,win32gui,os,playsound,pathlib,threading,math,subprocess
from PIL import Image,ImageTk

from pathlib import Path
libresource=str(pathlib.Path(__file__).parent.resolve() / 'libresource')+'/'





def IsDarkMode():
    """
    检查 Windows 10/11 是否启用了深色模式
    返回 True 表示深色模式，False 表示浅色模式
    """
    path = "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
    try:
        # 打开注册表键
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            # AppsUseLightTheme: 1 为浅色，0 为深色
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
    except FileNotFoundError:
        # 如果找不到该键（可能是极老版本的 Windows），默认返回 False
        return False

GWL_EXSTYLE = -20
WS_EX_DLGMODALFRAME = 0x00000001
WM_SETICON = 0x0080
ICON_SMALL = 0
ICON_BIG = 1
user32 = ctypes.windll.user32
DESKTOP_ALL = 0x000F01FF



def SetDarkTitleBar(window,):
    """
    仅适用于 Windows 10 版本 17763+ 和 Windows 11
    """

    try:
        window.update()
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
        get_parent = ctypes.windll.user32.GetParent
        hwnd = get_parent(window.winfo_id())
        rendering_policy = ctypes.c_int(1)
        
        set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
                            ctypes.byref(rendering_policy), 
                            ctypes.sizeof(rendering_policy))

        ctypes.windll.user32.SendMessageW(hwnd, 0x0086, 0, 0) # 先设为非活动
        ctypes.windll.user32.SendMessageW(hwnd, 0x0086, 1, 0) # 再设回活动状态
    except:
        pass






 
HIGHLIGHT='#0078D7' 
DISABLED='#6D6D6D'
GREENLIGHT='#06B025'
LINK='#5353FF'
YELLOWTEXTFG="#FFCC00"
TITLEBAR_ACTIVE='#000000'
TITLEBAR_INACTIVE='#2B2B2B'



if IsDarkMode():
    TITLEBARBG='#000000'
    WINDOWBG='#202020'
    TEXTFG="#f1f1f1"
    SECONDARYTEXTFG='#9B9B9B'
    WIDGETBG="#2b2b2b"
    TEXTBG="#3C3C3C"
    REDTEXTFG="#FF2828"
    BDCOLOR="#616161"
    FULLALPHA=0.4
    HALFALPHA=0.2
else:
    TITLEBARBG='#ffffff'
    WINDOWBG='#f0f0f0'
    TEXTFG="#000000"
    SECONDARYTEXTFG="#2D2D2D"
    WIDGETBG='#f0f0f0'
    TEXTBG="#ffffff"
    REDTEXTFG="#c20000"
    BDCOLOR="#ADADAD"
    FULLALPHA=0.2
    HALFALPHA=0.1
TOASTBG=WINDOWBG





def OpenTouchKeyboard():
    """
    唤起 Windows 现代触控键盘（TabTip / 任务栏右边那个）
    调用一次即可保证打开（已打开则不会关掉，纯唤起）
    """
    tabtip_paths = [
        r"C:\Program Files\Common Files\microsoft shared\ink\TabTip.exe",
        r"C:\Program Files (x86)\Common Files\microsoft shared\ink\TabTip.exe"]
    # 1. 优先用 COM 接口 Toggle（最干净、最符合系统行为）
    try:
        import win32gui
        from ctypes import HRESULT
        from ctypes.wintypes import HWND
        from comtypes import IUnknown, GUID, COMMETHOD
        import comtypes.client
        class ITipInvocation(IUnknown):
            _iid_ = GUID("{37c994e7-432b-4834-a2f7-dce1f13b834b}")
            _methods_ = [
                COMMETHOD([], HRESULT, "Toggle", (['in'], HWND, "hwndDesktop"))
            ]
        comtypes.CoInitialize()
        try:
            tip = comtypes.client.CreateObject(
                "{4ce576fa-83dc-4F88-951c-9d0782b4e376}",
                interface=ITipInvocation
            )
            tip.Toggle(win32gui.GetDesktopWindow())
            return True
        finally:
            comtypes.CoUninitialize()
    except Exception:
        pass  # COM 失败就走下面兜底
    # 2. 兜底：直接启动 TabTip.exe（进程不存在时必须先启动）
    for path in tabtip_paths:
        if Path(path).exists():
            try:
                # 用 start 方式启动，避免阻塞
                subprocess.Popen(
                                    [path],
                                    shell=False,
                                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                                )  
                return True
            except Exception:
                continue
    try:
        os.system(r'start "" "C:\Program Files\Common Files\microsoft shared\ink\TabTip.exe"')
        return True
    except Exception:
        return False




def SetImageTk(tk_widget, img_file_name, img_size=[32,32]):
    img_open = Image.open(img_file_name)
    img_w, img_h = img_open.size
    scale = min(img_size[0] / img_w, img_size[1] / img_h, 1)
    img_open = img_open.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
    
    # 创建 PhotoImage 对象
    img = ImageTk.PhotoImage(img_open)
    
    # 【关键修改】显式地将图像对象绑定到控件的属性上
    # 这样只要控件存在，图像对象就不会被垃圾回收
    tk_widget.config(image=img)
    tk_widget.image = img  # 保持引用
 
def set_image(tk_widget, img_file_name, img_size=[32,32]):
    """严正警告:已经被废弃,绝对不要用,用了就出问题"""
    img_open = Image.open(f"{libresource}/{img_file_name}")
    img_w, img_h = img_open.size
    scale = min(img_size[0] / img_w, img_size[1] / img_h, 1)
    img_open = img_open.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
    img = ImageTk.PhotoImage(img_open)
    tk_widget.config(image=img)
    tk_widget.image = img

def SetDPI(num=1):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(num)#1禁用,0默认
    except:
        pass

def SetParent(parent,child):
    u32=ctypes.windll.user32
    b_back=u32.GetParent(child.winfo_id())
    u32.SetParent(b_back,parent.winfo_id())

def SetExpandedTreeviewRowColor(widget, color1=WIDGETBG, color2=TEXTBG, fore_color=TEXTFG):
    """
    为Treeview设置交替行颜色（仅针对可见/已展开的行）
    :param widget: Treeview实例
    :param color1: 奇数行背景色 (默认WIDGETBG)
    :param color2: 偶数行背景色 (默认TEXTBG)
    """
    # 1. 定义两个标签并配置颜色
    widget.tag_configure('odd_row', background=color1, foreground=fore_color)
    widget.tag_configure('even_row', background=color2, foreground=fore_color)
    
    # 2. 递归获取所有可见（已展开）的节点
    def get_visible_items(parent=''):
        items = []
        for child in widget.get_children(parent):
            items.append(child)
            # 只有当子节点展开时才递归获取
            if widget.item(child, 'open'):
                items.extend(get_visible_items(child))
        return items
    
    # 3. 获取所有可见节点
    visible_items = get_visible_items()
    
    # 4. 遍历所有可见节点，按视觉顺序分配标签
    for index, item in enumerate(visible_items):
        # index 为偶数 -> even_row, index 为奇数 -> odd_row
        tag = 'even_row' if index % 2 == 0 else 'odd_row'
        
        # 获取该节点原有的 tags (避免覆盖其他状态标签)
        current_tags = widget.item(item, 'tags')
        if isinstance(current_tags, str):
            current_tags = (current_tags,)
            
        # 移除旧的颜色标签 (防止重复调用时标签叠加)
        new_tags = [t for t in current_tags if t not in ('odd_row', 'even_row')]
        new_tags.append(tag)
        
        # 重新设置 tags
        widget.item(item, tags=tuple(new_tags))


def GetWorkArea():
    """返回主显示器工作区: (x, y, width, height)"""
    monitor = win32api.MonitorFromPoint((0, 0))
    info = win32api.GetMonitorInfo(monitor)
    left, top, right, bottom = info["Work"]
    return (left, top, right - left, bottom - top)

def LoadFont(font_path, private=True, enumerable=False):
    FR_PRIVATE  = 0x10
    FR_NOT_ENUM = 0x20
    if isinstance(font_path, bytes):
        pathbuf = ctypes.create_string_buffer(font_path)
        AddFontResourceEx = ctypes.windll.gdi32.AddFontResourceExA
    elif isinstance(font_path, str):
        pathbuf = ctypes.create_unicode_buffer(font_path)
        AddFontResourceEx = ctypes.windll.gdi32.AddFontResourceExW
    else:
        raise TypeError('font_path 必须是 str 或 bytes')

    flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
    num_fonts_added = AddFontResourceEx(ctypes.byref(pathbuf), flags, 0)
    return bool(num_fonts_added)

def ConvertPlaceToRelative(widget, parent_width=None, parent_height=None):
    """
    传入一个Tkinter窗口实例，遍历其所有子组件，
    将place布局的绝对位置转换为比例位置。
    """
    # 获取窗口内部所有组件
    widgets = widget.winfo_children()
    
    for widget in widgets:
        # 获取该组件的place布局信息字典
        place_info = widget.place_info()
        
        # 如果组件没有使用place布局，则跳过
        if not place_info:
            # 递归处理子组件的子组件
            ConvertPlaceToRelative(widget)
            continue
            
        # 获取父容器（因为place是相对于父容器定位的）
        parent = widget.nametowidget(widget.winfo_parent())
        
        # 确保父容器已经更新了其几何尺寸，否则winfo_width/height可能返回1
        parent.update_idletasks()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # 如果父容器尺寸还是1（未渲染），给出警告并跳过
        if parent_width <= 1 or parent_height <= 1:
            print(f"警告: 父容器 {parent} 尚未完全渲染，无法准确转换组件 {widget} 的位置。")
            continue

        # 准备新的布局参数字典
        new_place_params = {}
        
        # 1. 处理 X 坐标 -> relx
        if 'x' in place_info and place_info['x']:
            abs_x = float(place_info['x'])
            new_place_params['relx'] = abs_x / parent_width
            new_place_params['x'] = 0  # 清除绝对坐标
            
        # 2. 处理 Y 坐标 -> rely
        if 'y' in place_info and place_info['y']:
            abs_y = float(place_info['y'])
            new_place_params['rely'] = abs_y / parent_height
            new_place_params['y'] = 0  # 清除绝对坐标
            
        # 3. 处理 宽度 -> relwidth
        if 'width' in place_info and place_info['width']:
            abs_w = float(place_info['width'])
            new_place_params['relwidth'] = abs_w / parent_width
            new_place_params['width'] = 0  # 清除绝对宽度
            
        # 4. 处理 高度 -> relheight
        if 'height' in place_info and place_info['height']:
            abs_h = float(place_info['height'])
            new_place_params['relheight'] = abs_h / parent_height
            new_place_params['height'] = 0  # 清除绝对高度

        # 保留原有的 anchor 参数（如果有）
        if 'anchor' in place_info:
            new_place_params['anchor'] = place_info['anchor']

        # 重新应用place布局
        widget.place(**new_place_params)
        
        # 递归处理该组件内部的子组件
        ConvertPlaceToRelative(widget)

def AlphaBlend(foreground_hex, background_hex,foreground_alpha=1.0):
    fg = foreground_hex.lstrip('#').lower()
    bg = background_hex.lstrip('#').lower()

    bg_r = int(bg[0:2], 16)
    bg_g = int(bg[2:4], 16)
    bg_b = int(bg[4:6], 16)

    fg_r = int(fg[0:2], 16)
    fg_g = int(fg[2:4], 16)
    fg_b = int(fg[4:6], 16)

    out_r = round(fg_r * foreground_alpha + bg_r * (1 - foreground_alpha))
    out_g = round(fg_g * foreground_alpha + bg_g * (1 - foreground_alpha))
    out_b = round(fg_b * foreground_alpha + bg_b * (1 - foreground_alpha))

    return "#{:02x}{:02x}{:02x}".format(out_r, out_g, out_b).upper()


def PlaySystemSound(sound_name):
    try:
        registry_path = (fr"AppEvents\Schemes\Apps\.Default\{sound_name}\.Current" )
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,registry_path) as key:
            sound_path, _ = winreg.QueryValueEx(key, "")
        playsound.playsound(sound_path.replace('%SystemRoot%',os.environ["WINDIR"]),block=False)
        return True
    except:
        return False

def get_windows_accent_color():
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
        # 这里的 AccentColor 存储的是 ABGR 格式的十六进制整数
        value, regtype = winreg.QueryValueEx(registry_key, "AccentColor")
        winreg.CloseKey(registry_key)
        
        # 转换为 HEX 格式的 RGB
        # 注册表里是 0xffccaabb -> 对应 BGR 顺序，我们需要提取成 RGB
        b = (value >> 16) & 0xff
        g = (value >> 8) & 0xff
        r = value & 0xff
        return f"#{r:02x}{g:02x}{b:02x}"
    except WindowsError:
        return None

def TkEntryMoveToRightSelectAll(widget):
    # 2. 选中所有文本
    widget.select_range(0, 'end')
    # 3. 将光标移至最右侧（末尾）
    widget.icursor('end')
    # 4. 将可视区域（滚动条/视口）移动到最右侧
    widget.xview_moveto(1.0)

def SetBorder(widget, mode='pack', bd=1, focusbd=1, color=BDCOLOR, focuscolor=HIGHLIGHT):
    current_bd = [bd]          # 用列表方便闭包修改

    def _update_borders(event=None):
        if current_bd[0] <= 0:
            return
        widget.update()
        if mode == 'pack':
            border_top.pack(fill='x', anchor='n', side='top')
            border_bottom.pack(fill='x', anchor='s', side='bottom')
            border_left.pack(fill='y', anchor='w', side='left')
            border_right.pack(fill='y', anchor='e', side='right')
        elif mode == 'place':
            # 强制用绝对坐标，避免相对定位失效
            w = widget.winfo_width()
            h = widget.winfo_height()
            d = current_bd[0]
            if w <= 1 or h <= 1:          # 尺寸尚未真正确定时先跳过
                return
            # 顶/底铺满宽度，左/右不重叠（避免角点变粗）
            border_top.place(x=0, y=0, width=w, height=d)
            border_bottom.place(x=0, y=h-d, width=w, height=d)
            border_left.place(x=0, y=d, width=d, height=h-d)
            border_right.place(x=w-d, y=d, width=d, height=h-d)

    def _focus_in(event=None):
        if focusbd != 0:
            current_bd[0] = focusbd
            for b in (border_top, border_bottom, border_left, border_right):
                b['bg'] = focuscolor
            _update_borders()
        else:
            _hide_borders()

    def _focus_out(event=None):
        if bd != 0:
            current_bd[0] = bd
            for b in (border_top, border_bottom, border_left, border_right):
                b['bg'] = color
            _update_borders()
        else:
            _hide_borders()

    def _hide_borders():
        if mode == 'pack':
            for b in (border_top, border_bottom, border_left, border_right):
                b.pack_forget()
        else:
            for b in (border_top, border_bottom, border_left, border_right):
                b.place_forget()

    # 创建边框 Frame
    border_top    = tk.Frame(widget, height=bd, bg=color)
    border_bottom = tk.Frame(widget, height=bd, bg=color)
    border_left   = tk.Frame(widget, width=bd,  bg=color)
    border_right  = tk.Frame(widget, width=bd,  bg=color)

    # 初始状态
    

    # 关键/尺寸变化时重新定位（关键！）
   # widget.bind('<Configure>', _update_borders, add='+')
    widget.bind('<FocusIn>',  _focus_in,  add='+')
    widget.bind('<FocusOut>', _focus_out, add='+')

    
    _focus_out()


def BindTipWindow(widget, text='', insert_picture_path=None, text_color=TEXTFG,bg=WIDGETBG, width=None, delay=100):
    """
    给任意控件绑定鼠标悬停提示框。

    参数:
        widget: 目标控件
        text: 提示文字
        insert_picture_path: 可选图片路径
        text_color: 文字颜色
        bg: 提示框背景色
        width: 提示框固定宽度（像素）。为 None 时使用 pack 自然布局，宽度由内容决定
        delay: 悬停多久后显示（毫秒）
    """
    if text_color is None:
        try:
            text_color = widget.cget('fg')
        except Exception:
            text_color = 'black'
    if bg is None:
        try:
            bg = widget.cget('bg')
        except Exception:
            bg = '#f0f0f0'

    tip_window = None
    after_id = None

    def destroy_tip(event=None):
        nonlocal tip_window, after_id
        if after_id is not None:
            try:
                widget.after_cancel(after_id)
            except Exception:
                pass
            after_id = None
        if tip_window is not None:
            try:
                tip_window.destroy()
            except Exception:
                pass
            tip_window = None

    def show_tip(event=None):
        nonlocal tip_window
        destroy_tip()

        tip_window = tk.Toplevel(widget)
        tip_window.overrideredirect(True)
        tip_window.resizable(False, False)
        tip_window.attributes('-topmost', True)
        tip_window.configure(bg=bg, bd=0)
        SetBorder(tip_window,color=HIGHLIGHT,bd=2,focusbd=2)
        # 文字标签
        label_kwargs = dict(
            text=text,
            justify='left',
            anchor='nw',
            bg=bg,
            fg=text_color,
            bd=0
        )
        if width is not None:
            label_kwargs['wraplength'] = width - 10

        label_text = tk.Label(tip_window, **label_kwargs)
        label_text.pack(fill='x', expand=True, padx=5, pady=5)

        # 可选图片
        if insert_picture_path is not None:
            try:
                img = Image.open(insert_picture_path)
                if width is not None:
                    max_w = width - 10
                    if img.width > max_w:
                        ratio = max_w / img.width
                        img = img.resize(
                            (int(img.width * ratio), int(img.height * ratio)),
                            Image.LANCZOS
                        )
                photo = ImageTk.PhotoImage(img)
                label_pic = tk.Label(tip_window, image=photo, bg=bg, bd=0)
                label_pic.image = photo
                label_pic.pack(fill='x', expand=True, padx=5, pady=(0, 5))
            except Exception:
                pass

        tip_window.update_idletasks()

        # 计算位置
        x = tip_window.winfo_pointerx() + 12
        y = tip_window.winfo_pointery() + 12
        req_w = tip_window.winfo_reqwidth()
        req_h = tip_window.winfo_reqheight()
        screen_w = tip_window.winfo_screenwidth()
        screen_h = tip_window.winfo_screenheight()

        if x + req_w > screen_w:
            x = tip_window.winfo_pointerx() - req_w - 12
        if x < 0:
            x = 0
        if y + req_h > screen_h:
            y = tip_window.winfo_pointery() - req_h - 12
        if y < 0:
            y = 0

        # width 有值时强制宽度，为 None 时使用内容自然宽度
        if width is not None:
            tip_window.geometry(f'{req_w}x{req_h}+{x}+{y}')
        else:
            tip_window.geometry(f'+{x}+{y}')   # 只定位，宽高由 pack 决定

    def schedule_tip(event=None):
        nonlocal after_id
        destroy_tip()
        after_id = widget.after(delay, show_tip)

    widget.bind('<Enter>', schedule_tip, add='+')
    widget.bind('<Leave>', destroy_tip, add='+')
    widget.bind('<ButtonPress>', destroy_tip, add='+')

    return destroy_tip



"""
#自己的边框
class DButton(tk.Label):
    def __init__(self, master, command=None, text='', default='normal',
                 bg=WIDGETBG, fg=TEXTFG, justify='center',
                 anchor='center', state='normal', takefocus=True,
                 **kw):
        super().__init__(master, **kw)
        self.command = command
        self.bg = bg
        self.fg = fg
        self['fg'] = fg
        self['bg'] = bg
        self['text'] = text
        self['anchor'] = anchor
        self["justify"] = justify
        self._default = default
        self._state = state
        self._takefocus = takefocus          # 记住用户期望的 takefocus
        self['takefocus'] = False if state == 'disabled' else takefocus

        # 将Label的bd永远设置为0
        self['bd'] = 0
        self['relief'] = 'flat'
        self.pack_propagate(False)

        # 创建四个边框Frame
        self._border_top = tk.Frame(self, bg=BDCOLOR,height=1)
        self._border_bottom = tk.Frame(self, bg=BDCOLOR,height=1)
        self._border_left = tk.Frame(self, bg=BDCOLOR,width=1)
        self._border_right = tk.Frame(self, bg=BDCOLOR,width=1)

        # 放置边框Frame
        self._border_top.pack(fill='x',side='top')
        self._border_bottom.pack(fill='x',side='bottom')
        self._border_left.pack(fill='y',side='left')
        self._border_right.pack(fill='y', side='right')

        self._key_pressed = False
        self._pressed_inside = False
        self._hover = False
        self._current_bd = 1  # 当前边框宽度

        self.default_change(self._default)
        self.bind_command()
        self.bind('<Enter>', self.on_enter,add='+')
        self.bind('<Leave>', self.on_leave,add='+')
        self.bind("<KeyPress-space>", self.on_space_press,add='+')
        self.bind("<KeyRelease-space>", self.on_space_release,add='+')
        self.bind('<Tab>', self.on_space_release_esc,add='+')
        self.bind('<FocusIn>', self.refresh_button_look,add='+')
        self.bind('<FocusOut>', self.refresh_button_look,add='+')
        self.bind('<FocusOut>', self.on_space_release,add='+')
        self.bind('<Escape>', self.on_space_release_esc,add='+')

        self.bind('<Configure>', self._on_resize)
        self.refresh_button_look()

        self.bind_default_active()

    def bind_default_active(self,):
        try:
            self.bind_id_return=self.winfo_toplevel().bind('<Return>', self.on_space_press_and_default, add='+')
            self.bind_id_return_release_return=self.winfo_toplevel().bind('<KeyRelease-Return>', self.on_space_release_and_default, add='+')
            return True
        except:
            return False
        
    def unbind_default_active(self,):
        try:
            self.winfo_toplevel().unbind('<Return>', funcid=self.bind_id_return)
            self.winfo_toplevel().unbind('<KeyRelease-Return>',funcid=self.bind_id_return_release_return)
            return True
        except:
            return False

    def _on_resize(self, event):
        
        self._update_border_coords(event.width, event.height)

    def _update_border_coords(self, w=None, h=None):
        if w is None:
            w = self.winfo_width()
        if h is None:
            h = self.winfo_height()
        if w <= 1 or h <= 1:
            return

        bd = self._current_bd

        self._border_top.config(height=bd)
        self._border_top.lift()

        self._border_bottom.config(height=bd)
        self._border_bottom.lift()

        self._border_left.config(width=bd)
        self._border_left.lift()

        self._border_right.config(width=bd)
        self._border_right.lift()

    def on_space_press_and_default(self, event):
        if self.default == 'active':
            self.on_space_press(event)

    def on_space_release_and_default(self, event):
        if self.default == 'active':
            self.on_space_release(event)

    def on_space_release_esc(self, event):
        self.on_space_release(event, focusout=True)

    def __setitem__(self, key, value):
        if key == 'default':
            if self.state == 'disabled':
                self.default = 'normal'
            else:
                self.default = value
        elif key == 'state':
            self.state = value
        elif key == 'command':
            self.command = value
        elif key == 'takefocus':
            self._takefocus = value
            if self.state != 'disabled':
                super().__setitem__('takefocus', value)
            else:
                super().__setitem__('takefocus', False)
        else:
            super().__setitem__(key, value)

    def configure(self, cnf=None, **kw):
        if 'default' in kw:
            new_default = kw.pop('default')
            self.default = new_default

        if 'state' in kw:
            new_state = kw.pop('state')
            self.state = new_state

        if 'bg' in kw:
            self.bg = kw['bg']
        if 'fg' in kw:
            self.fg = kw['fg']
        if 'command' in kw:
            new_command = kw.pop('command')
            self.command = new_command

        if 'takefocus' in kw:
            new_takefocus = kw.pop('takefocus')
            self._takefocus = new_takefocus
            if self.state != 'disabled':
                kw['takefocus'] = new_takefocus
            else:
                kw['takefocus'] = False

       
        if kw or cnf:
            return super().configure(cnf, **kw)

    config = configure

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        if self._default != value:
            self._default = value
            self.default_change(value)

    def default_change(self, value):
        self.refresh_button_look()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            self._state = value
            self.state_change(value)

    def state_change(self, value):
        self.refresh_button_look()

    # 统一外观刷新函数

    def refresh_button_look(self,event=None):
        bg = self.bg
        bd = 1
        border_color = BDCOLOR

        # 检查是否获得焦点
        if self.focus_get() == self:
            border_color = HIGHLIGHT
            
        # 1. 基础 hover 状态 (未按下鼠标)
        if self._hover and not (self._pressed_inside or self._key_pressed):
            bg = AlphaBlend(HIGHLIGHT, self.bg, HALFALPHA)
            border_color = HIGHLIGHT

        # 2. 激活/按下状态 (鼠标在按钮内按下，或键盘空格按下)
        if (self._pressed_inside and self._hover) or self._key_pressed:
            bg = AlphaBlend(HIGHLIGHT, self.bg, FULLALPHA)
            border_color = HIGHLIGHT

        # 3. 特殊状态：鼠标在内部按下后，移到了按钮外部
        elif self._pressed_inside and not self._hover:
            bg = AlphaBlend(HIGHLIGHT, self.bg, HALFALPHA)
            border_color = HIGHLIGHT

        # 4. Default 边框逻辑 (仅在非按下、非悬停时显示 active 粗边框)
        elif self.default == 'active':
            if not self._hover:
                bd = 2
                border_color = HIGHLIGHT
        # 5. 禁用状态 (最高优先级覆盖)
        if self.state == 'disabled':
            bg = AlphaBlend(DISABLED, WIDGETBG, foreground_alpha=0.5)
            border_color = BDCOLOR
            bd = 1

        self._current_bd = bd

        # 更新Label的背景色
        self['bg'] = bg

        # 更新边框Frame的颜色和大小
        self._border_top['bg'] = border_color
        self._border_bottom['bg'] = border_color
        self._border_left['bg'] = border_color
        self._border_right['bg'] = border_color

        # 更新边框Frame的大小
        self._update_border_coords()


    # =========================
    # 事件（仅改状态 + 刷新）
    # =========================
    def on_enter(self, event):
        if self.state != 'disabled':
            self._hover = True
            self.refresh_button_look()

    def on_leave(self, event):
        if self.state != 'disabled':
            self._hover = False
            self.refresh_button_look()

    def on_space_press(self, event):
        if self.state != 'disabled':
            self._key_pressed = True
            self.refresh_button_look()

    def on_space_release(self, event, focusout=False):
        if self.state != 'disabled':
            if self._key_pressed or focusout:
                self._key_pressed = False

                x, y = event.widget.winfo_pointerxy()
                widget = event.widget.winfo_containing(x, y)

                if widget != self:
                    self._hover = False

                if focusout:
                    self._pressed_inside = False

                self.refresh_button_look()

                if self.command and not focusout:
                    self.command()


    def bind_command(self):
        self._pressed_inside = False

        def handle_press(event):
            if self.state != 'disabled':
                self._pressed_inside = True
                self.focus()
                self.refresh_button_look()

        def handle_release(event):
            if self.state != 'disabled':
                x, y = event.widget.winfo_pointerxy()
                widget = event.widget.winfo_containing(x, y)

                _pressed_inside_temp = self._pressed_inside
                self._pressed_inside = False

                self.refresh_button_look()
                if _pressed_inside_temp and widget == self and self.command is not None:
                    self.command()

        self.bind("<Button-1>", handle_press, add='+')
        self.bind("<Button-1>", lambda _: self.focus_set(), add='+')
        self.bind("<ButtonRelease-1>", handle_release)
"""



class DButton(tk.Label):
    """
    深色模式自定义按钮控件（基于 Label + 四边 Frame 边框实现）

    完全兼容原有接口，可直接替换旧版 DButton。
    支持：
        - default: 'normal' / 'active'（激活时显示加粗高亮边框）
        - state:   'normal' / 'disabled'
        - command: 点击/空格/回车（仅 active 时）触发
        - 鼠标悬停、按下、焦点高亮、键盘空格/回车/Escape 行为
        - 动态边框宽度与颜色
    """

    def __init__(self, master, command=None, text='', default='normal',
                 bg=WIDGETBG, fg=TEXTFG, justify='center',
                 anchor='center', state='normal', takefocus=True,
                 **kw):
        super().__init__(master, **kw)

        # ---------- 基础属性 ----------
        self.command = command
        self.bg = bg
        self.fg = fg
        self._default = default
        self._state = state
        self._takefocus = takefocus          # 用户期望的 takefocus 值

        # 初始化 Label 外观
        self['fg'] = fg
        self['bg'] = bg
        self['text'] = text
        self['anchor'] = anchor
        self['justify'] = justify
        self['takefocus'] = False if state == 'disabled' else takefocus
        self['bd'] = 0
        self['relief'] = 'flat'
        self.pack_propagate(False)

        # ---------- 四边边框 Frame ----------
        self._border_top = tk.Frame(self, bg=BDCOLOR, height=1)
        self._border_bottom = tk.Frame(self, bg=BDCOLOR, height=1)
        self._border_left = tk.Frame(self, bg=BDCOLOR, width=1)
        self._border_right = tk.Frame(self, bg=BDCOLOR, width=1)

        self._border_top.pack(fill='x', side='top')
        self._border_bottom.pack(fill='x', side='bottom')
        self._border_left.pack(fill='y', side='left')
        self._border_right.pack(fill='y', side='right')

        # ---------- 内部状态 ----------
        self._key_pressed = False           # 空格键是否正在按下
        self._pressed_inside = False        # 鼠标是否在按钮内按下
        self._hover = False                 # 鼠标是否悬停
        self._current_bd = 1                # 当前边框宽度

        # 初始化外观与事件绑定
        self.default_change(self._default)
        self._bind_events()
        self.refresh_button_look()
        self.bind_default_active()

    # ==================================================================
    # 公共接口（保持与旧版完全兼容）
    # ==================================================================

    def bind_default_active(self):
        """绑定顶级窗口的 Return 键，使 active 按钮响应回车"""
        try:
            top = self.winfo_toplevel()
            self.bind_id_return = top.bind('<Return>', self._on_return_press, add='+')
            self.bind_id_return_release = top.bind('<KeyRelease-Return>', self._on_return_release, add='+')
            return True
        except Exception:
            return False

    def unbind_default_active(self):
        """取消顶级窗口的 Return 键绑定"""
        try:
            top = self.winfo_toplevel()
            top.unbind('<Return>', funcid=self.bind_id_return)
            top.unbind('<KeyRelease-Return>', funcid=self.bind_id_return_release)
            return True
        except Exception:
            return False

    def __setitem__(self, key, value):
        if key == 'default':
            self.default = 'normal' if self.state == 'disabled' else value
        elif key == 'state':
            self.state = value
        elif key == 'command':
            self.command = value
        elif key == 'takefocus':
            self._takefocus = value
            super().__setitem__('takefocus', False if self.state == 'disabled' else value)
        else:
            super().__setitem__(key, value)

    def configure(self, cnf=None, **kw):
        if 'default' in kw:
            self.default = kw.pop('default')
        if 'state' in kw:
            self.state = kw.pop('state')
        if 'bg' in kw:
            self.bg = kw['bg']
        if 'fg' in kw:
            self.fg = kw['fg']
        if 'command' in kw:
            self.command = kw.pop('command')
        if 'takefocus' in kw:
            self._takefocus = kw.pop('takefocus')
            kw['takefocus'] = False if self.state == 'disabled' else self._takefocus

        if kw or cnf:
            return super().configure(cnf, **kw)



    config = configure

    # ---------- 属性：default ----------
    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        if self._default != value:
            self._default = value
            self.default_change(value)

    def default_change(self, value):
        """default 属性变化时刷新外观"""
        self.refresh_button_look()

    # ---------- 属性：state ----------
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            self._state = value
            self.state_change(value)

    def state_change(self, value):
        """state 属性变化时刷新外观，并同步 takefocus"""
        if value == 'disabled':
            super().__setitem__('takefocus', False)
        else:
            super().__setitem__('takefocus', self._takefocus)
        self.refresh_button_look()

    # ==================================================================
    # 外观刷新（核心逻辑）
    # ==================================================================

    def refresh_button_look(self, event=None):
        """
        统一刷新按钮背景色与边框颜色/宽度。
        优先级（从高到低）：
            1. disabled
            2. 按下状态（鼠标在内部或空格键）
            3. 悬停 / 焦点
            4. default == 'active' 时的加粗边框
        """
        bg = self.bg
        bd = 1
        border_color = BDCOLOR

        # 焦点高亮
        if self.focus_get() == self:
            border_color = HIGHLIGHT

        # 1. 悬停（未按下）
        if self._hover and not (self._pressed_inside or self._key_pressed):
            bg = AlphaBlend(HIGHLIGHT, self.bg, HALFALPHA)
            border_color = HIGHLIGHT

        # 2. 按下（鼠标在按钮内或空格键）
        if (self._pressed_inside and self._hover) or self._key_pressed:
            bg = AlphaBlend(HIGHLIGHT, self.bg, FULLALPHA)
            border_color = HIGHLIGHT

        # 3. 鼠标按下后移出按钮
        elif self._pressed_inside and not self._hover:
            bg = AlphaBlend(HIGHLIGHT, self.bg, HALFALPHA)
            border_color = HIGHLIGHT

        # 4. default == 'active' 且非悬停时加粗边框
        elif self.default == 'active' and not self._hover:
            bd = 2
            border_color = HIGHLIGHT

        # 5. 禁用状态（最高优先级）
        if self.state == 'disabled':
            bg = AlphaBlend(DISABLED, WIDGETBG, foreground_alpha=0.5)
            border_color = BDCOLOR
            bd = 1

        self._current_bd = bd
        self['bg'] = bg

        # 更新四边边框颜色
        for border in (self._border_top, self._border_bottom,
                       self._border_left, self._border_right):
            border['bg'] = border_color

        self._update_border_size()

    def _update_border_size(self, w=None, h=None):
        """根据当前 _current_bd 更新四边 Frame 的尺寸"""
        if w is None:
            w = self.winfo_width()
        if h is None:
            h = self.winfo_height()
        if w <= 1 or h <= 1:
            return

        bd = self._current_bd
        self._border_top.config(height=bd)
        self._border_bottom.config(height=bd)
        self._border_left.config(width=bd)
        self._border_right.config(width=bd)

        # 确保边框始终在最上层
        self._border_top.lift()
        self._border_bottom.lift()
        self._border_left.lift()
        self._border_right.lift()

    def _on_resize(self, event):
        """窗口尺寸变化时同步边框尺寸"""
        self._update_border_size(event.width, event.height)

    # ==================================================================
    # 事件绑定与处理
    # ==================================================================

    def _bind_events(self):
        """统一绑定所有交互事件"""
        self.bind('<Enter>', self._on_enter, add='+')
        self.bind('<Leave>', self._on_leave, add='+')
        self.bind('<KeyPress-space>', self._on_space_press, add='+')
        self.bind('<KeyRelease-space>', self._on_space_release, add='+')
        self.bind('<Tab>', self._on_space_release_esc, add='+')
        self.bind('<FocusIn>', self.refresh_button_look, add='+')
        self.bind('<FocusOut>', self.refresh_button_look, add='+')
        self.bind('<FocusOut>', self._on_space_release, add='+')
        self.bind('<Escape>', self._on_space_release_esc, add='+')
        self.bind('<Configure>', self._on_resize)

        # 鼠标按下 / 释放
        self.bind('<Button-1>', self._on_mouse_press, add='+')
        self.bind('<Button-1>', lambda e: self.focus_set(), add='+')
        self.bind('<ButtonRelease-1>', self._on_mouse_release)

    # ---------- 鼠标事件 ----------
    def _on_enter(self, event):
        if self.state != 'disabled':
            self._hover = True
            self.refresh_button_look()

    def _on_leave(self, event):
        if self.state != 'disabled':
            self._hover = False
            self.refresh_button_look()

    def _on_mouse_press(self, event):
        if self.state != 'disabled':
            self._pressed_inside = True
            self.focus()
            self.refresh_button_look()

    def _on_mouse_release(self, event):
        if self.state != 'disabled':
            x, y = event.widget.winfo_pointerxy()
            widget = event.widget.winfo_containing(x, y)

            was_pressed = self._pressed_inside
            self._pressed_inside = False
            self.refresh_button_look()

            if was_pressed and widget == self and self.command is not None:
                self.command()

    # ---------- 键盘空格 / Escape / Tab ----------
    def _on_space_press(self, event):
        if self.state != 'disabled':
            self._key_pressed = True
            self.refresh_button_look()

    def _on_space_release(self, event, focusout=False):
        if self.state != 'disabled':
            if self._key_pressed or focusout:
                self._key_pressed = False

                x, y = event.widget.winfo_pointerxy()
                widget = event.widget.winfo_containing(x, y)
                if widget != self:
                    self._hover = False

                if focusout:
                    self._pressed_inside = False

                self.refresh_button_look()

                if self.command and not focusout:
                    self.command()

    def _on_space_release_esc(self, event):
        """Tab / Escape 时强制释放按下状态（不触发 command）"""
        self._on_space_release(event, focusout=True)

    # ---------- 回车键（仅 default=='active' 时响应） ----------
    def _on_return_press(self, event):
        if self.default == 'active':
            self._on_space_press(event)

    def _on_return_release(self, event):
        if self.default == 'active':
            self._on_space_release(event)


class DCheckbutton(tk.Frame):
    """
    高仿 ttk.Checkbutton (深色扁平风格) 的三态自定义控件
    variable 值: 0=未选, 1=选中, 2=部分选中(树状图)
    """
    def __init__(self, master=None, text="", variable=None, 
                 command=None, state="normal", takefocus=True, **kwargs):
        # 提取属于 Frame 的 kwargs，强制背景色为 WINDOWBG
        frame_kwargs = {k: v for k, v in kwargs.items() 
                        if k in ('padx', 'pady')}
        frame_kwargs['bg'] = WINDOWBG
        super().__init__(master, **frame_kwargs)
        
        # 核心变量与回调 (默认使用 IntVar 以支持 0, 1, 2 三态)
        self._variable = variable if variable is not None else tk.IntVar(value=0)
        self._command = command
        self._text = text
        self._state = state  # 'normal' 或 'disabled'
        self._takefocus = takefocus
        # 直接调用父类 configure 避免 __setitem__ 死循环报错
        super().configure(takefocus=False if state == 'disabled' else takefocus)
        
        self._hover = False
        self._pressed_inside = False # 记录鼠标是否在控件内按下

        # 监听变量变化，以便外部修改 variable 时控件能同步更新
        self._variable.trace_add("write", self._on_var_change)

        # --- 绘制指示器 ---
        self._indicator_size = 13
        self._canvas = tk.Canvas(self, width=self._indicator_size, 
                                 height=self._indicator_size, 
                                 highlightthickness=0, bd=0, bg=WINDOWBG)
        self._canvas.pack(side='left', padx=(0, 6), pady=2)

        # --- 绘制文本 ---
        self._label = tk.Label(self, text=self._text, anchor='w', 
                               bg=WINDOWBG, fg=TEXTFG)
        self._label.pack(side='left', fill='y')

        # --- 绑定事件 ---
        for widget in (self, self._canvas, self._label):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_press)
            widget.bind("<ButtonRelease-1>", self._on_release)


        # 首次绘制
        self.refresh_look()

    def _on_var_change(self, *args):
        """外部变量改变时触发重绘"""
        self.refresh_look()

    def _on_enter(self, event):
        if self._state != "disabled":
            self._hover = True
            self.refresh_look()

    def _on_leave(self, event):
        if self._state != "disabled":
            self._hover = False
            self.refresh_look()

    def _on_press(self, event):
        if self._state != "disabled":
            self._pressed_inside = True
            self.focus_set()
            self.refresh_look()

    def _on_release(self, event):
        if self._state != "disabled":
            # 判断释放时鼠标是否仍在控件内
            x, y = event.widget.winfo_pointerxy()
            target_widget = event.widget.winfo_containing(x, y)
            is_inside = target_widget in (self, self._canvas, self._label)
            
            # 如果按下且在内部释放，则触发选中逻辑
            if self._pressed_inside and is_inside:
                current_val = self._variable.get()
                self._variable.set(0 if current_val == 1 else 1)
                if self._command:
                    self._command()

            # 释放后重置按下状态，并根据是否还在内部更新 hover
            self._pressed_inside = False
            self._hover = is_inside
            self.refresh_look()


    def refresh_look(self):
        """统一外观刷新函数，严格参照 DButton 逻辑"""
        self._canvas.delete("all")
        
        val = self._variable.get()
        is_disabled = self._state == "disabled"
        
        # 默认基础色
        indicator_bg = TEXTBG
        indicator_border = BDCOLOR
        text_color = TEXTFG
        check_mark_color = TEXTFG

        # 1. 禁用状态 (最高优先级覆盖)
        if is_disabled:
            indicator_bg = AlphaBlend(DISABLED, TEXTBG, 0.2)
            indicator_border = DISABLED
            text_color = DISABLED
            check_mark_color = DISABLED
        else:
            # 2. 基础 hover 状态 (未按下鼠标)
            if self._hover and not self._pressed_inside:
                indicator_bg = AlphaBlend(HIGHLIGHT, TEXTBG, HALFALPHA)
                indicator_border = HIGHLIGHT
                # 保持文本颜色不变
                text_color = TEXTFG

            # 3. 激活/按下状态 (鼠标在内部按下)
            if self._pressed_inside and self._hover:
                indicator_border = HIGHLIGHT
                indicator_bg = AlphaBlend(HIGHLIGHT, TEXTBG, FULLALPHA)
                # 勾选标记颜色在按下时保持不变
                check_mark_color = TEXTFG
                text_color = TEXTFG

            # 4. 特殊状态：鼠标在内部按下后，移到了按钮外部
            elif self._pressed_inside and not self._hover:
                indicator_bg = AlphaBlend(HIGHLIGHT, TEXTBG, HALFALPHA)
                indicator_border = HIGHLIGHT
                text_color = TEXTFG

        # 更新文本颜色
        self._label.config(fg=text_color)

        size = self._indicator_size

        # 绘制纯扁平矩形方框
        self._canvas.create_rectangle(
            0, 0, size - 1, size - 1, 
            fill=indicator_bg, 
            outline=indicator_border, 
            width=1
        )
        
        # 绘制内部标记
        if val == 1:
            # 状态 1：实心勾选标记 (拐点够直)
            self._canvas.create_line(
                2.5, size / 2.0 + 0.5, 
                size / 2.0 - 1.5, size - 3, 
                size - 2.5, 2.5, 
                fill=check_mark_color, 
                width=2.0, 
                capstyle=tk.BUTT, 
                joinstyle=tk.BEVEL
            )
        elif val == 2:
            # 状态 2：部分选中(树状图)，框内实心正方形
            pad = 3 # 内部正方形距边框的间距
            self._canvas.create_rectangle(
                pad, pad, size - 1 - pad, size - 1 - pad, 
                fill=check_mark_color, 
                outline=check_mark_color, 
                width=1
            )



    # ------------------- 对外接口 -------------------
    def configure(self, *args, **kwargs):
        # 兼容 Tkinter 底层通过位置参数传值的调用方式 (如 self['key'] = value)
        if args and isinstance(args[0], dict):
            for key, value in args[0].items():
                kwargs[key] = value
            args = ()
        elif len(args) % 2 == 0 and args: # 键值对形式
            for i in range(0, len(args), 2):
                kwargs[args[i]] = args[i+1]
            args = ()
        elif len(args) == 1 and not kwargs: # 查询单个键
            return super().configure(args[0])

        if 'text' in kwargs:
            self._text = kwargs.pop('text')
            self._label.config(text=self._text)
        if 'state' in kwargs:
            self._state = kwargs.pop('state')
            super().configure(takefocus=False if self._state == 'disabled' else self._takefocus)
            self.refresh_look()
        if 'command' in kwargs:
            self._command = kwargs.pop('command')
        if 'variable' in kwargs:
            # 取消旧变量监听
            self._variable.trace_remove("write", self._variable.trace_info()[0][0])
            self._variable = kwargs.pop('variable')
            self._variable.trace_add("write", self._on_var_change)
            self.refresh_look()
        if 'takefocus' in kwargs:
            self._takefocus = kwargs.pop('takefocus')
            super().configure(takefocus=False if self._state == 'disabled' else self._takefocus)
            
        # 剩余参数丢给父类
        super().configure(*args, **kwargs)

    config = configure

    def cget(self, key):
        if key == 'text': return self._text
        if key == 'state': return self._state
        if key == 'variable': return self._variable
        return super().cget(key)

    def invoke(self):
        """模拟点击操作，仅在 0 和 1 之间切换"""
        current_val = self._variable.get()
        self._variable.set(0 if current_val == 1 else 1)
        if self._command:
            self._command()
        self.refresh_look()

    def select(self):
        """程序设定为选中状态 (1)"""
        self._variable.set(1)

    def deselect(self):
        """程序设定为未选状态 (0)"""
        self._variable.set(0)

    def toggle(self):
        """在 0 和 1 之间切换"""
        self.invoke()


class DAlphaButton(tk.Label):
    def __init__(self, master,command=None,text='',default='normal',bg=WINDOWBG,fg=TEXTFG,justify='center',anchor='center',state='normal', **kw):
        super().__init__(master,**kw)
        self.command=command
        self.bg=bg
        self.fg=fg
        self['fg']=fg
        self['bg']=bg
        self['text']=text
        self['anchor']=anchor
        self["justify"]=justify
        self._default = default
        self._state=state
        self['takefocus']=True
        self['bd']=0
        self['relief']='solid'
        self.pack_propagate(False)

        self._key_pressed = False
        self._pressed_inside=False
        self._hover = False   #  新增

        self.default_change(self._default)
        self.bind_command()
        self.bind('<Enter>',self.on_enter)
        self.bind('<Leave>',self.on_leave)
        self.bind("<KeyPress-space>", self.on_space_press)
        self.bind("<KeyRelease-space>", self.on_space_release)
        self.bind('<Tab>',self.on_space_release_esc)
        self.bind('<FocusOut>',self.on_space_release)
        self.bind('<Escape>',self.on_space_release_esc)

        self.refresh_button_look()  #  初始化刷新

        try:
            self.winfo_toplevel().bind('<Return>',self.on_space_press_and_default,add='+')
            self.winfo_toplevel().bind('<KeyRelease-Return>',self.on_space_release_and_default,add='+')
        except:
            pass

    def on_space_press_and_default(self,event):
        if self.default=='active':
            self.on_space_press(event)
    def on_space_release_and_default(self,event):
        if self.default=='active':
            self.on_space_release(event)

    def on_space_release_esc(self,event):
        self.on_space_release(event,focusout=True)

    def __setitem__(self, key, value):
        if key == 'default':
            self.default = value
        elif key=='state':
            self.state = value
        elif key=='command':
            self.command=value
        else:
            super().__setitem__(key, value)


            
    def configure(self, cnf=None, **kw):
        if 'default' in kw:
            new_default = kw.pop('default')
            self.default = new_default
        if 'state' in kw:
            new_state = kw.pop('state')
            self.state = new_state
        if 'bg' in kw:
            self.bg=kw['bg']
        if 'fg' in kw:
            self.fg=kw['fg']
        if 'command' in kw:
            self.command=kw['command']

        if kw or cnf:
            return super().configure(cnf, **kw)

    config = configure

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        if self._default != value:
            self._default = value
            self.default_change(value)

    def default_change(self, value):
       # self.default=value
        self.refresh_button_look()


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            self._state = value
            self.state_change(value)

    def state_change(self, value):
        #self.state=value
        self.refresh_button_look()



    # 统一外观刷新函数

    def refresh_button_look(self):
        bg = self.bg

        # 1. 基础 hover 状态 (未按下鼠标)
        if self._hover and not (self._pressed_inside or self._key_pressed):
            bg = AlphaBlend(HIGHLIGHT, self.bg, HALFALPHA)

        # 2. 激活/按下状态 (鼠标在按钮内按下，或键盘空格按下)
        if (self._pressed_inside and self._hover) or self._key_pressed:
            bg = AlphaBlend(HIGHLIGHT, self.bg, FULLALPHA)

        # 3. 特殊状态：鼠标在内部按下后，移到了按钮外部 (满足你的需求)
        elif self._pressed_inside and not self._hover:
            bg = AlphaBlend(HIGHLIGHT, self.bg, HALFALPHA)



        # 5. 禁用状态 (最高优先级覆盖)
        if self.state == 'disabled':
            bg = AlphaBlend(DISABLED, WIDGETBG, 0.5)
            self['takefocus'] = False
        else:
            self['takefocus'] = True

        self['bg'] = bg

    # =========================
    # 事件（仅改状态 + 刷新）
    # =========================

    def on_enter(self, event):
        if self.state!='disabled':
            self._hover = True
            self.refresh_button_look()

    def on_leave(self,event):
        if self.state!='disabled':
            self._hover = False
            self.refresh_button_look()

    def on_space_press(self, event):
        if self.state!='disabled':
            self._key_pressed = True
            self.refresh_button_look()

    def on_space_release(self, event,focusout=False):
        if self.state!='disabled':
            if self._key_pressed or focusout:
                self._key_pressed = False

                x, y = event.widget.winfo_pointerxy()
                widget = event.widget.winfo_containing(x, y)

                if widget != self:
                    self._hover = False

                if focusout:
                    self._pressed_inside = False   

                self.refresh_button_look()

                if self.command and not focusout:
                    self.command()

    def bind_command(self,):
        self._pressed_inside = False

        def handle_press(event):
            if self.state!='disabled':
                self._pressed_inside = True
                self.focus()
                self.refresh_button_look()

        def handle_release(event):
            if self.state!='disabled':
                x, y = event.widget.winfo_pointerxy()
                widget = event.widget.winfo_containing(x, y)

                _pressed_inside_temp=self._pressed_inside
                self._pressed_inside = False
                
                self.refresh_button_look()
                if _pressed_inside_temp and widget==self and self.command!=None:
                    self.command()

        self.bind("<Button-1>", handle_press,add='+')
        self.bind("<Button-1>",lambda _:self.focus_set(),add='+')
        self.bind("<ButtonRelease-1>", handle_release)


class DToastButton(tk.Label):
    def __init__(self, master,command=None,text='',default='normal',bg=TOASTBG,fg=SECONDARYTEXTFG,justify='center',anchor='center',state='normal', **kw):
        super().__init__(master,**kw)
        self.command=command
        self.bg=bg
        self.fg=fg
        self['fg']=fg
        self['bg']=bg
        self['text']=text
        self['anchor']=anchor
        self["justify"]=justify
        self._default = default
        self._state=state
        self['takefocus']=True
        self['bd']=0
        self['relief']='solid'
        self.pack_propagate(False)

        self._key_pressed = False
        self._pressed_inside=False
        self._hover = False   #  新增

        self.default_change(self._default)
        self.bind_command()
        self.bind('<Enter>',self.on_enter)
        self.bind('<Leave>',self.on_leave)
        self.bind("<KeyPress-space>", self.on_space_press)
        self.bind("<KeyRelease-space>", self.on_space_release)
        self.bind('<Tab>',self.on_space_release_esc)
        self.bind('<FocusOut>',self.on_space_release)
        self.bind('<Escape>',self.on_space_release_esc)

        self.refresh_button_look()  #  初始化刷新

        try:
            self.winfo_toplevel().bind('<Return>',self.on_space_press_and_default,add='+')
            self.winfo_toplevel().bind('<KeyRelease-Return>',self.on_space_release_and_default,add='+')
        except:
            pass

    def on_space_press_and_default(self,event):
        if self.default=='active':
            self.on_space_press(event)
    def on_space_release_and_default(self,event):
        if self.default=='active':
            self.on_space_release(event)

    def on_space_release_esc(self,event):
        self.on_space_release(event,focusout=True)

    def __setitem__(self, key, value):
        if key == 'default':
            self.default = value
        elif key=='state':
            self.state = value
        elif key=='command':
            self.command=value
        else:
            super().__setitem__(key, value)


            
    def configure(self, cnf=None, **kw):
        if 'default' in kw:
            new_default = kw.pop('default')
            self.default = new_default
        if 'state' in kw:
            new_state = kw.pop('state')
            self.state = new_state
        if 'bg' in kw:
            self.bg=kw['bg']
        if 'fg' in kw:
            self.fg=kw['fg']
        if 'command' in kw:
            self.command=kw['command']

        if kw or cnf:
            return super().configure(cnf, **kw)

    config = configure

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        if self._default != value:
            self._default = value
            self.default_change(value)

    def default_change(self, value):
       # self.default=value
        self.refresh_button_look()


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            self._state = value
            self.state_change(value)

    def state_change(self, value):
        #self.state=value
        self.refresh_button_look()



    # 统一外观刷新函数

    def refresh_button_look(self):
        fg = self.fg

        # 1. 基础 hover 状态 (未按下鼠标)
        if self._hover and not (self._pressed_inside or self._key_pressed):
            fg = TEXTFG

        # 2. 激活/按下状态 (鼠标在按钮内按下，或键盘空格按下)
        if (self._pressed_inside and self._hover) or self._key_pressed:
            fg = AlphaBlend(TEXTFG, self.fg, 0.5)

        # 3. 特殊状态：鼠标在内部按下后，移到了按钮外部 (满足你的需求)
        elif self._pressed_inside and not self._hover:
            fg = TEXTFG



        # 5. 禁用状态 (最高优先级覆盖)
        if self.state == 'disabled':
            fg = AlphaBlend(DISABLED, WIDGETBG, 0.5)
            self['takefocus'] = False
        else:
            self['takefocus'] = True

        self['fg'] = fg

    # =========================
    # 事件（仅改状态 + 刷新）
    # =========================

    def on_enter(self, event):
        if self.state!='disabled':
            self._hover = True
            self.refresh_button_look()

    def on_leave(self,event):
        if self.state!='disabled':
            self._hover = False
            self.refresh_button_look()

    def on_space_press(self, event):
        if self.state!='disabled':
            self._key_pressed = True
            self.refresh_button_look()

    def on_space_release(self, event,focusout=False):
        if self.state!='disabled':
            if self._key_pressed or focusout:
                self._key_pressed = False

                x, y = event.widget.winfo_pointerxy()
                widget = event.widget.winfo_containing(x, y)

                if widget != self:
                    self._hover = False

                if focusout:
                    self._pressed_inside = False   

                self.refresh_button_look()

                if self.command and not focusout:
                    self.command()

    def bind_command(self,):
        self._pressed_inside = False

        def handle_press(event):
            if self.state!='disabled':
                self._pressed_inside = True
                self.focus()
                self.refresh_button_look()

        def handle_release(event):
            if self.state!='disabled':
                x, y = event.widget.winfo_pointerxy()
                widget = event.widget.winfo_containing(x, y)

                _pressed_inside_temp=self._pressed_inside
                self._pressed_inside = False
                
                self.refresh_button_look()
                if _pressed_inside_temp and widget==self and self.command!=None:
                    self.command()

        self.bind("<Button-1>", handle_press,add='+')
        self.bind("<Button-1>",lambda _:self.focus_set(),add='+')
        self.bind("<ButtonRelease-1>", handle_release)


'''

class DEntry(tk.Entry):

    def __init__(self, master,bd=1,relief='solid',bg=TEXTBG,fg=TEXTFG,insertbackground=HIGHLIGHT,
                 insertontime=500,insertofftime=500,insertwidth=2,font='TkDefaultFont',
                 disabledforeground=TEXTFG,disabledbackground=AlphaBlend(DISABLED,TEXTBG,foreground_alpha=0.4),
                 readonlybackground=TEXTBG,selectbackground=AlphaBlend(TEXTBG,HIGHLIGHT,0.3),selectforeground=TEXTFG,**kw):
        super().__init__(master,**kw)

        self.config(bd=bd,relief=relief,bg=bg,fg=fg,insertbackground=insertbackground,insertontime=insertontime,
                    font=font,insertwidth=insertwidth,insertofftime=insertofftime,
                    disabledforeground=disabledforeground,disabledbackground=disabledbackground,
                    readonlybackground=readonlybackground,selectbackground=selectbackground,selectforeground=selectforeground,
                    **kw)
    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def configure(self, cnf=None, **kw):
        if kw or cnf:
            return super().configure(cnf, **kw)

    config = configure

class DSpinbox(tk.Frame):
    def __init__(self, master,int_only=True,increment=1,from_=-float('inf'),to=float('inf') , **kw):
        spinbox_keys = ['width', 'font', 'fg', 'bg', 'justify', 'textvariable', 'insertbackground','increment',
                        'from_','to','state']
        spinbox_kwargs = {k: kw.pop(k) for k in list(kw.keys()) if k in spinbox_keys}

        super().__init__(master,**kw)
        self['bd']=1
        self['bg']=WINDOWBG
        self['highlightthickness']=0
        self['relief']='solid'

        self.master=master
        self.int_only=int_only

        # ✅ increment 类型自适应
        self.increment = int(increment) if int_only else float(increment)

        self.from_=from_
        self.to=to

        self.Entry=DEntry(self,)
        self.Entry.config(bd=0,relief='solid',bg=TEXTBG,fg=TEXTFG,
                          insertbackground=HIGHLIGHT,insertontime=500,
                          insertofftime=500,insertwidth=2,font='TkDefaultFont',)
        self.Entry.config(**spinbox_kwargs)

        self.Entry.bind("<MouseWheel>",self.mousewheel)

        vcmd = (self.register(self.on_validate), '%P')
        invcmd = (self.register(self.on_invalid))
        self.Entry.config(validate="key", validatecommand=vcmd, invalidcommand=invcmd)

        self.Entry.bind('<Up>',self.up_number)
        self.Entry.bind('<Down>',self.down_number)

        self.Frame_DButton=tk.Frame(self,bd=0,bg=TEXTBG,)
        self.Frame_DButton.pack(side='right',fill='both',expand=1,)
        self.Entry.pack(side='left',expand=True,fill='both')

        self.DButton_up=DButton(self.Frame_DButton,  text='+',command=self.up_number,width=2)
        self.DButton_up.pack(side='left',fill='both',expand=True,padx=2,pady=2)
        #self.DButton_up.place(x=2,y=2,width=20,height=self.Frame_DButton.winfo_reqheight()/2 - 3)

        self.DButton_down=DButton(self.Frame_DButton, text='-', command=self.down_number,width=2)
        self.DButton_down.pack(side='right',fill='both',expand=True,padx=2,pady=2)
        #self.DButton_down.place(x=2,y=self.Frame_DButton.winfo_reqheight()/2+3,width=20,height=self.Frame_DButton.winfo_reqheight()/2 - 3)

        
        self.Frame_DButton.bind('<Up>',self.up_number)
        self.Frame_DButton.bind('<Down>',self.down_number)
        self.DButton_up.bind('<Up>',self.up_number)
        self.DButton_up.bind('<Down>',self.down_number)
        self.DButton_down.bind('<Up>',self.up_number)
        self.DButton_down.bind('<Down>',self.down_number)

        # ===== 新增：记录最近一次合法值 =====
        self._last_valid_value = self.Entry.get()

        widgets = (
            self,
            self.Entry,
            self.Frame_DButton,
            self.DButton_up,
            self.DButton_down,
        )

        for w in widgets:
            w.bind('<FocusIn>', self._focus_in, add='+')
            w.bind('<FocusOut>', self._focus_out, add='+')

    # ========= 整数验证 =========
    def _is_valid_int(self, s):
        if s == '':
            return True
        if s == '-':
            return True
        if s.startswith('-'):
            return s[1:].isdigit()
        return s.isdigit()

    # ========= 浮点验证 =========
    def _is_valid_float(self, s):
        if s in ('', '-', '.', '-.'):
            return True

        if s.count('.') > 1:
            return False

        if '-' in s[1:]:
            return False

        try:
            float(s)
            return True
        except:
            return False

    # ===== 新增 =====
    def _focus_in(self, event=None):
        text = self.Entry.get()

        try:
            if text == '':
                self._last_valid_value = ''
                return

            if self.int_only:
                value = int(text)
            else:
                value = float(text)

            if self.from_ <= value <= self.to:
                self._last_valid_value = text

        except:
            pass

    # ===== 新增 =====
    def _focus_out(self, event=None):
        self.after_idle(self._check_focus_leave)

    # ===== 新增 =====
    def _check_focus_leave(self):
        focus_widget = self.focus_get()

        # 焦点仍然在 DSpinbox 内部
        if focus_widget is not None:
            w = focus_widget
            while w is not None:
                if w is self:
                    return
                w = w.master

        text = self.Entry.get()

        # ===== 空字符串允许 =====
        if text == '':
            self._last_valid_value = ''
            return

        try:
            if self.int_only:
                value = int(text)
            else:
                value = float(text)

            if not (self.from_ <= value <= self.to):
                raise ValueError

            self._last_valid_value = text

        except:
            win32api.MessageBeep()

            self.delete(0, 'end')
            self.insert('end', self._last_valid_value)

    def up_number(self,beep=True):
        if getattr(self, '_state', 'normal') == 'disabled':
            return

        temp_number=self.Entry.get()

        if temp_number in ('', '-', '.', '-.'):
            new_value = str(self.from_)
        else:
            try:
                num = float(temp_number) if not self.int_only else int(temp_number)
                new_number = num + self.increment

                if self.from_ <= new_number <= self.to:
                    new_value = str(new_number)
                else:
                    new_value = str(self.to)
                    if beep:
                        win32api.MessageBeep()
            except:
                new_value = str(self.from_)

        self.delete(0,'end')
        self.insert('end',new_value)

    def down_number(self,beep=True):
        if getattr(self, '_state', 'normal') == 'disabled':
            return

        temp_number=self.Entry.get()

        if temp_number in ('', '-', '.', '-.'):
            new_value = str(self.from_)
        else:
            try:
                num = float(temp_number) if not self.int_only else int(temp_number)
                new_number = num - self.increment

                if self.from_ <= new_number <= self.to:
                    new_value = str(new_number)
                else:
                    new_value = str(self.from_)
                    if beep:
                        win32api.MessageBeep()
            except:
                new_value = str(self.from_)

        self.delete(0,'end')
        self.insert('end',new_value)

    def __getattr__(self, name):
        return getattr(self.Entry, name)

    def insert(self, index, s):
        s = str(s)
        if self.int_only:
            if self._is_valid_int(s):
                self.Entry['validate']='none'
                self.Entry.insert(index, s)
                self.Entry['validate']='key'
        else:
            if self._is_valid_float(s):
                self.Entry['validate']='none'
                self.Entry.insert(index, s)
                self.Entry['validate']='key'

    def delete(self, first, last=None):
        self.Entry['validate']='none'
        self.Entry.delete(first, last)
        self.Entry['validate']='key'

    def on_validate(self,P):
        if self.int_only:
            return self._is_valid_int(P)
        else:
            return self._is_valid_float(P)

    def on_invalid(self):
        win32api.MessageBeep()

    def mousewheel(self,event):
        if getattr(self, '_state', 'normal') == 'disabled':
            return

        delta = event.delta if hasattr(event, 'delta') else 0

        if delta>0:
            for i in range(int(delta/120)):
                self.up_number(beep=False)
        elif delta<0:
            for i in range(-int(delta/120)):
                self.down_number(beep=False)

class DCombobutton(tk.Frame):
    def __init__(self, master ,values=[],close_list_command=None, **kw):
        self._state = kw.pop('state', 'readonly')
        combobox_keys = ['width', 'font', 'fg', 'bg', 'justify', 'textvariable', 'insertbackground',
                         'invalidcommand','xscrollcommand','state']
        combobox_kwargs = {k: kw.pop(k) for k in list(kw.keys()) if k in combobox_keys}
        super().__init__(master,**kw)
        self['bd']=1
        self['relief']='solid'
        self['bg']=TEXTBG
        self.close_list_command = close_list_command   # ← 新增
        self.values=values
        self.Entry=DEntry(self,)
        self.Entry.config(bd=0,)#state='readonly')
        self.Entry.config(**combobox_kwargs)
        self.DButton_show_list=DAlphaButton(self, text=' ∨ ', command=self.tell_show_list,bd=0,)
        self.DButton_show_list.pack(side='right',fill='y',)
        self.Entry.pack(side='left',expand=1,fill='both')
        self.Entry.bind('<MouseWheel>',self.entry_mousewheel)
        self.Entry.bind('<Up>',self.entry_up)
        self.Entry.bind('<Down>',self.entry_down)
        self.Entry.bind('<space>',self.tell_show_list_space)
        self._apply_state()
    def __setitem__(self, key, value):
        if key == 'state':
            self.state = value
        elif key=='values':
            self.values=value
        else:
            super().__setitem__(key, value)
    @property
    def state(self):
        return self._state
    @state.setter
    def state(self, value):
        if value not in ('normal', 'readonly', 'disabled'):
            raise ValueError("state must be 'normal', 'readonly' or 'disabled'")
        if self._state == value:
            return
        self._state = value
        self._apply_state()
    def _apply_state(self):
        state = self._state
        # Entry
        self.Entry.config(state=state)
        # Button
        if state == 'disabled':
            self.DButton_show_list.config(state='disabled')
        else:
            self.DButton_show_list.config(state='normal')
        # 绑定控制
        self.Entry.unbind('<Button-1>')
        if state == 'readonly':
            # readonly下点击输入框弹出下拉列表，并改变鼠标样式为箭头
            self.Entry.bind('<Button-1>', self.tell_show_list)
            self.Entry.config(cursor='arrow')
        elif state == 'normal':
            # normal下解绑点击弹出列表的事件，让输入框可以正常聚焦和输入，鼠标为文本选择样式
            self.Entry.config(cursor='xterm')
        elif state == 'disabled':
            self.Entry.config(cursor='arrow')
    def entry_up(self,event):
        self.entry_mousewheel(None,keyboard_delta=120)

    def entry_down(self,event):
        self.entry_mousewheel(None,keyboard_delta=-120)

    def entry_mousewheel(self, event, keyboard_delta=0):
        if self._state == 'disabled':
            return
        if keyboard_delta != 0:
            delta = keyboard_delta
        else:
            delta = event.delta

        old_value = self.Entry.get()

        if self.Entry.get() in self.values:
            roll_line = int(delta / 120)
            index_present_value = self.values.index(self.Entry.get())
            index_new_value = index_present_value - roll_line
            if index_new_value + 1 > len(self.values):
                index_new_value = len(self.values) - 1
            if index_new_value < 0:
                index_new_value = 0
            self.Entry['state'] = 'normal'
            self.Entry.delete(0, 'end')
            self.Entry.insert(0, self.values[index_new_value])
            self.Entry['state'] = self._state
        elif delta > 0 and self.values:
            self.Entry['state'] = 'normal'
            self.Entry.delete(0, 'end')
            self.Entry.insert(0, self.values[-1])
            self.Entry['state'] = self._state
        elif delta < 0 and self.values:
            self.Entry['state'] = 'normal'
            self.Entry.delete(0, 'end')
            self.Entry.insert(0, self.values[0])
            self.Entry['state'] = self._state

        # 值确实变化时触发
        if self.close_list_command and self.Entry.get() != old_value:
            self.close_list_command()

    def configure(self, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        if 'state' in kw: 
            self.state = kw.pop('state')
        if 'values' in kw:
            self.values = kw.pop('values')
        if 'bg' in kw:
            self.bg=kw['bg']
            self.Entry.config(bg=kw['bg'])
        if 'fg' in kw:
            self.fg=kw['fg']
            self.Entry.config(fg=kw['fg'])
        return super().configure(cnf, **kw)
    config = configure
    def tell_show_list(self,event=None):
        if self._state == 'disabled':
            return
        try:
            if self.Toplevel_listwindow.winfo_class()=='Toplevel_listwindow':
                self.close_window_animation()
            else:
                self.show_list()
        except:
            self.show_list()
    def tell_show_list_space(self,event=None):
        if self._state in ['normal','disabled']:
            return
        else:
            self.tell_show_list()


    def show_list(self):
        def close_window_animation():
            self.DButton_show_list.config(text=' ∨ ',)
            self.Entry.focus()
            self.Toplevel_listwindow.destroy()
        self.close_window_animation=close_window_animation
        def open_window_animation():
            self.DButton_show_list.config(text=' ∧ ',) 
            self.Toplevel_listwindow.geometry('%dx%d'%(self.winfo_width(),self.Toplevel_listwindow.winfo_reqheight()))
        self.open_window_animation=open_window_animation
        def close_Toplevel_listwindow(event=None):
            x, y = self.winfo_pointerxy()
            widget = self.winfo_containing(x, y)
            if self._state=='readonly':
                if  (widget not in [self.DButton_show_list,self.Entry] ) or (event and event.keysym=='Escape'):
                    close_window_animation()
            elif self._state=='normal':
                if  widget != self.DButton_show_list or (event and event.keysym=='Escape'):
                    close_window_animation()
            else:
                close_window_animation()
        def close_Toplevel_listwindow_escape(event=None):
            close_window_animation()
        self.DButton_show_list.config(text=' ∧ ')
        self.Toplevel_listwindow=tk.Toplevel(self,class_='Toplevel_listwindow')
        self.Toplevel_listwindow.resizable(0,0)
        self.Toplevel_listwindow.overrideredirect(True)
        self.Toplevel_listwindow['bd']=0
        self.Toplevel_listwindow["highlightthickness"]=0
        self.Toplevel_listwindow['bg']=TEXTBG
        self.Toplevel_listwindow.focus()
        self.Toplevel_listwindow.attributes('-topmost',True)
        self.Toplevel_listwindow.bind('<FocusOut>',close_Toplevel_listwindow)
        self.Toplevel_listwindow.bind('<Escape>',close_Toplevel_listwindow_escape)
        List_values=tk.Listbox(self.Toplevel_listwindow,bd=1,relief='solid',bg=TEXTBG,highlightthickness=0,fg=TEXTFG,
                               activestyle='none',selectmode='browse',exportselection=0,selectbackground=AlphaBlend(HIGHLIGHT,TEXTBG,0.5),
                               selectforeground=TEXTFG,height=len(self.values))
        for value in self.values:
            List_values.insert('end',str(value))
        if self.Entry.get() in self.values:
            try:
                index = self.values.index(self.Entry.get())
                List_values.selection_clear(0, tk.END)
                List_values.selection_set(index)
                List_values.see(index)
                List_values.activate(index)
            except:
                pass
        List_values.pack(fill='both',expand=True)
        List_values.update()
        List_values.focus()
        def update_text_entry(event=None):
            selected_indices = List_values.curselection()
            if selected_indices:
                old_value = self.Entry.get()
                new_value = List_values.get(selected_indices[0])
                self.Entry['state'] = 'normal'
                self.Entry.delete(0, 'end')
                self.Entry.insert(0, new_value)
                self.Entry['state'] = self._state
                close_Toplevel_listwindow()
                # 列表关闭且新值与关闭前不同才触发
                if self.close_list_command and new_value != old_value:
                    self.close_list_command()
        self.Toplevel_listwindow.bind('<space>',update_text_entry)
        List_values.bind('<ButtonRelease-1>',update_text_entry)
        List_values.bind('<Return>',update_text_entry)
        self.Toplevel_listwindow.geometry('%dx0+%d+%d'%(self.winfo_width(),self.winfo_rootx(),self.winfo_rooty()+self.winfo_height()))
        open_window_animation()
        self.Toplevel_listwindow.wait_window(self.Toplevel_listwindow)
    def __getattr__(self, name):
        return getattr(self.Entry, name)


'''



#自己的边框
class DEntry(tk.Entry):
    def __init__(self, master,
                 bd=1, relief='solid',
                 bg=TEXTBG, fg=TEXTFG,
                 insertbackground=HIGHLIGHT,
                 insertontime=500, insertofftime=500, insertwidth=2,
                 font='TkDefaultFont',
                 disabledforeground=TEXTFG,
                 disabledbackground=AlphaBlend(DISABLED, TEXTBG, foreground_alpha=0.4),
                 readonlybackground=TEXTBG,
                 selectbackground=AlphaBlend(TEXTBG, HIGHLIGHT, 0.3),
                 selectforeground=TEXTFG,
                 border=True,          # 内部使用时传 False
                 border_color=BDCOLOR,
                 **kw):
        # 先把用户可能传的 bd/relief 拿走，永远强制 0
        kw.pop('bd', None)
        kw.pop('relief', None)
        super().__init__(master, **kw)

        self._border = border
        self._border_color = border_color
        self._current_bd = 1
        self._focus = False

        # 永远强制
        super().configure(
            bd=0, relief='flat',
            bg=bg, fg=fg,
            insertbackground=insertbackground,
            insertontime=insertontime, insertofftime=insertofftime,
            insertwidth=insertwidth, font=font,
            disabledforeground=disabledforeground,
            disabledbackground=disabledbackground,
            readonlybackground=readonlybackground,
            selectbackground=selectbackground,
            selectforeground=selectforeground
        )

        # DEntry 本身就是输入框，保证可聚焦（容器类控件的焦点应落到其子 Entry）
        try:
            if str(self.cget('state')) != 'disabled':
                self.configure(takefocus=1)
        except Exception:
            pass

        if self._border:
            self._create_borders()
            self.bind('<Configure>', self._on_resize, add='+')
            self.bind('<FocusIn>', self._on_focus_in, add='+')
            self.bind('<FocusOut>', self._on_focus_out, add='+')
            self._update_border_coords()
            self._update_border_color()

    def _create_borders(self):
        self._border_top = tk.Frame(self, bg=self._border_color, height=1)
        self._border_bottom = tk.Frame(self, bg=self._border_color, height=1)
        self._border_left = tk.Frame(self, bg=self._border_color, width=1)
        self._border_right = tk.Frame(self, bg=self._border_color, width=1)

        # 用 place 叠在四边，不干扰 Entry 内部文本区域
        self._border_top.pack(side='top',fill='x')
        self._border_bottom.pack(side='bottom',fill='x')
        self._border_left.pack(side='left',fill='y')
        self._border_right.pack(side='right',fill='y')

    def _on_resize(self, event):
        self._update_border_coords(event.width, event.height)

    def _update_border_coords(self, w=None, h=None):
        if not self._border:
            return
        if w is None:
            w = self.winfo_width()
        if h is None:
            h = self.winfo_height()
        if w <= 1 or h <= 1:
            return
        bd = self._current_bd
        self._border_top.config(height=bd)
        self._border_bottom.config( height=bd)
        self._border_left.config(width=bd)
        self._border_right.config(width=bd)

    def _on_focus_in(self, event=None):
        self._focus = True
        self._update_border_color()

    def _on_focus_out(self, event=None):
        self._focus = False
        self._update_border_color()

    def _update_border_color(self):
        if not self._border:
            return
        color = HIGHLIGHT if self._focus else self._border_color
        for b in (self._border_top, self._border_bottom,
                  self._border_left, self._border_right):
            b['bg'] = color

    def set_border_color(self, color):
        self._border_color = color
        self._update_border_color()

    # ---------- 强制 bd 永远为 0，防止外部再改 ----------
    def __setitem__(self, key, value):
        if key in ('bd', 'borderwidth'):
            value = 0
        elif key == 'relief':
            value = 'flat'
        super().__setitem__(key, value)

    def configure(self, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        # 合并
        if isinstance(cnf, dict):
            kw.update(cnf)
        if 'bd' in kw or 'borderwidth' in kw:
            kw['bd'] = 0
            kw.pop('borderwidth', None)
        if 'relief' in kw:
            kw['relief'] = 'flat'
        if kw:
            return super().configure(**kw)

    config = configure

#自己的边框
class DCombobutton(tk.Frame):
    def __init__(self, master, values=[], close_list_command=None, **kw):
        self._state = kw.pop('state', 'readonly')
        combobox_keys = ['width', 'font', 'fg', 'bg', 'justify', 'textvariable',
                         'insertbackground', 'invalidcommand', 'xscrollcommand', 'state']
        combobox_kwargs = {k: kw.pop(k) for k in list(kw.keys()) if k in combobox_keys}

        super().__init__(master, **kw)

        # 自身边框强制 0
        self['bd'] = 0
        self['relief'] = 'flat'
        self['highlightthickness'] = 0
        self['bg'] = TEXTBG

        self.close_list_command = close_list_command
        self.values = list(values)
        self._current_bd = 1
        self._border_color = BDCOLOR
        self._focus = False

        # 四个边框
        self._border_top = tk.Frame(self, bg=BDCOLOR, height=1)
        self._border_bottom = tk.Frame(self, bg=BDCOLOR, height=1)
        self._border_left = tk.Frame(self, bg=BDCOLOR, width=1)
        self._border_right = tk.Frame(self, bg=BDCOLOR, width=1)

        self._border_top.pack(fill='x', side='top')
        self._border_bottom.pack(fill='x', side='bottom')
        self._border_left.pack(fill='y', side='left')
        self._border_right.pack(fill='y', side='right')

        # 内部 Entry 关闭自身边框
        self.Entry = DEntry(self, border=False)
        self.Entry.config(bd=0, **combobox_kwargs)

        self.DButton_show_list = DAlphaButton(self, text='  ∨  ', command=self.tell_show_list, bd=0,bg=TEXTBG)
        self.DButton_show_list.pack(side='right', fill='y')
        self.Entry.pack(side='left', expand=1, fill='both')

        self.Entry.bind('<MouseWheel>', self.entry_mousewheel)
        self.Entry.bind('<Up>', self.entry_up)
        self.Entry.bind('<Down>', self.entry_down)
        self.Entry.bind('<space>', self.tell_show_list_space)

        # 容器本身不参与 Tab 焦点，焦点交给内部 Entry
        try:
            self.configure(takefocus=0)
        except Exception:
            pass
        try:
            self.Entry.configure(takefocus=1)
        except Exception:
            pass
        try:
            self.DButton_show_list.configure(takefocus=0)
        except Exception:
            pass

        self.bind('<Configure>', self._on_resize, add='+')
        self.bind('<FocusIn>', self._on_focus_in, add='+')
        self.bind('<FocusOut>', self._on_focus_out, add='+')
        self.Entry.bind('<FocusIn>', self._on_focus_in, add='+')
        self.Entry.bind('<FocusOut>', self._on_focus_out, add='+')
        self.DButton_show_list.bind('<FocusIn>', self._on_focus_in, add='+')
        self.DButton_show_list.bind('<FocusOut>', self._on_focus_out, add='+')

        self._apply_state()
        self._update_border_coords()

    def _on_resize(self, event):
        self._update_border_coords(event.width, event.height)

    def _update_border_coords(self, w=None, h=None):
        if w is None:
            w = self.winfo_width()
        if h is None:
            h = self.winfo_height()
        if w <= 1 or h <= 1:
            return
        bd = self._current_bd
        self._border_top.config(height=bd)
        self._border_bottom.config(height=bd)
        self._border_left.config(width=bd)
        self._border_right.config(width=bd)

    def _update_border_color(self):
        color = HIGHLIGHT if self._focus else self._border_color
        for b in (self._border_top, self._border_bottom,
                  self._border_left, self._border_right):
            b['bg'] = color

    def set_border_color(self, color):
        self._border_color = color
        self._update_border_color()

    def _on_focus_in(self, event=None):
        # 若焦点落在容器 Frame 上，立刻转给内部 Entry
        if event is not None and getattr(event, 'widget', None) is self:
            try:
                self.Entry.focus_set()
            except Exception:
                pass
            return
        self._focus = True
        self._update_border_color()

    def _on_focus_out(self, event=None):
        # 简单处理：焦点真正离开整个控件才变回
        self.after_idle(self._check_focus_leave)

    def _check_focus_leave(self):
        focus_widget = self.focus_get()
        if focus_widget is not None:
            w = focus_widget
            while w is not None:
                if w is self:
                    return
                w = getattr(w, 'master', None)
        self._focus = False
        self._update_border_color()

    # ---------- 原有 state / values / 列表逻辑保持不变 ----------
    def __setitem__(self, key, value):
        if key == 'state':
            self.state = value
        elif key == 'values':
            self.values = value
        else:
            super().__setitem__(key, value)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value not in ('normal', 'readonly', 'disabled'):
            raise ValueError("state must be 'normal', 'readonly' or 'disabled'")
        if self._state == value:
            return
        self._state = value
        self._apply_state()

    def _apply_state(self):
        state = self._state
        self.Entry.config(state=state)
        if state == 'disabled':
            self.DButton_show_list.config(state='disabled')
        else:
            self.DButton_show_list.config(state='normal')
        self.Entry.unbind('<Button-1>')
        if state == 'readonly':
            self.Entry.bind('<Button-1>', self.tell_show_list)
            self.Entry.config(cursor='arrow')
        elif state == 'normal':
            self.Entry.config(cursor='xterm')
        elif state == 'disabled':
            self.Entry.config(cursor='arrow')

    def entry_up(self, event):
        self.entry_mousewheel(None, keyboard_delta=120)

    def entry_down(self, event):
        self.entry_mousewheel(None, keyboard_delta=-120)

    def entry_mousewheel(self, event, keyboard_delta=0):
        if self._state == 'disabled':
            return
        if keyboard_delta != 0:
            delta = keyboard_delta
        else:
            delta = event.delta
        old_value = self.Entry.get()
        if self.Entry.get() in self.values:
            roll_line = int(delta / 120)
            index_present_value = self.values.index(self.Entry.get())
            index_new_value = index_present_value - roll_line
            if index_new_value + 1 > len(self.values):
                index_new_value = len(self.values) - 1
            if index_new_value < 0:
                index_new_value = 0
            self.Entry['state'] = 'normal'
            self.Entry.delete(0, 'end')
            self.Entry.insert(0, self.values[index_new_value])
            self.Entry['state'] = self._state
        elif delta > 0 and self.values:
            self.Entry['state'] = 'normal'
            self.Entry.delete(0, 'end')
            self.Entry.insert(0, self.values[-1])
            self.Entry['state'] = self._state
        elif delta < 0 and self.values:
            self.Entry['state'] = 'normal'
            self.Entry.delete(0, 'end')
            self.Entry.insert(0, self.values[0])
            self.Entry['state'] = self._state
        if self.close_list_command and self.Entry.get() != old_value:
            self.close_list_command()

    def configure(self, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        if 'state' in kw:
            self.state = kw.pop('state')
        if 'values' in kw:
            self.values = kw.pop('values')
        if 'bg' in kw:
            self.bg = kw['bg']
            self.Entry.config(bg=kw['bg'])
        if 'fg' in kw:
            self.fg = kw['fg']
            self.Entry.config(fg=kw['fg'])
        return super().configure(cnf, **kw)

    config = configure

    def tell_show_list(self, event=None):
        if self._state == 'disabled':
            return
        try:
            if self.Toplevel_listwindow.winfo_class() == 'Toplevel_listwindow':
                self.close_window_animation()
            else:
                self.show_list()
        except:
            self.show_list()

    def tell_show_list_space(self, event=None):
        if self._state in ['normal', 'disabled']:
            return
        else:
            self.tell_show_list()

    def show_list(self):
        def close_window_animation():
            self.DButton_show_list.config(text='  ∨  ')
            self.Entry.focus()
            self.Toplevel_listwindow.destroy()
        self.close_window_animation = close_window_animation

        def open_window_animation():
            self.DButton_show_list.config(text='  ∧  ')
            self.Toplevel_listwindow.geometry('%dx%d' % (
                self.winfo_width(), self.Toplevel_listwindow.winfo_reqheight()))
        self.open_window_animation = open_window_animation

        def close_Toplevel_listwindow(event=None):
            x, y = self.winfo_pointerxy()
            widget = self.winfo_containing(x, y)
            if self._state == 'readonly':
                if (widget not in [self.DButton_show_list, self.Entry]) or (event and event.keysym == 'Escape'):
                    close_window_animation()
            elif self._state == 'normal':
                if widget != self.DButton_show_list or (event and event.keysym == 'Escape'):
                    close_window_animation()
            else:
                close_window_animation()

        def close_Toplevel_listwindow_escape(event=None):
            close_window_animation()

        self.DButton_show_list.config(text='  ∧  ')
        self.Toplevel_listwindow = tk.Toplevel(self, class_='Toplevel_listwindow')
        self.Toplevel_listwindow.resizable(0, 0)
        self.Toplevel_listwindow.overrideredirect(True)
        self.Toplevel_listwindow['bd'] = 0
        self.Toplevel_listwindow["highlightthickness"] = 0
        self.Toplevel_listwindow['bg'] = TEXTBG
        self.Toplevel_listwindow.focus()
        self.Toplevel_listwindow.attributes('-topmost', True)
        self.Toplevel_listwindow.bind('<FocusOut>', close_Toplevel_listwindow)
        self.Toplevel_listwindow.bind('<Escape>', close_Toplevel_listwindow_escape)

        List_values = tk.Listbox(self.Toplevel_listwindow, bd=1, relief='solid', bg=TEXTBG,
                                 highlightthickness=0, fg=TEXTFG,font=self.Entry['font'],
                                 activestyle='none', selectmode='browse', exportselection=0,
                                 selectbackground=AlphaBlend(HIGHLIGHT, TEXTBG, 0.5),
                                 selectforeground=TEXTFG, height=min(len(self.values),15))
        for value in self.values:

            List_values.insert('end', str(value))
        if self.Entry.get() in self.values:
            try:
                index = self.values.index(self.Entry.get())
                List_values.selection_clear(0, 'end')
                List_values.selection_set(index)
                List_values.see(index)
                List_values.activate(index)
            except:
                pass
        List_values.pack(fill='both', expand=True,side='left')


        scrollbar_y=DScrollbar(self.Toplevel_listwindow,command=List_values.yview,width=20)
        scrollbar_y.pack(fill='y',side='right')
        List_values.config(yscrollcommand=scrollbar_y.set)

        
        List_values.update()
        List_values.focus()


        def update_text_entry(event=None):
            selected_indices = List_values.curselection()
            if selected_indices:
                old_value = self.Entry.get()
                new_value = List_values.get(selected_indices[0])
                self.Entry['state'] = 'normal'
                self.Entry.delete(0, 'end')
                self.Entry.insert(0, new_value)
                self.Entry['state'] = self._state
                close_Toplevel_listwindow()
                if self.close_list_command and new_value != old_value:
                    self.close_list_command()

        self.Toplevel_listwindow.bind('<space>', update_text_entry)
        List_values.bind('<ButtonRelease-1>', update_text_entry)
        List_values.bind('<Return>', update_text_entry)
        self.Toplevel_listwindow.geometry('%dx0+%d+%d' % (
            self.winfo_width(), self.winfo_rootx(), self.winfo_rooty() + self.winfo_height()))
        open_window_animation()
        self.Toplevel_listwindow.wait_window(self.Toplevel_listwindow)

    def __getattr__(self, name):
        return getattr(self.Entry, name)

#自己的边框
class DSpinbox(tk.Frame):
    def __init__(self, master, int_only=True, increment=1,
                 from_=-float('inf'), to=float('inf'), **kw):
        spinbox_keys = ['width', 'font', 'fg', 'bg', 'justify', 'textvariable',
                        'insertbackground', 'increment', 'from_', 'to', 'state']
        spinbox_kwargs = {k: kw.pop(k) for k in list(kw.keys()) if k in spinbox_keys}

        super().__init__(master, **kw)

        # 自身边框强制 0，改用四个 Frame
        self['bd'] = 0
        self['relief'] = 'flat'
        self['highlightthickness'] = 0
        self['bg'] = WINDOWBG

        self.master = master
        self.int_only = int_only
        self.increment = int(increment) if int_only else float(increment)
        self.from_ = from_
        self.to = to
        self._current_bd = 1
        self._border_color = BDCOLOR
        self._focus = False

        # 四个边框（完全参考 DButton 的 pack 方式）
        self._border_top = tk.Frame(self, bg=BDCOLOR, height=1)
        self._border_bottom = tk.Frame(self, bg=BDCOLOR, height=1)
        self._border_left = tk.Frame(self, bg=BDCOLOR, width=1)
        self._border_right = tk.Frame(self, bg=BDCOLOR, width=1)

        self._border_top.pack(fill='x', side='top')
        self._border_bottom.pack(fill='x', side='bottom')
        self._border_left.pack(fill='y', side='left')
        self._border_right.pack(fill='y', side='right')

        # 内部 Entry 关闭自身边框
        self.Entry = DEntry(self, border=False)
        self.Entry.config(bd=0, relief='flat', bg=TEXTBG, fg=TEXTFG,
                          insertbackground=HIGHLIGHT, insertontime=500,
                          insertofftime=500, insertwidth=2, font='TkDefaultFont')
        self.Entry.config(**spinbox_kwargs)

        self.Entry.bind("<MouseWheel>", self.mousewheel)
        vcmd = (self.register(self.on_validate), '%P')
        invcmd = (self.register(self.on_invalid))
        self.Entry.config(validate="key", validatecommand=vcmd, invalidcommand=invcmd)
        self.Entry.bind('<Up>', self.up_number)
        self.Entry.bind('<Down>', self.down_number)

        self.Frame_DButton = tk.Frame(self, bd=0, bg=TEXTBG)
        self.Frame_DButton.pack(side='right', fill='both', expand=1)
        self.Entry.pack(side='left', expand=True, fill='both')

        self.DButton_up = DAlphaButton(self.Frame_DButton, text='+', command=self.up_number, width=2,bg=TEXTBG)
        self.DButton_up.pack(side='left', fill='both', expand=True, padx=(0,0), pady=0)
        self.DButton_down = DAlphaButton(self.Frame_DButton, text='-', command=self.down_number, width=2,bg=TEXTBG)
        self.DButton_down.pack(side='right', fill='both', expand=True, padx=(0,0), pady=0)

        self.Frame_DButton.bind('<Up>', self.up_number)
        self.Frame_DButton.bind('<Down>', self.down_number)
        self.DButton_up.bind('<Up>', self.up_number)
        self.DButton_up.bind('<Down>', self.down_number)
        self.DButton_down.bind('<Up>', self.up_number)
        self.DButton_down.bind('<Down>', self.down_number)

        self._last_valid_value = self.Entry.get()

        # 容器本身不参与 Tab 焦点，焦点交给内部 Entry
        try:
            self.configure(takefocus=0)
        except Exception:
            pass
        try:
            self.Entry.configure(takefocus=1)
        except Exception:
            pass
        try:
            self.Frame_DButton.configure(takefocus=0)
            self.DButton_up.configure(takefocus=0)
            self.DButton_down.configure(takefocus=0)
        except Exception:
            pass

        widgets = (self, self.Entry, self.Frame_DButton, self.DButton_up, self.DButton_down)
        for w in widgets:
            w.bind('<FocusIn>', self._focus_in, add='+')
            w.bind('<FocusOut>', self._focus_out, add='+')

        self.bind('<Configure>', self._on_resize, add='+')
        self._update_border_coords()

    def _on_resize(self, event):
        self._update_border_coords(event.width, event.height)

    def _update_border_coords(self, w=None, h=None):
        if w is None:
            w = self.winfo_width()
        if h is None:
            h = self.winfo_height()
        if w <= 1 or h <= 1:
            return
        bd = self._current_bd
        self._border_top.config(height=bd)
        self._border_bottom.config(height=bd)
        self._border_left.config(width=bd)
        self._border_right.config(width=bd)

    def _update_border_color(self):
        color = HIGHLIGHT if self._focus else self._border_color
        for b in (self._border_top, self._border_bottom,
                  self._border_left, self._border_right):
            b['bg'] = color

    def set_border_color(self, color):
        self._border_color = color
        self._update_border_color()

    # ===== 焦点（控制整体边框颜色） =====
    def _focus_in(self, event=None):
        # 若焦点落在容器 Frame 上，立刻转给内部 Entry
        if event is not None and getattr(event, 'widget', None) is self:
            try:
                self.Entry.focus_set()
            except Exception:
                pass
            return

        self._focus = True
        self._update_border_color()
        text = self.Entry.get()
        try:
            if text == '':
                self._last_valid_value = ''
                return
            if self.int_only:
                value = int(text)
            else:
                value = float(text)
            if self.from_ <= value <= self.to:
                self._last_valid_value = text
        except:
            pass


    def _focus_out(self, event=None):
        self.after_idle(self._check_focus_leave)

    def _check_focus_leave(self):
        focus_widget = self.focus_get()
        if focus_widget is not None:
            w = focus_widget
            while w is not None:
                if w is self:
                    return
                w = w.master
        self._focus = False
        self._update_border_color()

        text = self.Entry.get()
        if text == '':
            self._last_valid_value = ''
            return
        try:
            if self.int_only:
                value = int(text)
            else:
                value = float(text)
            if not (self.from_ <= value <= self.to):
                raise ValueError
            self._last_valid_value = text
        except:
            win32api.MessageBeep()
            self.delete(0, 'end')
            self.insert('end', self._last_valid_value)

    # ========== 下面验证 / 增减 / 代理方法保持原样 ==========
    def _is_valid_int(self, s):
        if s == '':
            return True
        if s == '-':
            return True
        if s.startswith('-'):
            return s[1:].isdigit()
        return s.isdigit()

    def _is_valid_float(self, s):
        if s in ('', '-', '.', '-.'):
            return True
        if s.count('.') > 1:
            return False
        if '-' in s[1:]:
            return False
        try:
            float(s)
            return True
        except:
            return False

    def up_number(self, beep=True):
        if getattr(self, '_state', 'normal') == 'disabled':
            return
        temp_number = self.Entry.get()
        if temp_number in ('', '-', '.', '-.'):
            new_value = str(self.from_)
        else:
            try:
                num = float(temp_number) if not self.int_only else int(temp_number)
                new_number = num + self.increment
                if self.from_ <= new_number <= self.to:
                    new_value = str(new_number)
                else:
                    new_value = str(self.to)
                    if beep:
                        win32api.MessageBeep()
            except:
                new_value = str(self.from_)
        self.delete(0, 'end')
        self.insert('end', new_value)

    def down_number(self, beep=True):
        if getattr(self, '_state', 'normal') == 'disabled':
            return
        temp_number = self.Entry.get()
        if temp_number in ('', '-', '.', '-.'):
            new_value = str(self.from_)
        else:
            try:
                num = float(temp_number) if not self.int_only else int(temp_number)
                new_number = num - self.increment
                if self.from_ <= new_number <= self.to:
                    new_value = str(new_number)
                else:
                    new_value = str(self.from_)
                    if beep:
                        win32api.MessageBeep()
            except:
                new_value = str(self.from_)
        self.delete(0, 'end')
        self.insert('end', new_value)

    def __getattr__(self, name):
        return getattr(self.Entry, name)

    def insert(self, index, s):
        s = str(s)
        if self.int_only:
            if self._is_valid_int(s):
                self.Entry['validate'] = 'none'
                self.Entry.insert(index, s)
                self.Entry['validate'] = 'key'
        else:
            if self._is_valid_float(s):
                self.Entry['validate'] = 'none'
                self.Entry.insert(index, s)
                self.Entry['validate'] = 'key'

    def delete(self, first, last=None):
        self.Entry['validate'] = 'none'
        self.Entry.delete(first, last)
        self.Entry['validate'] = 'key'

    def on_validate(self, P):
        if self.int_only:
            return self._is_valid_int(P)
        else:
            return self._is_valid_float(P)

    def on_invalid(self):
        win32api.MessageBeep()

    def mousewheel(self, event):
        if getattr(self, '_state', 'normal') == 'disabled':
            return
        delta = event.delta if hasattr(event, 'delta') else 0
        if delta > 0:
            for i in range(int(delta / 120)):
                self.up_number(beep=False)
        elif delta < 0:
            for i in range(-int(delta / 120)):
                self.down_number(beep=False)





class DProgressbar(tk.Frame):
    """
    Windows 风格进度条
    - determinate：只有运动柔光高光（边缘完全融入主体）
    - indeterminate：纯色块，无高光
    """
    def __init__(self, master=None,
                 orient='horizontal',
                 length=200,
                 mode='determinate',
                 maximum=100,
                 value=0,
                 variable=None,
                 bg=WIDGETBG,
                 barcolor=GREENLIGHT,
                 bd=1,
                 **kw):

        super().__init__(master, bg=bg, bd=0, highlightthickness=0, **kw)

        self._maximum = max(1.0, float(maximum))
        self._value   = max(0.0, min(float(value), self._maximum))
        self._orient  = orient.lower()
        self._mode    = mode.lower()
        self.variable = variable
        self.barcolor = barcolor
        self.troughcolor = bg
        self._bd = bd

        # 边框
        self._bt = tk.Frame(self, bg=BDCOLOR, height=bd)
        self._bb = tk.Frame(self, bg=BDCOLOR, height=bd)
        self._bl = tk.Frame(self, bg=BDCOLOR, width=bd)
        self._br = tk.Frame(self, bg=BDCOLOR, width=bd)
        self._bt.pack(fill='x', side='top')
        self._bb.pack(fill='x', side='bottom')
        self._bl.pack(fill='y', side='left')
        self._br.pack(fill='y', side='right')

        # 槽 + 画布
        self._trough = tk.Frame(self, bg=bg, bd=0, highlightthickness=0)
        self._trough.pack(fill='both', expand=True)
        self._canvas = tk.Canvas(self._trough, bg=bg, highlightthickness=0, bd=0)
        self._canvas.pack(fill='both', expand=True)

        # 动画状态
        self._shine_pos = -0.45
        self._ind_pos   = 0.0
        self._ind_dir   = 1
        self._animating = False
        self._shine_on  = False
        self._after_id  = None
        self._shine_id  = None

        if variable is not None:
            variable.trace_add('write', self._on_var)
            try:
                self._value = float(variable.get())
            except Exception:
                pass

        if self._orient == 'horizontal':
            self.configure(width=length, height=30)
        else:
            self.configure(width=30, height=length)

        self.bind('<Configure>', lambda e: self._redraw())
        self._canvas.bind('<Configure>', lambda e: self._redraw())
        self.after(30, self._check_shine)

    # -------------------- 公共接口 --------------------
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = max(0.0, min(float(v), self._maximum))
        if self.variable is not None:
            try:
                self.variable.set(self._value)
            except Exception:
                pass
        self._redraw()

    @property
    def maximum(self):
        return self._maximum

    @maximum.setter
    def maximum(self, v):
        self._maximum = max(1.0, float(v))
        self._value = min(self._value, self._maximum)
        self._redraw()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, v):
        self._mode = str(v).lower()
        self._check_shine()
        self._redraw()

    @property
    def orient(self):
        return self._orient

    def start(self, interval=16):
        if self._mode != 'indeterminate':
            return
        self._animating = True
        self._tick_ind(interval)

    def stop(self):
        self._animating = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def step(self, amount=1.0):
        if self._mode == 'determinate':
            self.value = self.value + amount

    def configure(self, cnf=None, **kw):
        if 'value' in kw:    self.value = kw.pop('value')
        if 'maximum' in kw:  self.maximum = kw.pop('maximum')
        if 'mode' in kw:     self.mode = kw.pop('mode')
        if 'barcolor' in kw:
            self.barcolor = kw.pop('barcolor')
            self._redraw()
        if kw or cnf:
            return super().configure(cnf, **kw)
    config = configure

    # -------------------- 内部 --------------------
    def _on_var(self, *a):
        try:
            self._value = float(self.variable.get())
            self._redraw()
        except Exception:
            pass

    def _rgb(self, color):
        r, g, b = self.winfo_rgb(color)
        return r >> 8, g >> 8, b >> 8

    def _to_hex(self, r, g, b):
        return f'#{max(0, min(255, int(r))):02x}{max(0, min(255, int(g))):02x}{max(0, min(255, int(b))):02x}'

    def _check_shine(self):
        if self._mode == 'determinate' and not self._shine_on:
            self._shine_on = True
            self._tick_shine()
        elif self._mode != 'determinate':
            self._shine_on = False
            if self._shine_id:
                self.after_cancel(self._shine_id)
                self._shine_id = None

    def _tick_shine(self):
        if not self._shine_on:
            return
        self._shine_pos += 0.020
        if self._shine_pos > 1.45:
            self._shine_pos = -0.45
        self._redraw()
        self._shine_id = self.after(30, self._tick_shine)

    def _tick_ind(self, interval):
        if not self._animating:
            return
        self._ind_pos += 0.03 * self._ind_dir
        if self._ind_pos >= 1.0:
            self._ind_pos = 1.0
            self._ind_dir = -1
        elif self._ind_pos <= 0.0:
            self._ind_pos = 0.0
            self._ind_dir = 1
        self._redraw()
        self._after_id = self.after(interval, lambda: self._tick_ind(interval))

    def _redraw(self, event=None):
        c = self._canvas
        c.delete('all')
        w, h = c.winfo_width(), c.winfo_height()
        if w <= 1 or h <= 1:
            return

        if self._mode == 'determinate':
            ratio = self._value / self._maximum
            if self._orient == 'horizontal':
                bw = max(0, int(w * ratio))
                if bw > 0:
                    self._draw_shine(c, 0, 0, bw, h, True)
            else:
                bh = max(0, int(h * ratio))
                if bh > 0:
                    self._draw_shine(c, 0, h - bh, w, bh, False)
        else:
            length = max(28, int((w if self._orient == 'horizontal' else h) * 0.27))
            if self._orient == 'horizontal':
                x = int(self._ind_pos * (w - length))
                c.create_rectangle(x, 0, x + length, h, fill=self.barcolor, outline='')
            else:
                y = int(self._ind_pos * (h - length))
                c.create_rectangle(0, y, w, y + length, fill=self.barcolor, outline='')

    # ==================================================================
    # 高光：边缘强度强制降到接近 0，实现无缝衔接
    # ==================================================================
    def _draw_shine(self, c, x, y, bw, bh, horizontal=True):
        # 1. 纯色主体
        c.create_rectangle(x, y, x + bw, y + bh, fill=self.barcolor, outline='', tags='bar')

        # 2. 运动柔光（用 AlphaBlend 与绿色融合，降低亮度）
        shine_w = max(28, int(bw * 0.62))
        center = x + int(self._shine_pos * (bw + shine_w * 0.5)) - shine_w // 2

        # 高光基础色（白色），通过 AlphaBlend 与 barcolor 融合
        # foreground_alpha 越小，高光越贴近绿色、越不刺眼
        # 推荐范围：0.25 ~ 0.45
        base_highlight = AlphaBlend('#FFFFFF', self.barcolor, foreground_alpha=0.6)

        left  = max(x, center - shine_w // 2)
        right = min(x + bw, center + shine_w // 2)
        half  = shine_w / 2.0

        for px in range(left, right):
            dist = (px - center) / half

            # 高斯 + 边缘 smoothstep，保证两侧完全融入
            raw = math.exp(-0.5 * (dist / 0.55) ** 2)
            edge = max(0.0, 1.0 - abs(dist))
            edge_factor = edge * edge * (3.0 - 2.0 * edge)
            intensity = raw * edge_factor

            if intensity < 0.02:
                continue

            # 再用一次 AlphaBlend，按强度把高光叠到绿色上
            # intensity 越大越亮，但整体已经被 0.35 压过，不会过爆
            col = AlphaBlend(base_highlight, self.barcolor, foreground_alpha=intensity)
            c.create_line(px, y, px, y + bh, fill=col, width=1, tags='shine')
    def destroy(self):
        self.stop()
        self._shine_on = False
        if self._shine_id:
            self.after_cancel(self._shine_id)
        super().destroy()

class RainbowLoding(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.master=master
        self['height']=5
        self.label_amout=(self.master.winfo_screenwidth()//344) + 2
        self.move_pixel=0
        self.labels=[]
        self.create_labels()
        self.after(10,self.move_labels)
        
    
    def create_labels(self):
        for i in range(self.label_amout):
            label=tk.Label(self,bd=0,relief='flat',anchor='center',compound='center',height=5)
            self.labels.append(label)
            label.image=ImageTk.PhotoImage(Image.open(f'{libresource}hueColorBar.png'))
            label.config(image=label.image)

    def move_labels(self):
        for i,label in enumerate(self.labels):
            if i*344-self.move_pixel <=-344:
                label.place(x=self.label_amout*344-self.move_pixel,y=0,width=344,height=5)
            else:
                label.place(x=i*344-self.move_pixel,y=0,width=344,height=5)
        self.move_pixel+=2
        if self.move_pixel>=344:
            self.move_pixel=0       
        self.after(10,self.move_labels)


class DScrollbar(tk.Frame):
    """
    纯 tk + DButton 实现的自定义滚动条
    支持垂直/水平，接口与 tk.Scrollbar 兼容，可无缝切换
    """
    def __init__(self, master=None, orient='vertical', command=None,
                 bg=None, troughcolor=None, activebackground=None,
                 width=16, **kw):          # 默认宽度改为 16，更易点击
        # 主题颜色
        self._bg = bg or WINDOWBG
        self._trough = troughcolor or WIDGETBG
        self._thumb_normal = TEXTBG if IsDarkMode() else BDCOLOR
        self._thumb_hover  = AlphaBlend(HIGHLIGHT, self._thumb_normal, 0.35) if IsDarkMode() else HIGHLIGHT
        self._thumb_active = HIGHLIGHT
        self._arrow_bg     = WIDGETBG
        self._arrow_fg     = TEXTFG

        

        # 先把自定义参数弹出来，避免传给 Frame
        for key in ('command', 'orient', 'bg', 'troughcolor',
                    'activebackground', 'width'):
            kw.pop(key, None)

        super().__init__(master, bg=self._bg, **kw)

        self.orient = orient.lower()
        self.command = command
        self._width = max(12, int(width))          # 最小厚度保护
        self._arrowsize = self._width              # 强制正方形
        self._first = 0.0
        self._last  = 1.0
        self._dragging = False
        self._drag_start = 0
        self._drag_first = 0.0
        self._hover = False

        # 固定尺寸
        if self.orient == 'vertical':
            super().configure(width=self._width)
        else:
            super().configure(height=self._width)
        self.pack_propagate(False)
        self.grid_propagate(False)

        # ---------- 箭头按钮（强制正方形） ----------
        if self.orient == 'vertical':
            # 上箭头
            self.up_frame = tk.Frame(self, width=self._width, height=self._arrowsize,
                                     bg=self._arrow_bg, bd=0, highlightthickness=0)
            self.up_frame.pack(side='top', fill='x')
            self.up_frame.pack_propagate(False)

            self.up_btn = DAlphaButton(self.up_frame, text='∧', command=self._scroll_up,
                                  bg=self._arrow_bg, fg=self._arrow_fg,
                                  font=('', 8), takefocus=False)
            self.up_btn.pack(fill='both', expand=True)

            # 下箭头
            self.down_frame = tk.Frame(self, width=self._width, height=self._arrowsize,
                                       bg=self._arrow_bg, bd=0, highlightthickness=0)
            self.down_frame.pack(side='bottom', fill='x')
            self.down_frame.pack_propagate(False)

            self.down_btn = DAlphaButton(self.down_frame, text='∨', command=self._scroll_down,
                                    bg=self._arrow_bg, fg=self._arrow_fg,
                                    font=('', 8), takefocus=False)
            self.down_btn.pack(fill='both', expand=True)

        else:
            # 左箭头
            self.up_frame = tk.Frame(self, width=self._arrowsize, height=self._width,
                                     bg=self._arrow_bg, bd=0, highlightthickness=0)
            self.up_frame.pack(side='left', fill='y')
            self.up_frame.pack_propagate(False)

            self.up_btn = DAlphaButton(self.up_frame, text='＜', command=self._scroll_up,
                                  bg=self._arrow_bg, fg=self._arrow_fg,
                                  font=('', 8), takefocus=False)
            self.up_btn.pack(fill='both', expand=True)

            # 右箭头
            self.down_frame = tk.Frame(self, width=self._arrowsize, height=self._width,
                                       bg=self._arrow_bg, bd=0, highlightthickness=0)
            self.down_frame.pack(side='right', fill='y')
            self.down_frame.pack_propagate(False)

            self.down_btn = DAlphaButton(self.down_frame, text='＞', command=self._scroll_down,
                                    bg=self._arrow_bg, fg=self._arrow_fg,
                                    font=('', 8), takefocus=False)
            self.down_btn.pack(fill='both', expand=True)

        # ---------- 轨道 + 滑块（可延伸部分最小 20） ----------
        self.trough = tk.Frame(self, bg=self._trough, bd=0, highlightthickness=0)
        if self.orient == 'vertical':
            self.trough.pack(side='top', fill='both', expand=True)
            # 保证轨道区域至少 20 像素高
            self.trough.configure(height=20)
            self.trough.pack_propagate(False)   # 防止被压缩得太狠
        else:
            self.trough.pack(side='left', fill='both', expand=True)
            self.trough.configure(width=20)
            self.trough.pack_propagate(False)

        self.canvas = tk.Canvas(self.trough, bg=self._trough,
                                highlightthickness=0, bd=0)
        self.canvas.pack(fill='both', expand=True)

        self.thumb = self.canvas.create_rectangle(0, 0, 1, 1,
                                                  fill=self._thumb_normal,
                                                  outline='', tags='thumb',
                                                  state='hidden')

        # 事件绑定
        self.canvas.bind('<Configure>', self._on_configure)
        self.canvas.bind('<Button-1>', self._on_press)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.canvas.bind('<Enter>', self._on_enter)
        self.canvas.bind('<Leave>', self._on_leave)
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Button-4>', lambda e: self._scroll_units(-1))
        self.canvas.bind('<Button-5>', lambda e: self._scroll_units(1))

        self.canvas.tag_bind('thumb', '<Enter>', self._on_thumb_enter)
        self.canvas.tag_bind('thumb', '<Leave>', self._on_thumb_leave)

        self._update_thumb()

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------
    def set(self, first, last):
        try:
            self._first = float(first)
            self._last  = float(last)
        except Exception:
            self._first, self._last = 0.0, 1.0
        self._update_thumb()

    def get(self):
        return self._first, self._last

    def configure(self, cnf=None, **kw):
        if isinstance(cnf, dict):
            kw = {**cnf, **kw}
            cnf = None

        if 'command' in kw:
            self.command = kw.pop('command')
        if 'orient' in kw:
            kw.pop('orient')
        if 'bg' in kw:
            self._bg = kw.pop('bg')
            super().configure(bg=self._bg)
        if 'troughcolor' in kw:
            self._trough = kw.pop('troughcolor')
            self.trough.configure(bg=self._trough)
            self.canvas.configure(bg=self._trough)
        if 'activebackground' in kw:
            self._thumb_active = kw.pop('activebackground')
        if 'width' in kw:
            self._width = max(12, int(kw.pop('width')))
            self._arrowsize = self._width
            if self.orient == 'vertical':
                super().configure(width=self._width)
            else:
                super().configure(height=self._width)

        if kw:
            return super().configure(**kw)
        return None

    config = configure

    def __setitem__(self, key, value):
        if key == 'command':
            self.command = value
        elif key == 'orient':
            pass
        elif key == 'bg':
            self._bg = value
            super().configure(bg=value)
        elif key == 'troughcolor':
            self._trough = value
            self.trough.configure(bg=value)
            self.canvas.configure(bg=value)
        elif key == 'activebackground':
            self._thumb_active = value
        elif key == 'width':
            self._width = max(12, int(value))
            self._arrowsize = self._width
            if self.orient == 'vertical':
                super().configure(width=self._width)
            else:
                super().configure(height=self._width)
        else:
            super().__setitem__(key, value)

    def __getitem__(self, key):
        if key == 'command':
            return self.command
        if key == 'orient':
            return self.orient
        if key == 'bg':
            return self._bg
        if key == 'troughcolor':
            return self._trough
        if key == 'width':
            return self._width
        return super().__getitem__(key)

    # ------------------------------------------------------------------
    # 内部实现
    # ------------------------------------------------------------------
    def _on_configure(self, event=None):
        self._update_thumb()

    def _update_thumb(self):
        if not self.winfo_exists():
            return

        # 内容不足以滚动时隐藏滑块
        if self._last - self._first >= 0.999:
            self.canvas.itemconfigure(self.thumb, state='hidden')
            return

        self.canvas.itemconfigure(self.thumb, state='normal')

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        if self.orient == 'vertical':
            total = h
            size = max(20, int((self._last - self._first) * total))  # 滑块最小 20
            pos  = int(self._first * total)
            if pos + size > total:
                pos = max(0, total - size)
            self.canvas.coords(self.thumb, 1, pos, w - 1, pos + size)
        else:
            total = w
            size = max(20, int((self._last - self._first) * total))
            pos  = int(self._first * total)
            if pos + size > total:
                pos = max(0, total - size)
            self.canvas.coords(self.thumb, pos, 1, pos + size, h - 1)

    def _fraction(self, event):
        if self.orient == 'vertical':
            total = self.canvas.winfo_height()
            if total <= 0:
                return 0.0
            return max(0.0, min(1.0, event.y / total))
        else:
            total = self.canvas.winfo_width()
            if total <= 0:
                return 0.0
            return max(0.0, min(1.0, event.x / total))

    def _on_press(self, event):
        items = self.canvas.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1)
        if self.thumb in items and self.canvas.itemcget(self.thumb, 'state') != 'hidden':
            self._dragging = True
            self._drag_start = event.y if self.orient == 'vertical' else event.x
            self._drag_first = self._first
            self.canvas.itemconfigure(self.thumb, fill=self._thumb_active)
        else:
            frac = self._fraction(event)
            span = self._last - self._first
            if span >= 0.999:
                return
            new_first = max(0.0, min(1.0 - span, frac - span / 2))
            self._move_to(new_first)

    def _on_drag(self, event):
        if not self._dragging:
            return
        if self.orient == 'vertical':
            total = max(1, self.canvas.winfo_height())
            delta = (event.y - self._drag_start) / total
        else:
            total = max(1, self.canvas.winfo_width())
            delta = (event.x - self._drag_start) / total

        span = self._last - self._first
        new_first = max(0.0, min(1.0 - span, self._drag_first + delta))
        self._move_to(new_first)

    def _on_release(self, event):
        self._dragging = False
        if self.canvas.itemcget(self.thumb, 'state') != 'hidden':
            fill = self._thumb_hover if self._hover else self._thumb_normal
            self.canvas.itemconfigure(self.thumb, fill=fill)

    def _move_to(self, first):
        span = self._last - self._first
        self._first = first
        self._last  = first + span
        self._update_thumb()
        if self.command:
            self.command('moveto', self._first)

    def _scroll_units(self, direction):
        if self.command:
            self.command('scroll', direction, 'units')

    def _scroll_up(self):
        self._scroll_units(-1)

    def _scroll_down(self):
        self._scroll_units(1)

    def _on_mousewheel(self, event):
        delta = -1 if event.delta > 0 else 1
        self._scroll_units(delta)

    def _on_enter(self, event):
        self._hover = True
        if not self._dragging and self.canvas.itemcget(self.thumb, 'state') != 'hidden':
            self.canvas.itemconfigure(self.thumb, fill=self._thumb_hover)

    def _on_leave(self, event):
        self._hover = False
        if not self._dragging and self.canvas.itemcget(self.thumb, 'state') != 'hidden':
            self.canvas.itemconfigure(self.thumb, fill=self._thumb_normal)

    def _on_thumb_enter(self, event):
        self._hover = True
        if not self._dragging:
            self.canvas.itemconfigure(self.thumb, fill=self._thumb_hover)

    def _on_thumb_leave(self, event):
        if not self._dragging:
            self._hover = False
            self.canvas.itemconfigure(self.thumb, fill=self._thumb_normal)








def MessageBox(parent=None, text='', title='', icon='none',text_true='确定',text_false='取消', buttonmode=1, defaultfocus=1):
    # 辅助函数：更精确地计算文本高度（改进版）


    def close_MessageBox_window():
        if parent:
            parent.attributes('-disabled', 'false')
        MessageBox_window.destroy()
        if parent:
            parent.focus_set()

    def return_value(value):
        nonlocal rtn
        rtn = value
        close_MessageBox_window()

    def handle_key(event):
        focused = MessageBox_window.focus_get()
        if event.keysym == 'Escape':  # If ESC key is pressed, return None
            return_value(None)
        elif focused in (ok_button, None):
            return_value(True)
        elif focused == cancel_button:
            return_value(False)

    def update_button_focus(event=None):
        if buttonmode == 2:
            if MessageBox_window.focus_get() == cancel_button:
                ok_button['default'], cancel_button['default'] = 'normal', 'active'
            else:# MessageBox_window.focus_get() == ok_button:
                ok_button['default'], cancel_button['default'] = 'active', 'normal'
    # 初始化 rtn
    rtn = None

    # 窗口初始化
    MessageBox_window = tk.Toplevel(parent) if parent else tk.Tk()
    
    MessageBox_window.title(title)
    initial_window_width = 390
    initial_window_height = 170 # This is a placeholder, will be updated later
    

    MessageBox_window.geometry(f'{initial_window_width}x{initial_window_height}+'
                                f'{(MessageBox_window.winfo_screenwidth() - initial_window_width) // 2}+'
                                f'{(MessageBox_window.winfo_screenheight() - initial_window_height) // 2}')
    


    #MessageBox_window.resizable(False, False)
    MessageBox_window.protocol("WM_DELETE_WINDOW", close_MessageBox_window)
    MessageBox_window['bg']=WINDOWBG
    MessageBox_window.focus_set()


    if parent:
        parent.attributes('-disabled', 'true')
        MessageBox_window.wm_transient(parent)

    Label_icon = tk.Label(MessageBox_window, anchor='center',bg=WINDOWBG)
    Label_icon.place(x=20, y=20, width=45, height=45)


    Frame_cauculate= tk.Frame(MessageBox_window,bd=0)
    Frame_cauculate.place(x=-20000, y=-20000, width=290, height=20000)

    Label_cauculate = tk.Label(Frame_cauculate,bg=WINDOWBG,fg=TEXTFG, wraplength=280, text=text, justify='left', anchor='nw',)
    Label_cauculate.pack(fill='x',side='top')
    Label_text_height=max(Label_cauculate.winfo_reqheight(), 90)
    Frame_cauculate.destroy()


    Label_text = tk.Label(MessageBox_window,bg=WINDOWBG,fg=TEXTFG, wraplength=280, text=text, justify='left', anchor='nw',)
    
    Label_text.place(x=80, y=20, width=290, height=Label_text_height)

    if icon != 'none':
        SetImageTk(Label_icon, f"{libresource}/{icon}.ico", img_size=(45, 45))

    

    
    buttons_y = 35+Label_text_height

    new_window_height = buttons_y + 50

    MessageBox_window.geometry(f'{initial_window_width}x{new_window_height}+'
                                f'{(MessageBox_window.winfo_screenwidth() - initial_window_width) // 2}+'
                                f'{(MessageBox_window.winfo_screenheight() - new_window_height) // 2}')

    if buttonmode == 1:
        MessageBox_window.bind('<Escape>', handle_key)
        
        ok_button = DButton(MessageBox_window, text=text_true, command=lambda: return_value(True), default='active')
        ok_button.place(x=290, y=buttons_y, width=80, height=30)
        ok_button.focus()

    elif buttonmode == 2:
        MessageBox_window.bind('<Escape>', lambda e: return_value(None))

        ok_button = DButton(MessageBox_window, text=text_true, command=lambda: return_value(True), )
        ok_button.place(x=190, y=buttons_y, width=80, height=30)

        cancel_button = DButton(MessageBox_window, text=text_false, command=lambda: return_value(False))
        cancel_button.place(x=290, y=buttons_y, width=80, height=30)

        ok_button.bind("<FocusIn>", update_button_focus)
        cancel_button.bind("<FocusIn>", update_button_focus)
        ok_button.bind("<FocusOut>", update_button_focus)
        cancel_button.bind("<FocusOut>", update_button_focus)

        (ok_button if defaultfocus == 1 else cancel_button).focus()
        (ok_button if defaultfocus == 1 else cancel_button)['default']='active'
    else:
        raise ValueError("buttonmode 只能为 1 或 2")

    beep_map = {
        'question': win32con.MB_ICONQUESTION, 
        'safe_warning':win32con.MB_ICONWARNING,
        'error': win32con.MB_ICONERROR, 
        'stop': win32con.MB_ICONERROR, 
        'warning': win32con.MB_ICONWARNING,
        'info': win32con.MB_ICONINFORMATION, 
        'correct': win32con.MB_ICONINFORMATION,
        'none': 0
    }



    #convert_place_to_relative(MessageBox_window)
    MessageBox_window.wm_iconbitmap(f"{libresource}icon.ico")
    SetDarkTitleBar(MessageBox_window)
    win32api.MessageBeep(beep_map.get(icon, 0))
    MessageBox_window.wait_window(MessageBox_window)
    return rtn







def InputBox(title='', text='', parent=None, default='', canspace=True, canempty=False,allowspecialchar=True,text_true='确定',text_false='取消'):
    rt = None
    def close_handler():
        if parent:
            parent.attributes('-disabled', 'false')
        Input_Box_Auto_window.destroy()
        if parent:
            parent.focus_set()

    def close_handler_cancel():
        nonlocal rt
        rt = None
        close_handler()

    def have_common_char(str1, str2):
        """判断两个字符串是否存在相同部分
        :param str1: 字符串1
        :param str2: 字符串2
        :return: 存在相同True;不存在相同False
        """
        # 将字符串转换为集合
        set1 = set(str1)
        set2 = set(str2)
        
        # 求两个集合的交集
        intersection = set1 & set2
        
        # 如果交集不为空，则存在相同的字符
        return bool(intersection)
    
    def save():
        nonlocal rt
        rt = entry_filename.get().strip()

        if not canspace and ' ' in rt:
            win32api.MessageBeep()
            entry_filename.focus()
        elif not allowspecialchar:
            if have_common_char("|<>\"?*:/\\",rt):
                win32api.MessageBeep()
                entry_filename.focus()
            else:
                close_handler()
        elif canempty or rt:
            close_handler()
        else:
            win32api.MessageBeep()
            entry_filename.focus()


    def update_button_focus(event=None):
        if Input_Box_Auto_window.focus_get() == close_btn:
            save_btn['default'], close_btn['default'] = 'normal', 'active'
        else:
            save_btn['default'], close_btn['default'] = 'active', 'normal'


    # 创建窗口
    Input_Box_Auto_window = tk.Toplevel(parent) if parent else tk.Tk()
    Input_Box_Auto_window.title(title)
    Input_Box_Auto_window.geometry(f'420x120+{(Input_Box_Auto_window.winfo_screenwidth() - 420) // 2}+{(Input_Box_Auto_window.winfo_screenheight() - 120) // 2}')
    Input_Box_Auto_window.resizable(False, False)
    Input_Box_Auto_window['bg']=WINDOWBG
    Input_Box_Auto_window.protocol("WM_DELETE_WINDOW", close_handler_cancel)
    #Input_Box_Auto_window.bind('<Return>', save_)
    Input_Box_Auto_window.bind('<Escape>', lambda e: close_handler_cancel())


    if parent:
        parent.attributes('-disabled', 'true')
        Input_Box_Auto_window.wm_transient(parent)

    # UI 组件
   
    # 获取字体对象
    #temp_label = tk.Label(Input_Box_Auto_window)
    #actual_font = tkfont.Font(font=temp_label.cget('font'))
    #temp_label.destroy()

    Label_cauculate = tk.Label(Input_Box_Auto_window,bg=WINDOWBG,fg=TEXTFG, text=text, anchor='w',)
    Label_cauculate.pack(side='top')
    label_width = max(Label_cauculate.winfo_reqwidth()+10,80)  #calculate_label_width_with_font(text, actual_font, min_width=LABEL_MIN_WIDTH, buffer_pixels=20)
    entry_width = 380 - label_width  # 总宽度420减去左右边距和标签宽度
    Label_cauculate.destroy()



    tk.Label(Input_Box_Auto_window, text=text, anchor="w",bg=WINDOWBG,fg=TEXTFG).place(x=20, y=20, width=label_width, height=30)
    entry_filename = DEntry(Input_Box_Auto_window, takefocus=True)
    entry_filename.place(x=20 + label_width, y=20, width=entry_width, height=30)
    entry_filename.insert(0, default)
    entry_filename.focus()

    save_btn = DButton(Input_Box_Auto_window, text=text_true, command=save, default='active')
    save_btn.place(x=220, y=70, width=80, height=30)

    close_btn = DButton(Input_Box_Auto_window, text=text_false, command=close_handler_cancel)
    close_btn.place(x=320, y=70, width=80, height=30)

    save_btn.bind("<FocusIn>", update_button_focus)
    save_btn.bind("<FocusOut>", update_button_focus)
    close_btn.bind("<FocusIn>", update_button_focus)
    close_btn.bind("<FocusOut>", update_button_focus)

    Input_Box_Auto_window.wm_iconbitmap(f"{libresource}icon.ico")
    SetDarkTitleBar(Input_Box_Auto_window)
    Input_Box_Auto_window.wait_window(Input_Box_Auto_window)

    return rt





def ComboInputBox(title='', text='', parent=None,default='',value=[],state='readonly'):
    rt=None

    def close_handler():
        if parent!=None:
            parent.attributes('-disabled', 'false')
        Input_ComboboxBox_window.destroy()
        if parent!=None:
            parent.focus_set()
    def close_handler_cancel_(nothing):
        close_handler_cancel()
    def close_handler_cancel():
        nonlocal rt
        rt=None
        close_handler()
    def save():
        nonlocal rt
        rt=entry_filename.get()
        if rt.replace(' ','')!='':
            close_handler()
            return 0
        else:
            win32api.MessageBeep()
            entry_filename.focus()
            return 0

    def focus_see_(nothing):
        if Input_ComboboxBox_window.focus_get()!=None:
            if Input_ComboboxBox_window.focus_get()==close:
                save_btn['default']='normal'
                close['default']='active'
            else:
                close['default']='normal'
                save_btn['default']='active'


    if parent!=None:
        parent.attributes('-disabled', 'true')
        Input_ComboboxBox_window=tk.Toplevel(parent)
        Input_ComboboxBox_window.wm_transient(parent)
    else:
        Input_ComboboxBox_window=tk.Tk()
    Input_ComboboxBox_window.title(str(title))
    width=420
    height=120

    screenwidth = Input_ComboboxBox_window.winfo_screenwidth()
    screenheight = Input_ComboboxBox_window.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    Input_ComboboxBox_window.geometry(geometry)
    Input_ComboboxBox_window.resizable(width=False, height=False)
    #Input_ComboboxBox_window.bind('<Return>',save_)
    Input_ComboboxBox_window['bg']=WINDOWBG
    Input_ComboboxBox_window.protocol("WM_DELETE_WINDOW", close_handler_cancel)
    Input_ComboboxBox_window.bind('<Escape>',close_handler_cancel_)
    Input_ComboboxBox_window.focus_set()

    Var_value=tk.StringVar()
    Var_value.set(str(default))


    Label_cauculate = tk.Label(Input_ComboboxBox_window,bg=WINDOWBG,fg=TEXTFG, text=text, anchor='w',)
    Label_cauculate.pack(side='top')
    label_width = max(Label_cauculate.winfo_reqwidth()+10,80)  #calculate_label_width_with_font(text, actual_font, min_width=LABEL_MIN_WIDTH, buffer_pixels=20)
    entry_width = 380 - label_width  # 总宽度420减去左右边距和标签宽度
    Label_cauculate.destroy()


    tk.Label(Input_ComboboxBox_window, text=text, anchor="w",bg=WINDOWBG,fg=TEXTFG).place(x=20, y=20, width=label_width, height=30)
    entry_filename = DCombobutton(Input_ComboboxBox_window,values=value,textvariable=Var_value,state=state)
    entry_filename.place(x=20 + label_width, y=20, width=entry_width, height=30)
    entry_filename.focus_set()

    save_btn= DButton(Input_ComboboxBox_window, text="确定",command=save,default='active')
    save_btn.place(x=220, y=70, width=80, height=30)

    close = DButton(Input_ComboboxBox_window, text="取消", command=close_handler_cancel)
    close.place(x=320, y=70, width=80, height=30)
    
    save_btn.bind("<FocusIn>", focus_see_)
    save_btn.bind("<FocusOut>", focus_see_)
    close.bind("<FocusIn>", focus_see_)
    close.bind("<FocusOut>", focus_see_)
    
    
    Input_ComboboxBox_window.wm_iconbitmap(f'{libresource}icon.ico')
    SetDarkTitleBar(Input_ComboboxBox_window)
    Input_ComboboxBox_window.wait_window(Input_ComboboxBox_window)

    return rt



def PasswordBox(title='',text='',parent=None,defaultuser='',defaultfocus=1,defaultpassword='',defaultusertuple=(),savepassword_state=False,usernamestate='normal',autoreset_password=False):

    rt=(None,None,None)
    def close_password_box_window():
        if parent!=None:
            parent.attributes('-disabled','false')
        password_box_window.destroy()
        if parent!=None:
            parent.focus_set()
    def close_password_box_window_esc(event=None):
        nonlocal rt
        rt=(None,None,None)
        close_password_box_window()

    def ok(event=None):
        nonlocal rt
        if password_box_window.focus_get() is not None:
            if password_box_window.focus_get() == button_ok:
                entry_username__=entry_username.get()
                entry_password__=entry_password.get()
                rt=(entry_username__,entry_password__,save_cb.get())
                close_password_box_window()
            elif password_box_window.focus_get() == button_cancel:
                rt=(None,None,None)
                close_password_box_window()
            else:
                entry_username__=entry_username.get()
                entry_password__=entry_password.get()
                rt=(entry_username__,entry_password__,save_cb.get())
                close_password_box_window()

    if parent!=None:
        parent.attributes('-disabled','true')
        password_box_window=tk.Toplevel(parent)
        password_box_window.transient(parent)
    else:
        password_box_window=tk.Tk()
    password_box_window.title(title)
    # 设置窗口大小、居中
    width = 480
    height = 395
    screenwidth = password_box_window.winfo_screenwidth()
    screenheight = password_box_window.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height-100) / 2)
    password_box_window.geometry(geometry)
    password_box_window.config(highlightthickness=0,bd=0)
    password_box_window.protocol("WM_DELETE_WINDOW", close_password_box_window_esc)
    password_box_window.resizable(False,False)
    password_box_window.bind('<Escape>',close_password_box_window_esc)
    #password_box_window.bind('<Return>',ok)
    password_box_window.focus_set()
    password_box_window['bg']=WINDOWBG
    
    if IsDarkMode():
        # 1. 加载原始图片
        path = f'{libresource}passwordinput_headpicture.png'
        src_img = Image.open(path).convert("RGBA")
        
        # 2. 创建一个相同大小的黑色蒙层
        # alpha 取值范围为 0 (完全透明) 到 255 (完全不透明)
        alpha = 64
        overlay = Image.new('RGBA', src_img.size, (0, 0, 0, alpha))
        
        # 3. 合并图像
        combined_img = Image.alpha_composite(src_img, overlay)
        
        # 4. 转换为 Tkinter 兼容的对象
        # 注意：必须保持对 img 的引用，否则会被垃圾回收导致图片不显示
        img = ImageTk.PhotoImage(combined_img)
    else:
        img=tk.PhotoImage(width=480, height=93,file=f'{libresource}passwordinput_headpicture.png')
    tk.Label(password_box_window,image=img,bd=0,).place(x=0,y=0,width=480,height=93)

    tk.Label(password_box_window,text=text,anchor='w',bg=WINDOWBG,fg=TEXTFG).place(x=15,y=100,width=455,height=50)

    tk.Label(password_box_window,text='用户名(U):',anchor='w',underline=4,bg=WINDOWBG,fg=TEXTFG).place(x=15,y=160,width=155,height=30)
    entry_username=DCombobutton(password_box_window,values=defaultusertuple)
    entry_username.place(x=170,y=160,width=250,height=30)
    entry_username.insert(0,defaultuser)
    entry_username.config(state=usernamestate)
    def entry_username_focus_(nothing):
        entry_username.focus()
    password_box_window.bind('<Alt-u>',entry_username_focus_)


    DButton(password_box_window,text='...',state='disabled',underline=0).place(x=430,y=160,width=35,height=30)
    #这个...单纯是装饰,没有任何作用


    tk.Label(password_box_window,text='密码(P):',anchor='w',underline=3,bg=WINDOWBG,fg=TEXTFG).place(x=15,y=200,width=155,height=30)
    entry_password=DEntry(password_box_window,show='●')
    entry_password.place(x=170,y=200,width=250,height=30)
    entry_password.insert(0,defaultpassword)
    entry_password.focus()
    def entry_password_focus_(nothing):
        entry_password.focus()
    password_box_window.bind('<Alt-p>',entry_password_focus_)

    def reset_password(nothing):
        entry_password.delete(0,'end')
    if autoreset_password==True:
        entry_username.bind('<<ComboboxSelected>>',reset_password)
        entry_username.bind('<KeyPress>',reset_password)



    if defaultfocus==1:
        entry_username.focus()
    else:
        entry_password.focus()

    save_cb=tk.BooleanVar()
    save_cb.set(False)
    savepas=DCheckbutton(password_box_window,text='记住我的密码(R)',underline=7,variable=save_cb,onvalue=True,offvalue=False)
    savepas.place(x=170,y=240,width=250,height=30)
    def savepas_focus_(nothing):
        savepas.focus()
    if savepassword_state==True:
        password_box_window.bind('<Alt-r>',savepas_focus_)
    else:
        savepas['state']='disabled'

    button_ok=DButton(password_box_window,text='确定',command=ok,default='active',)
    button_ok.place(x=235,y=345,width=109,height=35)#x可以改为237 #button_ok.place(x=225,y=345,width=115,height=35)

    button_cancel=DButton(password_box_window,text='取消',command=close_password_box_window)
    button_cancel.place(x=356,y=345,width=109,height=35)#x=350,width=115
    def focus_see_(nothing):
        if password_box_window.focus_get() != None:
            if password_box_window.focus_get() == button_ok:
                button_cancel['default'] = 'normal'
                button_ok['default'] = 'active'
            elif password_box_window.focus_get() == button_cancel:
                button_ok['default'] = 'normal'
                button_cancel['default'] = 'active'
            else:
                button_cancel['default'] = 'normal'
                button_ok['default'] = 'active'
    
    savepas.bind("<FocusIn>", focus_see_)
    savepas.bind("<FocusOut>", focus_see_)
    button_ok.bind("<FocusIn>", focus_see_)
    button_ok.bind("<FocusOut>", focus_see_)
    button_cancel.bind("<FocusIn>", focus_see_)
    button_cancel.bind("<FocusOut>", focus_see_)


    SetDarkTitleBar(password_box_window)
    password_box_window.wm_iconbitmap(f'{libresource}password_key_input.ico')  
    password_box_window.wait_window(password_box_window)
    try:
        return rt
    except:
        return (None,None,'CANCEL')




"""
def PasswordBox2(title='', text='', parent=None, defaultuser='', defaultfocus=1, defaultpassword='', defaultusertuple=(), savepassword_state=False, usernamestate='normal', autoreset_password=False):
    rt = (None, None, None)

    # 如果有原父窗口，先禁用
    if parent is not None:
        parent.attributes('-disabled', 'true')

    # 当前线程原来的 Desktop
    original_desktop = user32.GetThreadDesktop(win32api.GetCurrentThreadId())

    # 创建新的 Desktop
    new_desktop = user32.CreateDesktopW("PythonPasswordBoxDesktop", None, None, 0, DESKTOP_ALL, None)

    if not new_desktop:
        if parent is not None:
            parent.attributes('-disabled', 'false')
        return (None, None, None)

    # 切换到新的 Desktop
    if not user32.SwitchDesktop(new_desktop):
        user32.CloseDesktop(new_desktop)

        if parent is not None:
            parent.attributes('-disabled', 'false')

        return (None, None, None)

    def password_box_thread():
        nonlocal rt

        # 当前线程绑定到新 Desktop
        if not user32.SetThreadDesktop(new_desktop):
            return

        # 密码窗口
        password_box_window = tk.Tk()
        password_box_window.title(title)

        width = 480
        height = 395

        screenwidth = password_box_window.winfo_screenwidth()
        screenheight = password_box_window.winfo_screenheight()

        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height - 100) / 2)
        password_box_window.geometry(geometry)

        password_box_window.config(highlightthickness=0, bd=0,bg=WINDOWBG)
        password_box_window.resizable(False, False)
        password_box_window.attributes('-topmost', True)


        def close_password_box_window():
            password_box_window.destroy()
            # 切换回原来的 Desktop
            user32.SwitchDesktop(original_desktop)
            # 关闭新 Desktop
            user32.CloseDesktop(new_desktop)

        def close_password_box_window_esc(event=None):
            nonlocal rt
            rt = (None, None, None)
            close_password_box_window()

        password_box_window.protocol("WM_DELETE_WINDOW", close_password_box_window_esc)
        password_box_window.bind('<Escape>', close_password_box_window_esc)
        if IsDarkMode():
            path = f'{libresource}passwordinput_headpicture.png'
            src_img = Image.open(path).convert("RGBA")
            alpha = 64
            overlay = Image.new('RGBA', src_img.size, (0, 0, 0, alpha))
            combined_img = Image.alpha_composite(src_img, overlay)
            img = ImageTk.PhotoImage(combined_img)
        else:
            img = tk.PhotoImage(width=480, height=93, file=f'{libresource}passwordinput_headpicture.png')

        tk.Label(password_box_window, image=img, bd=0).place(x=0, y=0, width=480, height=93)

        tk.Label(password_box_window, text=text, anchor='w', bg=WINDOWBG, fg=TEXTFG).place(x=15, y=100, width=455, height=50)

        tk.Label(password_box_window, text='用户名(U):', anchor='w', underline=4, bg=WINDOWBG, fg=TEXTFG).place(x=15, y=160, width=155, height=30)

        entry_username = DCombobutton(password_box_window, values=defaultusertuple)
        entry_username.place(x=170, y=160, width=250, height=30)
        entry_username.insert(0, defaultuser)
        entry_username.config(state=usernamestate)

        def entry_username_focus_(nothing):
            entry_username.focus()

        password_box_window.bind('<Alt-u>', entry_username_focus_)

        DButton(password_box_window, text='...', state='disabled', underline=0).place(x=430, y=160, width=35, height=30)
        tk.Label(password_box_window, text='密码(P):', anchor='w', underline=3, bg=WINDOWBG, fg=TEXTFG).place(x=15, y=200, width=155, height=30)

        entry_password = DEntry(password_box_window, show='●')
        entry_password.place(x=170, y=200, width=250, height=30)
        entry_password.insert(0, defaultpassword)

        def entry_password_focus_(nothing):
            entry_password.focus()

        password_box_window.bind('<Alt-p>', entry_password_focus_)

    
        def reset_password(nothing):
            entry_password.delete(0, 'end')

        if autoreset_password:
            entry_username.bind('<<ComboboxSelected>>', reset_password)
            entry_username.bind('<KeyPress>', reset_password)

        if defaultfocus == 1:
            entry_username.focus()
        else:
            entry_password.focus()


        s = ttk.Style()
        s.configure('c.TCheckbutton', anchor='w', background=WINDOWBG, foreground=TEXTFG)

        save_cb = tk.BooleanVar()
        save_cb.set(False)

        savepas = ttk.Checkbutton(password_box_window, text='记住我的密码(R)', underline=7, style='c.TCheckbutton', variable=save_cb, onvalue=True, offvalue=False)
        savepas.place(x=170, y=240, width=250, height=30)

        def savepas_focus_(nothing):
            savepas.focus()

        if savepassword_state:
            password_box_window.bind('<Alt-r>', savepas_focus_)
        else:
            savepas['state'] = 'disabled'

        def ok(event=None):
            nonlocal rt

            if password_box_window.focus_get() is not None:
                if password_box_window.focus_get() == button_ok:
                    entry_username__ = entry_username.get()
                    entry_password__ = entry_password.get()
                    rt = (entry_username__, entry_password__, save_cb.get())
                    close_password_box_window()

                elif password_box_window.focus_get() == button_cancel:
                    rt = (None, None, None)
                    close_password_box_window()

                else:
                    entry_username__ = entry_username.get()
                    entry_password__ = entry_password.get()
                    rt = (entry_username__, entry_password__, save_cb.get())
                    close_password_box_window()

        button_ok = DButton(password_box_window, text='确定', command=ok, default='active')
        button_ok.place(x=235, y=345, width=109, height=35)

        button_cancel = DButton(password_box_window, text='取消', command=close_password_box_window)
        button_cancel.place(x=356, y=345, width=109, height=35)

        def focus_see_(nothing):
            if password_box_window.focus_get() != None:
                if password_box_window.focus_get() == button_ok:
                    button_cancel['default'] = 'normal'
                    button_ok['default'] = 'active'

                elif password_box_window.focus_get() == button_cancel:
                    button_ok['default'] = 'normal'
                    button_cancel['default'] = 'active'

                else:
                    button_cancel['default'] = 'normal'
                    button_ok['default'] = 'active'

        savepas.bind("<FocusIn>", focus_see_)
        savepas.bind("<FocusOut>", focus_see_)
        button_ok.bind("<FocusIn>", focus_see_)
        button_ok.bind("<FocusOut>", focus_see_)
        button_cancel.bind("<FocusIn>", focus_see_)
        button_cancel.bind("<FocusOut>", focus_see_)

        PlaySystemSound('WindowsUnlock')

        SetDarkTitleBar(password_box_window)

        password_box_window.wm_iconbitmap(f'{libresource}password_key_input.ico')

        # 显示密码框
        password_box_window.focus()

        # Tkinter 主循环
        password_box_window.wait_window(password_box_window)

    # 创建新 Desktop 中的 Tkinter 线程
    thread = threading.Thread(target=password_box_thread)
    thread.start()

    # 等待密码框结束
    thread.join()

    # 切换回原来的 Desktop,多一次防止出错
    user32.SwitchDesktop(original_desktop)
     #关闭新 Desktop
    user32.CloseDesktop(new_desktop)

    # 恢复父窗口
    if parent is not None:
        parent.attributes('-disabled', 'false')
        parent.focus_set()

    return rt
"""

def IsolatedDesktopPasswordBox(title='', text='', parent=None, defaultuser='', defaultfocus=1, defaultpassword='', defaultusertuple=(), savepassword_state=False, usernamestate='normal', autoreset_password=False):
    rt = (None, None, None)

    if parent is not None:
        parent.attributes('-disabled', 'true')

    original_desktop = user32.GetThreadDesktop(win32api.GetCurrentThreadId())

    new_desktop = user32.CreateDesktopW("PythonPasswordBoxDesktop", None, None, 0, DESKTOP_ALL, None)

    if not new_desktop:
        if parent is not None:
            parent.attributes('-disabled', 'false')
        return (None, None, None)

    if not user32.SwitchDesktop(new_desktop):
        user32.CloseDesktop(new_desktop)

        if parent is not None:
            parent.attributes('-disabled', 'false')

        return (None, None, None)

    def password_box_thread():
        nonlocal rt

        if not user32.SetThreadDesktop(new_desktop):
            return

        # 新桌面主窗口
        main_window = tk.Tk()
        main_window.title('')
        main_window.attributes('-topmost', True)
        main_window.overrideredirect(1)
        screenwidth = main_window.winfo_screenwidth()
        screenheight = main_window.winfo_screenheight()
        main_window.geometry(f'{screenwidth}x{screenheight}+0+0')
        main_window.config( bg=get_windows_accent_color() if get_windows_accent_color()!=None else WINDOWBG )

        def close_password_box_window():
            main_window.destroy()
            user32.SwitchDesktop(original_desktop)
            user32.CloseDesktop(new_desktop)

        def close_password_box_window_esc(event=None):
            nonlocal rt
            rt = (None, None, None)
            close_password_box_window()

        main_window.protocol("WM_DELETE_WINDOW", close_password_box_window_esc)
        main_window.bind('<Escape>', close_password_box_window_esc)




        # 容器
        password_box_window = tk.Frame(main_window,bg=WINDOWBG, width=484, height=399,bd=2,relief='solid' )
        password_box_window.pack(expand=True,)
        password_box_window.pack_propagate(False)




        img = tk.PhotoImage(width=480, height=93, file=f'{libresource}passwordinput_headpicture.png')

        tk.Label(password_box_window, image=img, bd=0).place(x=0, y=0, width=480, height=93)
        tk.Label(password_box_window, text=text, anchor='w', bg=WINDOWBG, fg=TEXTFG).place(x=15, y=100, width=455, height=50)
        tk.Label(password_box_window, text='用户名(U):', anchor='w', underline=4, bg=WINDOWBG, fg=TEXTFG).place(x=15, y=160, width=155, height=30)

        entry_username = DCombobutton(password_box_window, values=defaultusertuple)
        entry_username.place(x=170, y=160, width=250, height=30)
        entry_username.insert(0, defaultuser)
        entry_username.config(state=usernamestate)

        def entry_username_focus_(nothing):
            entry_username.focus()

        password_box_window.bind('<Alt-u>', entry_username_focus_)

        DButton(password_box_window, text='...', state='disabled', underline=0).place(x=430, y=160, width=35, height=30)
        tk.Label(password_box_window, text='密码(P):', anchor='w', underline=3, bg=WINDOWBG, fg=TEXTFG).place(x=15, y=200, width=155, height=30)

        entry_password = DEntry(password_box_window, show='●')
        entry_password.place(x=170, y=200, width=250, height=30)
        entry_password.insert(0, defaultpassword)

        def entry_password_focus_(nothing):
            entry_password.focus()

        password_box_window.bind('<Alt-p>', entry_password_focus_)

        def reset_password(nothing):
            entry_password.delete(0, 'end')

        if autoreset_password:
            entry_username.bind('<<ComboboxSelected>>', reset_password)
            entry_username.bind('<KeyPress>', reset_password)

        if defaultfocus == 1:
            entry_username.focus()
        else:
            entry_password.focus()

        s = ttk.Style()
        s.configure('c.TCheckbutton', anchor='w', background=WINDOWBG, foreground=TEXTFG)

        save_cb = tk.BooleanVar()
        save_cb.set(False)

        savepas = ttk.Checkbutton(password_box_window, text='记住我的密码(R)', underline=7, style='c.TCheckbutton', variable=save_cb, onvalue=True, offvalue=False)

        savepas.place(x=170, y=240, width=250,height=30)

        def savepas_focus_(nothing):
            savepas.focus()

        if savepassword_state:
            password_box_window.bind('<Alt-r>', savepas_focus_)
        else:
            savepas['state'] = 'disabled'

        def ok(event=None):
            nonlocal rt

            if password_box_window.focus_get() is not None:
                if password_box_window.focus_get() == button_ok:
                    entry_username__ = entry_username.get()
                    entry_password__ = entry_password.get()
                    rt = (entry_username__, entry_password__, save_cb.get())
                    close_password_box_window()

                elif password_box_window.focus_get() == button_cancel:
                    rt = (None, None, None)
                    close_password_box_window()

                else:
                    entry_username__ = entry_username.get()
                    entry_password__ = entry_password.get()
                    rt = (entry_username__, entry_password__, save_cb.get())
                    close_password_box_window()

        button_ok = DButton(password_box_window, text='确定', command=ok, default='active')
        button_ok.place(x=235, y=345, width=109, height=35)

        button_cancel = DButton(password_box_window, text='取消', command=close_password_box_window)
        button_cancel.place( x=356, y=345, width=109, height=35)

        def focus_see_(nothing):
            if password_box_window.focus_get() != None:
                if password_box_window.focus_get() == button_ok:
                    button_cancel['default'] = 'normal'
                    button_ok['default'] = 'active'

                elif password_box_window.focus_get() == button_cancel:
                    button_ok['default'] = 'normal'
                    button_cancel['default'] = 'active'

                else:
                    button_cancel['default'] = 'normal'
                    button_ok['default'] = 'active'

        savepas.bind("<FocusIn>", focus_see_)
        savepas.bind("<FocusOut>", focus_see_)
        button_ok.bind("<FocusIn>", focus_see_)
        button_ok.bind("<FocusOut>", focus_see_)
        button_cancel.bind("<FocusIn>", focus_see_)
        button_cancel.bind("<FocusOut>", focus_see_)

        PlaySystemSound('WindowsUnlock')

        SetDarkTitleBar(main_window)

        main_window.wm_iconbitmap(f'{libresource}password_key_input.ico')

        main_window.focus()

        main_window.wait_window(main_window)


    thread = threading.Thread(target=password_box_thread)
    thread.start()

    thread.join()

    user32.SwitchDesktop(original_desktop)

    user32.CloseDesktop(new_desktop)

    if parent is not None:
        parent.attributes('-disabled', 'false')
        parent.focus_set()

    return rt


class StrayIcon:
    WM_NOTIFYICON = win32con.WM_USER + 20 # 自定义消息ID

    def __init__(self, icon_path='', options=[], prompt_text='', left_click=None):
        self.icon_path = icon_path
        self.options = options
        self.prompt_text = prompt_text
        self.left_click_callback = left_click
        self.hwnd = None
        self.nid = None
        self.running = False
        self.checked_states = {} # 用于存储勾选菜单项的状态
        self.disabled_states = {} # 用于存储菜单项的禁用状态

        # Register a window class
        wc = win32gui.WNDCLASS()
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "PythonTrayIconClass"
        wc.lpfnWndProc = self._wndProc # 注册消息处理函数
        class_atom = win32gui.RegisterClass(wc)

        # Create the window (it will be hidden)
        self.hwnd = win32gui.CreateWindow(
            class_atom,
            "Python Tray Icon Window",
            win32con.WS_OVERLAPPEDWINDOW,
            0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
            0, 0, wc.hInstance, None
        )
        win32gui.UpdateWindow(self.hwnd)

        # Load icon
        self.hicon = None
        if icon_path:
            # 直接加载ICO文件，不再进行图片转换
            self.hicon = self._load_icon(icon_path) 

        # Add the icon to the system tray
        self.nid = (self.hwnd,                   # window handle
                    0,                           # icon ID
                    win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP, # flags
                    self.WM_NOTIFYICON,          # message ID
                    self.hicon,                  # icon handle
                    self.prompt_text)            # tooltip text

        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, self.nid)
        except Exception as e:
            print(f"初始化托盘图标失败: {e}")
            # 如果加载失败，可以考虑使用默认图标或退出

        # 初始化勾选和禁用状态
        for i, (text, callback, item_type) in enumerate(self.options):
            menu_id = win32con.WM_USER + 100 + i
            if item_type == 'check':
                self.checked_states[menu_id] = False
            
            if item_type != 'line': # 分隔线不需要禁用状态
                self.disabled_states[menu_id] = False # 默认所有非分隔线菜单项都是启用的

    def _load_icon(self, icon_path):
        """
        直接加载ICO文件并返回HICON句柄。
        不再进行图片转换。
        """
        if not os.path.exists(icon_path):
            # 如果文件不存在，立即抛出错误
            raise FileNotFoundError(f"图标文件找不到: {icon_path}")
        
        # 验证文件是否是ICO格式（简单检查后缀名，更严谨需读取文件头）
        if not icon_path.lower().endswith(".ico"):
            raise ValueError(f"图标文件必须是 .ico 格式: {icon_path}")

        try:
            # 直接使用win32gui加载ICO文件
            hicon = win32gui.LoadImage(
                0, 
                icon_path, # 直接传入ico文件路径
                win32con.IMAGE_ICON, 
                0, 0, # 使用0,0并结合LR_DEFAULTSIZE来加载默认尺寸
                win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            )
            
            if hicon == 0: # LoadImage 返回0表示失败
                # 进一步检查GetLastError()可以获取更详细的错误信息
                # 例如：win32api.GetLastError()
                raise FileNotFoundError(f"无法加载图标文件 '{icon_path}'，可能文件损坏或格式不正确。")
            return hicon
        except Exception as e:
            # 捕获win32gui.LoadImage可能抛出的异常
            raise FileNotFoundError(f"加载图标文件 '{icon_path}' 失败: {e}") from e

    def _wndProc(self, hwnd, msg, wparam, lparam):
        """窗口消息处理函数。"""
        if msg == self.WM_NOTIFYICON:
            if lparam == win32con.WM_LBUTTONUP: # 左键单击
                
                if self.left_click_callback:
                    self.left_click_callback()
            elif lparam == win32con.WM_RBUTTONUP: # 右键单击
                self._show_context_menu()
            return 1
        elif msg == win32con.WM_COMMAND: # 处理菜单项点击事件
            cmd_id = win32api.LOWORD(wparam)
            # 确保 cmd_id 在有效范围内，并且不是分隔线
            if (cmd_id >= win32con.WM_USER + 100 and 
                cmd_id < win32con.WM_USER + 100 + len(self.options)):

                chosen_index = cmd_id - (win32con.WM_USER + 100)
                
                # 再次检查索引有效性
                if chosen_index < len(self.options):
                    # 在调用回调之前检查是否被禁用
                    # 分隔线没有回调，这里也排除掉
                    item_type = self.options[chosen_index][2]
                    if item_type != 'line' and not self.disabled_states.get(cmd_id, False): 
                        if item_type == 'check':
                            # 切换勾选状态
                            self.checked_states[cmd_id] = not self.checked_states[cmd_id]
                        
                        callback = self.options[chosen_index][1]
                        if callback:
                            callback()
            return 1
        elif msg == win32con.WM_DESTROY:
            # 删除托盘图标并释放图标句柄
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, self.nid)
            if self.hicon and self.hicon != 0:
                win32gui.DestroyIcon(self.hicon) # 释放图标资源
            win32gui.PostQuitMessage(0) # 退出消息循环
            return 1
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _show_context_menu(self):
        """显示右键上下文菜单。"""
        menu = win32gui.CreatePopupMenu()
        for i, (text, callback, item_type) in enumerate(self.options):
            menu_id = win32con.WM_USER + 100 + i # 菜单项ID

            if item_type == 'line':
                win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, '') 
            else: # 'text' or 'check' type
                flags = win32con.MF_STRING
                if item_type == 'check' and self.checked_states.get(menu_id, False):
                    flags |= win32con.MF_CHECKED
                
                # 添加禁用标志
                # 只有非分隔线项才可能被禁用
                if self.disabled_states.get(menu_id, False):
                    flags |= win32con.MF_GRAYED # MF_GRAYED 用于禁用菜单项

                win32gui.AppendMenu(menu, flags, menu_id, text)

        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd) # 确保菜单显示在前面
        
        win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_LEFTALIGN | win32con.TPM_RIGHTBUTTON,
            pos[0], pos[1], 0, self.hwnd, None
        )
        win32gui.DestroyMenu(menu)

    def is_checked(self, option_text):
        """
        检查指定文本的勾选项是否被勾选。
        Args:
            option_text (str): 菜单项的文本。
        Returns:
            bool: 如果被勾选则返回 True，否则返回 False。
        """
        for i, (text, _, item_type) in enumerate(self.options):
            if item_type == 'check' and text == option_text:
                menu_id = win32con.WM_USER + 100 + i
                return self.checked_states.get(menu_id, False)
        return False

    def set_checked(self, option_text, state):
        """
        直接设置指定勾选项的勾选状态。
        Args:
            option_text (str): 勾选项的文本。
            state (bool): 目标状态，True 为勾选，False 为不勾选。
        Returns:
            bool: 如果成功设置状态则返回 True，否则返回 False (例如，未找到该勾选项)。
        """
        for i, (text, _, item_type) in enumerate(self.options):
            if item_type == 'check' and text == option_text:
                menu_id = win32con.WM_USER + 100 + i
                self.checked_states[menu_id] = bool(state)
                return True
        return False

    def set_state(self, option_text, state_type):
        """
        设置指定菜单项的启用/禁用状态。
        Args:
            option_text (str): 要设置的菜单项的文本。
            state_type (str): 'normal' 表示启用，'disabled' 表示禁用。
        Returns:
            bool: 如果成功设置状态则返回 True，否则返回 False (例如，未找到该菜单项)。
        """
        # 根据 state_type 确定 target_state (True 表示禁用，False 表示启用)
        target_state = False # 默认为启用 ('normal')
        if state_type == 'disabled':
            target_state = True 
        elif state_type != 'normal': # 如果传入了不支持的状态类型
            print(f"警告: 未知的状态类型 '{state_type}'。支持 'normal' 和 'disabled'。")
            return False

        found = False
        for i, (text, _, item_type) in enumerate(self.options):
            # 只有非分隔线菜单项才能被设置状态
            if item_type != 'line' and text == option_text: 
                menu_id = win32con.WM_USER + 100 + i
                # 更新 disabled_states 字典
                self.disabled_states[menu_id] = target_state
                found = True
                break
        return found

    def run(self):
        """启动消息循环，保持托盘图标活跃。"""
        self.running = True
        win32gui.PumpMessages()

    def stop(self):
        """停止托盘图标并退出。"""
        if self.running:
            win32gui.PostMessage(self.hwnd, win32con.WM_DESTROY, 0, 0)
            self.running = False

    def set_stray_icon(self, icon_path):
        """
        动态设置托盘图标。此方法现在只接受 .ico 文件。
        Args:
            icon_path (str): 新图标文件的路径 (.ico 格式)。
        Returns:
            bool: 如果成功设置图标则返回 True，否则返回 False。
        """
        try:
            # 释放旧图标句柄（如果存在且有效）
            if self.hicon and self.hicon != 0:
                win32gui.DestroyIcon(self.hicon)
            
            # 直接加载新的ICO文件
            new_hicon = self._load_icon(icon_path)
            self.hicon = new_hicon

            # 更新托盘图标
            self.nid = (self.hwnd, 0, 
                        win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                        self.WM_NOTIFYICON, 
                        self.hicon, 
                        self.prompt_text)
            
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, self.nid)
            return True
        except (FileNotFoundError, ValueError) as e:
            print(f"设置托盘图标失败: {e}")
            return False
        except Exception as e:
            print(f"设置托盘图标时发生未知错误: {e}")
            return False

    def set_text(self, original_text,new_text):
        #补充这里,修改项的文本功能
        """
        修改指定菜单项的文本。
        Args:
            original_text (str): 菜单项当前的文本。
            new_text (str): 菜单项新的文本。
        Returns:
            bool: 如果成功修改文本则返回 True，否则返回 False (例如，未找到该菜单项)。
        """
        found = False
        for i, (text, callback, item_type) in enumerate(self.options):
            if text == original_text:
                # 更新 options 列表中的元组。由于元组不可变，需要创建一个新的元组。
                self.options[i] = (new_text, callback, item_type)
                found = True
                break
        return found



class DTitleBarButton(tk.Label):
    def __init__(self, master,command=None,text='',default='normal',bg=TITLEBAR_ACTIVE,fg=TEXTFG,justify='center',anchor='center',state='normal', **kw):
        super().__init__(master,**kw)
        self.command=command
        self.bg=bg
        self.fg=fg
        self['fg']=fg
        self['bg']=bg
        self['text']=text
        self['anchor']=anchor
        self["justify"]=justify
        self._default = default
        self._state=state
        self['bd']=0
        self['relief']='solid'
        self.pack_propagate(False)
        self['takefocus']=False

        self._key_pressed = False
        self._pressed_inside=False
        self._hover = False   #  新增

        self.default_change(self._default)
        self.bind_command()
        self.bind('<Enter>',self.on_enter)
        self.bind('<Leave>',self.on_leave)
        self.bind("<KeyPress-space>", self.on_space_press)
        self.bind("<KeyRelease-space>", self.on_space_release)
        self.bind('<Tab>',self.on_space_release_esc)
        self.bind('<FocusOut>',self.on_space_release)
        self.bind('<Escape>',self.on_space_release_esc)

        self.refresh_button_look()  #  初始化刷新

        try:
            self.master.bind('<Return>',self.on_space_press_and_default,add='+')
            self.master.bind('<KeyRelease-Return>',self.on_space_release_and_default,add='+')
        except:
            pass

    def on_space_press_and_default(self,event):
        if self.default=='active':
            self.on_space_press(event)
    def on_space_release_and_default(self,event):
        if self.default=='active':
            self.on_space_release(event)

    def on_space_release_esc(self,event):
        self.on_space_release(event,focusout=True)

    def __setitem__(self, key, value):
        if key == 'default':
            self.default = value
        elif key=='state':
            self.state = value
        elif key=='command':
            self.command=value
        else:
            super().__setitem__(key, value)


            
    def configure(self, cnf=None, **kw):
        if 'default' in kw:
            new_default = kw.pop('default')
            self.default = new_default
        if 'state' in kw:
            new_state = kw.pop('state')
            self.state = new_state
        if 'bg' in kw:
            self.bg=kw['bg']
        if 'fg' in kw:
            self.fg=kw['fg']
        if 'command' in kw:
            self.command=kw['command']

        if kw or cnf:
            return super().configure(cnf, **kw)

    config = configure

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        if self._default != value:
            self._default = value
            self.default_change(value)

    def default_change(self, value):
       # self.default=value
        self.refresh_button_look()


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            self._state = value
            self.state_change(value)

    def state_change(self, value):
        #self.state=value
        self.refresh_button_look()



    # 统一外观刷新函数

    def refresh_button_look(self):
     
        bg = self.bg

        # 1. 基础 hover 状态 (未按下鼠标)
        if self._hover and not (self._pressed_inside or self._key_pressed):
            
            bg = REDTEXTFG

        # 2. 激活/按下状态 (鼠标在按钮内按下，或键盘空格按下)
        if (self._pressed_inside and self._hover) or self._key_pressed:
            bg=AlphaBlend(REDTEXTFG,self.bg,0.7)

        # 3. 特殊状态：鼠标在内部按下后，移到了按钮外部 (满足你的需求)
        elif self._pressed_inside and not self._hover:
            bg=self.bg



        self['bg'] = bg

    # =========================
    # 事件（仅改状态 + 刷新）
    # =========================

    def on_enter(self, event):
        if self.state!='disabled':
            self._hover = True
            self.refresh_button_look()

    def on_leave(self,event):
        if self.state!='disabled':
            self._hover = False
            self.refresh_button_look()

    def on_space_press(self, event):
        if self.state!='disabled':
            self._key_pressed = True
            self.refresh_button_look()

    def on_space_release(self, event,focusout=False):
        if self.state!='disabled':
            if self._key_pressed or focusout:
                self._key_pressed = False

                x, y = event.widget.winfo_pointerxy()
                widget = event.widget.winfo_containing(x, y)

                if widget != self:
                    self._hover = False

                if focusout:
                    self._pressed_inside = False   

                self.refresh_button_look()

                if self.command and not focusout:
                    self.command()

    def bind_command(self,):
        self._pressed_inside = False

        def handle_press(event):
            if self.state!='disabled':
                self._pressed_inside = True
                self.focus()
                self.refresh_button_look()

        def handle_release(event):
            if self.state!='disabled':
                x, y = event.widget.winfo_pointerxy()
                widget = event.widget.winfo_containing(x, y)

                _pressed_inside_temp=self._pressed_inside
                self._pressed_inside = False
                
                self.refresh_button_look()
                if _pressed_inside_temp and widget==self and self.command!=None:
                    self.command()

        self.bind("<Button-1>", handle_press,add='+')
        self.bind("<Button-1>",lambda _:self.focus_set(),add='+')
        self.bind("<ButtonRelease-1>", handle_release)



"""
class MessageBoxN:
    def __init__(self, parent=None, text='', title='', icon='none', title_icon='none',
                 text_true='确定', text_false='取消', button_mode=1, default_focus=1):
        '''
        parent='Toplevel'时无论如何都会创建Toplevel而不是Tk
        '''
        # __init__ 专管赋值
        self.parent = parent
        self.text = text
        self.title = title
        self.icon = icon
        self.text_true = text_true
        self.text_false = text_false
        self.button_mode = button_mode
        self.default_focus = default_focus
        self.title_icon = title_icon
        
        # 初始化返回值和必要控件引用
        self.rtn = None
        self.msg_window = None
        self.ok_button = None
        self.cancel_button = None
        self._is_closing = False  # 增加防重入标志，防止重复关闭

        # --- 新增：用于窗口拖动的状态变量 ---
        self._drag_x = 0
        self._drag_y = 0
        self._is_dragging = False



    def layout_window(self):
        #专管布局窗口
        # 窗口初始化
        if self.parent==None:
            self.msg_window = tk.Tk()
        elif self.parent=='Toplevel':
            self.msg_window=tk.Toplevel()
        else:
            self.msg_window=tk.Toplevel(self.parent) 
        self.msg_window.title(self.title)
        if self.parent:
            self.parent.attributes('-disabled', 'true')
            self.msg_window.wm_transient(self.parent)

     
        self.msg_window.protocol("WM_DELETE_WINDOW", self._close_window)
        self.msg_window['bg'] = HIGHLIGHT
        self.msg_window.overrideredirect(1)

    
        #-----处理字体
        LoadFont(f"{libresource}/segmdl2.ttf")#    
        self.Font_icon_title_bar=tkfont.Font(family='Segoe MDL2 Assets',size=8,weight='bold')


        #---主控件
        self.frame_main=tk.Frame(self.msg_window,bg=WINDOWBG)
        self.frame_main.pack(fill='both',padx=1,pady=1,expand=1)


        # -----------------标题栏
        self.frame_title_bar=tk.Frame(self.frame_main,bg=TITLEBAR_ACTIVE)
        self.frame_title_bar.place(x=0,y=0,width=390,height=35)

        icon_offset_x = 5 if self.title_icon in [None,'none',''] else 30

        self.label_small_icon=tk.Label(self.frame_title_bar,bg=TITLEBAR_ACTIVE,anchor='center')
        
        if self.title_icon not in [None,'none','']:
            self.label_small_icon.place(x=3,y=0,width=30,height=35)
            SetImageTk(self.label_small_icon,f"{libresource}{self.title_icon}.ico", img_size=(20, 20))

        self.label_title=tk.Label(self.frame_title_bar,bg=TITLEBAR_ACTIVE,fg=TEXTFG,anchor='w',text=self.title)
        self.label_title.place(x=icon_offset_x,y=0,width=390-icon_offset_x-60,height=35)

        old_font = tkfont.Font(font=self.label_title.cget("font"))
        new_font = old_font.copy()
        new_font.configure(size=old_font.cget("size") ,weight='bold' )
        self.label_title.configure(font=new_font)

        self.button_close=DTitleBarButton(self.frame_title_bar,text='\uE106',anchor='center',font=self.Font_icon_title_bar,command=self._close_window,bg=TITLEBAR_ACTIVE)
        self.button_close.place(x=330,y=0,width=60,height=35)


        # --- 新增：为标题栏和标题文本绑定拖动事件 ---
        self.frame_title_bar.bind('<ButtonPress-1>', self.start_move)
        self.frame_title_bar.bind('<B1-Motion>', self.on_move)
        self.frame_title_bar.bind('<ButtonRelease-1>', self.stop_move)
        
        self.label_title.bind('<ButtonPress-1>', self.start_move)
        self.label_title.bind('<B1-Motion>', self.on_move)
        self.label_title.bind('<ButtonRelease-1>', self.stop_move)

        self.label_small_icon.bind('<ButtonPress-1>', self.start_move)
        self.label_small_icon.bind('<B1-Motion>', self.on_move)
        self.label_small_icon.bind('<ButtonRelease-1>', self.stop_move)


        #---主窗口
        self.frame_window=tk.Frame(self.frame_main,bg=WINDOWBG)
        self.frame_window.place(x=0,y=35,width=390)

        # 大图标区域
        label_icon = tk.Label(self.frame_window, anchor='center', bg=WINDOWBG)
        label_icon.place(x=20, y=20, width=50, height=50)

        # 隐藏Frame用于计算文本高度
        frame_calculate = tk.Frame(self.frame_window, bd=0)
        frame_calculate.place(x=-20000, y=-20000, width=290, height=20000)

        label_calculate = tk.Label(frame_calculate, bg=WINDOWBG, fg=TEXTFG, 
                                   wraplength=280, text=self.text, justify='left', anchor='nw')
        label_calculate.pack(fill='x', side='top')
        label_text_height = max(label_calculate.winfo_reqheight(), 90)
        frame_calculate.destroy()

        # 实际文本区域
        label_text = tk.Label(self.frame_window, bg=WINDOWBG, fg=TEXTFG, 
                              wraplength=280, text=self.text, justify='left', anchor='nw')
        label_text.place(x=80, y=20, width=290, height=label_text_height)

        if self.icon != 'none':
            SetImageTk(label_icon, f"{libresource}/{self.icon}.ico", img_size=(48, 48))

        # 按钮位置及窗口高度自适应
        initial_window_width = 392
        screen_width = self.msg_window.winfo_screenwidth()
        screen_height = self.msg_window.winfo_screenheight()
        pos_x = (screen_width - initial_window_width) // 2
        buttons_y = 35 + label_text_height
        new_window_height = buttons_y + 92-5
        pos_y_new = (screen_height - new_window_height) // 2
        self.msg_window.geometry(f'{initial_window_width}x{new_window_height}+{pos_x}+{pos_y_new}')
        frame_window_height =buttons_y+50
        self.frame_window.place(height=frame_window_height)

        # 按钮模式布局
        if self.button_mode == 1:
            self.msg_window.bind('<Escape>', self._handle_key)
            
            self.ok_button = DButton(self.frame_window, text=self.text_true, 
                                     command=lambda: self._return_value(True), default='active')
            self.ok_button.place(x=290, y=buttons_y, width=80, height=30)
            self.ok_button.focus()
        elif self.button_mode == 2:
            self.msg_window.bind('<Escape>', lambda e: self._return_value(None))

            self.ok_button = DButton(self.frame_window, text=self.text_true, 
                                     command=lambda: self._return_value(True))
            self.ok_button.place(x=190, y=buttons_y, width=80, height=30)

            self.cancel_button = DButton(self.frame_window, text=self.text_false, 
                                         command=lambda: self._return_value(False))
            self.cancel_button.place(x=290, y=buttons_y, width=80, height=30)

            self.ok_button.bind("<FocusIn>", self._update_button_focus)
            self.cancel_button.bind("<FocusIn>", self._update_button_focus)
            self.ok_button.bind("<FocusOut>", self._update_button_focus)
            self.cancel_button.bind("<FocusOut>", self._update_button_focus)

            # 设置默认焦点
            focus_btn = self.ok_button if self.default_focus == 1 else self.cancel_button
            focus_btn.focus()
            focus_btn['default'] = 'active'
        else:
            raise ValueError("button_mode 只能为 1 或 2")

        
        #----------窗口事件绑定
        self.msg_window.bind('<FocusIn>', self._focus_in)
        self.msg_window.bind('<FocusOut>', self._focus_out)
        self.all_widgets = self.get_all_widgets(self.msg_window)
        # 为所有控件绑定 FocusIn 和 FocusOut 事件
        for widget in self.all_widgets:

            widget.bind('<FocusIn>', self._focus_in,add='+')
            widget.bind('<FocusOut>', self._focus_out,add='+')
        
        # --------声音提示映射
        beep_map = {
            'question': win32con.MB_ICONQUESTION, 
            'safe_warning': win32con.MB_ICONWARNING,
            'error': win32con.MB_ICONERROR, 
            'stop': win32con.MB_ICONERROR, 
            'warning': win32con.MB_ICONWARNING,
            'info': win32con.MB_ICONINFORMATION, 
            'correct': win32con.MB_ICONINFORMATION,
            'none': 0
        }

        self.msg_window.wm_iconbitmap(f"{libresource}icon.ico")
        SetDarkTitleBar(self.msg_window)
        win32api.MessageBeep(beep_map.get(self.icon, 0)) 

        self.msg_window.wait_window(self.msg_window)

    def run_message(self,):
        self.layout_window()
        return self.rtn

    def _close_window(self):
        # 防重入，避免多次点击或多次事件触发导致重复销毁
        if self._is_closing:
            return
        self._is_closing = True

        # 先解绑事件，防止在销毁过程中触发残留回调
        if self.msg_window:
            self.msg_window.unbind('<Escape>')
        if self.ok_button:
            self.ok_button.unbind("<FocusIn>")
            self.ok_button.unbind("<FocusOut>")
        if self.cancel_button:
            self.cancel_button.unbind("<FocusIn>")
            self.cancel_button.unbind("<FocusOut>")

        # 【关键修复】先恢复父窗口状态和焦点，最后再销毁自身
        # 因为 focus_set() 会触发 FocusIn/FocusOut 事件，如果窗口已销毁就会报错
        if self.parent:
            self.parent.attributes('-disabled', 'false')
            self.parent.focus_set()
            
        if self.msg_window:
            self.msg_window.destroy()

    def _return_value(self, value):
        # 设置返回值并关闭窗口
        self.rtn = value
        self._close_window()

    def _handle_key(self, event):
        # 如果正在关闭，直接忽略后续按键事件
        if self._is_closing:
            return
            
        # 处理键盘事件
        focused = self.msg_window.focus_get()
        if event.keysym == 'Escape':
            self._return_value(None)
        elif focused in (self.ok_button, None):
            self._return_value(True)
        elif focused == self.cancel_button:
            self._return_value(False)

    def _update_button_focus(self, event=None):
        # 如果正在关闭，直接忽略焦点更新事件
        if self._is_closing:
            return
            
        # 更新按钮的默认激活状态样式
        if self.button_mode == 2:
            if self.msg_window.focus_get() == self.cancel_button:
                self.ok_button['default'], self.cancel_button['default'] = 'normal', 'active'
            else:  # focus_get() == ok_button
                self.ok_button['default'], self.cancel_button['default'] = 'active', 'normal'

    def _focus_in(self,event=None):
        self.msg_window['bg']=HIGHLIGHT
        self.frame_title_bar['bg']=TITLEBAR_ACTIVE
        self.label_small_icon['bg']=TITLEBAR_ACTIVE
        self.button_close.config(bg=TITLEBAR_ACTIVE)
        self.label_title['bg']=TITLEBAR_ACTIVE
        
    def _focus_out(self,event=None):
        self.msg_window['bg']=WINDOWBG
        self.frame_title_bar['bg']=TITLEBAR_INACTIVE
        self.label_small_icon['bg']=TITLEBAR_INACTIVE
        self.button_close.config(bg=TITLEBAR_INACTIVE)
        self.label_title['bg']=TITLEBAR_INACTIVE

    # --- 新增：窗口拖动相关方法 ---
    def start_move(self, event):
        self._focus_in()
        #记录鼠标按下时的初始位置
        self._drag_x = event.x
        self._drag_y = event.y
        self._is_dragging = True
        # 如果事件源自 label_title，阻止事件向 frame_title_bar 冒泡，避免重复触发
        if event.widget == self.label_title:
            return "break"

    def on_move(self, event):
        #鼠标移动时，计算偏移量并更新窗口位置
        if not self._is_dragging:
            return
            
        # 获取鼠标在屏幕上的绝对坐标
        x = self.msg_window.winfo_x() + (event.x - self._drag_x)
        y = self.msg_window.winfo_y() + (event.y - self._drag_y)
        
        # 更新窗口位置
        self.msg_window.geometry(f'+{x}+{y}')
        
        if event.widget == self.label_title:
            return "break"

    def stop_move(self, event):
        #鼠标释放时，结束拖动
        self._is_dragging = False
        if event.widget == self.label_title:
            return "break"
        
    def get_all_widgets(self, widget):
        #获取指定控件及其所有子控件
        widgets = [widget]
        if isinstance(widget, (tk.Frame, tk.Toplevel)):
            for child in widget.winfo_children():
                widgets.extend(self.get_all_widgets(child))
        return widgets
"""



class ToastNotification:
    def __init__(self,parent=None,icon='none',title='',text_blod='粗体大字',text_thin='普通小字',image='none',
                 more_option_command=None,stretch_command='DETACHWINDOW',stretch_command_in_mainthread=True,
                 stay_time=0):
        self.parent=parent
        self.icon=icon
        self.title=title
        self.text_blod=text_blod
        self.text_thin=text_thin
        self.image=image
        self.more_option_command=more_option_command
        self.stretch_command=stretch_command
        self.stretch_command_in_mainthread=stretch_command_in_mainthread
        self.stay_time=stay_time

        self.is_showing_label_close_tip = False
        self.close_tip_animation_running = False  # 标记动画是否正在运行
        self.close_tip_animation_completed = False 
        self.close_tip_shrink_animation_running = False  # 标记缩小动画是否正在运行
        self.close_tip_initial_width = 0  # 保存标签初始宽度，用于缩小动画
        self.close_toast_after=False#在缩小动画之后是否需要关闭窗口,与stretch_command相呼应
        #是否拉伸窗口超过一个阈值
        # 注意：使用 property 装饰器时，不能在 __init__ 中直接给 self.stretch_window 赋值，
        # 否则会触发装饰器的 setter，而此时 _on_stretch_window_changed 方法可能还未完全绑定。
        # 所以我们直接给内部私有变量赋初始值。
        self._stretch_window = False
        self.stretch_activate_animation_running = False  #新增
        self.stretch_activate_animation_completed = False  
        self.stretch_deactivate_animation_running = False  
        self.stretch_deactivate_initial_width = 0  
        self.stretch_deactivate_initial_height = 0 
    def _auto_close_timer(self):
        """如果 stay_time > 0，则自动关闭通知窗口"""
        if self.stay_time > 0:
            self.ToastNotification_window.after(int(self.stay_time * 1000), self.close_toast)

    def layout_window(self,):
        self.ToastNotification_window=tk.Tk()if self.parent==None else tk.Toplevel(self.parent)
        self.ToastNotification_window.overrideredirect(1)
        self.ToastNotification_window.config(bd=0,relief='solid',bg=HIGHLIGHT,highlightthickness=0)
        self.ToastNotification_window.attributes('-topmost',True)


        LoadFont(f"{libresource}/segmdl2.ttf")#    
        self.Font_icon_title_bar=tkfont.Font(family='Segoe MDL2 Assets',size=8)#,weight='bold')

        self.Frame_main=tk.Frame(self.ToastNotification_window,bg=TOASTBG,bd=0)

        #-----------------标题栏
        title_bar_icon_offset_x=35 if self.icon not in [None,'none',''] else 0
        title_bar_more_option_offset_x=30 if self.more_option_command!=None else 0

        Frame_title_bar=tk.Frame(self.Frame_main,bg=TOASTBG,)
        Frame_title_bar.place(x=20,y=20,width=420,height=30)

        if self.icon not in [None,'none','']:
            Label_small_icon=tk.Label(Frame_title_bar,bg=TOASTBG,anchor='center')
            Label_small_icon.place(x=0,y=0,width=30,height=30)
            SetImageTk(Label_small_icon,f"{libresource}{self.icon}.ico", img_size=(24, 24))

        Label_title=tk.Label(Frame_title_bar,bg=TOASTBG,fg=TEXTFG,anchor='w',text=self.title)
        Label_title.place(x=title_bar_icon_offset_x,y=0,width=420-title_bar_icon_offset_x-title_bar_more_option_offset_x,height=30)

        if self.more_option_command!=None:
            self.Button_more_option=DToastButton(Frame_title_bar,text='',font=self.Font_icon_title_bar,command=self.more_option_command)
            self.Button_more_option.place(x=360,y=0,width=30,height=30)
        else:
            self.Button_more_option=None

        Button_close=DToastButton(Frame_title_bar,text='\uE106',font=self.Font_icon_title_bar,command=self.close_toast)
        Button_close.place(x=390,y=0,width=30,height=30)

        #------------------------文字区
        Frame_text=tk.Frame(self.Frame_main,bg=TOASTBG)
        
        if self.image not in ['none','',None]:
            text_frame_offset_x=80
            Label_image=tk.Label(Frame_text,anchor='center',bg=TOASTBG)
            Label_image.place(x=0,y=0,width=70,height=80)
            SetImageTk(Label_image,self.image,[64,64])
        else:
            text_frame_offset_x=0

        '''Frame_cauculate=tk.Frame(self.Frame_main,bd=0)
        Frame_cauculate.place(x=-20000, y=-20000, width=420-text_frame_offset_x, height=20000)
        Cauculate_Label_text_blod=tk.Label(Frame_cauculate,text=self.text_blod,bg=TOASTBG,fg=TEXTFG,wraplength=415-text_frame_offset_x,justify='left',anchor='w')
        self.set_label_bold_and_big(Cauculate_Label_text_blod)
        Cauculate_Label_text_blod.pack(fill='x',side='top')
        height_Label_text_blod=Cauculate_Label_text_blod.winfo_reqheight()
        Frame_cauculate.destroy()'''

        Label_text_blod=tk.Label(Frame_text,text=self.text_blod,bg=TOASTBG,fg=TEXTFG,wraplength=415-text_frame_offset_x,justify='left',anchor='w')
        self.set_label_bold_and_big(Label_text_blod)
        Label_text_blod.place(x=text_frame_offset_x,y=0,width=420-text_frame_offset_x,)
        height_Label_text_blod=Label_text_blod.winfo_reqheight()
        Label_text_blod.place(height=height_Label_text_blod)


        '''Frame_cauculate= tk.Frame(self.Frame_main,bd=0)
        Frame_cauculate.place(x=-20000, y=-20000, width=420-text_frame_offset_x, height=20000)
        Cauculate_Label_text_thin=tk.Label(Frame_cauculate,text=self.text_thin,bg=TOASTBG,fg=SECONDARYTEXTFG,wraplength=415-text_frame_offset_x,justify='left',anchor='w')
        self.set_label_big(Cauculate_Label_text_thin)
        Cauculate_Label_text_thin.pack(fill='x',side='top')
        height_Label_text_thin=Cauculate_Label_text_thin.winfo_reqheight()
        Frame_cauculate.destroy()'''

        Label_text_thin=tk.Label(Frame_text,text=self.text_thin,bg=TOASTBG,fg=SECONDARYTEXTFG,wraplength=415-text_frame_offset_x,justify='left',anchor='w')
        self.set_label_big(Label_text_thin)
        Label_text_thin.place(x=text_frame_offset_x,y=height_Label_text_blod,width=420-text_frame_offset_x,)
        height_Label_text_thin=Label_text_thin.winfo_reqheight()
        Label_text_thin.place(height=height_Label_text_thin)


        
        if self.image not in ['none','',None]:
            self.all_height=90+max(height_Label_text_thin+height_Label_text_blod,80)
            Frame_text.place(x=20,y=70,width=420,height=max(height_Label_text_thin+height_Label_text_blod,80))
        else:
            self.all_height=90+height_Label_text_thin+height_Label_text_blod
            Frame_text.place(x=20,y=70,width=420,height=height_Label_text_blod+height_Label_text_thin)

        self.Label_close_tip=tk.Label(self.ToastNotification_window,text='\uF3B1',bg=TOASTBG,fg=TEXTFG,font=self.Font_icon_title_bar)
        self.set_label_bold_and_big(self.Label_close_tip,add_size=36)
        self.Label_close_tip.place(x=-20000,y=-20000,width=1,height=1)
        self.Label_close_tip.lift()

        self.Label_stretch_window_tip=tk.Label(self.ToastNotification_window,text='\uF714',bg=TOASTBG,fg=TEXTFG,font=self.Font_icon_title_bar)
        self.set_label_bold_and_big(self.Label_stretch_window_tip,add_size=42)
        self.Label_stretch_window_tip.place(x=-20000,y=-20000,width=1,height=1)
        self.Label_stretch_window_tip.lift()

        #self.Label_stay_time_tip=tk.Label(self.Frame_main,bg=GREENLIGHT)
        #self.Label_stay_time_tip.place(x=0,y=0,width=460,height=3)

        self.traverse_widgets_bind(self.ToastNotification_window)#防止同时触发两个事件
        self.Frame_main.bind('<Enter>',self.enter_frame_main)
        self.Frame_main.bind('<Leave>',self.leave_frame_main) 

    def enter_frame_main(self,event=None):
        if self.more_option_command:
            self.Button_more_option.config(text='\uE10C')

    def leave_frame_main(self,event=None):
        if self.more_option_command:
            self.Button_more_option.config(text='')  

    def traverse_widgets_bind(self,parent):
        
        #递归遍历父控件下的所有子控件
        
        for widget in parent.winfo_children():
            # 1. 在这里编写你对控件的操作逻辑
            #print(f"控件对象: {widget}, 控件类型: {type(widget).__name__}")
            
            if not isinstance(widget, DToastButton,):
                widget.bind('<Button-1>', self.mouse_down)
                widget.bind("<B1-Motion>", self.drag, add='+')
                widget.bind("<ButtonRelease-1>", self.mouse_up)  # 新增松开鼠标绑定
            # 2. 如果当前控件还有子控件（比如它是一个 Frame），则递归遍历它
            if widget.winfo_children():
                self.traverse_widgets_bind(widget)

    def mouse_down(self, event=None):
        # 记录鼠标按下时的屏幕绝对坐标
        self.mouse_down_x = event.x_root
        self.mouse_down_y = event.y_root
        
        # 记录窗口初始的几何状态（用于拖拽时计算基准，以及松开时瞬间恢复）
        self.init_window_x = self.ToastNotification_window.winfo_x()
        self.init_window_y = self.ToastNotification_window.winfo_y()
        self.init_window_w = self.ToastNotification_window.winfo_width()
        self.init_window_h = self.ToastNotification_window.winfo_height()

    def drag(self, event=None):
        # 鼠标末坐标 - 初坐标
        delta_x = event.x_root - self.mouse_down_x
        delta_y = event.y_root - self.mouse_down_y

        # --- 计算勾股定理距离并判断 stretch_window 状态 ---
        distance = (delta_x**2 + delta_y**2)**0.5
        new_stretch_state = True if (delta_x < 0 and distance > 500) else False
        
        # 【核心改变】直接给 self.stretch_window 赋值即可！
        # 装饰器会自动拦截赋值操作，判断是否改变，并在改变后触发 _on_stretch_window_changed
        self.stretch_window = new_stretch_state

        # delta_x > 0 执行单一向右运动，否则调整大小
        if delta_x > 0:
            # 向右：不调整大小与纵向位移，只让窗口随鼠标x差值而位移
            new_x = self.init_window_x + delta_x
            new_y = self.init_window_y
            new_w = self.init_window_w
            new_h = self.init_window_h
            self.ToastNotification_window.geometry(f'{new_w}x{new_h}+{new_x}+{new_y}')
            
            if delta_x > 200:
                # 获取工作区信息
                monitor = win32api.MonitorFromPoint((0, 0))
                info = win32api.GetMonitorInfo(monitor)
                work_area_x = info["Work"][0]
                work_area_width = info["Work"][2]

                # 计算标签目标宽度
                window_x = self.ToastNotification_window.winfo_x() + 2
                target_width = work_area_x + work_area_width - window_x + 20
                
                # 如果动画未运行且未完成，则启动动画
                if not self.close_tip_animation_running and not self.close_tip_animation_completed:
                    self.close_tip_animation_running = True
                    self._animate_close_tip(0, target_width)
                # 如果动画已完成，则直接更新标签大小
                elif self.close_tip_animation_completed:
                    self.Label_close_tip.place(x=1, y=1, width=target_width, height=self.all_height)
                    self.Label_close_tip.lift()
                # 如果动画正在运行，则更新目标宽度
                elif self.close_tip_animation_running:
                    self.close_tip_target_width = target_width
                
            elif 0 < delta_x <= 200:
                # 如果动画正在运行或已完成，则启动缩小动画
                if self.close_tip_animation_running or self.close_tip_animation_completed:
                    # 停止展开动画
                    self.close_tip_animation_running = False
                    self.close_tip_animation_completed = False
                    
                    # 获取当前标签宽度作为缩小动画的初始宽度
                    current_width = self.Label_close_tip.winfo_width()
                    if current_width > 1:  # 确保标签当前是可见的
                        self.close_tip_initial_width = current_width
                        self.close_tip_shrink_animation_running = True
                        self._animate_close_tip_shrink(0)
        else:
            # 向左 (含正上、正下、左上、左下)：需要调整大小
            if delta_y <= 0:
                # 向左上角(含正上方,正左方向)：右下角点保持不变
                fixed_right_x = self.init_window_x + self.init_window_w
                fixed_bottom_y = self.init_window_y + self.init_window_h
                
                new_x = self.init_window_x + delta_x
                new_y = self.init_window_y + delta_y
                
                new_w = fixed_right_x - new_x
                new_h = fixed_bottom_y - new_y
                
                new_w = max(new_w, 50)
                new_h = max(new_h, 50)
                if new_w == 50: new_x = fixed_right_x - 50
                if new_h == 50: new_y = fixed_bottom_y - 50

                self.ToastNotification_window.geometry(f'{int(new_w)}x{int(new_h)}+{int(new_x)}+{int(new_y)}')
                
            else:
                # 向左下方(包含正下方向)：右上角点保持静止
                fixed_right_x = self.init_window_x + self.init_window_w
                fixed_top_y = self.init_window_y
                
                new_x = self.init_window_x + delta_x
                new_y = fixed_top_y
                
                new_w = fixed_right_x - new_x
                new_h = (self.init_window_y + self.init_window_h + delta_y) - fixed_top_y
                
                new_w = max(new_w, 50)
                new_h = max(new_h, 50)
                if new_w == 50: new_x = fixed_right_x - 50
                if new_h == 50: new_y = fixed_top_y + 50
                
                self.ToastNotification_window.geometry(f'{int(new_w)}x{int(new_h)}+{int(new_x)}+{int(new_y)}')

    def mouse_up(self, event=None):
        delta_x = event.x_root - self.mouse_down_x
        if callable(self.stretch_command) and self.stretch_window: 
            ctypes.windll.user32.SetWindowLongW(ctypes.windll.user32.GetWindowLongW(self.ToastNotification_window.winfo_id(), -8),win32con.GWL_EXSTYLE,
                                                 win32con.WS_EX_TRANSPARENT | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST)
            if self.stretch_command_in_mainthread:
                self.stretch_command()
            else:
                self.ToastNotification_window.after(1,self.stretch_command) 
            self.close_toast_after=True
            self.bounce_back_animation()
            return 
        self.stretch_window=False#必须放在callable判断逻辑之后
        
       # 判断是否向右拖动超过200像素(你修改的阈值)
        if delta_x > 200:
            # 超过阈值，触发关闭动画，不恢复原状
            self.close_toast()
        elif delta_x <= 0:
            # 【新增】向左拖动松开，触发回弹动画
            self.bounce_back_animation()
        else:
            self.bounce_back_right_animation()

        # 清理临时属性
        # if hasattr(self, 'init_window_x'):
        # del self.init_window_x, self.init_window_y, self.init_window_w, self.init_window_h

    def _animate_close_tip(self, current_step, initial_target_width):
        
        #为Label_close_tip添加从左往右宽度逐渐增大的动画
        #使用缓动函数: eased = 1 - (1 - t) ** 4
        #目标宽度会随着窗口拖动实时更新
        
        if not self.close_tip_animation_running:
            return  # 如果动画被停止，则退出
        
        # 保存初始目标宽度，用于计算动画进度
        if not hasattr(self, '_initial_target_width'):
            self._initial_target_width = initial_target_width
            
        # 获取当前实时目标宽度
        monitor = win32api.MonitorFromPoint((0, 0))
        info = win32api.GetMonitorInfo(monitor)
        work_area_x = info["Work"][0]
        work_area_width = info["Work"][2]
        window_x = self.ToastNotification_window.winfo_x() + 2
        current_target_width = work_area_x + work_area_width - window_x + 20
        
        total_steps = 30  # 动画总帧数
        t = min(current_step / total_steps, 1.0)  # 归一化进度 0→1
        
        # 使用指定的缓动函数
        eased = 1 - (1 - t) ** 4
        
        # 计算当前宽度，使用实时更新的目标宽度
        current_width = int(current_target_width * eased)
        
        # 更新标签位置和大小
        self.Label_close_tip.place(x=1, y=1, width=current_width, height=self.all_height)
        self.Label_close_tip.lift()
        
        # 如果动画未完成，则继续下一帧
        if t < 1.0:
            self.ToastNotification_window.after(8, lambda: self._animate_close_tip(current_step + 1, initial_target_width))
        else:
            self.close_tip_animation_running = False  # 动画完成，标记为未运行
            self.close_tip_animation_completed = True  # 标记动画已完成
            # 清除临时变量
            if hasattr(self, '_initial_target_width'):
                del self._initial_target_width

    def _animate_close_tip_shrink(self, current_step):
        
        #为Label_close_tip添加从右往左宽度逐渐缩小的动画
        #使用缓动函数: eased = 1 - (1 - t) ** 4
        
        if not self.close_tip_shrink_animation_running:
            return  # 如果动画被停止，则退出
        
        total_steps = 30  # 动画总帧数
        t = min(current_step / total_steps, 1.0)  # 归一化进度 0→1
        
        # 使用指定的缓动函数
        eased = 1 - (1 - t) ** 2
        
        # 计算当前宽度，从初始宽度缩小到0
        current_width = int(self.close_tip_initial_width * (1 - eased))-2
      
        
        # 更新标签位置和大小
        self.Label_close_tip.place(x=1, y=1, width=current_width, height=self.all_height)
        self.Label_close_tip.lift()
        
        # 如果动画未完成，则继续下一帧
        if t < 1.0:
            self.ToastNotification_window.after(8, lambda: self._animate_close_tip_shrink(current_step + 1))
        else:
            self.close_tip_shrink_animation_running = False  # 动画完成，标记为未运行
            # 隐藏标签
            self.Label_close_tip.place(x=-20000, y=-20000, width=1, height=1)

    def bounce_back_animation(self,):
        if self.close_toast_after:
            self.stretch_window=False 
        #向左拖动松开后的回弹动画
        # 初始化动画参数
        if not hasattr(self, '_bounce_step'):
            self._bounce_step = 0
            self._bounce_total_steps = 30  # 回弹动画总帧数，可调
            
            # 记录当前变形的状态作为起点
            self._bounce_start_x = self.ToastNotification_window.winfo_x()
            self._bounce_start_y = self.ToastNotification_window.winfo_y()
            self._bounce_start_w = self.ToastNotification_window.winfo_width()
            self._bounce_start_h = self.ToastNotification_window.winfo_height()
            
            # 记录初始状态作为终点
            self._bounce_target_x = self.init_window_x
            self._bounce_target_y = self.init_window_y
            self._bounce_target_w = self.init_window_w
            self._bounce_target_h = self.init_window_h
            
            # 计算需要恢复的差值
            self._bounce_dx = self._bounce_target_x - self._bounce_start_x
            self._bounce_dy = self._bounce_target_y - self._bounce_start_y
            self._bounce_dw = self._bounce_target_w - self._bounce_start_w
            self._bounce_dh = self._bounce_target_h - self._bounce_start_h

        self._bounce_step += 1
        t = min(self._bounce_step / self._bounce_total_steps, 1.0)
        
        # 你要求的回弹函数: 1 - (1 - t) ** 4
        # 这是一个 EaseOutQuart 缓动，开始快然后慢，回弹感很自然
        eased = 1 - (1 - t) ** 4
        
        # 计算当前帧的几何状态
        cur_x = int(self._bounce_start_x + self._bounce_dx * eased)
        cur_y = int(self._bounce_start_y + self._bounce_dy * eased)
        cur_w = int(self._bounce_start_w + self._bounce_dw * eased)
        cur_h = int(self._bounce_start_h + self._bounce_dh * eased)
        
        self.ToastNotification_window.geometry(f'{cur_w}x{cur_h}+{cur_x}+{cur_y}')
        #self.ToastNotification_window.update()
        
        # 动画结束，清理临时变量
        if t >= 1.0:
            try:
                del self._bounce_step
                del self._bounce_total_steps
                del self._bounce_start_x, self._bounce_start_y, self._bounce_start_w, self._bounce_start_h
                del self._bounce_target_x, self._bounce_target_y, self._bounce_target_w, self._bounce_target_h
                del self._bounce_dx, self._bounce_dy, self._bounce_dw, self._bounce_dh
            except:
                pass

            if self.close_toast_after:
                self.close_toast() 
            return
            
        self.ToastNotification_window.after(8, self.bounce_back_animation) # 约60fps

    def bounce_back_right_animation(self):
        # 向右拖动松开后的回弹动画
        # 初始化动画参数
        if not hasattr(self, '_bounce_right_step'):
            self._bounce_right_step = 0
            self._bounce_right_total_steps = 30  # 回弹动画总帧数，可调
            
            # 记录当前变形的状态作为起点
            self._bounce_right_start_x = self.ToastNotification_window.winfo_x()
            self._bounce_right_start_y = self.ToastNotification_window.winfo_y()
            self._bounce_right_start_w = self.ToastNotification_window.winfo_width()
            self._bounce_right_start_h = self.ToastNotification_window.winfo_height()
            
            # 记录初始状态作为终点
            self._bounce_right_target_x = self.init_window_x
            self._bounce_right_target_y = self.init_window_y
            self._bounce_right_target_w = self.init_window_w
            self._bounce_right_target_h = self.init_window_h
            
            # 计算需要恢复的差值
            self._bounce_right_dx = self._bounce_right_target_x - self._bounce_right_start_x
            self._bounce_right_dy = self._bounce_right_target_y - self._bounce_right_start_y
            self._bounce_right_dw = self._bounce_right_target_w - self._bounce_right_start_w
            self._bounce_right_dh = self._bounce_right_target_h - self._bounce_right_start_h

        self._bounce_right_step += 1
        t = min(self._bounce_right_step / self._bounce_right_total_steps, 1.0)
        
        # 你要求的回弹函数: 1 - (1 - t) ** 8
        # 这是一个更平滑的 EaseOut 缓动，回弹感更柔和
        eased = 1 - (1 - t) ** 8
        
        # 计算当前帧的几何状态
        cur_x = int(self._bounce_right_start_x + self._bounce_right_dx * eased)
        cur_y = int(self._bounce_right_start_y + self._bounce_right_dy * eased)
        cur_w = int(self._bounce_right_start_w + self._bounce_right_dw * eased)
        cur_h = int(self._bounce_right_start_h + self._bounce_right_dh * eased)
        
        self.ToastNotification_window.geometry(f'{cur_w}x{cur_h}+{cur_x}+{cur_y}')
        #self.ToastNotification_window.update()
        
        # 动画结束，清理临时变量
        if t >= 1.0:
            try:
                del self._bounce_right_step
                del self._bounce_right_total_steps
                del self._bounce_right_start_x, self._bounce_right_start_y, self._bounce_right_start_w, self._bounce_right_start_h
                del self._bounce_right_target_x, self._bounce_right_target_y, self._bounce_right_target_w, self._bounce_right_target_h
                del self._bounce_right_dx, self._bounce_right_dy, self._bounce_right_dw, self._bounce_right_dh
            except:pass
            return
            
        self.ToastNotification_window.after(8, self.bounce_back_right_animation)
    
    def run_toast(self):
        self.layout_window()#必须放在这里,否则会报错

        PlaySystemSound('Notification.Default')
        self.Frame_main.place(x=1,y=1,width=460,height=self.all_height)
        
        #---一次运算与显示,防止降低性能
        work_area_x,work_area_y,work_area_width,work_area_height=GetWorkArea()
        self.window_target_x=work_area_x+work_area_width-490
        self.window_start_x=work_area_x+work_area_width+20
        self.window_target_y=work_area_y+work_area_height-self.all_height-20

        self.ToastNotification_window.geometry(f'462x{self.all_height + 2}')
        self.ToastNotification_window.update_idletasks()   # 强制计算一次真实尺寸
        self.convert_place_to_relative(self.Frame_main,462,self.all_height + 2,)
        self.show_window_animation()
        ctypes.windll.user32.SetWindowLongW(ctypes.windll.user32.GetWindowLongW(self.ToastNotification_window.winfo_id(), -8),win32con.GWL_EXSTYLE, win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST)

        self._auto_close_timer()
        self.ToastNotification_window.wait_window()

    def show_window_animation(self):
        # 初始化（只在第一次执行时做）
        if not hasattr(self, '_anim_step'):
            self._anim_step = 0
            self._total_steps = 50          # 总帧数，可调（越大越慢）
            self._start_x = self.window_start_x
            self._target_x = self.window_target_x
            self._distance = self._start_x - self._target_x   # 正数

        self._anim_step += 1
        t = min(self._anim_step / self._total_steps, 1.0)   # 归一化进度 0→1
        s = 2.8          # 过冲强度，越大越过越多、回弹越明显
        eased = 1 + (t - 1)**5 * (s + 1) + (t - 1)**4 * s

        # 计算当前 x
        self.window_present_x = int(self._start_x - self._distance * eased)
        self.ToastNotification_window.geometry(f'462x{self.all_height + 2}+{self.window_present_x}+{self.window_target_y}')
        #self.ToastNotification_window.update()

        if t >= 1.0:
            # 动画结束，清理临时变量
            del self._anim_step
            del self._total_steps
            del self._start_x
            del self._target_x
            del self._distance
            return
        self.window_alpha = 1
        self.ToastNotification_window.after(8, self.show_window_animation)

    def close_toast(self,):
        # 获取窗口当前的真实X坐标，避免松手时瞬移回原位再开始动画
        current_x = self.ToastNotification_window.winfo_x()
        # 计算动画终点（屏幕右侧外）
      
        # 计算步长：保证无论从哪里开始，滑出速度基本一致，且不会越界
        step = current_x + 10
        
        self.ToastNotification_window.geometry(f'+{step}+{self.window_target_y}')
        # 透明度渐变
        self.window_alpha -= 0.02
            
        self.ToastNotification_window.attributes('-alpha', max(self.window_alpha, 0))
        #self.ToastNotification_window.update()
        if step >= self.window_target_x + 490:
            self.ToastNotification_window.destroy()
        else:
           self.ToastNotification_window.after(4, self.close_toast)

    # ================= 使用 property 装饰器实现状态监听 =================
    @property
    def stretch_window(self):
        """获取 stretch_window 状态"""
        return self._stretch_window
    @stretch_window.setter
    def stretch_window(self, new_value):
        """设置 stretch_window 状态，并在值发生改变时自动触发回调"""
        # 只有当新值与旧值不同时，才触发变更逻辑
        if new_value != self._stretch_window:
            old_value = self._stretch_window  # 保存旧值（即变化前的状态）
            self._stretch_window = new_value  # 更新为新值（此时状态已更改）
            # 状态更改后，触发判断函数，将旧值传入以便反推
            self._on_stretch_window_changed(old_value)
    # =====================================================================

    def _on_stretch_window_changed(self, old_stretch_state):
        #当 stretch_window 状态更改后触发的判断函数
        #根据变化后的状态反推变化前的状态，并运行不同的动画函数
        current_stretch_state = self.stretch_window  # 读取新值
        # 修改：只有当 stretch_command 是函数时才播放动画  #修改
        if not callable(self.stretch_command):  #修改
            return  #修改
        if current_stretch_state == True and old_stretch_state == False:
            # 状态从 False 变为 True：触发拉伸激活动画
            self.animate_stretch_activate()
        elif current_stretch_state == False and old_stretch_state == True:
            # 状态从 True 变为 False：触发拉伸取消动画
            self.animate_stretch_deactivate()

    def animate_stretch_activate(self):
        #拉伸激活动画 
        
        self.stretch_activate_animation_running = True  #新增
        self.stretch_activate_animation_completed = False  #新增
        self._animate_stretch_activate_tip(0)  #新增

    def animate_stretch_deactivate(self):
        #拉伸取消动画 
        
        self.stretch_activate_animation_running = False  #新增 (停止可能正在运行的展开动画)
        self.stretch_deactivate_initial_width = self.Label_stretch_window_tip.winfo_width()  #新增
        self.stretch_deactivate_initial_height = self.Label_stretch_window_tip.winfo_height()  #新增
        self.stretch_deactivate_animation_running = True  #新增
        self._animate_stretch_deactivate_tip(0)  #新增

    def _animate_stretch_activate_tip(self, current_step):  #新增
        """  
        为Label_stretch_window_tip添加从右下角往左上角增大的动画  #新增
        使用缓动函数: eased = 1 - (1 - t) ** 4  #新增
        目标大小会随着窗口拉伸实时更新  #新增
        """  
        if not self.stretch_activate_animation_running:  #新增
            return  
        
        total_steps = 30  
        t = min(current_step / total_steps, 1.0)  
        eased = 1 - (1 - t) ** 4  


        # 获取窗口当前实时宽高，适配拉伸导致的大小改变  
        cur_w = self.ToastNotification_window.winfo_width()  #新增
        cur_h = self.ToastNotification_window.winfo_height()  #新增
        
        # 计算边框厚度(1像素)，并实时适配拉伸导致的边框粗细增加  #新增
        border_thickness = max(1, int(abs(cur_w - self.init_window_w) / 50) + 1) if cur_w != self.init_window_w else 1  #新增
        
        # 从右下角往左上角增大，距离边缘1像素实现边框效果  #新增
        target_width = cur_w - 2 * border_thickness  #新增
        target_height = cur_h - 2 * border_thickness  #新增
        
        current_width = int(target_width * eased)  #新增
        current_height = int(target_height * eased)  #新增
        
        # anchor='se' 保证了标签右下角固定，向左上角扩展  #新增
        self.Label_stretch_window_tip.place(  #新增
            relx=1.0, rely=1.0, anchor='se',  #新增
            x=-border_thickness, y=-border_thickness,  #新增
            width=current_width, height=current_height  #新增
        )  #新增
        self.Label_stretch_window_tip.lift()  #新增
        
        if t < 1.0:  #新增
            self.ToastNotification_window.after(8, lambda: self._animate_stretch_activate_tip(current_step + 1))  #新增
        else:  #新增
            self.stretch_activate_animation_running = False  #新增
            self.stretch_activate_animation_completed = True  #新增
            # 新增：动画完成后，继续实时更新标签大小以适应窗口拉伸  #新增
            self._update_stretch_tip_size()  #新增

    def _update_stretch_tip_size(self):  #新增
        """  #新增
        动画完成后，实时更新标签大小以适应窗口拉伸  #新增
        """  #新增
        # 修改：添加检查，如果拉伸动画已完成或正在运行消失动画，则停止更新  #修改
        if not self.stretch_activate_animation_completed or self.stretch_deactivate_animation_running:  #修改
            return  #新增
            
        # 获取窗口当前实时宽高  #新增
        cur_w = self.ToastNotification_window.winfo_width()  #新增
        cur_h = self.ToastNotification_window.winfo_height()  #新增
        
        # 计算边框厚度  #新增
        border_thickness = max(1, int(abs(cur_w - self.init_window_w) / 50) + 1) if cur_w != self.init_window_w else 1  #新增
        
        # 计算标签大小  #新增
        target_width = cur_w - 2 * border_thickness  #新增
        target_height = cur_h - 2 * border_thickness  #新增
        
        # 更新标签位置和大小  #新增
        self.Label_stretch_window_tip.place(  #新增
            relx=1.0, rely=1.0, anchor='se',  #新增
            x=-border_thickness, y=-border_thickness,  #新增
            width=target_width, height=target_height )  

  
        # 继续下一帧更新  #新增
        self.ToastNotification_window.after(8, self._update_stretch_tip_size)  #新增

    def _animate_stretch_deactivate_tip(self, current_step):  #新增
        """  #新增
        为Label_stretch_window_tip添加从左上角往右下角缩小的动画  #新增
        使用缓动函数: eased = 1 - (1 - t) ** 4  #新增
        """  #新增
        if not self.stretch_deactivate_animation_running:  #新增
            return  #新增
            
        total_steps = 30  #新增
        t = min(current_step / total_steps, 1.0)  #新增
        eased = 1 - (1 - t) ** 4  #新增


        # 计算当前缩小尺寸，从初始宽高缩小到0  #新增
        current_width = int(self.stretch_deactivate_initial_width * (1 - eased))  #新增
        current_height = int(self.stretch_deactivate_initial_height * (1 - eased))  #新增
        
        # 获取窗口当前实时宽高，适配拉伸导致的边框粗细增加  #新增
        cur_w = self.ToastNotification_window.winfo_width()  #新增
        cur_h = self.ToastNotification_window.winfo_height()  #新增
        border_thickness = max(1, int(abs(cur_w - self.init_window_w) / 50) + 1) if cur_w != self.init_window_w else 1  #新增
        
        # anchor='se' 保证了标签右下角固定，向左上角缩小  #新增
        self.Label_stretch_window_tip.place(  #新增
            relx=1.0, rely=1.0, anchor='se',  #新增
            x=-border_thickness, y=-border_thickness,  #新增
            width=current_width, height=current_height  #新增
        )  #新增
        self.Label_stretch_window_tip.lift()  #新增
        
        if t < 1.0:  #新增
            self.ToastNotification_window.after(8, lambda: self._animate_stretch_deactivate_tip(current_step + 1))  #新增
        else:  #新增
            self.stretch_deactivate_animation_running = False  #新增
            self.stretch_activate_animation_completed = False  #修改：重置完成状态，防止_update_stretch_tip_size继续运行
            # 隐藏标签  #新增
            self.Label_stretch_window_tip.place(x=-20000, y=-20000, width=1, height=1)  #新增

    def set_label_bold_and_big(self, label,add_size=3):
        old_font = tkfont.Font(font=label.cget("font"))
        #print(old_font.cget("size")) 9
        new_font = old_font.copy()
        new_font.configure(weight="bold",size=old_font.cget("size") + add_size)
        label.configure(font=new_font)
       
    def set_label_big(self, label,):
        old_font = tkfont.Font(font=label.cget("font"))
        new_font = old_font.copy()
        new_font.configure(
            size=old_font.cget("size") + 2
        )
        label.configure(font=new_font)

    def convert_place_to_relative(self,widget, parent_width=None, parent_height=None):
        if parent_width is None or parent_height is None:
            parent_width = widget.winfo_width()
            parent_height = widget.winfo_height()
            if parent_width <= 1 or parent_height <= 1:
                parent_width = widget.winfo_reqwidth()
                parent_height = widget.winfo_reqheight()

        def _convert(w, pw, ph):
            info = w.place_info()
            if info:
                try:
                    x = float(info.get('x', 0))
                    y = float(info.get('y', 0))
                    width = float(info.get('width', 0)) if info.get('width') else None
                    height = float(info.get('height', 0)) if info.get('height') else None

                    relx = x / pw if pw > 0 else 0
                    rely = y / ph if ph > 0 else 0
                    relwidth = width / pw if (width is not None and pw > 0) else None
                    relheight = height / ph if (height is not None and ph > 0) else None

                    place_kwargs = {
                        'relx': relx,
                        'rely': rely,
                        'anchor': info.get('anchor', 'nw')
                    }
                    if relwidth is not None:
                        place_kwargs['relwidth'] = relwidth
                    if relheight is not None:
                        place_kwargs['relheight'] = relheight

                    w.place_forget()
                    w.place(**place_kwargs)

                except Exception as e:
                    print(f"转换失败 {w}: {e}")

            child_w = w.winfo_width() if w.winfo_width() > 1 else w.winfo_reqwidth()
            child_h = w.winfo_height() if w.winfo_height() > 1 else w.winfo_reqheight()

            for child in w.winfo_children():
                _convert(child, child_w, child_h)

        _convert(widget, parent_width, parent_height)



class MessageBoxModernError:
    def __init__(self, parent=None, title_icon='icon', title='',
                 text_blod='', text='', icon='none',
                 text_true='确定', text_false='取消', button_mode=1, default_focus=1):
        self.parent = parent
        self.title_icon = title_icon
        self.title = title
        self.text_blod = text_blod
        self.text_thin = text
        self.icon = icon
        # 新增按钮相关参数
        self.text_true = text_true
        self.text_false = text_false
        self.button_mode = button_mode
        self.default_focus = default_focus
        
        # 初始化返回值和必要控件引用
        self.rtn = None
        self.ok_button = None
        self.cancel_button = None

    def layout_window(self):
        self.message_window = tk.Toplevel(self.parent) if self.parent!=None else tk.Tk()
        if self.parent:
            self.parent.attributes('-disabled', 'true')
            self.message_window.wm_transient(self.parent)
            #self.message_window.grab_set()  # 添加这行，使窗口获得焦点并阻止与父窗口的交互

        self.message_window.overrideredirect(1)
        self.message_window.resizable(0,0)
        self.message_window.config(bd=0, bg=HIGHLIGHT, highlightthickness=0)
        self.message_window.protocol("WM_DELETE_WINDOW", self._close_window)
        self.message_window.title(self.title)

        LoadFont(f"{libresource}/segmdl2.ttf")
        self.Font_icon_title_bar = tkfont.Font(family='Segoe MDL2 Assets', size=8)

        self.Frame_main = tk.Frame(self.message_window, bg=WINDOWBG, bd=0)

        # -----------------标题栏
        title_bar_icon_offset_x = 35 if self.title_icon not in [None, 'none', ''] else 0

        Frame_title_bar = tk.Frame(self.Frame_main, bg=WINDOWBG)
        Frame_title_bar.place(x=20, y=20, width=420, height=30)

        if self.title_icon not in [None, 'none', '']:
            Label_small_icon = tk.Label(Frame_title_bar, bg=WINDOWBG, anchor='center')
            Label_small_icon.place(x=0, y=0, width=30, height=30)
            SetImageTk(Label_small_icon, f"{libresource}{self.title_icon}.ico", img_size=(24, 24))

        Label_title = tk.Label(Frame_title_bar, bg=WINDOWBG, fg=TEXTFG, anchor='w', text=self.title)
        Label_title.place(x=title_bar_icon_offset_x, y=0, width=420 - title_bar_icon_offset_x, height=30)

        old_font = tkfont.Font(font=Label_title.cget("font"))
        new_font = old_font.copy()
        new_font.configure(weight="bold",size=old_font.cget("size")+1)
        Label_title.configure(font=new_font)

        Button_close = DTitleBarButton(Frame_title_bar,bg=WINDOWBG,takefocus=False, text='\uE106', font=self.Font_icon_title_bar, command=self._close_window)
        Button_close.place(x=390, y=0, width=30, height=30)

        old_font = tkfont.Font(font=Button_close.cget("font"))
        new_font = old_font.copy()
        new_font.configure(weight="bold")
        Button_close.configure(font=new_font)

        # ------------------------文字区
        Frame_text = tk.Frame(self.Frame_main, bg=WINDOWBG)

        if self.icon not in ['none', '', None]:
            text_frame_offset_x = 80
            Label_image = tk.Label(Frame_text, anchor='center', bg=WINDOWBG)
            Label_image.place(x=0, y=0, width=70, height=70)
            SetImageTk(Label_image, f"{libresource}{self.icon}.ico", [64, 64])
        else:
            text_frame_offset_x = 0

        # 计算粗体文本高度
        Frame_cauculate = tk.Frame(self.Frame_main, bd=0)
        Frame_cauculate.place(x=-20000, y=-20000, width=420 - text_frame_offset_x, height=20000)
        Cauculate_Label_text_blod = tk.Label(Frame_cauculate, text=self.text_blod, bg=WINDOWBG, fg=TEXTFG, wraplength=415 - text_frame_offset_x, justify='left', anchor='w')
        self.set_label_bold_and_big(Cauculate_Label_text_blod)
        Cauculate_Label_text_blod.pack(fill='x', side='top')
        height_Label_text_blod = Cauculate_Label_text_blod.winfo_reqheight() if self.text_blod!='' else 0
        Frame_cauculate.destroy()

        Label_text_blod = tk.Label(Frame_text, text=self.text_blod, bg=WINDOWBG, fg=TEXTFG, wraplength=415 - text_frame_offset_x, justify='left', anchor='w')
        self.set_label_bold_and_big(Label_text_blod)
        Label_text_blod.place(x=text_frame_offset_x, y=0, width=420 - text_frame_offset_x, height=height_Label_text_blod)

        # 计算细体文本高度
        Frame_cauculate = tk.Frame(self.Frame_main, bd=0)
        Frame_cauculate.place(x=-20000, y=-20000, width=420 - text_frame_offset_x, height=20000)
        Cauculate_Label_text_thin = tk.Label(Frame_cauculate, text=self.text_thin, bg=WINDOWBG, fg=SECONDARYTEXTFG, wraplength=415 - text_frame_offset_x, justify='left', anchor='w')
        #self.set_label_big(Cauculate_Label_text_thin)
        Cauculate_Label_text_thin.pack(fill='x', side='top')
        height_Label_text_thin = Cauculate_Label_text_thin.winfo_reqheight()
        Frame_cauculate.destroy()

        Label_text_thin = tk.Label(Frame_text, text=self.text_thin, bg=WINDOWBG, fg=SECONDARYTEXTFG if self.text_blod!='' else TEXTFG,
                                    wraplength=415 - text_frame_offset_x, justify='left', anchor='w')

        Label_text_thin.place(x=text_frame_offset_x, y=height_Label_text_blod, width=420 - text_frame_offset_x, height=height_Label_text_thin)

        # 布局计算
        if self.icon not in ['none', '', None]:
            self.all_height = 140+ max(height_Label_text_thin + height_Label_text_blod, 80)
            Frame_text.place(x=20, y=70, width=420, height=max(height_Label_text_thin + height_Label_text_blod, 80))
        else:
            self.all_height = 140 + height_Label_text_thin + height_Label_text_blod
            Frame_text.place(x=20, y=70, width=420, height=height_Label_text_blod + height_Label_text_thin)

        #-----------------------按钮区
        self.frame_button=tk.Frame(self.Frame_main,bg=WINDOWBG)
        self.frame_button.place(x=20,y=self.all_height-50 , width=420,height=30)
        
        # 按钮模式布局
        if self.button_mode == 1:
            self.message_window.bind('<Escape>', self._handle_key)
            self.ok_button = DButton(self.frame_button, text=self.text_true, 
                                     command=lambda: self._return_value(True), default='active')
            self.ok_button.place(x=340, y=0, width=80, height=30)
            self.ok_button.focus()
        elif self.button_mode == 2:
            self.message_window.bind('<Escape>', lambda e: self._return_value(None))
            self.ok_button = DButton(self.frame_button, text=self.text_true, 
                                     command=lambda: self._return_value(True))
            self.ok_button.place(x=240, y=0, width=80, height=30)
            self.cancel_button = DButton(self.frame_button, text=self.text_false, 
                                         command=lambda: self._return_value(False))
            self.cancel_button.place(x=340, y=0, width=80, height=30)
            self.ok_button.bind("<FocusIn>", self._update_button_focus)
            self.cancel_button.bind("<FocusIn>", self._update_button_focus)
            self.ok_button.bind("<FocusOut>", self._update_button_focus)
            self.cancel_button.bind("<FocusOut>", self._update_button_focus)

            # 设置默认焦点
            focus_btn = self.ok_button if self.default_focus == 1 else self.cancel_button
            focus_btn.focus()
            focus_btn['default'] = 'active'
        else:
            raise ValueError("button_mode 只能为 1 或 2")
        self.Frame_main.place(x=1, y=1, width=460, height=self.all_height)
        self._bind_event_to_all_except_custom(self.message_window,'<ButtonPress-1>',self._start_move,custom_classes=(DButton,DTitleBarButton))
        self._bind_event_to_all_except_custom(self.message_window,'<B1-Motion>',self._on_move,custom_classes=(DButton,DTitleBarButton))
        self._bind_event_to_all_except_custom(self.message_window,'<Escape>',self._close_window,)


    def run_message(self):
        self.layout_window()
        beep_map = {
            'question': win32con.MB_ICONQUESTION, 
            'safe_warning': win32con.MB_ICONWARNING,
            'error': win32con.MB_ICONERROR, 
            'stop': win32con.MB_ICONERROR, 
            'warning': win32con.MB_ICONWARNING,
            'info': win32con.MB_ICONINFORMATION, 
            'correct': win32con.MB_ICONINFORMATION,
            'none': 0,}

        if self.title_icon!='none': self.message_window.wm_iconbitmap(f"{libresource}{self.title_icon}.ico")

        screenwidth = GetWorkArea()[2]
        screenheight = GetWorkArea()[3]
        self.message_window.geometry(f'462x{self.all_height + 2}+{int((screenwidth-462)/2)}+{int((screenheight-self.all_height) / 2)}')
        self.message_window.update()
        self.message_window.focus_set()

        win32api.MessageBeep(beep_map.get(self.icon,0))
        self.message_window.wait_window(self.message_window)
        return self.rtn

    def _close_window(self):
        if self.parent:
            self.parent.attributes('-disabled', 'false')
        self.message_window.destroy()
        if self.parent:
            self.parent.focus_set()

    def _return_value(self, value):
        # 设置返回值并关闭窗口
        self.rtn = value
        self._close_window()

    def _handle_key(self, event):
        focused = self.message_window.focus_get()
        if event.keysym == 'Escape':
            self._return_value(None)
        elif focused in (self.ok_button, None):
            self._return_value(True)
        elif focused == self.cancel_button:
            self._return_value(False)

    def _update_button_focus(self, event=None):
        # 更新按钮的默认激活状态样式
        if self.button_mode == 2:
            if self.message_window.focus_get() == self.cancel_button:
                self.ok_button['default'], self.cancel_button['default'] = 'normal', 'active'
            else:  
                self.ok_button['default'], self.cancel_button['default'] = 'active', 'normal'

    def set_label_bold_and_big(self, label, add_size=3):
        old_font = tkfont.Font(font=label.cget("font"))
        new_font = old_font.copy()
        new_font.configure(weight="bold", size=old_font.cget("size") + add_size)
        label.configure(font=new_font)

    def _start_move(self, event):
        #记录鼠标按下时的初始位置
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_move(self, event):
        # 获取鼠标在屏幕上的绝对坐标
        x = self.message_window.winfo_x() + (event.x - self._drag_x)
        y = self.message_window.winfo_y() + (event.y - self._drag_y)
        
        # 更新窗口位置
        self.message_window.geometry(f'+{x}+{y}')
    
    def _bind_event_to_all_except_custom(self,parent, event_name, callback, custom_classes=None):
        """
        遍历 parent 里的所有控件，并绑定事件。
        如果遇到 custom_classes 中指定的自定义控件，则对其本身绑定事件，但不深入遍历其内部。
        
        :param parent: 顶层窗口或父级控件 (如 Toplevel, Frame)
        :param event_name: 事件名称，例如 '<Button-1>' 或 '<FocusIn>'
        :param callback: 事件触发的回调函数
        :param custom_classes: 元组或列表，包含不需要深入遍历的自定义控件类 (例如 (MyCustomPanel, TinyEditor))
        """
        if custom_classes is None:
            custom_classes = ()
            
        # 转换为元组方便 isinstance 判断
        custom_classes = tuple(custom_classes)

        # 1. 遍历当前父控件的所有子控件
        for child in parent.winfo_children():
           
            # 3. 判断是否是需要跳过深度遍历的自定义控件
            if not isinstance(child, custom_classes):
                # 如果是自定义控件，只绑定它本身（上面已绑），不再看它肚子里有什么
                child.bind(event_name, callback,add='+')
                
            # 4. 如果是普通控件（如 Frame、LabelFrame 等），则继续递归遍历它的子控件
            self._bind_event_to_all_except_custom(child, event_name, callback, custom_classes)





def MessageBoxModern(parent=None, title_icon='icon', title='',text_blod='', text='', icon='none',text_true='确定', text_false='取消', button_mode=1, default_focus=1,transient_parent=True):
    """
    显示一个现代化的消息框
    
    参数:
        parent: 父窗口
        title_icon: 标题栏图标名称
        title: 窗口标题
        text_blod: 粗体文本
        text: 普通文本
        icon: 消息图标 ('none', 'question', 'error', 'stop', 'warning', 'info', 'correct','还有别的')
        text_true: 确定按钮文本
        text_false: 取消按钮文本
        button_mode: 按钮模式 (1=仅确定按钮, 2=确定和取消按钮)
        default_focus: 默认焦点 (1=确定按钮, 2=取消按钮)
    
    返回:
        button_mode=1: True(确定) 或 None(关闭/ESC)
        button_mode=2: True(确定), False(取消) 或 None(关闭/ESC)
    """
    
    # 初始化返回值和必要控件引用
    rtn = None
    ok_button = None
    cancel_button = None
    

    
    def _close_window(event=None):
        nonlocal message_window
        if parent:
            parent.attributes('-disabled', 'false')
        message_window.destroy()
        if parent:
            parent.focus_set()

    def _return_value(value):
        nonlocal rtn
        # 设置返回值并关闭窗口
        rtn = value
        _close_window()

    def _handle_key(event):
        nonlocal ok_button, cancel_button
        focused = message_window.focus_get()
        if event.keysym == 'Escape':
            _return_value(None)
        elif focused in (ok_button, None):
            _return_value(True)
        elif focused == cancel_button:
            _return_value(False)

    def _update_button_focus(event=None):
        nonlocal ok_button, cancel_button
        # 更新按钮的默认激活状态样式
        if button_mode == 2:
            if message_window.focus_get() == cancel_button:
                ok_button['default'], cancel_button['default'] = 'normal', 'active'
            else:  
                ok_button['default'], cancel_button['default'] = 'active', 'normal'

    def set_label_bold_and_big(label, add_size=3):
        old_font = tkfont.Font(font=label.cget("font"))
        new_font = old_font.copy()
        new_font.configure(weight="bold", size=old_font.cget("size") + add_size)
        label.configure(font=new_font)



    message_window = tk.Toplevel(parent) if parent != None else tk.Tk()
    if parent:
        parent.attributes('-disabled', 'true')
        if transient_parent:message_window.wm_transient(parent)
    message_window.resizable(0, 0)
    message_window.config(bd=0, bg=WINDOWBG, highlightthickness=0)
    message_window.protocol("WM_DELETE_WINDOW", _close_window)
    message_window.title(title)
    message_window.focus()

    if icon not in ['none', '', None]:
        text_frame_offset_x = 100
        Label_image = tk.Label(message_window, anchor='center', bg=WINDOWBG)
        Label_image.place(x=20, y=20, width=70, height=70)
        SetImageTk(Label_image, f"{libresource}{icon}.ico", [64, 64])
    else:
        text_frame_offset_x = 20

    Label_text_blod = tk.Label(message_window, text=text_blod, bg=WINDOWBG, fg=TEXTFG, 
                            wraplength=400 - text_frame_offset_x, justify='left', anchor='w')
    set_label_bold_and_big(Label_text_blod)
    Label_text_blod.place(x=text_frame_offset_x, y=20, width=410 - text_frame_offset_x, )

    Label_text_thin = tk.Label(message_window, text=text, bg=WINDOWBG, fg=SECONDARYTEXTFG if text_blod != '' else TEXTFG,
                            wraplength=400 - text_frame_offset_x, justify='left', anchor='w')

    Label_text_thin.place(x=text_frame_offset_x, y=Label_text_blod.winfo_reqheight()+20, width=410 - text_frame_offset_x, )

    # 布局计算
    if icon not in ['none', '', None]:
        all_height = 90 + max(Label_text_thin.winfo_reqheight() + Label_text_blod.winfo_reqheight(), 80)
    else:
        all_height = 90 + Label_text_thin.winfo_reqheight() + Label_text_blod.winfo_reqheight()

    # 按钮模式布局
    if button_mode == 1:
        message_window.bind('<Escape>', _handle_key)
        ok_button = DButton(message_window, text=text_true, 
                            command=lambda: _return_value(True), default='active')
        ok_button.place(x=330, y=all_height-50, width=80, height=30)
        ok_button.focus()
    elif button_mode == 2:
        message_window.bind('<Escape>', lambda e: _return_value(None))
        ok_button = DButton(message_window, text=text_true, 
                            command=lambda: _return_value(True))
        ok_button.place(x=230, y=all_height-50, width=80, height=30)
        cancel_button = DButton(message_window, text=text_false, 
                                command=lambda: _return_value(False))
        cancel_button.place(x=330, y=all_height-50, width=80, height=30)
        ok_button.bind("<FocusIn>", _update_button_focus)
        cancel_button.bind("<FocusIn>", _update_button_focus)
        ok_button.bind("<FocusOut>", _update_button_focus)
        cancel_button.bind("<FocusOut>", _update_button_focus)

        # 设置默认焦点
        focus_btn = ok_button if default_focus == 1 else cancel_button
        focus_btn.focus()
        focus_btn['default'] = 'active'
    else:
        raise ValueError("button_mode 只能为 1 或 2")

    message_window.bind('<Escape>', _close_window)

    screenwidth = GetWorkArea()[2]
    screenheight = GetWorkArea()[3]
    message_window.geometry(f'430x{all_height}+{int((screenwidth-450)/2)}+{int((screenheight-all_height) / 2)}')



    
    beep_map = {
        'question': win32con.MB_ICONQUESTION, 
        'safe_warning': win32con.MB_ICONWARNING,
        'error': win32con.MB_ICONERROR, 
        'stop': win32con.MB_ICONERROR, 
        'warning': win32con.MB_ICONWARNING,
        'info': win32con.MB_ICONINFORMATION, 
        'correct': win32con.MB_ICONINFORMATION,
        'none': 0,
    }

    SetDarkTitleBar(message_window)  
    message_window.wm_iconbitmap(f"{libresource}{title_icon}.ico")
    

    win32api.MessageBeep(beep_map.get(icon, 0))
    message_window.wait_window()
    
    return rtn


def EntryBox(parent=None,title_icon='icon',title='',text_blod='',text='',entrys=(['',''],['','']),icon='none',text_true='确定',text_false='取消',):
    """
    显示现代化多输入框窗口

    参数:
        parent: 父窗口
        title_icon: 标题栏图标
        title: 窗口标题
        text_blod: 粗体提示文本
        text: 普通提示文本
        entrys: 输入框列表，格式[['名称','默认值'],...]
        icon: 图标类型
        text_true: 确定按钮文本
        text_false: 取消按钮文本



    返回:
        确定: tuple(所有输入框内容)
        取消: False
        关闭/ESC: None
    """
    rtn=None
    ok_button=None
    cancel_button=None
    entry_widgets=[]

    def _close_window(event=None):
        nonlocal entry_window
        if parent: parent.attributes('-disabled','false')
        entry_window.destroy()
        if parent: parent.focus_set()

    def _return_value(value):
        nonlocal rtn
        rtn=value
        _close_window()

    def return_tulpe():
        nonlocal rtn
        rtn=tuple(i.get() for i in entry_widgets)
        _close_window()

    def _update_button_focus(event=None):
        nonlocal ok_button,cancel_button

        if entry_window.focus_get()==cancel_button: ok_button['default'],cancel_button['default']='normal','active'
        else: ok_button['default'],cancel_button['default']='active','normal'

    def set_label_bold_and_big(label,add_size=3):
        old_font=tkfont.Font(font=label.cget("font"))
        new_font=old_font.copy()
        new_font.configure(weight="bold",size=old_font.cget("size")+add_size)
        label.configure(font=new_font)

    entry_window=tk.Toplevel(parent) if parent else tk.Tk()

    if parent:
        parent.attributes('-disabled','true')
        entry_window.wm_transient(parent)

    entry_window.resizable(0,0)
    entry_window.config(bd=0,bg=WINDOWBG,highlightthickness=0)
    entry_window.protocol("WM_DELETE_WINDOW",_close_window)
    entry_window.title(title)
    entry_window.focus()


    if icon not in ['none','',None]:
        text_frame_offset_x=100
        Label_image=tk.Label(entry_window,anchor='center',bg=WINDOWBG)
        Label_image.place(x=20,y=20,width=70,height=70)
        SetImageTk(Label_image,f"{libresource}{icon}.ico",[64,64])
    else:
        text_frame_offset_x=20

    Label_text_blod=tk.Label(entry_window,text=text_blod,bg=WINDOWBG,fg=TEXTFG,wraplength=400-text_frame_offset_x,justify='left',anchor='w')
    set_label_bold_and_big(Label_text_blod)
    Label_text_blod.place(x=text_frame_offset_x,y=20,width=410-text_frame_offset_x)

    Label_text_thin=tk.Label(entry_window,text=text,bg=WINDOWBG,fg=SECONDARYTEXTFG if text_blod!='' else TEXTFG,wraplength=400-text_frame_offset_x,justify='left',anchor='w')
    Label_text_thin.place(x=text_frame_offset_x,y=Label_text_blod.winfo_reqheight()+20,width=410-text_frame_offset_x)

    if icon not in ['none','',None]: 
        text_height=20+max(Label_text_thin.winfo_reqheight()+Label_text_blod.winfo_reqheight(),80)
    else: 
        text_height=20+Label_text_thin.winfo_reqheight()+Label_text_blod.winfo_reqheight()

    entry_height=0

    for t in entrys:
        label_entry_text=tk.Label(entry_window,text=t[0],bg=WINDOWBG,fg=TEXTFG,anchor='w')
        label_entry_text.place(x=20,y=text_height+entry_height+20,width=100,height=30)

        entry=DEntry(entry_window,)
        entry.insert(0,t[1])
        entry.place(x=130,y=text_height+entry_height+20,width=280,height=30)

        entry_widgets.append(entry)
        entry_height+=50

    all_height=text_height+entry_height+50

    entry_window.bind('<Escape>',lambda e:_return_value(None))


    ok_button=DButton(entry_window,text=text_true,command=return_tulpe)
    ok_button.place(x=230,y=all_height-30,width=80,height=30)

    cancel_button=DButton(entry_window,text=text_false,command=lambda:_return_value(False))
    cancel_button.place(x=330,y=all_height-30,width=80,height=30)

    ok_button.bind("<FocusIn>",_update_button_focus)
    cancel_button.bind("<FocusIn>",_update_button_focus)
    ok_button.bind("<FocusOut>",_update_button_focus)
    cancel_button.bind("<FocusOut>",_update_button_focus)


    ok_button['default']='active'


    screenwidth=GetWorkArea()[2]
    screenheight=GetWorkArea()[3]
    entry_window.geometry(f'430x{all_height+20}+{int((screenwidth-450)/2)}+{int((screenheight-all_height)/2)}')

    entry_widgets[0].focus()
    TkEntryMoveToRightSelectAll(entry_widgets[0])
               
    beep_map={'question':win32con.MB_ICONQUESTION,
              'error':win32con.MB_ICONERROR,
              'stop':win32con.MB_ICONERROR,
              'warning':win32con.MB_ICONWARNING,
              'info':win32con.MB_ICONINFORMATION,
              'correct':win32con.MB_ICONINFORMATION,
              'none':0}

    SetDarkTitleBar(entry_window)
    entry_window.wm_iconbitmap(f"{libresource}{title_icon}.ico")
    if  beep_map.get(icon,0)!=0:
        win32api.MessageBeep(beep_map.get(icon,0))

    entry_window.wait_window()

    return rtn



class ImagePreview(tk.Frame):
    def __init__(self, master=None, image=None, auto_zoom=False, **kwargs):
        # 提取属于 Canvas 的视觉属性，其余留给 Frame
        canvas_keys = tk.Canvas().keys()
        canvas_kwargs = {k: v for k, v in kwargs.items() if k in canvas_keys}
        frame_kwargs = {k: v for k, v in kwargs.items() if k not in canvas_kwargs}

        super().__init__(master, **frame_kwargs)

        self._image_path = image
        self._auto_zoom = auto_zoom
        self._scale = 1
        self._offset_x = 0
        self._offset_y = 0
        self._drag_x = 0
        self._drag_y = 0

        # 将提取到的视觉属性(如 bg, bd, relief 等)应用在 Canvas 上
        self.canvas = tk.Canvas(self, highlightthickness=0, **canvas_kwargs)
        self.canvas.pack(fill="both", expand=True)

        self.original_image = None
        self.display_image = None
        self.image_id = None

        if image:
            self.load_image(image)

        self.canvas.bind("<MouseWheel>", self.wheel)
        self.canvas.bind("<Button-1>", self.mouse_down)
        self.canvas.bind("<B1-Motion>", self.mouse_drag)
        self.canvas.bind("<Button-2>", self.mouse_down)
        self.canvas.bind("<B2-Motion>", self.mouse_drag)
        self.bind("<Configure>", self.resize)

    def load_image(self, path):
        self._image_path = path
        self.original_image = Image.open(path).convert("RGBA")
        self._scale = 1
        self._offset_x = self._offset_y = 0
        if self._auto_zoom:
            self.fit_image()
        else:
            self.update_image()

    def update_image(self):
        if not self.original_image:
            return

        w = int(self.original_image.width * self._scale)
        h = int(self.original_image.height * self._scale)

        # 动态选择重采样算法：
        # 缩小到 75% 及以下时使用平滑算法 (LANCZOS)，保证缩小状态下的观感
        # 放大或微缩时使用最近邻 (NEAREST)，保证像素级精度查看
        if self._scale <1:
            resample_method = Image.Resampling.LANCZOS
        else:
            resample_method = Image.Resampling.NEAREST

        img = self.original_image.resize((w, h), resample_method)
        self.display_image = ImageTk.PhotoImage(img)

        if self.image_id:
            self.canvas.delete(self.image_id)

        self.image_id = self.canvas.create_image(
            self._offset_x, self._offset_y, image=self.display_image, anchor="nw"
        )

    def fit_image(self):
        if not self.original_image:
            return

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw <= 1 or ch <= 1:
            return

        iw = self.original_image.width
        ih = self.original_image.height

        self._scale = min(cw / iw, ch / ih)
        self._offset_x = (cw - iw * self._scale) / 2
        self._offset_y = (ch - ih * self._scale) / 2

        self.update_image()

    def resize(self, event):
        if self._auto_zoom:
            self.fit_image()

    def zoom(self, value):
        if not self.original_image:
            return

        old = self._scale
        self._scale = max(0.05, min(20, self._scale * value))

        cx = self.canvas.winfo_width() / 2
        cy = self.canvas.winfo_height() / 2

        self._offset_x = cx - (cx - self._offset_x) * self._scale / old
        self._offset_y = cy - (cy - self._offset_y) * self._scale / old

        self.update_image()

    def move(self, x, y):
        self._offset_x += x
        self._offset_y += y
        self.update_image()

    def wheel(self, event):
        if event.state & 0x4:
            self.move(0, -event.delta / 5)
        elif event.state & 0x1:
            self.move(-event.delta / 5, 0)
        else:
            self.zoom(1.1 if event.delta > 0 else 0.9)

    def mouse_down(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def mouse_drag(self, event):
        self.move(event.x - self._drag_x, event.y - self._drag_y)
        self._drag_x = event.x
        self._drag_y = event.y

    # ================= 重写配置接口，使视觉属性动态生效 =================
    def config(self, cnf=None, **kwargs):
        if cnf is not None:
            if isinstance(cnf, str):
                # 读取单个属性
                if cnf == "image": return self._image_path
                if cnf == "auto_zoom": return self._auto_zoom
                if cnf in self.canvas.keys(): return self.canvas.cget(cnf)
                return super().cget(cnf)
            kwargs.update(cnf)

        # 写入属性：分离 Frame 属性与 Canvas 属性
        canvas_keys = self.canvas.keys()
        canvas_kw = {}
        frame_kw = {}

        for k, v in kwargs.items():
            if k == "image":
                self.load_image(v)
            elif k == "auto_zoom":
                self._auto_zoom = v
                if v: self.fit_image()
            elif k in canvas_keys:
                canvas_kw[k] = v
            else:
                frame_kw[k] = v

        if canvas_kw:
            self.canvas.config(**canvas_kw)
        if frame_kw:
            super().config(**frame_kw)

    configure = config

    def __setitem__(self, key, value):
        self.config(**{key: value})

    def __getitem__(self, key):
        return self.config(key)













if __name__=='__main__':
    SetDPI()

    '''
    a=ToastNotification(text_blod='你好!',text_thin="自己写的简易通知弹窗,能自行运算大小,带有丝滑动画",
                        title='应用程序',
                        icon="icon.ico",
                        image=f"{libresource}/correct.ico",
                        more_option_command=lambda:print("点击了更多选项按钮"),
                        stretch_command=None,
                        stretch_command_in_mainthread=0)
    a.run_toast()'''

    
    text='7f@K#9x!Q¥Ω≈ç√∞∑µ'
    
   # MessageBoxModern(title='错误',text_blod='Python抛出异常',text=text,title_icon='icon',icon='error',button_mode=2)

    #EntryBox(title='fuck',text='i fuck you',entrys=[['aaa:',''],['bbb:','B']],icon='error',text_blod='灾难性故障')

   # ToastNotification(parent=None,text_blod='IFUCKYOU',text_thin=text,image=f'{libresource}error.ico',stretch_command=lambda:print('fuck')).run_toast()




    SetDPI()
    
    '''def close_root(event=None):
        root.destroy()
        sys.exit()
    root=tk.Tk()
    
    root.title('万岁WanSei® Modelbench-Tools')
    root['bg']=WINDOWBG
    width=780
    height=400#400
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(geometry)
    #root.resizable(0,0)
    root.config(bd=0,highlightthickness=0)
    root.protocol('WM_DELETE_WINDOW',close_root)

    root.focus()
    #RainbowLoding_demo=RainbowLoding(root)
    #RainbowLoding_demo.pack(fill='x',side='top')


    a=DSpinbox(root,from_=0)
    a.place(x=20,y=20,width=180,height=30)

    c=DCombobutton(root,values=['FUCK','hi'],state='normal')
    c.place(x=300,y=0,width=150,height=30)
    
    b=DSpinbox(root,from_=0)
    b.place(x=20,y=100,width=180,height=30)

    p=ImagePreview(root,image="D:/Desktop/好老师.jpg",bg='#00ff00',bd=10,relief='solid')
    p.place(x=20,y=160,width=500,height=400)

    y=DCheckbutton(root,text='fuckyou')
    y.place(x=500,y=100,width=180,height=30)

    m=DButton(root,text='fuck',)
    m.place(x=400,y=20,width=80,height=30)

    n=DButton(root,text='fuck',)
    n.place(x=450,y=20,width=80,height=30)
    SetDarkTitleBar(root)
    root.iconbitmap(f'{libresource}icon.ico')

    SetBorder(root,bd=0)
    ConvertPlaceToRelative(root)

    root.mainloop()'''




    # ====================== 演示（优化版） ======================
    root = tk.Tk()
    root.title('DProgressbar – 边缘无缝衔接')
    W, H = 700, 400
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f'{W}x{H}+{(sw-W)//2}+{(sh-H-80)//2}')
    root.config(bg=WINDOWBG, bd=0, highlightthickness=0)
    root.focus()

    # ---------- 进度条 ----------
    tk.Label(root, text='Determinate（边缘无缝柔光）', bg=WINDOWBG, fg=TEXTFG,
            ).place(x=20, y=8)

    pb = DProgressbar(root, orient='horizontal', mode='determinate',
                    maximum=100, value=45, barcolor=GREENLIGHT)
    pb.place(x=20, y=32, width=520, height=30)





    tk.Label(root, text='Indeterminate（无高光）', bg=WINDOWBG, fg=TEXTFG,
            font=('', 10)).place(x=20, y=78)

    pb3 = DProgressbar(root, orient='horizontal', mode='indeterminate',
                    barcolor=GREENLIGHT)
    pb3.place(x=20, y=102, width=520, height=30)
    pb3.start(100)          # 不确定模式内部动画间隔（越小越快）




    tk.Label(root, text='垂直', bg=WINDOWBG, fg=TEXTFG,).place(x=560, y=8)
    pb2 = DProgressbar(root, orient='vertical', mode='determinate',
                    maximum=100, value=60, barcolor=HIGHLIGHT)
    pb2.place(x=580, y=32, width=30, height=200)

    # ---------- 演示控制 ----------
    bf = tk.Frame(root, bg=WINDOWBG)
    bf.place(x=20, y=155)

    # 可调参数（改这里就能控制速度）
    DEMO_INTERVAL = 10          # 每次更新间隔（毫秒），越小越快
    DEMO_STEP     = 0.2         # 每次增加的进度值，越大跳得越快

    running = False
    _demo_after_id = None

    def add(d):
        """手动加减进度"""
        pb.value = pb.value + d
        pb2.value = max(0, min(100, pb2.value + d * 0.7))

    def _demo_tick():
        """演示动画的一帧"""
        global _demo_after_id
        if not running:
            return
        pb.value = (pb.value + DEMO_STEP) % (pb.maximum + DEMO_STEP)
        # 垂直条做一点联动（可选）
        pb2.value = 20 + 60 * abs((pb.value / 50) - 1)
        _demo_after_id = root.after(DEMO_INTERVAL, _demo_tick)

    def start_demo():
        global running, _demo_after_id
        if running:
            return
        running = True
        _demo_tick()

    def stop_demo():
        global running, _demo_after_id
        running = False
        if _demo_after_id:
            root.after_cancel(_demo_after_id)
            _demo_after_id = None

    def reset():
        stop_demo()
        pb.value = 0
        pb2.value = 0



    DButton(bf, text=' +5 ', command=lambda: add(5)).pack(side='left', padx=3)
    DButton(bf, text=' -5 ', command=lambda: add(-5)).pack(side='left', padx=3)
    DButton(bf, text='开始演示', command=start_demo).pack(side='left', padx=3)
    DButton(bf, text='停止演示', command=stop_demo).pack(side='left', padx=3)
    DButton(bf, text='重置', command=reset).pack(side='left', padx=3)

    tk.Label(root, text='调速方法见下方说明',
            bg=WINDOWBG, fg=SECONDARYTEXTFG,).place(x=20, y=210)

    root.mainloop()
    '''
    def on_exit():
        print("退出应用程序...")
        StrayIcon_obj.stop()

    def show_message():
        win32api.MessageBox(0, "你点击了弹出消息！", "提示", win32con.MB_ICONINFORMATION)

    def toggle_feature():
        current_state = StrayIcon_obj.is_checked("我的功能")
        print(f"功能状态切换：{current_state} -> {not current_state}")
        # 这里可以执行与功能切换相关的逻辑

    def left_click_action():
        print("托盘图标被左键单击了！")
        win32api.MessageBox(0, "托盘图标被左键单击了！", "左键点击", win32con.MB_OK)

    def disable_message_item():
        print("尝试禁用/启用 '弹出消息' 菜单项...")
        # 简单演示，可以根据当前状态来切换
        if StrayIcon_obj.set_state("弹出消息", "disabled"):
            print("'弹出消息' 已被禁用。再次点击它，你将无法点击，需要重新运行程序来测试启用。")
        else:
            print("无法禁用 '弹出消息'。")


    options = [
        ("弹出消息", show_message, 'text'),
        ("勾选项", None, 'check'),#toggle_feature
        ("点击我改变文本!", lambda:StrayIcon_obj.set_text("点击我改变文本!", '你好'),'text'),
        ("禁用消息项", disable_message_item, 'text'), # 新增一个用于测试禁用功能的菜单项
        ("", None, 'line'), # 分隔线
        ("退出", on_exit, 'text')
    ]

    StrayIcon_obj= StrayIcon(icon_path=f'{libresource}icon.ico', options=options, prompt_text='我的托盘图标', left_click=left_click_action)

    StrayIcon_obj.run()'''
