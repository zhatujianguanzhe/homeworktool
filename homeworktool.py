VERSION="1.2.6"
#一定要放在第一行
import  os, sys, win32api, webbrowser, json,  datetime,traceback, ctypes, copy,re
from tkinter import  filedialog, colorchooser
from laotaoui import *
import tkinter.font as tkfont
from PIL import Image, ImageDraw, ImageFont, ImageTk

import urllib.request
import urllib.error


# ========== 导出图片 / 界面默认值（运行时以 settings 为准）==========
DEFAULT_EXPORT_SETTINGS = {
    'EXPORT_FONT_SUBJECT': 120,
    'EXPORT_FONT_CONTENT': 100,
    'EXPORT_FONT_DATE': 110,
    'EXPORT_FONT_SUBJECT_MIN': 40,
    'EXPORT_FONT_CONTENT_MIN': 32,
    'EXPORT_FONT_NAME': '宋体',
    'EXPORT_FONT_FALLBACK_NAMES': [
        '宋体', '微软雅黑', 'Microsoft YaHei', '黑体', 'SimHei',
        'Segoe UI Symbol', 'Segoe UI', 'Arial Unicode MS', 'Arial',
    ],
    'EXPORT_LINE_SPACING_CONTENT': 10,
    'EXPORT_LINE_SPACING_SUBJECT': 15,
    'EXPORT_SUBJECT_GAP': 32,
    'EXPORT_MARGIN_X': 300,
    'EXPORT_MARGIN_BOTTOM': 150,
    'EXPORT_DATE_Y': 120,
    'EXPORT_START_Y': 280,
    'EXPORT_GAP_CENTER': 60,
    'EXPORT_FONT_ATTENDANCE': 90,
    'highlight_box': [0, 0, 0, 0],
    'color_mode': 'system',
    # 导出背景
    'background_mode': '纯色',           # 纯色 | 图片
    'background_color': '#FAF9E6',      # 底色（纯色模式或图片未铺满时的底）
    'background_image_path': '',
    'background_stretch_mode': '完全拉伸',  # 完全拉伸|横向拉伸|纵向拉伸|不拉伸
}

DEFAULT_SETTINGS_FILE = {
    "password": {"admin": "", "default": ""},
    "highlight_box": [0, 0, 0, 0],
    "EXPORT_FONT_SUBJECT": 120,
    "EXPORT_FONT_CONTENT": 100,
    "EXPORT_FONT_DATE": 110,
    "EXPORT_FONT_ATTENDANCE": 90,
    "EXPORT_FONT_SUBJECT_MIN": 40,
    "EXPORT_FONT_CONTENT_MIN": 32,
    "EXPORT_FONT_NAME": "宋体",
    "EXPORT_FONT_FALLBACK_NAMES": [
        "宋体", "微软雅黑", "Microsoft YaHei", "黑体", "SimHei",
        "Segoe UI Symbol", "Segoe UI", "Arial Unicode MS", "Arial",
    ],
    "EXPORT_LINE_SPACING_CONTENT": 10,
    "EXPORT_LINE_SPACING_SUBJECT": 15,
    "EXPORT_SUBJECT_GAP": 32,
    "EXPORT_MARGIN_X": 300,
    "EXPORT_MARGIN_BOTTOM": 150,
    "EXPORT_DATE_Y": 120,
    "EXPORT_START_Y": 280,
    "EXPORT_GAP_CENTER": 60,
    "YAHEI_TEXT_FONT": "TkDefaultFont",
    "disable_highdpi_scaling": True,
    "auto_set_desktop_background": True,
    "expected_attendance": 50,
    "attendance_enabled": False,
    "color_mode": "system",
    "background_mode": "纯色",
    "background_color": "#FAF9E6",
    "background_image_path": "",
    "background_stretch_mode": "完全拉伸",
}

# 高级设置表：说明, 变量名
ADVANCED_SETTING_ROWS = [
    ('科目标题字号', 'EXPORT_FONT_SUBJECT'),
    ('作业内容字号', 'EXPORT_FONT_CONTENT'),
    ('日期字号', 'EXPORT_FONT_DATE'),
    ('考勤字号', 'EXPORT_FONT_ATTENDANCE'),
    ('科目标题最小字号', 'EXPORT_FONT_SUBJECT_MIN'),
    ('作业内容最小字号', 'EXPORT_FONT_CONTENT_MIN'),
    ('导出主字体名称', 'EXPORT_FONT_NAME'),
    ('缺字回退字体列表(JSON数组)', 'EXPORT_FONT_FALLBACK_NAMES'),
    ('作业内容行间距', 'EXPORT_LINE_SPACING_CONTENT'),
    ('科目标题后与首条作业间距', 'EXPORT_LINE_SPACING_SUBJECT'),
    ('不同科目额外间距', 'EXPORT_SUBJECT_GAP'),
    ('左右边距', 'EXPORT_MARGIN_X'),
    ('底边距', 'EXPORT_MARGIN_BOTTOM'),
    ('日期纵向位置', 'EXPORT_DATE_Y'),
    ('内容起始纵向位置', 'EXPORT_START_Y'),
    ('中间分割线两侧留白', 'EXPORT_GAP_CENTER'),
    ('高亮矩形[x,y,宽,高]', 'highlight_box'),
    ('界面字体(名称(如TkDefaultFont)或["名称",字号])', 'YAHEI_TEXT_FONT'),

]

# 作业末尾样式标记（保存时保留;导出时解析后去掉）
HOMEWORK_STYLE_MARKERS = frozenset('RGYBOFH')
HOMEWORK_STYLE_COLORS = {
    'R': (200, 30, 30),
    'G': (0, 110, 40),
    'Y': (180, 140, 0),
    'B': (30, 160, 220),
}





MITLICENSE="""MIT License

Copyright © 2026 炸图监管者

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

YAHEI_TEXT_FONT = ['微软雅黑', 12]  # 启动时由 settings 覆盖

def parse_homework_style(content):
    """解析作业末尾的 R/G/Y/B/O/F/H 标记.
    返回 (显示文本, 颜色RGB或None, 是否加粗, 是否反色F, 是否背景像素反色H).
    F=反色：黑底；前景默认白，仍受颜色/加粗影响。
    H=与背景图像对应像素反色显示文字（RGB 按通道取反）。
    """
    if not content:
        return '', None, False, False, False
    i = len(content)
    found = []
    while i > 0 and content[i - 1] in HOMEWORK_STYLE_MARKERS:
        i -= 1
        found.append(content[i])
    color = None
    bold = False
    inverse = False
    bg_invert = False
    for ch in found:
        if ch == 'O':
            bold = True
        elif ch == 'F':
            inverse = True
        elif ch == 'H':
            bg_invert = True
        elif ch in HOMEWORK_STYLE_COLORS and color is None:
            color = HOMEWORK_STYLE_COLORS[ch]
    return content[:i], color, bold, inverse, bg_invert



def get_ONLINE_VERSION(url: str) -> list:
    # 获取 GitHub 文本文件第一行，通过 exec 解析版本号，
    # 并返回形如 [1, 0, 2] 的整数列表。
    
    if "github.com" in url and "/blob/" in url:
        url = url.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob/", "/")
    
    
    # 1. 使用 urllib 获取文件内容
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read().decode("utf-8")
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        raise RuntimeError(f"获取文件失败: {e}") from e

    # 2. 获取第一行内容（假设格式为 VERSION="1.0.2"）
    first_line = content.strip().splitlines()[0]

    namespace = {}
    exec(first_line, {}, namespace)
    version_str = namespace.get("VERSION",'0.0.0')
 
    version_list = [int(x) for x in version_str.split(".")]
    return version_list

def get_local_version():
    return [int(x) for x in VERSION.split(".")]




# 定义可观察的字典,实现数据变更自动触发UI刷新
class ObservableHomeworkDict(dict):
    def __init__(self, update_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_callback = update_callback

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        # 当给科目赋值时(如 self.homework_data['语文'] = [...]),自动触发刷新
        self._update_callback(key)

    def __delitem__(self, key):
        super().__delitem__(key)
        # 如果需要删除科目功能,删除时也会触发(此处UI中无需刷新已删除的节点,故pass)

    def pop(self, key, *args):
        result = super().pop(key, *args)
        return result


class Main():
    def __init__(self,):
        global YAHEI_TEXT_FONT

        # 启动时校验四个 JSON：缺失则创建默认内容并警告
        self._ensure_json_files()
        self._load_json_files()
        self.load_runtime_settings()

        # 初始化作业数据存储字典,绑定自动刷新回调函数
        self.homework_data = ObservableHomeworkDict(self._update_subject_ui)

        LoadFont(f'{libresource}/WS_Segoe_MDL2_Assets-Regular.ttf')

        self.layout_window()
        self.apply_homework_template()
        self.autoload_homework_histroy()
        self.mainloop()

    def _ensure_json_files(self):
        """校验设置/模板/历史记录/考勤四个 JSON 是否存在；不存在则写入默认内容并弹窗提示。"""
        specs = [
            (
                'homeworktool_settings.json',
                '设置文件',
                DEFAULT_SETTINGS_FILE,
            ),
            (
                'homeworktool_template.json',
                '作业模板文件',
                {},
            ),
            (
                'homeworktool_previous_homework.json',
                '历史记录文件',
                {},
            ),
            (
                'homeworktool_attendance.json',
                '考勤历史文件',
                {},
            ),
        ]
        for path, display_name, default_obj in specs:
            if os.path.isfile(path):
                continue
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(default_obj, f, ensure_ascii=False, indent=2)
            MessageBoxModern(
                parent=None,
                title='警告',
                icon='warning',
                text_blod=f'{display_name}不存在，已创建默认文件。',
                text=path,
            )

    def _load_json_files(self):
        """读取四个 JSON；格式错误时回退默认值并警告（不影响继续运行）。"""
        # 设置
        try:
            with open('homeworktool_settings.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError('设置文件根节点必须是对象')
            self.settings = data
        except Exception:
            MessageBoxModern(
                parent=None,
                title='警告',
                icon='warning',
                text_blod='读取设置文件失败，已使用默认设置。',
                text=traceback.format_exc(),
            )
            self.settings = dict(DEFAULT_SETTINGS_FILE)
            try:
                with open('homeworktool_settings.json', 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        # 模板
        try:
            with open('homeworktool_template.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.homework_template = data if isinstance(data, dict) else {}
        except Exception:
            MessageBoxModern(
                parent=None,
                title='警告',
                icon='warning',
                text_blod='读取作业模板文件失败，不影响运行。',
                text=traceback.format_exc(),
            )
            self.homework_template = {}

        # 历史记录
        try:
            with open('homeworktool_previous_homework.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.previous_homework = data if isinstance(data, dict) else {}
        except Exception:
            MessageBoxModern(
                parent=None,
                title='警告',
                icon='warning',
                text_blod='读取历史记录文件失败，不影响运行。',
                text=traceback.format_exc(),
            )
            self.previous_homework = {}

        # 考勤
        try:
            with open('homeworktool_attendance.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.attendance_history = data if isinstance(data, dict) else {}
        except Exception:
            MessageBoxModern(
                parent=None,
                title='警告',
                icon='warning',
                text_blod='读取考勤历史文件失败，不影响运行。',
                text=traceback.format_exc(),
            )
            self.attendance_history = {}

    def layout_window(self,):
        self.root=tk.Tk()
        self.root.title('万岁™作业布置与展示工具    (合肥市阳光中学特供版 & 合肥市第一中学特供版)')
        SetDarkTitleBar(self.root)
        width = 1200
        height = 800
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(geometry)
        self.root['bg']=WINDOWBG
        self.root.protocol('WM_DELETE_WINDOW', self.exit_app)


        if isinstance(YAHEI_TEXT_FONT,str):
            self.font_icon=tkfont.Font(family='WS_Segoe_MDL2_Assets',size=9)
        else:
            self.font_icon=tkfont.Font(family='WS_Segoe_MDL2_Assets',size=self.settings.get('YAHEI_TEXT_FONT',['微软雅黑', 12])[1])


        threading.Thread(target=self.check_update,daemon=True).start()

        style = ttk.Style()
        style.theme_use("alt")

        style.configure("Main.Treeview", rowheight=40,
                        fieldbackground=WINDOWBG,
                        background=WINDOWBG,
                        foregroung=TEXTFG,
                        borderwidth=0,
                        highlightthickness=0,
                        font=YAHEI_TEXT_FONT ) # 填充背景色
   
        style.configure("Main.Treeview.Heading",
                        background=WINDOWBG,      # 表头背景色
                        foreground=TEXTFG,        # 表头文字颜色
                        borderwidth=0,
                        highlightthickness=0,
                        font=YAHEI_TEXT_FONT)          # 扁平化边框
        # 3. 关键步骤：锁死动态样式（防止鼠标悬停或点击时变回系统默认的灰色）
        
        style.map("Main.Treeview.Heading",
                background=[('active', WIDGETBG),  # 鼠标悬停时的深蓝色
                            ('pressed', WINDOWBG)], # 鼠标点击时的更深蓝色
                foreground=[('active', TEXTFG),
                            ('pressed', TEXTFG)],
                borderwidth=[('active', 0), ('pressed', 0)],    
                highlightthickness=[('active', 0), ('pressed', 0)],   )
        # 配置被选中时的颜色
        style.map("Main.Treeview",
                background=[('selected', AlphaBlend(WINDOWBG,HIGHLIGHT,0.5))],
                foreground=[('selected',TEXTFG )],
                borderwidth=[('active', 0), ('pressed', 0)],    # 外边框宽度设为 0
                highlightthickness=[('active', 0), ('pressed', 0)],)    # 高亮边框宽度设为 0

        tk.Label(self.root, bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor='w',text='双击科目或作业进入编辑模式,记得点击"保存作业"按钮!').place(x=20, y=750, width=860, height=30)


        self.scrollbar_treeview_y=DScrollbar(self.root)
        self.scrollbar_treeview_y.place(x=870,y=20,width=30,height=720)
        self.treeview_homework= ttk.Treeview(self.root, show="tree headings", columns=["homework"],takefocus=True,
                                          selectmode='browse', yscrollcommand=self.scrollbar_treeview_y.set,style='Main.Treeview')
        self.treeview_homework.place(x=20,y=20,width=850,height=720)

        self.scrollbar_treeview_y.config(command=self.treeview_homework.yview)

        self.treeview_homework.heading("#0", text="科目", anchor='center')
        self.treeview_homework.heading("homework", text="作业内容", anchor='center')

        self.treeview_homework.column("#0", width=150, anchor='w')
        self.treeview_homework.column("homework", width=680, anchor='w')
        
        # 绑定展开和收起事件,同时刷新状态文字和行颜色
        def on_treeview_open(event):
            item = self.treeview_homework.focus()
            
            self.root.after_idle(lambda: self._update_subject_state(item))
            self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))

        def on_treeview_close(event):
            item = self.treeview_homework.focus()
       
            self.root.after_idle(lambda: self._update_subject_state(item))
            self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))

        self.treeview_homework.bind('<<TreeviewOpen>>', on_treeview_open)
        self.treeview_homework.bind('<<TreeviewClose>>', on_treeview_close)

        self.treeview_homework.bind('<Double-Button-1>', self.edit_homework)


        self.button_edit_homework=DButton(self.root,text='编辑科目',fg=GREENLIGHT,font=YAHEI_TEXT_FONT,command=self.edit_homework)
        self.button_edit_homework.place(x=920,y=20,width=260,height=60)

        self.button_export_image=DButton(self.root,text='生成图片',font=YAHEI_TEXT_FONT,fg=HIGHLIGHT,command=self.export_homework_image)
        self.button_export_image.place(x=920,y=100,width=260,height=60)

        self.button_save_homework_file=DButton(self.root,text='保存作业',font=YAHEI_TEXT_FONT,command=self.save_homework_history)
        self.button_save_homework_file.place(x=920,y=180,width=260,height=60)

        self.button_load_homework_file=DButton(self.root,text='回溯历史记录',font=YAHEI_TEXT_FONT,command=self.load_homework_history)
        self.button_load_homework_file.place(x=920,y=260,width=260,height=60)

        # 自习考勤：两行 —— 勾选 + 实到人数（实到写入考勤历史,不写配置；应到在设置中）
        self.var_attendance_enabled = tk.BooleanVar(value=bool(getattr(self, 'attendance_enabled', False)))
        self.checkbutton_attendance = DCheckbutton(self.root, text='考勤人数:',variable=self.var_attendance_enabled,command=self._on_attendance_toggle,)
        self.checkbutton_attendance.place(x=920, y=340, width=260, height=30)

        _exp = max(int(getattr(self, 'expected_attendance', 50) or 50),0)
 
        self.spinbox_attendance = DTouchSpinbox2(self.root, long_press_ms=50, int_only=True, from_=0, to=_exp, increment=1, )
        # 优先读今日考勤历史中的实到；没有则用设置里的应到人数
        self.spinbox_attendance.place(x=920, y=380, width=260, height=40)
        self._load_attendance_into_ui()
        # 仅勾选时可编辑
        self._set_attendance_spinbox_state(bool(self.var_attendance_enabled.get()))

        # 「清理历史记录」已移至设置页「账密设置」右侧；主界面其余按钮位置不变
        self.button_exit_app=DButton(self.root,text='关闭程序',font=YAHEI_TEXT_FONT,command=self.exit_app,fg=REDTEXTFG)
        self.button_exit_app.place(x=920,y=590,width=260,height=60)

        self.button_settings=DButton(self.root,text='设置',command=self.open_settings_window,)
        self.button_settings.place(x=920,y=670,width=80,height=30)

        self.button_about=DButton(self.root,text='关于',command=self.about,)
        self.button_about.place(x=1020,y=670,width=80,height=30)

        self.frame_open_update_website=tk.Frame(self.root,bg=WINDOWBG,)
        self.frame_open_update_website.place(x=920,y=720,width=260,height=60)

        self.button_open_update_website=DAlphaButton(self.frame_open_update_website,text='正在获取更新',font=YAHEI_TEXT_FONT)
        self.button_open_update_website.pack(fill='both',expand=True)

        ConvertPlaceToRelative(self.root)

    def check_update(self,):
        update_file_url = "https://github.com/zhatujianguanzhe/homeworktool/blob/main/homeworktool.py"
        update_file_url_backup = "https://hfyzdns.cn/sandbox/s/wanseitool/homeworktool.py"
        try:
            self.ONLINE_VERSION = get_ONLINE_VERSION(update_file_url)
        except Exception:
            print(f"从Github获取更新失败:\n=======================\n{traceback.format_exc()}\n=======================\n\n正在从镜像获取更新.")
            try:
                self.ONLINE_VERSION = get_ONLINE_VERSION(update_file_url_backup)
            except Exception:
                self.ONLINE_VERSION = None
                print(f"从镜像获取更新失败:\n=======================\n{traceback.format_exc()}\n=======================\n")
            
        local_version=get_local_version()
        print(f"最新版本: {self.ONLINE_VERSION}\n当前版本: {local_version}")


        
        if self.ONLINE_VERSION==None:
            self.UPDATE_LEVEL='unknow'
            self.button_open_update_website.config(text='获取更新失败',command=self.open_update_window)
         #   tk.Label(self.frame_open_update_website,bg=WINDOWBG,text="获取更新失败",fg=TEXTFG,font=YAHEI_TEXT_FONT).pack(fill='both')
        elif self.ONLINE_VERSION[0]> local_version[0]:
            self.UPDATE_LEVEL='high'
            self.button_open_update_website.config(command=self.open_update_window, text=f"发现大更新版本: V{'.'.join([str(x) for x in self.ONLINE_VERSION])}",fg=REDTEXTFG)
        elif self.ONLINE_VERSION[0]==local_version[0] and self.ONLINE_VERSION[1]> local_version[1]:
            self.UPDATE_LEVEL='medium'
            self.button_open_update_website.config(command=self.open_update_window, text=f"发现质量更新版本: V{'.'.join([str(x) for x in self.ONLINE_VERSION])}",fg=YELLOWTEXTFG)
        elif self.ONLINE_VERSION[0]==local_version[0] and self.ONLINE_VERSION[1]==local_version[1] and self.ONLINE_VERSION[2]> local_version[2]:
            self.UPDATE_LEVEL='low'
            self.button_open_update_website.config(command=self.open_update_window, text=f"发现小更新版本: V{'.'.join([str(x) for x in self.ONLINE_VERSION])}",fg=HIGHLIGHT)
        else:
            self.UPDATE_LEVEL='none'
            self.button_open_update_website.config(text='当前已是最新版本',fg=GREENLIGHT,command=self.open_update_window, )
           
    def open_update_window(self,):
        def close_update_window(event=None):
            self.root.attributes('-disabled', False)
            self.update_window.destroy()
            self.root.focus_set()
        self.root.attributes('-disabled', True)
        self.update_window = tk.Toplevel(self.root)
        self.update_window.title('软件更新')
        self.update_window.geometry(f'240x220+{(self.update_window.winfo_screenwidth() - 240) // 2}+{(self.update_window.winfo_screenheight() - 220) // 2}')
        self.update_window.resizable(False, False)
        self.update_window['bg'] = WINDOWBG
        self.update_window.protocol('WM_DELETE_WINDOW', close_update_window)
        self.update_window.bind('<Escape>', close_update_window)
        self.update_window.wm_transient(self.root)
        self.update_window.focus()
        color_dict={'unknow':SECONDARYTEXTFG,'high':REDTEXTFG,'medium':YELLOWTEXTFG,'low':HIGHLIGHT,'none':GREENLIGHT}

        tk.Label(self.update_window,bg=WINDOWBG,text='当前版本:',fg=TEXTFG).place(x=20,y=20,height=30)
        label_local_version=tk.Label(self.update_window,anchor='e',text=VERSION,bg=WINDOWBG,fg=color_dict[self.UPDATE_LEVEL])
        label_local_version.place(x=130,y=20,width=90,height=30)

        tk.Label(self.update_window,fg=TEXTFG,bg=WINDOWBG,text='最新版本:').place(x=20,y=70,height=30)
        label_online_version=tk.Label(self.update_window,anchor='e',text='.'.join([str(x) for x in self.ONLINE_VERSION]) if self.ONLINE_VERSION!=None else "获取失败",bg=WINDOWBG,fg=SECONDARYTEXTFG)
        label_online_version.place(x=130,y=70,width=90,height=30)

        button_goto_github_release=DButton(self.update_window,text='前往Github下载页',command=lambda:webbrowser.open('https://github.com/zhatujianguanzhe/homeworktool/releases'))
        button_goto_github_release.place(x=20,y=120,width=200,height=30)

        button_goto_github_release=DButton(self.update_window,text='前往社团网站下载页(推荐)',command=lambda:webbrowser.open('https://hfyzdns.cn/sandbox/s/wanseitool/'))
        button_goto_github_release.place(x=20,y=170,width=200,height=30)

        SetDarkTitleBar(self.update_window)
        self.update_window.wm_iconbitmap(f"{libresource}icon.ico")
        self.update_window.mainloop()

    def load_runtime_settings(self):
        """从 settings 合并导出/界面常量到 self.export_cfg. 并同步全局 YAHEI_TEXT_FONT."""
        global YAHEI_TEXT_FONT
        if not isinstance(getattr(self, 'settings', None), dict):
            self.settings = {}

        cfg = dict(DEFAULT_EXPORT_SETTINGS)
        for k, default in DEFAULT_EXPORT_SETTINGS.items():
            if k in self.settings:
                cfg[k] = self.settings[k]
        # 兼容旧字段
        if 'highlight_box' in self.settings:
            cfg['highlight_box'] = self.settings['highlight_box']
        self.export_cfg = cfg

        # 写回 settings，保证文件里始终有完整键
        for k, v in cfg.items():
            self.settings.setdefault(k, v)

        self.disable_highdpi_scaling = bool(self.settings.get('disable_highdpi_scaling', False))
        if self.disable_highdpi_scaling:
            SetDPI()
        self.auto_set_desktop_background = bool(self.settings.get('auto_set_desktop_background', True))

        try:
            self.expected_attendance = int(self.settings.get('expected_attendance', 50))
        except (TypeError, ValueError):
            self.expected_attendance = 50
        self.settings['expected_attendance'] = self.expected_attendance
        self.attendance_enabled = bool(self.settings.get('attendance_enabled', False))
        self.settings['attendance_enabled'] = self.attendance_enabled

        font_setting = self.settings.get('YAHEI_TEXT_FONT', ['微软雅黑', 12])
        YAHEI_TEXT_FONT = font_setting
        self.settings['YAHEI_TEXT_FONT'] = font_setting

        # 深色/浅色模式: 仅允许 system / dark / light
        cm = str(self.settings.get('color_mode', self._cfg('color_mode', 'system')) or 'system').strip().lower()
        if cm not in ('system', 'dark', 'light'):
            cm = 'system'
        self.color_mode = cm
        self.settings['color_mode'] = cm
        if hasattr(self, 'export_cfg'):
            self.export_cfg['color_mode'] = cm

    def _cfg(self, key, default=None):
        """读取导出配置项."""
        if hasattr(self, 'export_cfg') and key in self.export_cfg:
            return self.export_cfg[key]
        return DEFAULT_EXPORT_SETTINGS.get(key, default)

    def _parse_bg_color(self, value, fallback=(250, 249, 230)):
        """解析 #RRGGBB / R,G,B / 名称近似；失败返回 fallback."""
        if value is None:
            return fallback
        s = str(value).strip()
        if not s:
            return fallback
        if s.startswith('#') and len(s) >= 7:
            try:
                return (int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16))
            except ValueError:
                return fallback
        if ',' in s:
            try:
                parts = [int(float(x.strip())) for x in s.split(',')[:3]]
                if len(parts) == 3:
                    return tuple(max(0, min(255, p)) for p in parts)
            except (TypeError, ValueError):
                return fallback
        return fallback

    def _make_export_background(self, img_width, img_height):
        """按设置生成导出用底图 (RGB)."""
        mode = str(self._cfg('background_mode', '纯色') or '纯色').strip()
        color = self._parse_bg_color(self._cfg('background_color', '#FAF9E6'))
        base = Image.new('RGB', (img_width, img_height), color)
        if mode != '图片':
            return base
        path = str(self._cfg('background_image_path', '') or '').strip()
        if not path or not os.path.isfile(path):
            return base
        try:
            fg = Image.open(path).convert('RGB')
        except Exception:
            return base
        stretch = str(self._cfg('background_stretch_mode', '完全拉伸') or '完全拉伸').strip()
        fw, fh = fg.size
        if fw <= 0 or fh <= 0:
            return base
        if stretch == '完全拉伸':
            fg = fg.resize((img_width, img_height), Image.LANCZOS)
            base.paste(fg, (0, 0))
        elif stretch == '横向拉伸':
            # 宽铺满，高按比例，垂直居中
            new_h = max(1, int(round(img_width * fh / float(fw))))
            fg = fg.resize((img_width, new_h), Image.LANCZOS)
            y = (img_height - new_h) // 2
            base.paste(fg, (0, y))
        elif stretch == '纵向拉伸':
            new_w = max(1, int(round(img_height * fw / float(fh))))
            fg = fg.resize((new_w, img_height), Image.LANCZOS)
            x = (img_width - new_w) // 2
            base.paste(fg, (x, 0))
        else:
            # 不拉伸：原尺寸居中（超出则裁剪居中区域）
            if fw >= img_width and fh >= img_height:
                left = (fw - img_width) // 2
                top = (fh - img_height) // 2
                fg = fg.crop((left, top, left + img_width, top + img_height))
                base.paste(fg, (0, 0))
            else:
                x = (img_width - fw) // 2
                y = (img_height - fh) // 2
                base.paste(fg, (x, y))
        return base

    def export_homework_image(self):

        """将当前作业导出为3840x2160的jpg图片（左右两列,自动换行,字号自适应缩小）"""
        if not self.verify_admin_password():
            return

        # 检查是否有作业
        has_homework = any(len(homework) > 0 for homework in self.homework_data.values())
      
        try:
            img_width, img_height = 3840, 2160
            bg_color = self._parse_bg_color(self._cfg('background_color', '#FAF9E6'))
            text_color = (0, 0, 0)
            divider_color = (160, 160, 160)

            date = datetime.datetime.now().strftime('%Y-%m-%d')

            # 科目顺序
            default_subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']
            template_subjects = list(self.homework_template.keys())
            all_subjects = []
            for subject in default_subjects + template_subjects:
                if subject not in all_subjects:
                    all_subjects.append(subject)
            for subject in self.homework_data.keys():
                if subject not in all_subjects:
                    all_subjects.append(subject)

            # 收集要绘制的块：('subject', text) 或 ('content', text)
            blocks = []
            for subject in all_subjects:
                homework_list = self.homework_data.get(subject, [])
                if not homework_list:
                    continue
                blocks.append(('subject', f"{subject}:", None, False, False, False))
                for index, content in enumerate(homework_list, start=1):
                    body, style_color, style_bold, style_inverse, style_bg_invert = parse_homework_style(content)
                    blocks.append(('content', f"  {index}.{body}", style_color, style_bold, style_inverse, style_bg_invert))
                blocks.append(('gap', '', None, False, False, False))  # 科目之间的额外间距

            # 使用模块级常量
            margin_x = int(self._cfg('EXPORT_MARGIN_X'))
            margin_bottom = int(self._cfg('EXPORT_MARGIN_BOTTOM'))
            date_y = int(self._cfg('EXPORT_DATE_Y'))
            start_y = int(self._cfg('EXPORT_START_Y'))
            gap_center = int(self._cfg('EXPORT_GAP_CENTER'))
            center_x = img_width // 2
            col_width = center_x - margin_x - gap_center

            size_subject = int(self._cfg('EXPORT_FONT_SUBJECT'))
            size_content = int(self._cfg('EXPORT_FONT_CONTENT'))
            size_date = int(self._cfg('EXPORT_FONT_DATE'))
            min_size_subject = int(self._cfg('EXPORT_FONT_SUBJECT_MIN'))
            min_size_content = int(self._cfg('EXPORT_FONT_CONTENT_MIN'))

            line_spacing_content = int(self._cfg('EXPORT_LINE_SPACING_CONTENT'))
            line_spacing_subject = int(self._cfg('EXPORT_LINE_SPACING_SUBJECT'))
            subject_gap = int(self._cfg('EXPORT_SUBJECT_GAP'))

            def _try_truetype(name_or_path, size):
                """按字体名或路径加载;失败返回 None"""
                try:
                    return ImageFont.truetype(name_or_path, size)
                except (OSError, IOError):
                    return None

            def load_font_chain(size):
                """
                按 EXPORT_FONT_NAME 与回退列表加载字体链.
                链中第一个为优先字体,缺字时向后查找.
                """
                names = []
                for n in (self._cfg('EXPORT_FONT_NAME'),) + tuple(self._cfg('EXPORT_FONT_FALLBACK_NAMES') or []):
                    if n and n not in names:
                        names.append(n)
                chain = []
                for name in names:
                    f = _try_truetype(name, size)
                    if f is not None:
                        chain.append(f)
                # 再尝试 Windows 字体目录下常见文件（名称加载失败时）
                fonts_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')
                file_candidates = [
                    'simsun.ttc', 'simsun.ttf', 'msyh.ttc', 'msyh.ttf',
                    'simhei.ttf', 'segoeui.ttf', 'seguisym.ttf', 'arial.ttf',
                ]
                for fn in file_candidates:
                    path = os.path.join(fonts_dir, fn)
                    if os.path.isfile(path):
                        f = _try_truetype(path, size)
                        if f is not None and f not in chain:
                            chain.append(f)
                if not chain:
                    chain.append(ImageFont.load_default())
                return chain

            def load_fonts(s_subj, s_cont, s_date):
                return (
                    load_font_chain(s_subj),
                    load_font_chain(s_cont),
                    load_font_chain(s_date),
                )

            def font_has_char(font, char):
                """判断字体是否包含该字符（粗略：mask 有非空 bbox）"""
                if not char or char in ('\n', '\r', '\t'):
                    return True
                try:
                    mask = font.getmask(char)
                    box = mask.getbbox()
                    return box is not None
                except (TypeError, ValueError, OSError):
                    return False

            def pick_font(char, font_chain):
                """为单字符在字体链中选第一个可用字体"""
                for f in font_chain:
                    if font_has_char(f, char):
                        return f
                return font_chain[-1]

            def text_width(draw_obj, text, font_chain):
                """按字符选用字体后累计宽度（font_chain 为列表;兼容单字体）"""
                if not text:
                    return 0
                if not isinstance(font_chain, (list, tuple)):
                    font_chain = [font_chain]
                w = 0
                for ch in text:
                    f = pick_font(ch, font_chain)
                    bbox = draw_obj.textbbox((0, 0), ch, font=f)
                    w += bbox[2] - bbox[0]
                return w

            def text_height(draw_obj, text, font_chain):
                if not text:
                    text = '中'
                if not isinstance(font_chain, (list, tuple)):
                    font_chain = [font_chain]
                h = 0
                for ch in text:
                    f = pick_font(ch, font_chain)
                    bbox = draw_obj.textbbox((0, 0), ch, font=f)
                    h = max(h, bbox[3] - bbox[1])
                if h <= 0:
                    f = font_chain[0]
                    bbox = draw_obj.textbbox((0, 0), '中', font=f)
                    h = bbox[3] - bbox[1]
                return h

            def draw_text_mixed(draw_obj, xy, text, fill, font_chain, anchor=None, bold=False):
                """按字符缺字回退绘制;支持 anchor='mt';bold 时用描边模拟加粗"""
                if not text:
                    return
                if not isinstance(font_chain, (list, tuple)):
                    font_chain = [font_chain]
                x, y = xy
                if anchor == 'mt':
                    total_w = text_width(draw_obj, text, font_chain)
                    x = x - total_w / 2
                offsets = [(0, 0), (1, 0), (0, 1), (1, 1)] if bold else [(0, 0)]
                for ch in text:
                    f = pick_font(ch, font_chain)
                    for dx, dy in offsets:
                        draw_obj.text((x + dx, y + dy), ch, fill=fill, font=f)
                    bbox = draw_obj.textbbox((0, 0), ch, font=f)
                    x += bbox[2] - bbox[0]

            def wrap_plain(draw_obj, text, font, max_width):
                """普通按像素宽度换行,返回行文本列表"""
                if not text:
                    return ['']
                if text_width(draw_obj, text, font) <= max_width:
                    return [text]
                lines = []
                current = ''
                for ch in text:
                    trial = current + ch
                    if text_width(draw_obj, trial, font) <= max_width:
                        current = trial
                    else:
                        if current:
                            lines.append(current)
                        if text_width(draw_obj, ch, font) > max_width:
                            lines.append(ch)
                            current = ''
                        else:
                            current = ch
                if current:
                    lines.append(current)
                return lines if lines else ['']

            def wrap_content_hang(draw_obj, text, font, max_width):
                """
                作业内容换行：续行与「数字.」之后的第一个字符对齐.
                返回 list of (text, x_offset_px)
                例: "  1.完成练习册很长..."
                    第一行从列起点画;续行 x 偏移 = 「  1.」的宽度
                """
                m = re.match(r'^(\s*\d+\.)', text)
                if not m:
                    return [(line, 0) for line in wrap_plain(draw_obj, text, font, max_width)]
                prefix = m.group(1)
                body = text[len(prefix):]
                indent = text_width(draw_obj, prefix, font)
                # 续行开头再多一个空格,与「数字.」后内容对齐时略偏右一点
                space_w = text_width(draw_obj, ' ', font)
                body_width = max(max_width - indent - space_w, 20)

                if text_width(draw_obj, text, font) <= max_width:
                    return [(text, 0)]

                # 第一行：尽量塞满整列宽
                first_body = ''
                rest = body
                for i, ch in enumerate(body):
                    trial = prefix + body[:i + 1]
                    if text_width(draw_obj, trial, font) <= max_width:
                        first_body = body[:i + 1]
                        rest = body[i + 1:]
                    else:
                        break
                result = [(prefix + first_body, 0)]
                if rest:
                    for line in wrap_plain(draw_obj, rest, font, body_width):
                        # 续行开头多一个空格
                        result.append((' ' + line, indent))
                return result

            def try_layout(draw_obj, font_subj, font_cont, line_spacing_content, line_spacing_subject, subject_gap):
                """
                尝试把 blocks 排进左右两列.
                成功返回 (True, left_lines, right_lines)
                left/right_lines: list of (x, y, text, font)
                """
                left_x = margin_x
                right_x = center_x + gap_center
                max_y = img_height - margin_bottom

                left_items = []
                right_items = []
                current_col = 'left'
                y = start_y

                def place_line(text, font, extra_after=0, x_offset=0, style_color=None, style_bold=False, style_inverse=False, style_bg_invert=False):
                    nonlocal y, current_col
                    h = text_height(draw_obj, text if text else '中', font)
                    if y + h > max_y:
                        if current_col == 'left':
                            current_col = 'right'
                            y = start_y
                        else:
                            return False
                    base_x = left_x if current_col == 'left' else right_x
                    target = left_items if current_col == 'left' else right_items
                    target.append((base_x + x_offset, y, text, font, style_color, style_bold, style_inverse, style_bg_invert))
                    y = y + h + extra_after
                    return True

                for kind, text, style_color, style_bold, style_inverse, style_bg_invert in blocks:
                    if kind == 'gap':
                        y += subject_gap
                        continue
                    font = font_subj if kind == 'subject' else font_cont
                    spacing_after = line_spacing_subject if kind == 'subject' else line_spacing_content
                    if kind == 'content':
                        lines = wrap_content_hang(draw_obj, text, font, col_width)
                    else:
                        lines = [(line, 0) for line in wrap_plain(draw_obj, text, font, col_width)]
                    for i, (line, x_off) in enumerate(lines):
                        after = spacing_after if i == len(lines) - 1 else max(2, line_spacing_content // 2)
                        if not place_line(line, font, after, x_off, style_color, style_bold, style_inverse, style_bg_invert):
                            return False, None, None
                return True, left_items, right_items

            # 临时 draw 用于测宽（不落在最终图上）
            probe_img = self._make_export_background(img_width, img_height)
            probe_draw = ImageDraw.Draw(probe_img)

            final_left = final_right = None
            font_subject = font_content = font_date = None

            while size_subject >= min_size_subject and size_content >= min_size_content:
                font_subject, font_content, font_date = load_fonts(size_subject, size_content, size_date)
                ok, left_items, right_items = try_layout(
                    probe_draw, font_subject, font_content,
                    line_spacing_content, line_spacing_subject, subject_gap
                )
                if ok:
                    final_left, final_right = left_items, right_items
                    break
                # 放不下：字号再减 2,继续尝试
                size_subject -= 2
                size_content -= 2
                size_date = max(min_size_content, size_date - 2)

            if final_left is None:
                # 最小字号仍放不下,强制用最小字号画（可能溢出,但尽量完成）
                font_subject, font_content, font_date = load_fonts(min_size_subject, min_size_content, min_size_content)
                _, final_left, final_right = try_layout(
                    probe_draw, font_subject, font_content,
                    2, 8, 12
                )
                final_left = final_left or []
                final_right = final_right or []

            # 正式绘制
            img = self._make_export_background(img_width, img_height)
            draw = ImageDraw.Draw(img)

            # settings 中的高亮区域：在所有文字之前绘制深绿色矩形 [x, y, 宽, 高]
            hb = self._cfg('highlight_box') or self.settings.get('highlight_box')
            if hb and len(hb) >= 4:
                hx, hy, hw, hh = int(hb[0]), int(hb[1]), int(hb[2]), int(hb[3])
                if hw > 0 and hh > 0:
                    highlight_fill = (0, 110, 40)  # 深绿色
                    draw.rectangle(
                        [hx, hy, hx + hw, hy + hh],
                        fill=highlight_fill,
                        outline=None,
                    )
            draw_text_mixed(draw, (center_x, date_y), date, text_color, font_date, anchor='mt')

            # 自习考勤：标题居中后,在标题右侧单行黑底白字（字号取 EXPORT_FONT_ATTENDANCE）
            if hasattr(self, 'var_attendance_enabled'):
                att_on = bool(self.var_attendance_enabled.get())
            else:
                att_on = bool(getattr(self, 'attendance_enabled', False))
            if att_on:
                exp_n = int(getattr(self, 'expected_attendance', 50) or 50)
                act_n = self._get_actual_attendance_from_ui()
                self._save_attendance_record(date=date, expected=exp_n, actual=act_n)
                att_size = int(self._cfg('EXPORT_FONT_ATTENDANCE', 90) or 90)
                if att_size < 12:
                    att_size = 12
                font_att = load_font_chain(att_size)
                att_text = f'应到:{exp_n}人  实到:{act_n}人'
                tw = text_width(draw, att_text, font_att)
                th = text_height(draw, att_text, font_att)
                pad_x, pad_y = 20, 12
                box_w = tw + pad_x * 2
                box_h = th + pad_y * 2
                date_w = text_width(draw, date, font_date)
                date_h = text_height(draw, date, font_date)
                gap_after_title = max(40, size_date // 2)
                box_x1 = int(center_x + date_w / 2 + gap_after_title)
                margin_right = int(self._cfg('EXPORT_MARGIN_X'))
                if box_x1 + box_w > img_width - margin_right:
                    box_x1 = img_width - margin_right - box_w
                box_x2 = box_x1 + box_w
                box_cy = date_y + date_h / 2.0
                box_y1 = int(box_cy - box_h / 2.0)
                if box_y1 < 10:
                    box_y1 = 10
                box_y2 = box_y1 + box_h
                draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=(0, 0, 0), outline=None)
                draw_text_mixed(
                    draw, (box_x1 + pad_x, box_y1 + pad_y),
                    att_text, (255, 255, 255), font_att,
                )
            dash_len, gap_len = 24, 16
            y = start_y - 20
            while y < img_height - margin_bottom:
                y2 = min(y + dash_len, img_height - margin_bottom)
                draw.line([(center_x, y), (center_x, y2)], fill=divider_color, width=4)
                y = y2 + gap_len

            for item in (final_left or []) + (final_right or []):
                # 兼容 6/7/8 元组
                style_bg_invert = False
                if len(item) >= 8:
                    x, y, text, font, style_color, style_bold, style_inverse, style_bg_invert = item[:8]
                elif len(item) >= 7:
                    x, y, text, font, style_color, style_bold, style_inverse = item[:7]
                else:
                    x, y, text, font, style_color, style_bold = item[:6]
                    style_inverse = False
                if style_bg_invert:
                    # H：与背景图像对应像素反色（颜色标记忽略；仍可加粗）
                    if text:
                        font_chain = font if isinstance(font, (list, tuple)) else [font]
                        mask = Image.new('L', img.size, 0)
                        mask_draw = ImageDraw.Draw(mask)
                        draw_text_mixed(mask_draw, (x, y), text, 255, font_chain, bold=bool(style_bold))
                        bbox = mask.getbbox()
                        if bbox:
                            pix = img.load()
                            mp = mask.load()
                            x0, y0, x1, y1 = bbox
                            for py in range(y0, y1):
                                for px in range(x0, x1):
                                    a = mp[px, py]
                                    if not a:
                                        continue
                                    r, g, b = pix[px, py]
                                    inv = (255 - r, 255 - g, 255 - b)
                                    if a >= 250:
                                        pix[px, py] = inv
                                    else:
                                        k = a / 255.0
                                        pix[px, py] = (
                                            int(r + (inv[0] - r) * k),
                                            int(g + (inv[1] - g) * k),
                                            int(b + (inv[2] - b) * k),
                                        )
                elif style_inverse:
                    # F：黑底；前景默认白，若有颜色标记则用该颜色
                    fill = style_color if style_color else (255, 255, 255)
                    th = text_height(draw, text if text else '中', font)
                    tw = text_width(draw, text if text else '', font)
                    pad = 4
                    draw.rectangle(
                        [x - pad, y - pad, x + tw + pad, y + th + pad],
                        fill=(0, 0, 0),
                        outline=None,
                    )
                    draw_text_mixed(draw, (x, y), text, fill, font, bold=bool(style_bold))
                else:
                    fill = style_color if style_color else text_color
                    draw_text_mixed(draw, (x, y), text, fill, font, bold=bool(style_bold))

            filename = f"./homework_image/{date}.jpg"
            filepath = os.path.abspath(filename)
            
            dir_path = os.path.dirname(filepath)
            os.makedirs(dir_path, exist_ok=True)
            
            img.save(filepath, 'JPEG', quality=95)

            # 设为桌面壁纸（Windows，受 auto_set_desktop_background 开关控制）
            if getattr(self, 'auto_set_desktop_background', True):
                wallpaper_ok = False
                wallpaper_err = ''
                try:
                    SPI_SETDESKWALLPAPER = 20
                    SPIF_UPDATEINIFILE = 0x01
                    SPIF_SENDWININICHANGE = 0x02
                    result = ctypes.windll.user32.SystemParametersInfoW(
                        SPI_SETDESKWALLPAPER, 0, filepath,
                        SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
                    )
                    wallpaper_ok = bool(result)
                    if not wallpaper_ok:
                        wallpaper_err = 'SystemParametersInfoW 返回失败'
                except Exception as e:
                    wallpaper_err = str(e)

                if not wallpaper_ok:
                    if getattr(self, '_cli_mode', False):
                        print(f'[警告] 图片已保存至: {filepath}')
                        print(f'[警告] 设为桌面背景失败: {wallpaper_err}')
                    else:
                        MessageBoxModern(
                            parent=self.root, title='成功',
                            text=f'图片已保存至: {filepath}\n但设为桌面背景失败,详细信息:\n{wallpaper_err}',
                            text_blod='导出成功,设壁纸失败', icon='warning'
                        )

        except Exception:
            if getattr(self, '_cli_mode', False):
                print(f'[错误] 导出作业图片失败:\n{traceback.format_exc()}')
                raise
            MessageBoxModern(parent=self.root, title='错误', text=traceback.format_exc(), text_blod='导出作业图片失败', icon='error')

    def exit_app(self,):
        # 退出时保存今日实到考勤（若已勾选）
        if bool(self.var_attendance_enabled.get()):
            self._save_attendance_record()
        self.save_homework_history(silent=True)
        self.root.destroy()
        sys.exit()

    def _set_attendance_spinbox_state(self, enabled):
        """考勤 Spinbox：勾选时 normal,未勾选时 disabled."""
        state = 'normal' if enabled else 'disabled'
        
        self.spinbox_attendance.config(state=state)
       
    def _on_attendance_toggle(self):
        """主界面自习考勤勾选变化时写入 settings（仅开关,不含实到人数）."""
        enabled = bool(self.var_attendance_enabled.get())
        self.attendance_enabled = enabled
        self.settings['attendance_enabled'] = enabled
        self._set_attendance_spinbox_state(enabled)
        self._save_settings_file_quiet()

    def _load_attendance_into_ui(self, date=None):
        """从考勤历史读取指定日期（默认今日）的实到人数写入主界面 Spinbox；
        无记录时用设置中的应到人数。
        """
        if date is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        # 先保证 history 已加载
        if not isinstance(getattr(self, 'attendance_history', None), dict):
            self.attendance_history = {}
            with open('homeworktool_attendance.json', 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                self.attendance_history = loaded
        spin_val = int(getattr(self, 'expected_attendance', 50) or 50)
        rec = self.attendance_history.get(date)
        if isinstance(rec, dict) and 'actual' in rec:
            try:
                spin_val = int(rec.get('actual'))
            except (TypeError, ValueError):
                pass
        elif isinstance(rec, (int, float)):
            spin_val = int(rec)

        # 写入 Spinbox（即使当前 disabled 也要先 normal 再写回状态）
        was_on = bool(self.var_attendance_enabled.get()) if hasattr(self, 'var_attendance_enabled') else bool(getattr(self, 'attendance_enabled', False))
       
        self.spinbox_attendance.config(state='normal')
        self.spinbox_attendance.delete(0, tk.END)
        self.spinbox_attendance.insert(0, str(int(spin_val)))
        self._set_attendance_spinbox_state(was_on)

    def _get_actual_attendance_from_ui(self):
        """读取主界面实到人数 Spinbox,失败返回 0；允许负数；disabled 时也能读."""
        was_disabled = str(self.spinbox_attendance.cget('state')).lower() == 'disabled'
        if was_disabled:
            self.spinbox_attendance.config(state='normal')
       
        val = int(float(self.spinbox_attendance.get()))
 
        if was_disabled:
            self._set_attendance_spinbox_state(False)
        return val

    def _save_attendance_record(self, date=None, expected=None, actual=None):
        """将当日应到/实到写入 homeworktool_attendance.json（按日期为键,与作业历史类似）."""
        if date is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        if expected is None:
            try:
                expected = int(getattr(self, 'expected_attendance', 50) or 50)
            except (TypeError, ValueError):
                expected = 50
        if actual is None:
            actual = self._get_actual_attendance_from_ui()
        try:
            expected = int(expected)
        except (TypeError, ValueError):
            expected = 50
        try:
            actual = int(actual)
        except (TypeError, ValueError):
            actual = 0

        history = dict(self.attendance_history) if isinstance(getattr(self, 'attendance_history', None), dict) else {}
        with open('homeworktool_attendance.json', 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            history = loaded
        history[date] = {
            'expected': expected,
            'actual': actual,
        }
        self.attendance_history = history
        try:
            with open('homeworktool_attendance.json', 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def _save_settings_file_quiet(self):
        with open('homeworktool_settings.json', 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
  
    def get_subject_password(self, subject):
        """获取科目对应密码;无独立条目时回退 default"""
        pwd_map = self.settings.get('password', {})
        if subject in pwd_map:
            return pwd_map.get(subject, '') or ''
        return pwd_map.get('default', '') or ''

    def verify_subject_password(self, subject):
        """验证科目密码.密码为空则直接通过.返回 True/False."""
        expected = self.get_subject_password(subject)
        if expected == '':
            return True
        while True:
            password = self.open_password_window()
            if password in [None, False]:
                return False
            elif password == expected:
                return True
            else:
                MessageBoxModern(self.root, title='错误', icon='error', text_blod='密码错误', text='密码错误,请重试或咨询课代表.')

    def verify_admin_password(self):
        if getattr(self, '_cli_mode', False):
            return True
        """验证管理员密码.密码为空则直接通过."""
        expected = self.settings.get('password', {}).get('admin', '') or ''
        if expected == '':
            return True
        while True:
            password = self.open_password_window()
            if password in [None, False]:
                return False
            elif password == expected:
                return True
            else:
                MessageBoxModern(self.root, title='错误', icon='error', text_blod='管理员密码错误', text='密码错误,请重试或咨询课管理员.')

    def edit_homework(self, event=None):
        """主界面：双击行为见绑定说明；按钮仍按当前选中行编辑科目。"""
        # —— 双击 Treeview：按列/行类型分流 ——
        if event is not None and getattr(event, 'widget', None) is self.treeview_homework:
            try:
                row = self.treeview_homework.identify_row(event.y)
                col = self.treeview_homework.identify_column(event.x)
            except Exception:
                row, col = '', ''
            if not row:
                return
            parent = self.treeview_homework.parent(row)
            is_subject_row = (not parent)

            # 科目列：#0（树列）
            if col in ('#0', ''):
                if is_subject_row:
                    # 科目行 → 展开/收起，不打开编辑
                    opened = bool(self.treeview_homework.item(row, 'open'))
                    self.treeview_homework.item(row, open=not opened)
                    self.treeview_homework.selection_set(row)
                    self.treeview_homework.focus(row)
                    self.root.after_idle(lambda r=row: self._update_subject_state(r))
                    self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))
                    return 'break'
                else:
                    # 科目列上的作业子行 → 打开该科目编辑
                    self.open_edit_window_homework(parent)
                    return 'break'
            else:
                # 作业内容列 → 打开编辑（科目行或子行均可）
                subject = parent if parent else row
                self.open_edit_window_homework(subject)
                return 'break'

        # —— 按钮 / 其他调用：按选中行 ——
        selected = self.treeview_homework.selection()
        if not selected:
            win32api.MessageBeep()
            return
        item = selected[0]
        parent = self.treeview_homework.parent(item)
        subject = parent if parent else item
        self.open_edit_window_homework(subject)

    def remove_homework(self,):
        """删除选中的作业"""
        # 获取当前选中的项目
        selected = self.treeview_homework.selection()
        if not selected:
            win32api.MessageBeep()
            return
            
        # 选中的项目可能是科目节点,也可能是作业子节点
        item = selected[0]
        parent = self.treeview_homework.parent(item)
        
        # 如果没有父节点,说明选中的是科目行,报错
        if not parent:
            win32api.MessageBeep()
            return
            
      
        subject = parent
        # 获取该作业在列表中的序号（注意：Treeview中子节点的顺序与列表顺序一致）
        index = self.treeview_homework.index(item) + 1  # Treeview index从0开始,所以+1

        
        if not self.verify_subject_password(subject):
            return
        self.remove_treeview(subject, index)

    def open_edit_window_homework(self, subject):
        # 打开窗口前先验证该科目密码（为空则跳过）
        if not self.verify_subject_password(subject):
            return

        # 提前占位,供闭包使用
        edit_entry = [None]
        editing_index = [None]
        editing_item = [None]
        tree_ref = [None]
        frame_number_ref = [None]
        side_buttons_ref = [None]

        def close_window_homework(event=None):
            # 关闭前若正在编辑则先提交
            if edit_entry[0] is not None:
                commit_edit()
            window_homework.destroy()
            if self.treeview_homework.exists(subject):
                self.treeview_homework.item(subject, open=True)
                self._update_subject_state(subject)
                self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))
            self.root.focus()

        def on_window_escape(event=None):
            # 编辑中：Esc 只取消本次编辑,不关窗口
            if edit_entry[0] is not None:
                cancel_edit()
                return 'break'
            close_window_homework()

        window_homework = tk.Toplevel(self.root)
        window_homework.transient(self.root)
        window_homework.title(f"编辑科目 「{subject}」")
        SetDarkTitleBar(window_homework)
        width = 900
        height = 880
        screenwidth = window_homework.winfo_screenwidth()
        screenheight = window_homework.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        window_homework.geometry(geometry)
        window_homework['bg'] = WINDOWBG
        window_homework.protocol("WM_DELETE_WINDOW", close_window_homework)
        window_homework.bind('<Escape>', on_window_escape)
        window_homework.focus()

        # 工作列表（与 homework_data 同步）
        working_list = list(self.homework_data.get(subject, []))

        # ========== 表格（与主界面样式一致） ==========
        scrollbar_y = DScrollbar(window_homework)
        scrollbar_y.place(x=860, y=20, width=20, height=300)

        tree = ttk.Treeview(window_homework, show="tree headings", columns=["homework"],
                            takefocus=True, selectmode='browse',style='Main.Treeview',
                            yscrollcommand=scrollbar_y.set)
        tree.place(x=20, y=20, width=840, height=300)
        scrollbar_y.config(command=tree.yview)
        tree_ref[0] = tree

        tree.heading("#0", text="序号", anchor='center')
        tree.heading("homework", text="作业内容", anchor='center')
        tree.column("#0", width=50, anchor='center')
        tree.column("homework", width=700, anchor='w')

        def safe_set_row_color():
            """防止窗口已销毁后 after_idle 访问已删除的 tree 报错"""
            t = tree_ref[0]
            if t is not None and t.winfo_exists():
                SetExpandedTreeviewRowColor(t)
        def refresh_tree():
            for child in tree.get_children():
                tree.delete(child)
            for index, content in enumerate(working_list, start=1):
                tree.insert('', 'end', text=str(index), values=(content,))
            self.root.after_idle(safe_set_row_color)

        def sync_to_data():
            self.homework_data[subject] = list(working_list)

        refresh_tree()

        # ========== 右侧三个按钮：加号 / 三点 / 减号（40x40,间距20） ==========
        def is_focus_in_widget_or_children(focused, target):
            if focused is None or target is None:
                return False
            w = focused
            while w is not None:
                if w == target:
                    return True
                w = getattr(w, 'master', None)
                if w is None:
                    break
            return False

        def is_focus_on_keyboard_or_side():
            focused = window_homework.focus_get()
            if focused is None:
                return False
            # 键盘区域
            if frame_number_ref[0] is not None and is_focus_in_widget_or_children(focused, frame_number_ref[0]):
                return True
            # 右侧三个按钮
            if side_buttons_ref[0]:
                for btn in side_buttons_ref[0]:
                    if is_focus_in_widget_or_children(focused, btn):
                        return True
            return False

        def is_focus_on_edit():
            if edit_entry[0] is None:
                return False
            focused = window_homework.focus_get()
            if focused is None:
                return False
            if is_focus_in_widget_or_children(focused, edit_entry[0]):
                return True
            if hasattr(edit_entry[0], 'Entry') and is_focus_in_widget_or_children(focused, edit_entry[0].Entry):
                return True
            return False

        def cancel_edit():
            """取消本次编辑：丢弃输入；若是新建的空行则移除，否则保留原内容"""
            if edit_entry[0] is None:
                return
            idx = editing_index[0]
            edit_entry[0].destroy()
            edit_entry[0] = None
            editing_index[0] = None
            editing_item[0] = None
            button_ok.bind_default_active()
            if idx is not None and 0 <= idx < len(working_list):
                if working_list[idx].replace('\t', '').replace(' ', '') == '':
                    del working_list[idx]
                    sync_to_data()
            refresh_tree()

        def commit_edit():
            if edit_entry[0] is None:
                return
            try:
                new_text = edit_entry[0].get()
            except Exception:
                new_text = ''
            idx = editing_index[0]
            edit_entry[0].destroy()
            edit_entry[0] = None
            editing_index[0] = None
            editing_item[0] = None

            if idx is None or idx < 0 or idx >= len(working_list):
                button_ok.bind_default_active()
                return
            if new_text.replace('\t', '').replace(' ', '') == '':
                # 空内容视为删除
                del working_list[idx]
            else:
                working_list[idx] = new_text

            button_ok.bind_default_active()
            sync_to_data()
            refresh_tree()

        def start_edit(force_item=None):
            

            # 若已在编辑同一项,直接返回
            selected = tree.selection()
            if not selected and force_item is None:
                return
            item = force_item if force_item is not None else selected[0]
            if not tree.exists(item):
                return
            idx = tree.index(item)
            # 已经在编辑同一行则不重复创建
            if edit_entry[0] is not None and editing_item[0] == item:
                edit_entry[0].Entry.focus_set()
                return
            if edit_entry[0] is not None:
                commit_edit()
                # commit 后 item 可能失效,重新按 index 找
                children = tree.get_children()
                if idx >= len(children):
                    return
                item = children[idx]
                tree.selection_set(item)
                tree.focus(item)

            content = tree.item(item, 'values')[0] if tree.item(item, 'values') else ''

            # 只覆盖第二列（作业内容）,不覆盖序号列
            tree.update_idletasks()
            bbox = tree.bbox(item, column='homework')
            if not bbox:
                # 备用：整行 bbox 后手动偏移序号列宽度
                bbox = tree.bbox(item)
                if not bbox:
                    return
                bx, by, bw, bh = bbox
                col0_width = tree.column('#0', 'width')
                bx = bx + col0_width
                bw = max(bw - col0_width, 50)
            else:
                bx, by, bw, bh = bbox

            abs_x = tree.winfo_x() + bx
            abs_y = tree.winfo_y() + by

            entry = DCombobutton(window_homework, font=YAHEI_TEXT_FONT, state='normal')
            if subject in self.homework_template and 'template' in self.homework_template[subject]:
                entry['values'] = self.homework_template[subject]['template']
            entry.Entry.insert(0, content)
            entry.place(x=abs_x, y=abs_y, width=max(bw, 80), height=max(bh, 36))
            entry.Entry.focus_set()
            entry.Entry.select_range(0, tk.END)
            entry.Entry.icursor(tk.END)

            edit_entry[0] = entry
            editing_index[0] = idx
            editing_item[0] = item

            def on_focus_out(event=None):
                # 延迟检查,给小键盘按钮时间处理点击
                window_homework.after(150, _check_commit_after_focusout)
            entry.Entry.bind('<FocusOut>', on_focus_out, add='+')
            entry.bind('<FocusOut>', on_focus_out, add='+')

            # 回车接受编辑,Esc 取消编辑（阻止事件继续冒泡到窗口）
            def on_entry_return(event=None):
                commit_edit()
                return 'break'
            def on_entry_escape(event=None):
                cancel_edit()
                return 'break'
            entry.Entry.bind('<Return>', on_entry_return, add='+')
            entry.Entry.bind('<KP_Enter>', on_entry_return, add='+')
            entry.Entry.bind('<Escape>', on_entry_escape, add='+')
            entry.bind('<Return>', on_entry_return, add='+')
            entry.bind('<Escape>', on_entry_escape, add='+')

            button_ok.unbind_default_active()

            

        def _check_commit_after_focusout():
            if edit_entry[0] is None:
                return
            # 焦点仍在编辑框内 → 不销毁
            if is_focus_on_edit():
                return
            # 焦点在小键盘或右侧按钮上 → 不销毁（用户正在用键盘输入）
            if is_focus_on_keyboard_or_side():
                return
            # 其它情况视为编辑结束
            commit_edit()

        def add_homework():
            if edit_entry[0] is not None:
                commit_edit()
            working_list.append('')
            sync_to_data()
            refresh_tree()
            children = tree.get_children()
            if children:
                last = children[-1]
                tree.selection_set(last)
                tree.focus(last)
                tree.see(last)
                start_edit(force_item=last)

        def remove_selected():
            # 必须先记住要删除的下标：commit_edit / refresh_tree 会重建节点导致 selection 丢失
            idx = None
            if edit_entry[0] is not None and editing_index[0] is not None:
                idx = editing_index[0]
                # 丢弃正在编辑的内容,直接删行
                edit_entry[0].destroy()
                edit_entry[0] = None
                editing_index[0] = None
                editing_item[0] = None
                button_ok.bind_default_active()
            else:
                selected = tree.selection()
                if not selected:
                    win32api.MessageBeep()
                    return
                idx = tree.index(selected[0])
            if idx is not None and 0 <= idx < len(working_list):
                del working_list[idx]
                sync_to_data()
                refresh_tree()



        # 单击表格：
        # - 点到当前编辑行 → 保持编辑
        # - 点到其它行 → 结束编辑并进入该行（按索引切换,因 refresh 会换掉 item iid）
        # - 点到空白处：若正在编辑则仅结束编辑;若未编辑则新建一行并开始编辑
        def on_tree_click(event):
            clicked_row = tree.identify_row(event.y)
            if edit_entry[0] is not None:
                # 点在当前正在编辑的那一行上 → 保持编辑,不结束
                if clicked_row and editing_item[0] is not None and clicked_row == editing_item[0]:
                    return
                # 提交前记住目标行下标,以及当前编辑行是否会因空内容被删除
                target_idx = None
                if clicked_row:
                    try:
                        target_idx = tree.index(clicked_row)
                    except Exception:
                        target_idx = None
                will_delete = False
                old_edit_idx = editing_index[0]
                try:
                    txt = edit_entry[0].get()
                    will_delete = (txt.replace('\t', '').replace(' ', '') == '')
                except Exception:
                    will_delete = False
                # 结束当前编辑（会 refresh_tree,item iid 全部作废）
                commit_edit()
                # 正在编辑时点空白处：只结束,不再新建
                if not clicked_row:
                    return
                # 若提交时删掉了前面的行,目标下标需要前移
                if target_idx is not None and will_delete and old_edit_idx is not None and old_edit_idx < target_idx:
                    target_idx -= 1
                # 按索引选中并进入编辑
                if target_idx is not None:
                    def _switch_to_row(i=target_idx):
                        children = tree.get_children()
                        if 0 <= i < len(children):
                            item = children[i]
                            tree.selection_set(item)
                            tree.focus(item)
                            tree.see(item)
                            start_edit(force_item=item)
                    window_homework.after(30, _switch_to_row)
                return
            if clicked_row:
                # 未在编辑：点到某一行,延迟进入该行编辑（等 Treeview 完成选中）
                window_homework.after(30, lambda: start_edit())
            else:
                # 未在编辑状态时点空白处 → 新建一项作业
                window_homework.after(30, add_homework)
        tree.bind('<ButtonRelease-1>', on_tree_click, add='+')

        # ========== 小键盘功能逻辑（保持原样,目标改为当前编辑框） ==========
        def insert_char(char):
            if edit_entry[0] is None:
                win32api.MessageBeep()
                return
            target = edit_entry[0]
            if target.selection_present():
                target.delete(tk.SEL_FIRST, tk.SEL_LAST)
            target.insert(tk.INSERT, char)
            target.Entry.focus_set()

        def delete_back():
            if edit_entry[0] is None:
                return
            target = edit_entry[0]
            try:
                if target.selection_present():
                    target.delete(tk.SEL_FIRST, tk.SEL_LAST)
                else:
                    pos = target.index(tk.INSERT)
                    if pos > 0:
                        target.delete(pos - 1)
            except tk.TclError:
                pos = target.index(tk.INSERT)
                if pos > 0:
                    target.delete(pos - 1)
            target.Entry.focus_set()

        def delete_forward():
            if edit_entry[0] is None:
                return
            target = edit_entry[0]
            try:
                if target.selection_present():
                    target.delete(tk.SEL_FIRST, tk.SEL_LAST)
                else:
                    pos = target.index(tk.INSERT)
                    if pos < len(target.get()):
                        target.delete(pos)
            except tk.TclError:
                pos = target.index(tk.INSERT)
                if pos < len(target.get()):
                    target.delete(pos)
            target.Entry.focus_set()

        def move_cursor_left():
            if edit_entry[0] is None:
                return
            target = edit_entry[0]
            if target.selection_present():
                sel_start = target.index(tk.SEL_FIRST)
                target.select_clear()
                target.icursor(sel_start)
            else:
                current_pos = target.index(tk.INSERT)
                new_pos = current_pos - 1
                target.icursor(max(0, new_pos))
            target.Entry.focus_set()

        def move_cursor_right():
            if edit_entry[0] is None:
                return
            target = edit_entry[0]
            if target.selection_present():
                sel_end = target.index(tk.SEL_LAST)
                target.select_clear()
                target.icursor(sel_end)
            else:
                current_pos = target.index(tk.INSERT)
                text_len = len(target.get())
                new_pos = current_pos + 1
                target.icursor(min(new_pos, text_len))
            target.Entry.focus_set()

        def select_all():
            if edit_entry[0] is None:
                return
            target = edit_entry[0]
            if target.selection_present():
                target.select_clear()
            target.select_range(0, tk.END)
            target.Entry.focus_set()

        # ========== 键盘区域（保持原设计,仅调整位置） ==========
        frame_number = tk.Frame(window_homework, bg=WINDOWBG)
        frame_number.place(x=20, y=340, width=860, height=440)
        SetBorder(frame_number, focuscolor=BDCOLOR)
        frame_number_ref[0] = frame_number

        button_number_1 = DButton(frame_number, text='1', font=YAHEI_TEXT_FONT, command=lambda: insert_char('1'), takefocus=0)
        button_number_1.place(x=20, y=70, width=50, height=50)

        button_number_2 = DButton(frame_number, text='2', font=YAHEI_TEXT_FONT, command=lambda: insert_char('2'), takefocus=0)
        button_number_2.place(x=80, y=70, width=50, height=50)

        button_number_3 = DButton(frame_number, text='3', font=YAHEI_TEXT_FONT, command=lambda: insert_char('3'), takefocus=0)
        button_number_3.place(x=140, y=70, width=50, height=50)

        button_number_4 = DButton(frame_number, text='4', font=YAHEI_TEXT_FONT, command=lambda: insert_char('4'), takefocus=0)
        button_number_4.place(x=20, y=130, width=50, height=50)

        button_number_5 = DButton(frame_number, text='5', font=YAHEI_TEXT_FONT, command=lambda: insert_char('5'), takefocus=0)
        button_number_5.place(x=80, y=130, width=50, height=50)

        button_number_6 = DButton(frame_number, text='6', font=YAHEI_TEXT_FONT, command=lambda: insert_char('6'), takefocus=0)
        button_number_6.place(x=140, y=130, width=50, height=50)

        button_number_7 = DButton(frame_number, text='7', font=YAHEI_TEXT_FONT, command=lambda: insert_char('7'), takefocus=0)
        button_number_7.place(x=20, y=190, width=50, height=50)

        button_number_8 = DButton(frame_number, text='8', font=YAHEI_TEXT_FONT, command=lambda: insert_char('8'), takefocus=0)
        button_number_8.place(x=80, y=190, width=50, height=50)

        button_number_9 = DButton(frame_number, text='9', font=YAHEI_TEXT_FONT, command=lambda: insert_char('9'), takefocus=0)
        button_number_9.place(x=140, y=190, width=50, height=50)

        button_number_0 = DButton(frame_number, text='0', font=YAHEI_TEXT_FONT, command=lambda: insert_char('0'), takefocus=0)
        button_number_0.place(x=80, y=250, width=50, height=50)

        button_number_space = DButton(frame_number, text='\uE75D', font=self.font_icon, command=lambda: insert_char(' '), takefocus=0)
        button_number_space.place(x=20, y=250, width=50, height=50)

        button_number_backspace = DButton(frame_number, text='\uE750', font=self.font_icon, command=delete_back, takefocus=0)
        button_number_backspace.place(x=140, y=250, width=50, height=50)

        button_number_tilde = DButton(frame_number, text='~', font=YAHEI_TEXT_FONT, command=lambda: insert_char('~'), takefocus=0)
        button_number_tilde.place(x=200, y=70, width=50, height=50)

        button_number_P = DButton(frame_number, text='P', font=YAHEI_TEXT_FONT, command=lambda: insert_char('P'), takefocus=0)
        button_number_P.place(x=200, y=130, width=50, height=50)

        button_number_T = DButton(frame_number, text='T', font=YAHEI_TEXT_FONT, command=lambda: insert_char('T'), takefocus=0)
        button_number_T.place(x=200, y=190, width=50, height=50)

        button_number_del = DButton(frame_number, text='Del', font=YAHEI_TEXT_FONT, command=delete_forward, takefocus=0)
        button_number_del.place(x=200, y=250, width=50, height=50)

        button_number_goto_left = DButton(frame_number, text='\uE0A6', font=self.font_icon, command=move_cursor_left, takefocus=0)
        button_number_goto_left.place(x=20, y=310, width=50, height=50)

        button_number_goto_right = DButton(frame_number, text='\uE0AB', font=self.font_icon, command=move_cursor_right, takefocus=0)
        button_number_goto_right.place(x=80, y=310, width=50, height=50)

        button_number_select_all = DButton(frame_number, text='\uE13E', font=self.font_icon, command=select_all, takefocus=0)
        button_number_select_all.place(x=140, y=310, width=50, height=50)

        def run_open_touch_keyboard():
            OpenTouchKeyboard()
            if edit_entry[0] is None:
                return
            edit_entry[0].Entry.focus_set()
        button_number_open_touch_keyboard= DButton(frame_number, text='\uF741', font=self.font_icon, command=run_open_touch_keyboard, takefocus=0)
        button_number_open_touch_keyboard.place(x=20, y=370, width=50, height=50)

        def commit_and_add():
            """勾选：结束当前编辑,并新建一行继续编辑"""
            commit_edit()
            add_homework()

        button_number_commit_edit = DButton(frame_number, text='\uE001', font=self.font_icon, command=commit_and_add, takefocus=0)
        button_number_commit_edit.place(x=200, y=310, width=50, height=50)



        button_add = DButton(frame_number, text='\uF164', font=self.font_icon, command=add_homework, takefocus=0)
        button_add.place(x=140, y=370, width=50, height=50)

        '''button_edit = DButton(window_homework, text='∷', font=YAHEI_TEXT_FONT, command=lambda: start_edit(), takefocus=0)
        button_edit.place(x=20, y=220, width=40, height=40)'''

        button_del = DButton(frame_number, text='\uF166', font=self.font_icon, command=remove_selected, takefocus=0)
        button_del.place(x=200, y=370, width=50, height=50)

        side_buttons_ref[0] = (button_add,  button_del)


        tk.Label(frame_number, font=YAHEI_TEXT_FONT, anchor='w', text='数字键盘:', bg=WINDOWBG, fg=TEXTFG).place(x=20, y=20, width=240, height=40)
        

        tk.Label(frame_number, font=YAHEI_TEXT_FONT, anchor='w', text='量词候选词:', bg=WINDOWBG, fg=TEXTFG).place(x=270, y=20, width=240, height=40)
        text_measureword = tk.Text(frame_number, bd=0, highlightthickness=0, bg=TEXTBG, fg=TEXTFG,
                                   font=YAHEI_TEXT_FONT,
                                   insertbackground=GREENLIGHT,
                                   insertontime=500, insertofftime=500, insertwidth=4,
                                   selectforeground=TEXTFG, selectbackground=HIGHLIGHT, cursor='arrow',
                                   state='disabled')
        SetBorder(text_measureword)
        text_measureword.place(x=270, y=70, width=270, height=350)
        scrollbar_text_measureword = DScrollbar(frame_number, command=text_measureword.yview)
        scrollbar_text_measureword.place(x=540, y=70, width=20, height=350)
        text_measureword.config(yscrollcommand=scrollbar_text_measureword.set)

        tk.Label(frame_number, font=YAHEI_TEXT_FONT, anchor='w', text='其它候选词:', bg=WINDOWBG, fg=TEXTFG).place(x=580, y=20, width=240, height=40)
        text_otherword = tk.Text(frame_number, bd=0, highlightthickness=0, bg=TEXTBG, fg=TEXTFG,
                                 font=YAHEI_TEXT_FONT,
                                 insertbackground=GREENLIGHT,
                                 insertontime=500, insertofftime=500, insertwidth=3,
                                 selectforeground=TEXTFG, selectbackground=HIGHLIGHT, cursor='arrow',
                                 state='disabled')
        SetBorder(text_otherword)
        text_otherword.place(x=580, y=70, width=240, height=350)
        scrollbar_text_otherword = DScrollbar(frame_number, command=text_otherword.yview)
        scrollbar_text_otherword.place(x=820, y=70, width=20, height=350)
        text_otherword.config(yscrollcommand=scrollbar_text_otherword.set)

        # 填充候选词（科目已固定）
        def toggle_style_marker(letter):
            """在作业末尾切换样式字母.
            - O：加粗，有则删、无则加（可与颜色、反色共存）
            - F：反色（黑底，前景默认白），有则删、无则加（可与颜色、加粗共存）
            - R/G/Y/B：末尾只允许一个颜色；点新颜色会替换旧颜色；再点同一颜色则去掉
            只处理末尾连续的 RGYBOFHH.
            """
            if edit_entry[0] is None:
                win32api.MessageBeep()
                return
            target = edit_entry[0]
            try:
                s = target.get()
            except Exception:
                s = ''
            # 从末尾取出已有标记
            i = len(s)
            while i > 0 and s[i - 1] in HOMEWORK_STYLE_MARKERS:
                i -= 1
            body = s[:i]
            markers = list(s[i:])
            color_letters = set(HOMEWORK_STYLE_COLORS.keys())  # R G Y B

            if letter == 'O':
                if 'O' in markers:
                    markers = [m for m in markers if m != 'O']
                else:
                    markers.append('O')
            elif letter == 'F':
                if 'F' in markers:
                    markers = [m for m in markers if m != 'F']
                else:
                    markers = [m for m in markers if m != 'H']
                    markers.append('F')
            elif letter == 'H':
                if 'H' in markers:
                    markers = [m for m in markers if m != 'H']
                else:
                    markers = [m for m in markers if m != 'F']
                    markers.append('H')
            elif letter in color_letters:
                if letter in markers:
                    # 再点同一颜色 → 去掉该颜色，保留 O/F
                    markers = [m for m in markers if m != letter]
                else:
                    # 换新颜色：去掉所有旧颜色，保留 O/F，再追加本颜色
                    markers = [m for m in markers if m not in color_letters]
                    markers.append(letter)
            else:
                return

            # 规范化顺序：颜色 → F → O，且各最多一个
            has_o = 'O' in markers
            has_f = 'F' in markers
            has_h = 'H' in markers
            colors = [m for m in markers if m in color_letters]
            color = colors[-1] if colors else None
            tail = ''
            if color:
                tail += color
            if has_f:
                tail += 'F'
            if has_h:
                tail += 'H'
            if has_o:
                tail += 'O'
            new_s = body + tail
            target.delete(0, tk.END)
            target.insert(0, new_s)
            target.Entry.focus_set()
            target.Entry.icursor(tk.END)
        if subject in self.homework_template:
            for text in self.homework_template[subject].get('measureword', []):
                button = DButton(
                    text_measureword,
                    text=text,
                    command=lambda t=text: insert_char(t),
                    font=YAHEI_TEXT_FONT,
                    padx=15,
                    pady=15,)
                text_measureword.window_create('insert', window=button)
            for text in self.homework_template[subject].get('otherword', []):
                button = DButton(
                    text_otherword,
                    text=text,
                    command=lambda t=text: insert_char(t),
                    font=YAHEI_TEXT_FONT,
                    padx=15,
                    pady=15,)
                text_otherword.window_create('insert', window=button)
        style_btns = [
            ('R', REDTEXTFG),
            ('G', GREENLIGHT),
            ('Y', YELLOWTEXTFG),
            ('B', HIGHLIGHT),
            ('O', TEXTFG),
            ('F', TEXTFG),  # 反色：黑底，前景默认白
            ('H', TEXTFG),  # 背景像素反色显示文字
        ]
        for letter, fg in style_btns:
            try:
                button = DButton(
                    text_otherword,
                    text=letter,
                    command=lambda L=letter: toggle_style_marker(L),
                    font=('微软雅黑', 12, 'bold'),
                    fg=fg,
                    padx=15,
                    pady=15,)
                text_otherword.window_create('insert', window=button)
            except Exception:
                button = DButton(
                    text_otherword,
                    text=letter,
                    command=lambda L=letter: toggle_style_marker(L),
                    font=YAHEI_TEXT_FONT,
                    padx=15,
                    pady=15,)
                text_otherword.window_create('insert', window=button)

        # 点击窗口其他地方结束编辑（键盘区域、编辑框、右侧按钮除外）
        def on_window_button1(event):
            if edit_entry[0] is None:
                return
            w = event.widget
            # 编辑框内部
            if is_focus_in_widget_or_children(w, edit_entry[0]) or \
               (hasattr(edit_entry[0], 'Entry') and is_focus_in_widget_or_children(w, edit_entry[0].Entry)):
                return
            # 键盘区域内点击不结束编辑
            if is_focus_in_widget_or_children(w, frame_number):
                return
            # 右侧按钮
            if side_buttons_ref[0]:
                for btn in side_buttons_ref[0]:
                    if is_focus_in_widget_or_children(w, btn):
                        return
            # 表格本身点击由 on_tree_click 处理,这里不强制 commit（避免和单击进入编辑冲突）
            if is_focus_in_widget_or_children(w, tree):
                return
            commit_edit()
        window_homework.bind('<Button-1>', on_window_button1, add='+')

        button_ok=DButton(window_homework,text='完成',default='active',command=close_window_homework,font=YAHEI_TEXT_FONT)
        button_ok.place(x=20,y=800,width=860,height=60)


        ConvertPlaceToRelative(window_homework)
        window_homework.iconbitmap(f"{libresource}icon.ico")
        window_homework.wait_window()

    def open_password_window(self,):
        def close_window_password(event=None):
            self.root.attributes('-disabled', False)
            window_password.destroy()
            self.root.focus()
        result=None
        self.root.attributes('-disabled', True)
        window_password=tk.Toplevel(self.root)
        window_password.transient(self.root)
        window_password.title("输入密码")
        SetDarkTitleBar(window_password)
        width = 260
        height = 400
        screenwidth = window_password.winfo_screenwidth()
        screenheight = window_password.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        window_password.geometry(geometry)
        window_password['bg']=WINDOWBG
        window_password.protocol("WM_DELETE_WINDOW", close_window_password)
        window_password.bind('<Escape>',close_window_password)
        window_password.focus()

        entry_password=DEntry(window_password,state='readonly',font=YAHEI_TEXT_FONT,show='•',justify='center')
        entry_password.place(x=20,y=20,width=140,height=40)

        def insert_char(char):
            entry_password['state']='normal'
            entry_password.insert(tk.INSERT, char)
            entry_password['state']='readonly'
            
        def delete_back():
            entry_password['state']='normal'
            # 删除光标前一个字符
            pos = entry_password.index(tk.INSERT)
            if pos > 0:
                entry_password.delete(pos - 1)
            entry_password['state']='readonly'

        def ok():
            nonlocal result
            result=entry_password.get()
        
            
            close_window_password()


        button_number_backspace=DButton(window_password,text='\uE750',font=self.font_icon,command=delete_back)
        button_number_backspace.place(x=180,y=20,width=60,height=40)

        button_number_1=DButton(window_password,text='1',font=YAHEI_TEXT_FONT,command=lambda: insert_char('1'))
        button_number_1.place(x=20,y=80,width=60,height=60)

        button_number_2=DButton(window_password,text='2',font=YAHEI_TEXT_FONT,command=lambda: insert_char('2'))
        button_number_2.place(x=100,y=80,width=60,height=60)

        button_number_3=DButton(window_password,text='3',font=YAHEI_TEXT_FONT,command=lambda: insert_char('3'))
        button_number_3.place(x=180,y=80,width=60,height=60)

        button_number_4=DButton(window_password,text='4',font=YAHEI_TEXT_FONT,command=lambda: insert_char('4'))
        button_number_4.place(x=20,y=160,width=60,height=60)

        button_number_5=DButton(window_password,text='5',font=YAHEI_TEXT_FONT,command=lambda: insert_char('5'))
        button_number_5.place(x=100,y=160,width=60,height=60)

        button_number_6=DButton(window_password,text='6',font=YAHEI_TEXT_FONT,command=lambda: insert_char('6'))
        button_number_6.place(x=180,y=160,width=60,height=60)

        button_number_7=DButton(window_password,text='7',font=YAHEI_TEXT_FONT,command=lambda: insert_char('7'))
        button_number_7.place(x=20,y=240,width=60,height=60)

        button_number_8=DButton(window_password,text='8',font=YAHEI_TEXT_FONT,command=lambda: insert_char('8'))
        button_number_8.place(x=100,y=240,width=60,height=60)

        button_number_9=DButton(window_password,text='9',font=YAHEI_TEXT_FONT,command=lambda: insert_char('9'))
        button_number_9.place(x=180,y=240,width=60,height=60)

        button_number_0=DButton(window_password,text='0',font=YAHEI_TEXT_FONT,command=lambda: insert_char('0'))
        button_number_0.place(x=100,y=320,width=60,height=60)

        button_number_ok=DButton(window_password,text='确定',font=YAHEI_TEXT_FONT,command=ok)
        button_number_ok.place(x=20,y=320,width=60,height=60)

        button_number_cancel=DButton(window_password,text='取消',font=YAHEI_TEXT_FONT,command=close_window_password)
        button_number_cancel.place(x=180,y=320,width=60,height=60)

        window_password.iconbitmap(f"{libresource}icon.ico")
        window_password.wait_window()

        return result

    def password_control(self,):
        # 构建可选账户列表：admin、default、模板中的科目、settings中已有科目
        accounts = ['admin', 'default']
        for subject in self.homework_template.keys():
            if subject not in accounts:
                accounts.append(subject)
        for key in self.settings.get('password', {}).keys():
            if key not in accounts:
                accounts.append(key)
        result = PasswordBox(
            title='账号密码控制',
            text='请选择要修改密码的账户,并输入当前密码进行验证.',
            parent=self.window_settings,
            defaultuser='admin',
            defaultfocus=1,
            defaultpassword='',
            defaultusertuple=tuple(accounts),
            savepassword_state=False,
            usernamestate='normal',
            autoreset_password=True
        )

        if result is None or result[0] is None or result[1] is None:
            return  # 用户取消
        if result[0].replace(' ','')=='':
            MessageBoxModern(self.window_settings,icon='error',title='错误',text='用户名不能为空',text_blod='用户名不能为空')
            return

        username, password, _ = result

        # 验证密码
        if username == 'admin':
            correct_pwd = self.settings['password'].get('admin', '')
        else:
            correct_pwd = self.settings['password'].get(username, self.settings['password'].get('default', ''))

        if password != correct_pwd:
            MessageBoxModern(
                parent=self.window_settings,
                title='错误',
                icon='error',
                text_blod='密码错误',
                text='密码错误,请重试或咨询课管理员.'
            )
            return

        # 验证通过,提示即将输入新密码
        MessageBoxModern(
            parent=self.window_settings,
            title='成功',
            icon='correct',
            text_blod='验证成功',
            text='接下来将要输入新密码,请连续输入两次新密码.')

        # 第一次输入新密码
        new_pwd1 = self.open_password_window()
        if new_pwd1 in [None, False]:
            return  # 用户取消

        # 第二次输入新密码
        new_pwd2 = self.open_password_window()
        if new_pwd2 in [None, False]:
            return  # 用户取消

        if new_pwd1 != new_pwd2:
            MessageBoxModern(
                parent=self.window_settings,
                title='错误',
                icon='error',
                text_blod='两次密码不一致',
                text='两次输入的密码不相同,请重试.'
            )
            return

        # 两次密码相同,执行更改
        # 若科目在模板中但 settings 中没有,则新建
        if 'password' not in self.settings:
            self.settings['password'] = {}
        if username not in self.settings['password']:
            # 新建条目（无论是模板科目还是其他）
            self.settings['password'][username] = new_pwd1
        else:
            self.settings['password'][username] = new_pwd1

        try:
            with open('homeworktool_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            MessageBoxModern(
                parent=self.window_settings,
                title='成功',
                icon='correct',
                text_blod='密码修改成功',
                text=f'账户「{username}」的密码已成功修改.'
            )
        except Exception:
            MessageBoxModern(
                parent=self.window_settings,
                title='错误',
                icon='error',
                text_blod='保存设置失败',
                text=traceback.format_exc()
            )

    def save_homework_history(self, silent=False):
        """将当前作业保存到历史记录.成功时不弹窗,按钮短暂显示「成功」."""
        try:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            # 同步写入当日考勤历史（勾选自习考勤时）
            if hasattr(self, 'var_attendance_enabled'):
                att_on = bool(self.var_attendance_enabled.get())
            else:
                att_on = bool(getattr(self, 'attendance_enabled', False))
            if att_on:
                self._save_attendance_record(date=date)
            history = {}
            try:
                with open('homeworktool_previous_homework.json', 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                MessageBoxModern(parent=self.root,title='错误',text=traceback.format_exc(),text_blod='写入历史记录文件失败',icon='error')
            today_homework = {
                subject: homework
                for subject, homework in self.homework_data.items()
                if homework
            }

            history[date] = today_homework

            with open('homeworktool_previous_homework.json', 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            if silent:
                return

            # 成功：按钮文字改为「成功」,0.5 秒后恢复
            btn = self.button_save_homework_file
            old_text = btn['text']
            btn['text'] = '成功'
            def _restore():
                if btn.winfo_exists():
                    btn['text'] = old_text
                    btn._update_border_size()
            self.root.after(500, _restore)
        except Exception:
            if not silent:
                MessageBoxModern(parent=self.root,title='错误',text=traceback.format_exc(),text_blod='写入历史记录文件失败',icon='error')

    def clear_homework_history(self):
        """清空 previous_homework 历史记录（需 admin 密码）"""
        if not self.verify_admin_password():
            return
        confirm = MessageBoxModern(
            parent=self.window_settings,
            title='警告',
            icon='warning',
            text_blod='清理历史记录',
            text='三思而后行!\n将删除homeworktool_previous_homework.json中的全部历史记录,此操作不可撤销,是否继续?',
            button_mode=2,
            text_true='清理',
            text_false='取消',
        )
        if confirm is not True:
            return
        try:
            with open('homeworktool_previous_homework.json', 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            self.previous_homework = {}
            MessageBoxModern(
                parent=self.window_settings,
                title='成功',
                icon='correct',
                text_blod='清理完成',
                text='历史记录已全部清空.'
            )
        except Exception:
            MessageBoxModern(
                parent=self.window_settings,
                title='错误',
                icon='error',
                text_blod='清理历史记录失败',
                text=traceback.format_exc()
            )

    def load_homework_history(self):
        """载入历史记录：左侧日期列表 + 右侧图片预览，确定后进入科目导入窗口。"""
        if not self.verify_admin_password():
            return

        try:
            with open('homeworktool_previous_homework.json', 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            MessageBoxModern(
                parent=self.root, title='错误', icon='error',
                text_blod='载入历史记录文件失败', text=traceback.format_exc(),
            )
            return

        if not isinstance(history, dict) or not history:
            MessageBoxModern(
                parent=self.root, title='提示', icon='info',
                text_blod='无历史记录', text='homeworktool_previous_homework.json 中没有任何日期记录.',
            )
            return

        # 仅使用历史文件中出现的日期，忽略磁盘上多余图片
        date_list = sorted(
            (d for d in history.keys() if isinstance(history.get(d), dict)),
            reverse=True,
        )
        if not date_list:
            MessageBoxModern(
                parent=self.root, title='提示', icon='info',
                text_blod='无历史记录', text='历史文件中没有可导入的日期条目.',
            )
            return

        def close_win(event=None):
            win.destroy()
            self.root.focus()
        win = tk.Toplevel(self.root)
        win.title('回溯历史记录')
        SetDarkTitleBar(win)
        w, h = 900, 540
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry('%dx%d+%d+%d' % (w, h, (sw - w) // 2, (sh - h) // 2))
        win['bg'] = WINDOWBG
        win.protocol('WM_DELETE_WINDOW', close_win)
        win.bind('<Escape>', close_win)
        win.focus()

        # 左侧日期列表 + 滚动条（样式与设置界面 Listbox 一致）
        listbox_date = tk.Listbox(
            win, bd=0, bg=TEXTBG, highlightthickness=0, fg=TEXTFG,
            activestyle='none', selectmode='browse', exportselection=0,
            selectbackground=AlphaBlend(HIGHLIGHT, TEXTBG, 0.5), selectforeground=TEXTFG,
            font=YAHEI_TEXT_FONT,
        )
        listbox_date.place(x=20, y=20, width=180, height=450)
        scrollbar_date = DScrollbar(win, command=listbox_date.yview)
        scrollbar_date.place(x=200, y=20, width=20, height=450)
        listbox_date.config(yscrollcommand=scrollbar_date.set)

        for d in date_list:
            listbox_date.insert(tk.END, d)

        # 右侧预览区域
        preview_frame = tk.Frame(win, bg=TEXTBG, highlightthickness=0, bd=0)
        preview_frame.place(x=240, y=20, width=640, height=450)

        label_preview = tk.Label(
            preview_frame, bg=TEXTBG, fg=SECONDARYTEXTFG,
            text='选择日期', anchor='center', font=YAHEI_TEXT_FONT,bd=1,relief='solid',)
        label_preview.place(x=0, y=0, relwidth=1, relheight=1)

        # 防止 PhotoImage 被回收；记住当前预览日期与源图
        label_preview._photo_ref = None
        preview_state = {'date': None, 'src_img': None, 'after_id': None}

        def clear_preview(msg='找不到图片'):
            preview_state['date'] = None
            preview_state['src_img'] = None
            label_preview._photo_ref = None
            label_preview.config(image='', text=msg, fg=SECONDARYTEXTFG)

        def _render_preview_image(src_img):
            """按预览控件当前尺寸等比缩放（以更短边为限，完整装入控件内）."""
            try:
                preview_frame.update_idletasks()
                pw = max(int(preview_frame.winfo_width()), 1)
                ph = max(int(preview_frame.winfo_height()), 1)
            except Exception:
                pw, ph = 640, 450
            iw, ih = src_img.size
            if iw <= 0 or ih <= 0:
                clear_preview('找不到图片')
                return
            # 更短的一边决定缩放比，保证整图可见
            scale = min(pw / float(iw), ph / float(ih))
            nw = max(1, int(iw * scale))
            nh = max(1, int(ih * scale))
            try:
                resized = src_img.resize((nw, nh), Image.Resampling.LANCZOS)
            except Exception:
                resized = src_img.resize((nw, nh), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            label_preview._photo_ref = photo
            label_preview.config(image=photo, text='')

        def show_preview_for_date(date_str):
            if not date_str:
                clear_preview('请选择日期')
                return
            img_path = os.path.abspath(os.path.join('.', 'homework_image', f'{date_str}.jpg'))
            if not os.path.isfile(img_path):
                clear_preview('找不到图片')
                return
            try:
                src = Image.open(img_path)
                # 转为 RGB 副本，避免文件句柄与模式问题
                src = src.convert('RGB')
                preview_state['date'] = date_str
                preview_state['src_img'] = src
                _render_preview_image(src)
            except Exception:
                clear_preview('找不到图片')

        def on_preview_configure(event=None):
            """窗口/预览区尺寸变化时重新等比缩放."""
            src = preview_state.get('src_img')
            if src is None:
                return
            aid = preview_state.get('after_id')
            if aid is not None:
                win.after_cancel(aid)
            def _do():
                preview_state['after_id'] = None
                if preview_state.get('src_img') is not None:
                    _render_preview_image(preview_state['src_img'])
            preview_state['after_id'] = win.after(50, _do)

        def on_date_select(event=None):
            sel = listbox_date.curselection()
            if not sel:
                clear_preview('请选择日期')
                return
            show_preview_for_date(listbox_date.get(sel[0]))

        listbox_date.bind('<<ListboxSelect>>', on_date_select)
        preview_frame.bind('<Configure>', on_preview_configure)
        label_preview.bind('<Configure>', on_preview_configure)

        # 默认选中第一项并预览
        listbox_date.selection_set(0)
        listbox_date.activate(0)
        listbox_date.see(0)
        show_preview_for_date(date_list[0])

        def do_ok(event=None):
            sel = listbox_date.curselection()
            if not sel:
                MessageBoxModern(
                    parent=win, title='错误', icon='error',
                    text_blod='未选择日期', text='请先在左侧选择要载入的日期.',
                )
                return
            target_date = listbox_date.get(sel[0])
            if target_date not in history:
                MessageBoxModern(
                    parent=win, title='错误', icon='error',
                    text_blod='该日作业的历史记录不存在',
                    text=f'找不到{target_date}的作业记录.',
                )
                return
            target_homework = history.get(target_date) or {}
            subjects = [s for s, items in target_homework.items() if items]
            if not subjects:
                MessageBoxModern(
                    parent=win, title='错误', icon='error',
                    text_blod='无可导入内容',
                    text=f'「{target_date}」的历史记录中没有作业条目.',
                )
                return
            close_win()
            self._open_import_homework_window(target_date, target_homework, subjects)

        btn_ok = DButton(win, text='确定', default='active', command=do_ok)
        btn_ok.place(x=700, y=490, width=80, height=30)
        btn_cancel = DButton(win, text='取消', command=close_win)
        btn_cancel.place(x=800, y=490, width=80, height=30)

        ConvertPlaceToRelative(win)
        win.iconbitmap(f'{libresource}icon.ico')
        win.wait_window()

    def _open_import_homework_window(self, target_date, target_homework, subjects):
        """导入选项：表格列出科目及其每条作业,默认全不勾选.
        勾选科目 = 导入该科全部作业;否则只导入勾选的作业项.
        """
        MERGE_OPTIONS = ['合并', '直接覆盖']

        def close_win(event=None):
            win.destroy()
            self.root.focus()
        win = tk.Toplevel(self.root)
        win.title(f'导入历史记录 日期「{target_date}」')
        SetDarkTitleBar(win)
        w, h = 720, 560
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry('%dx%d+%d+%d' % (w, h, (sw - w) // 2, (sh - h) // 2))
        win['bg'] = WINDOWBG
        win.protocol('WM_DELETE_WINDOW', close_win)
        win.bind('<Escape>', close_win)
        win.focus()

        tk.Label(
            win, bg=WINDOWBG, fg=TEXTFG, anchor='w',
            text=f'勾选要导入的科目或作业（默认全不选）.  日期「{target_date}」',
            font=YAHEI_TEXT_FONT,
        ).place(x=20, y=15, width=500, height=30)

        # 全局合并策略
        tk.Label(win, bg=WINDOWBG, fg=TEXTFG, text='合并方式:', anchor='e').place(x=480, y=15, width=80, height=30)
        combo_global = DCombobutton(win, values=MERGE_OPTIONS, state='readonly')
        combo_global['state'] = 'normal'
        combo_global.delete(0, tk.END)
        combo_global.insert(0, MERGE_OPTIONS[0])
        combo_global['state'] = 'readonly'
        combo_global.place(x=560, y=15, width=120, height=30)

        text_box = tk.Text(
            win, bd=0, highlightthickness=0, bg=WIDGETBG, fg=TEXTFG,
            font='TkDefaultFont',
            insertbackground=GREENLIGHT,
            insertontime=500, insertofftime=500, insertwidth=3,
            selectforeground=TEXTFG, selectbackground=HIGHLIGHT,
            cursor='arrow',
        )
        text_box.place(x=20, y=55, width=660, height=440)
        SetBorder(text_box)
        scroll = DScrollbar(win, bg=WINDOWBG, command=text_box.yview)
        scroll.place(x=680, y=55, width=20, height=440)
        text_box.config(yscrollcommand=scroll.set)

        # subject -> {'subj_var': BoolVar, 'items': [(text, BoolVar), ...]}
        row_data = {}

        def _on_subject_toggle(subject):
            """勾选科目时勾选其下全部作业;取消科目时取消全部作业."""
            info = row_data.get(subject)
            if not info:
                return
            val = bool(info['subj_var'].get())
            for _txt, ivar in info['items']:
                ivar.set(val)
        def _on_item_toggle(subject):
            """若全部子项勾选则勾选科目;若有未勾选则取消科目勾选."""
            info = row_data.get(subject)
            if not info or not info['items']:
                return
            all_on = all(bool(iv.get()) for _t, iv in info['items'])
            # 避免递归触发科目 command 再改子项：仅同步科目框显示
            info['subj_var'].set(all_on)
        for subject in subjects:
            hist_items = list(target_homework.get(subject) or [])
            if not hist_items:
                continue
            cur_items = list(self.homework_data.get(subject, []) or [])
            tip = f'历史{len(hist_items)}条 / 当前{len(cur_items)}条'

            # 科目行
            frame_subj = tk.Frame(text_box, bg=WINDOWBG, bd=0, highlightthickness=0)
            text_box.window_create('end', window=frame_subj, padx=10, pady=6)
            text_box.insert('end', '\n')

            subj_var = tk.BooleanVar(value=False)  # 默认不勾选
            chk_subj = DCheckbutton(
                frame_subj,
                text=f'{subject}  ({tip})',
                variable=subj_var,
                command=lambda s=subject: _on_subject_toggle(s),
            )
            chk_subj.pack(side='left', padx=10, pady=6)

            items_vars = []
            for hw in hist_items:
                frame_item = tk.Frame(text_box, bg=WIDGETBG, bd=0, highlightthickness=0)
                text_box.window_create('end', window=frame_item, padx=10, pady=2)
                text_box.insert('end', '\n')
                # 缩进占位
                tk.Label(frame_item, bg=WIDGETBG, width=4, text='').pack(side='left')
                item_var = tk.BooleanVar(value=False)  # 默认不勾选
                display = hw if len(hw) <= 60 else (hw[:57] + '...')
                chk_item = DCheckbutton(
                    frame_item,
                    text=display,
                    variable=item_var,
                    command=lambda s=subject: _on_item_toggle(s),
                )
                chk_item.pack(side='left', padx=6, pady=2, fill='x')
                items_vars.append((hw, item_var))

            row_data[subject] = {'subj_var': subj_var, 'items': items_vars}

        text_box.config(state='disabled')

        def do_import():
            # 全局合并方式
            try:
                mode = combo_global.Entry.get().strip()
            except Exception:
                try:
                    mode = combo_global.get().strip()
                except Exception:
                    mode = MERGE_OPTIONS[0]
            if mode not in MERGE_OPTIONS:
                mode = MERGE_OPTIONS[0]

            imported_any = False
            for subject, info in row_data.items():
                hist_all = list(target_homework.get(subject) or [])
                # 勾选科目 → 全部;否则仅勾选的子项
                if bool(info['subj_var'].get()):
                    selected = list(hist_all)
                else:
                    selected = [txt for txt, iv in info['items'] if bool(iv.get())]
                if not selected:
                    continue

                cur_list = list(self.homework_data.get(subject, []) or [])
                if mode == '直接覆盖':
                    # 覆盖：仅写入所选条目（不是整科历史）
                    new_list = list(selected)
                else:
                    seen = set(cur_list)
                    new_list = list(cur_list)
                    for item in selected:
                        if item not in seen:
                            new_list.append(item)
                            seen.add(item)

                if subject not in self.homework_data:
                    if not self.treeview_homework.exists(subject):
                        self.treeview_homework.insert('', 'end', iid=subject, text=subject, values=('',))
                    self.homework_data[subject] = new_list
                else:
                    self.homework_data[subject] = new_list
                imported_any = True

            for subject in self.homework_data.keys():
                if self.homework_data[subject]:
                    self.treeview_homework.item(subject, open=True)
                self._update_subject_state(subject)
            self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))
            close_win()
            if imported_any:
                MessageBoxModern(
                    parent=self.root, title='成功', icon='correct',
                    text_blod='载入历史记录成功',
                    text=f'已按所选策略导入「{target_date}」的作业记录.',
                )
            else:
                MessageBoxModern(
                    parent=self.root, title='提示', icon='info',
                    text_blod='未导入任何内容',
                    text='请至少勾选一个科目或一条作业后再确定.',
                )

        btn_ok = DButton(win, text='确定', default='active', command=do_import)
        btn_ok.place(x=520, y=510, width=80, height=30)
        btn_cancel = DButton(win, text='取消', command=close_win)
        btn_cancel.place(x=620, y=510, width=80, height=30)

        ConvertPlaceToRelative(win)
        win.iconbitmap(f'{libresource}icon.ico')
        win.wait_window()

    def autoload_homework_histroy(self):
        try:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            with open('homeworktool_previous_homework.json', 'r', encoding='utf-8') as f:
                history = json.load(f)
            if date in history:
                target_homework = history[date]
                # 1. 清空当前所有科目的作业数据
                for subject in list(self.homework_data.keys()):
                    self.homework_data[subject] = []
                    self.treeview_homework.item(subject, open=False)
                # 2. 遍历并加载指定日期的作业数据
                for subject, homework_list in target_homework.items():
                    if subject in self.homework_data:
                        self.homework_data[subject] = homework_list
                    else:
                        self.treeview_homework.insert('', 'end', iid=subject, text=subject, values=('',))
                        self.homework_data[subject] = homework_list
                # 3. 展开所有有作业的科目节点并刷新状态
                for subject in self.homework_data.keys():
                    if self.homework_data[subject]:
                        self.treeview_homework.item(subject, open=True)
                    self._update_subject_state(subject)
            #MessageBoxModern(parent=self.root, title='提示', text=f'已自动载入今日({date})的作业记录.', text_blod='自动载入历史记录成功', icon='info')
            # 同步载入今日考勤实到人数到主界面
            self._load_attendance_into_ui(date)
        except (OSError, json.JSONDecodeError, KeyError, tk.TclError, TypeError, ValueError):
            pass  # 自动加载失败不阻断启动
        self._load_attendance_into_ui()
    
    def apply_homework_template(self,):
        # 默认九科（保证绝对顺序）
        default_subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']
        # 提取配置文件中的科目名(键名)
        template_subjects = list(self.homework_template.keys())
        
        # 按顺序合并：先默认九科,再将配置文件中多出来的自定义科目写入在最后
        all_subjects = []
        for subject in default_subjects + template_subjects:
            if subject not in all_subjects:
                all_subjects.append(subject)
        
        for subject in all_subjects:
            # 模板只是提供词语候选,不是需要布置的作业,因此初始化时作业列表一律为空
            self.homework_data[subject] = []
            
            # 在树状图中插入父节点 (科目)
            self.treeview_homework.insert('', 'end', iid=subject, text=subject, values=('',))
            
            # 插入该科目下的作业子节点 (由于使用了ObservableHomeworkDict,上面赋值时已自动触发过一次,这里再调用一次确保初始化无误)
            self._update_subject_ui(subject)

    def _update_subject_state(self, subject, event=None):
        """内部辅助函数：根据子节点数量和展开状态,更新科目行的作业列提示文字"""
        # 检查节点是否存在
        if not self.treeview_homework.exists(subject):
            return

        # 检查是否为科目节点（没有父节点）
        parent = self.treeview_homework.parent(subject)
        if parent:  # 如果有父节点,说明是作业子节点,不处理
            return

        children = self.treeview_homework.get_children(subject)
        is_open = self.treeview_homework.item(subject, 'open')

        if len(children) == 0:
            state_text = "???"
        elif not is_open:
            state_text = "已被折叠,请展开查看..."
        else:
            state_text = "↓"
            
        self.treeview_homework.item(subject, values=(state_text,))

    def _update_subject_ui(self, subject):
        """内部辅助函数：根据数据刷新某一科目下的所有子节点UI"""
        # 防止科目在树状图中还未初始化时刷新报错
        if not self.treeview_homework.exists(subject):
            return
            
        # 删除该科目下旧的子节点
        for child in self.treeview_homework.get_children(subject):
            self.treeview_homework.delete(child)
            
        # 插入新的子节点,并在科目列加上 1 2 3 序号
        for index, content in enumerate(self.homework_data[subject], start=1):
            self.treeview_homework.insert(subject, 'end', text=str(index), values=(content,))
            
        # 子节点更新完毕后,同步刷新该科目的状态文字
        self._update_subject_state(subject)

        self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))

    def add_treeview(self, subject, content):
        """
        添加作业
        :param subject: 科目名称,如 '语文'
        :param content: 作业内容,如 '完成练习册第5页'
        """
        if subject not in self.homework_data:
            # 如果是新科目,在树状图末尾新增父节点
            self.treeview_homework.insert('', 'end', iid=subject, text=subject, values=('',))
            self.homework_data[subject] = []  # 这一步会自动触发 _update_subject_ui

        # 数据中添加作业 (直接对列表操作,字典监听不到,所以需要手动赋值触发监听)
        self.homework_data[subject] = self.homework_data[subject] + [content]
        self.treeview_homework.item(subject, open=True)
        self._update_subject_state(subject)

    def edit_treeview(self, subject, index, new_content):
        """
        修改指定序号的作业内容
        :param subject: 科目名称,如 '语文'
        :param index: 数字序号,从1开始,如 1 或 3
        :param new_content: 更改的内容
        """
        if subject not in self.homework_data:
            return
        
        # 将用户传入的1-based序号转换为0-based的列表索引
        list_index = index - 1
        if 0 <= list_index < len(self.homework_data[subject]):
            # 更新数据 (通过复制列表修改后再赋值,触发字典的监听器)
            temp_list = self.homework_data[subject]
            temp_list[list_index] = new_content
            self.homework_data[subject] = temp_list

    def remove_treeview(self, subject, index):
        """
        删除指定序号的作业内容
        :param subject: 科目名称,如 '语文'
        :param index: 数字序号,从1开始,如 1 或 3
        """
        if subject not in self.homework_data:
            return
            
        # 将用户传入的1-based序号转换为0-based的列表索引
        list_index = index - 1
        if 0 <= list_index < len(self.homework_data[subject]):
            # 删除数据 (通过复制列表删除后再赋值,触发字典的监听器)
            temp_list = self.homework_data[subject]
            del temp_list[list_index]
            self.homework_data[subject] = temp_list

    def mainloop(self,):
        SetExpandedTreeviewRowColor(self.treeview_homework)
        self.root.iconbitmap(f"{libresource}icon.ico")
        self.root.mainloop()

    def open_settings_window(self, ):
        """全局配置窗口：DPI/壁纸开关 + 科目与候选词模板编辑."""

        DEFAULT_SUBJECTS = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']

        # 工作副本：仅点「确定」后写回文件与内存
        import copy
        work_template = copy.deepcopy(self.homework_template) if isinstance(self.homework_template, dict) else {}
        # 保证默认科目在模板中有条目（可为空 dict）
        for s in DEFAULT_SUBJECTS:
            if s not in work_template:
                work_template[s] = {}
            if not isinstance(work_template[s], dict):
                work_template[s] = {}
            work_template[s].setdefault('template', list(work_template[s].get('template', []) or []))
            work_template[s].setdefault('measureword', list(work_template[s].get('measureword', []) or []))
            work_template[s].setdefault('otherword', list(work_template[s].get('otherword', []) or []))

        # 记录重命名：old_name -> new_name（用于保存时同步 password / homework_data / 树节点）
        rename_map = {}  # 最终生效的旧名->新名（链式合并）
        removed_subjects = set()

        def close_window_settings(event=None):
            window_settings.destroy()
            self.root.focus()
        window_settings = tk.Toplevel(self.root)
        self.window_settings=window_settings
        window_settings.title("全局设置")
        SetDarkTitleBar(window_settings)
        width = 920
        height = 590
        screenwidth = window_settings.winfo_screenwidth()
        screenheight = window_settings.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        window_settings.geometry(geometry)
        window_settings['bg'] = WINDOWBG
        window_settings.protocol("WM_DELETE_WINDOW", close_window_settings)
        window_settings.bind('<Escape>', close_window_settings)
        window_settings.focus()

        var_checkbutton_disable_highdpi_scaling = tk.BooleanVar()
        var_checkbutton_disable_highdpi_scaling.set(bool(self.disable_highdpi_scaling))
        checkbutton_disable_highdpi_scaling = DCheckbutton(
            window_settings,
            text='禁用高DPI缩放.建议在1080p及以下分辨率勾选,2K及以上不要勾选.',
            variable=var_checkbutton_disable_highdpi_scaling,
        )
        checkbutton_disable_highdpi_scaling.place(x=20, y=20, height=30)

        var_checkbutton_auto_set_desktop_background = tk.BooleanVar()
        var_checkbutton_auto_set_desktop_background.set(bool(self.auto_set_desktop_background))
        checkbutton_auto_set_desktop_background = DCheckbutton(
            window_settings,
            text='自动设置作业图片为桌面背景.',
            variable=var_checkbutton_auto_set_desktop_background,
        )
        checkbutton_auto_set_desktop_background.place(x=20, y=60, height=30)

        tk.Label(
            window_settings, bg=WINDOWBG, fg=TEXTFG, text='应到人数:', anchor='w',
        ).place(x=20, y=100, width=90, height=30)
        spinbox_expected_attendance = DSpinbox(
            window_settings, int_only=True, from_=float('-inf'), to=float('inf'), increment=1,
        )
        try:
            spinbox_expected_attendance.delete(0, tk.END)
            spinbox_expected_attendance.insert(
                0, str(int(getattr(self, 'expected_attendance', 50)))
            )
        except Exception:
            spinbox_expected_attendance.insert(0, '50')
        spinbox_expected_attendance.place(x=110, y=100, width=120, height=30)

        tk.Label(window_settings, bg=TEXTBG).place(x=20, y=150, width=880, height=2)

        tk.Label(window_settings, bg=WINDOWBG, fg=TEXTFG, text='科目设定:', anchor='w').place(x=20, y=170, height=30)
        listbox_subject = tk.Listbox(
            window_settings, bd=0, bg=TEXTBG, highlightthickness=0, fg=TEXTFG,
            activestyle='none', selectmode='browse', exportselection=0,
            selectbackground=AlphaBlend(HIGHLIGHT, TEXTBG, 0.5), selectforeground=TEXTFG,
        )
        listbox_subject.place(x=20, y=210, width=120, height=310)
        scrollber_y_listbox_subject = DScrollbar(window_settings, command=listbox_subject.yview)
        scrollber_y_listbox_subject.place(x=140, y=210, width=20, height=310)
        listbox_subject.config(yscrollcommand=scrollber_y_listbox_subject.set)

        button_add_subject = DButton(window_settings, text='\uF164', font=self.font_icon)
        button_add_subject.place(x=180, y=210, width=30, height=30)  # 不允许与程序内的默认科目重名.
        BindTipWindow(button_add_subject, text='新增科目')

        button_rename_subject = DButton(window_settings, text='\uED63', font=self.font_icon)
        button_rename_subject.place(x=180, y=260, width=30, height=30)
        # 不允许重命名程序内的默认科目.点击保存配置按钮之后要同步更改程序内数据和三个外部文件的数据,但不更改过去的作业历史记录
        BindTipWindow(button_rename_subject, text='重命名科目(默认九科不可改)')

        button_remove_subject = DButton(window_settings, text='\uF166', font=self.font_icon)
        button_remove_subject.place(x=180, y=310, width=30, height=30)  # 不允许删除程序内的默认科目.点击删除按钮的时候要弹窗疑问.
        BindTipWindow(button_remove_subject, text='删除科目(默认九科不可删)')


        tk.Label(window_settings, bg=TEXTBG).place(x=230, y=170, width=2, height=350)


        tk.Label(window_settings, bg=WINDOWBG, fg=TEXTFG, text='选中的科目相关设定(每行一项,直接编辑):', anchor='w').place(x=250, y=170, height=30)

        def _make_settings_text(parent):
            """样式参考 MCLangTool 主文本框."""
            t = tk.Text(parent, bd=0, highlightthickness=0, bg=TEXTBG, fg=TEXTFG,
                                 font='TkDefaultFont',
                                 insertbackground=GREENLIGHT,
                                 insertontime=500, insertofftime=500, insertwidth=3,
                                 selectforeground=TEXTFG, selectbackground=HIGHLIGHT,)
            SetBorder(t)
            return t

        tk.Label(window_settings, bg=WINDOWBG, fg=TEXTFG, text='作业:', anchor='w').place(x=250, y=210, height=30)
        text_homework = _make_settings_text(window_settings)
        text_homework.place(x=250, y=250, width=250, height=270)
        scrollber_y_text_homework = DScrollbar(window_settings, command=text_homework.yview, bg=WINDOWBG)
        scrollber_y_text_homework.place(x=500, y=250, width=20, height=270)
        text_homework.config(yscrollcommand=scrollber_y_text_homework.set)

        tk.Label(window_settings, bg=WINDOWBG, fg=TEXTFG, text='量词候选词:', anchor='w').place(x=540, y=210, height=30)
        text_measure_word = _make_settings_text(window_settings)
        text_measure_word.place(x=540, y=250, width=150, height=270)
        scrollber_y_text_measure_word = DScrollbar(window_settings, command=text_measure_word.yview, bg=WINDOWBG)
        scrollber_y_text_measure_word.place(x=690, y=250, width=20, height=270)
        text_measure_word.config(yscrollcommand=scrollber_y_text_measure_word.set)

        tk.Label(window_settings, bg=WINDOWBG, fg=TEXTFG, text='其它候选词:', anchor='w').place(x=730, y=210, height=30)
        text_other_word = _make_settings_text(window_settings)
        text_other_word.place(x=730, y=250, width=150, height=270)
        scrollber_y_text_other_word = DScrollbar(window_settings, command=text_other_word.yview, bg=WINDOWBG)
        scrollber_y_text_other_word.place(x=880, y=250, width=20, height=270)
        text_other_word.config(yscrollcommand=scrollber_y_text_other_word.set)

        button_advanced = DButton(window_settings, text='高级设置', command=lambda: self.open_advanced_settings_window(window_settings))
        button_advanced.place(x=20, y=540, width=100, height=30)

        button_password_control=DButton(window_settings,text='账密设置',command=self.password_control)
        button_password_control.place(x=140,y=540,width=100,height=30)


        button_background_image_settings=DButton(window_settings,text='背景图像设置',command=lambda: self.open_background_image_settings_window(window_settings))
        button_background_image_settings.place(x=260,y=540,width=120,height=30)


        button_clear_history=DButton(window_settings,text='清理历史记录',fg=REDTEXTFG,command=self.clear_homework_history)
        button_clear_history.place(x=400,y=540,width=120,height=30)


        button_ok = DButton(window_settings, text='确定', default='active')
        button_ok.place(x=720, y=540, width=80, height=30)
        button_ok.unbind_default_active()

        button_cancel = DButton(window_settings, text='取消', command=close_window_settings)
        button_cancel.place(x=820, y=540, width=80, height=30)
        button_cancel.unbind_default_active()

        # ---------- 辅助 ----------
        def ordered_subjects():
            """默认九科优先,其后为自定义科目(按当前 work_template 键顺序)."""
            seen = []
            for s in DEFAULT_SUBJECTS:
                if s in work_template and s not in seen:
                    seen.append(s)
            for s in work_template.keys():
                if s not in seen:
                    seen.append(s)
            return seen

        def refresh_subject_list(select_name=None):
            listbox_subject.delete(0, tk.END)
            for s in ordered_subjects():
                listbox_subject.insert(tk.END, s)
            if select_name and select_name in work_template:
                idx = ordered_subjects().index(select_name)
                listbox_subject.selection_clear(0, tk.END)
                listbox_subject.selection_set(idx)
                listbox_subject.activate(idx)
                listbox_subject.see(idx)
            elif listbox_subject.size() > 0:
                listbox_subject.selection_set(0)
                listbox_subject.activate(0)

        def current_subject():
            sel = listbox_subject.curselection()
            if not sel:
                return None
            return listbox_subject.get(sel[0])

        # 当前正在编辑的科目（切换科目前把文本写回 work_template）
        editing_subject = [None]

        def text_to_lines(widget):
            """文本框内容按行拆成列表，去掉末尾空行."""
            raw = widget.get('1.0', 'end-1c')
            lines = raw.split('\n')
            # 去掉尾部连续空行，中间空行保留为可编辑空位时也丢弃空串
            while lines and lines[-1] == '':
                lines.pop()
            return [ln for ln in lines if ln != '']

        def lines_to_text(widget, lines):
            widget.delete('1.0', tk.END)
            if lines:
                widget.insert('1.0', '\n'.join(lines))

        def flush_texts_to_template(subject):
            """把三个文本框当前内容写回 work_template[subject]."""
            if not subject or subject not in work_template:
                return
            work_template[subject]['template'] = text_to_lines(text_homework)
            work_template[subject]['measureword'] = text_to_lines(text_measure_word)
            work_template[subject]['otherword'] = text_to_lines(text_other_word)

        def fill_word_texts(subject):
            """从 work_template 填充三个文本框."""
            if not subject or subject not in work_template:
                lines_to_text(text_homework, [])
                lines_to_text(text_measure_word, [])
                lines_to_text(text_other_word, [])
                return
            data = work_template[subject]
            lines_to_text(text_homework, list(data.get('template', []) or []))
            lines_to_text(text_measure_word, list(data.get('measureword', []) or []))
            lines_to_text(text_other_word, list(data.get('otherword', []) or []))

        def on_subject_select(event=None):
            new_subj = current_subject()
            # 切换前保存上一科目的编辑
            if editing_subject[0] and editing_subject[0] in work_template:
                flush_texts_to_template(editing_subject[0])
            editing_subject[0] = new_subj
            fill_word_texts(new_subj)

        listbox_subject.bind('<<ListboxSelect>>', on_subject_select)

        # ---------- 科目增删改 ----------
        def add_subject():
            result = EntryBox(
                window_settings,
                title='新增科目',
                text_blod='输入新科目名称',
                text='不可与默认九科或已有科目重名.',
                entrys=[['科目名:', '']],
            )
            if not result:
                return
            name = (result[0] or '').strip()
            if not name:
                win32api.MessageBeep()
                return
            if name in DEFAULT_SUBJECTS:
                MessageBoxModern(
                    parent=window_settings, title='错误', icon='error',
                    text_blod='名称冲突', text='不允许与程序内的默认科目重名.',
                )
                return
            if name in work_template:
                MessageBoxModern(
                    parent=window_settings, title='错误', icon='error',
                    text_blod='名称冲突', text=f'科目「{name}」已存在.',
                )
                return
            work_template[name] = {'template': [], 'measureword': [], 'otherword': []}
            # 切换前保存当前科目编辑
            if editing_subject[0] and editing_subject[0] in work_template:
                flush_texts_to_template(editing_subject[0])
            refresh_subject_list(select_name=name)
            editing_subject[0] = name
            fill_word_texts(name)

        def rename_subject():
            subj = current_subject()
            if not subj:
                win32api.MessageBeep()
                return
            if subj in DEFAULT_SUBJECTS:
                MessageBoxModern(
                    parent=window_settings, title='错误', icon='error',
                    text_blod='不可重命名', text='不允许重命名程序内的默认科目.',
                )
                return
            result = EntryBox(
                window_settings,
                title='重命名科目',
                text_blod=f'将「{subj}」重命名为',
                text='保存后会同步程序数据与配置文件,但不改变历史记录.',
                entrys=[['新名称:', subj]],
            )
            if not result:
                return
            new_name = (result[0] or '').strip()
            if not new_name or new_name == subj:
                return
            if new_name in DEFAULT_SUBJECTS:
                MessageBoxModern(
                    parent=window_settings, title='错误', icon='error',
                    text_blod='名称冲突', text='不允许与程序内的默认科目重名.',
                )
                return
            if new_name in work_template:
                MessageBoxModern(
                    parent=window_settings, title='错误', icon='error',
                    text_blod='名称冲突', text=f'科目「{new_name}」已存在.',
                )
                return
            # 先把文本框内容写回旧名再重命名
            if editing_subject[0] == subj:
                flush_texts_to_template(subj)
            work_template[new_name] = work_template.pop(subj)
            # 合并链式重命名
            # 若此前已有 A->subj, 则改为 A->new_name
            for old, mid in list(rename_map.items()):
                if mid == subj:
                    rename_map[old] = new_name
            rename_map[subj] = new_name
            # 若 subj 是某次重命名的结果,去掉中间键
            if subj in rename_map and rename_map.get(subj) == new_name:
                pass
            # 清理：new_name 不应作为键出现在 rename_map 的源
            rename_map.pop(new_name, None)
            if editing_subject[0] == subj:
                editing_subject[0] = new_name
            refresh_subject_list(select_name=new_name)
            fill_word_texts(new_name)

        def remove_subject():
            subj = current_subject()
            if not subj:
                win32api.MessageBeep()
                return
            if subj in DEFAULT_SUBJECTS:
                MessageBoxModern(
                    parent=window_settings, title='错误', icon='error',
                    text_blod='不可删除', text='不允许删除程序内的默认科目.',
                )
                return
            confirm = MessageBoxModern(
                parent=window_settings,
                title='确认',
                icon='question',
                text_blod=f'删除科目「{subj}」?',
                text='将删除该科目的模板候选词配置.保存后会同步到程序与配置文件(历史记录中的该科作业保留).',
                button_mode=2,
                text_true='删除',
                text_false='取消',
            )
            if confirm is not True:
                return
            work_template.pop(subj, None)
            removed_subjects.add(subj)
            # 若该名是重命名目标,清理映射
            for old, mid in list(rename_map.items()):
                if mid == subj:
                    rename_map.pop(old, None)
            rename_map.pop(subj, None)
            refresh_subject_list()
            on_subject_select()

        button_add_subject.config(command=add_subject)
        button_rename_subject.config(command=rename_subject)
        button_remove_subject.config(command=remove_subject)

        def save_and_close():
            # 0) 先把当前科目文本框写回模板
            if editing_subject[0] and editing_subject[0] in work_template:
                flush_texts_to_template(editing_subject[0])

            # 1) 全局开关
            self.disable_highdpi_scaling = bool(var_checkbutton_disable_highdpi_scaling.get())
            self.auto_set_desktop_background = bool(var_checkbutton_auto_set_desktop_background.get())
            self.settings['disable_highdpi_scaling'] = self.disable_highdpi_scaling
            self.settings['auto_set_desktop_background'] = self.auto_set_desktop_background
            try:
                exp = int(float(spinbox_expected_attendance.get()))
            except (TypeError, ValueError):
                exp = int(getattr(self, 'expected_attendance', 50) or 50)
            if exp < 0:
                exp = 0
            self.expected_attendance = exp
            self.settings['expected_attendance'] = exp
            # 同步主界面实到 Spinbox 上限为新的应到人数（最小仍为 0）
            if hasattr(self, 'spinbox_attendance') and self.spinbox_attendance.winfo_exists():
                self.spinbox_attendance.from_ = 0
                self.spinbox_attendance.to = max(0, int(exp))
                try:
                    cur = int(float(self.spinbox_attendance.get() or 0))
                except Exception:
                    cur = 0
                if cur > exp:
                    was_on = False
                    try:
                        was_on = bool(self.var_attendance_enabled.get())
                    except Exception:
                        was_on = bool(getattr(self, 'attendance_enabled', False))
                   
                    self.spinbox_attendance.delete(0, tk.END)
                    self.spinbox_attendance.insert(0, str(int(exp)))
                    self._set_attendance_spinbox_state(was_on)
            for subj in list(removed_subjects):
                if subj in self.homework_data:
                    try:
                        del self.homework_data[subj]
                    except Exception:
                        self.homework_data.pop(subj, None)
                if self.treeview_homework.exists(subj):
                    self.treeview_homework.delete(subj)
                if 'password' in self.settings and subj in self.settings['password']:
                    if subj not in DEFAULT_SUBJECTS:
                        del self.settings['password'][subj]
            for old_name, new_name in list(rename_map.items()):
                if old_name == new_name:
                    continue
                # homework_data
                if old_name in self.homework_data:
                    self.homework_data[new_name] = self.homework_data.pop(old_name)
                elif new_name not in self.homework_data:
                    self.homework_data[new_name] = []
                # treeview 节点
                if self.treeview_homework.exists(old_name):
                    try:
                        # ttk.Treeview 无直接改 iid,删除旧节点再插新节点并迁子项
                        open_state = self.treeview_homework.item(old_name, 'open')
                        children_data = []
                        for child in self.treeview_homework.get_children(old_name):
                            children_data.append(self.treeview_homework.item(child, 'values'))
                        self.treeview_homework.delete(old_name)
                        if not self.treeview_homework.exists(new_name):
                            self.treeview_homework.insert('', 'end', iid=new_name, text=new_name, values=('',))
                        self.treeview_homework.item(new_name, open=open_state)
                        self._update_subject_ui(new_name)
                    except Exception:
                        if not self.treeview_homework.exists(new_name):
                            self.treeview_homework.insert('', 'end', iid=new_name, text=new_name, values=('',))
                        self._update_subject_ui(new_name)
                else:
                    if not self.treeview_homework.exists(new_name):
                        self.treeview_homework.insert('', 'end', iid=new_name, text=new_name, values=('',))
                    if new_name not in self.homework_data:
                        self.homework_data[new_name] = []
                    self._update_subject_ui(new_name)
                # settings.password 键同步
                pwd = self.settings.get('password', {})
                if old_name in pwd:
                    pwd[new_name] = pwd.pop(old_name)
            for name in work_template.keys():
                if name not in self.homework_data:
                    self.homework_data[name] = []
                if not self.treeview_homework.exists(name):
                    self.treeview_homework.insert('', 'end', iid=name, text=name, values=('',))
                    self._update_subject_ui(name)

            # 5) 写回模板与 settings
            self.homework_template = work_template
            try:
                with open('homeworktool_template.json', 'w', encoding='utf-8') as f:
                    json.dump(self.homework_template, f, ensure_ascii=False, indent=2)
            except Exception:
                MessageBoxModern(
                    parent=window_settings, title='错误', icon='error',
                    text_blod='保存模板失败', text=traceback.format_exc(),
                )
                return
            try:
                with open('homeworktool_settings.json', 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, ensure_ascii=False, indent=2)
            except Exception:
                MessageBoxModern(
                    parent=window_settings, title='错误', icon='error',
                    text_blod='保存设置失败', text=traceback.format_exc(),
                )
                return

            self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))
            close_window_settings()

        button_ok.config(command=save_and_close)

        # 初始填充
        refresh_subject_list()
        on_subject_select()

        ConvertPlaceToRelative(window_settings)
        window_settings.iconbitmap(f"{libresource}icon.ico")
        window_settings.wait_window()

    def open_advanced_settings_window(self, parent=None):
        """高级设置：三列表格（说明 / 变量名 / 值），双击值列编辑.
        数字用 DSpinbox;字符串/JSON 用 DEntry.
        滚动表格/滚动条时结束编辑（与 MCLangTool 一致）;DSpinbox 点 +/- 不结束编辑.
        """
        parent = parent or self.root

        # 使用 DSpinbox 的数值型键
        SPINBOX_KEYS = {
            'EXPORT_FONT_SUBJECT', 'EXPORT_FONT_CONTENT', 'EXPORT_FONT_DATE',
            'EXPORT_FONT_ATTENDANCE',
            'EXPORT_FONT_SUBJECT_MIN', 'EXPORT_FONT_CONTENT_MIN',
            'EXPORT_LINE_SPACING_CONTENT', 'EXPORT_LINE_SPACING_SUBJECT', 'EXPORT_SUBJECT_GAP',
            'EXPORT_MARGIN_X', 'EXPORT_MARGIN_BOTTOM', 'EXPORT_DATE_Y',
            'EXPORT_START_Y', 'EXPORT_GAP_CENTER',
        }

        def close_advanced_settings(event=None):
            window_advanced_settings.destroy()
            parent.focus()

        window_advanced_settings = tk.Toplevel(parent)
        window_advanced_settings.title('高级设置')
        SetDarkTitleBar(window_advanced_settings)
        window_width, window_height = 900, 560
        screen_width = window_advanced_settings.winfo_screenwidth()
        screen_height = window_advanced_settings.winfo_screenheight()
        window_advanced_settings.geometry('%dx%d+%d+%d'%(window_width, window_height, (screen_width - window_width) // 2,(screen_height - window_height) // 2,))
        window_advanced_settings['bg'] = WINDOWBG
        window_advanced_settings.protocol('WM_DELETE_WINDOW', close_advanced_settings)
        window_advanced_settings.bind('<Escape>', close_advanced_settings)
        window_advanced_settings.focus()

        tk.Label(window_advanced_settings, bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor='w',text='双击"值"列编辑,重新打开软件后生效.',).place(x=20, y=10, width=860, height=30)

        style = ttk.Style()
        style.theme_use('alt')
        style.configure(
            'Adv.Treeview', rowheight=28,
            fieldbackground=WINDOWBG, background=WINDOWBG, foreground=TEXTFG,
            borderwidth=0, highlightthickness=0,
        )
        style.configure(
            'Adv.Treeview.Heading',
            background=WINDOWBG, foreground=TEXTFG, borderwidth=0, highlightthickness=0,
        )
        style.map(
            'Adv.Treeview.Heading',
            background=[('active', WIDGETBG), ('pressed', WINDOWBG)],
            foreground=[('active', TEXTFG), ('pressed', TEXTFG)],
        )
        style.map(
            'Adv.Treeview',
            background=[('selected', AlphaBlend(WINDOWBG, HIGHLIGHT, 0.5))],
            foreground=[('selected', TEXTFG)],
        )

        scrollbar_advanced = DScrollbar(window_advanced_settings, bg=WINDOWBG)
        scrollbar_advanced.place(x=860, y=50, width=20, height=450)
        treeview_advanced = ttk.Treeview(
            window_advanced_settings, show='headings', columns=('desc', 'name', 'value'),
            selectmode='browse', yscrollcommand=scrollbar_advanced.set, style='Adv.Treeview',
        )
        treeview_advanced.place(x=20, y=50, width=840, height=450)
        scrollbar_advanced.config(command=treeview_advanced.yview)
        SetBorder(treeview_advanced)

        treeview_advanced.heading('desc', text='说明', anchor='center')
        treeview_advanced.heading('name', text='变量名', anchor='center')
        treeview_advanced.heading('value', text='值', anchor='center')
        treeview_advanced.column('desc', width=300, anchor='w')
        treeview_advanced.column('name', width=240, anchor='w')
        treeview_advanced.column('value', width=290, anchor='w')

        work_settings = {}
        for _desc, key in ADVANCED_SETTING_ROWS:
            if key == 'YAHEI_TEXT_FONT':
                work_settings[key] = copy.deepcopy(self.settings.get(key, YAHEI_TEXT_FONT))
            else:
                work_settings[key] = copy.deepcopy(self._cfg(key, DEFAULT_EXPORT_SETTINGS.get(key)))

        def value_to_display(value):
            if isinstance(value, (list, dict, tuple)):
                try:
                    return json.dumps(value, ensure_ascii=False)
                except Exception:
                    return str(value)
            return str(value)

        def refresh_rows():
            for item_id in treeview_advanced.get_children():
                treeview_advanced.delete(item_id)
            for desc, key in ADVANCED_SETTING_ROWS:
                treeview_advanced.insert(
                    '', 'end', iid=key,
                    values=(desc, key, value_to_display(work_settings.get(key, ''))),
                )
            window_advanced_settings.after_idle(lambda: SetExpandedTreeviewRowColor(treeview_advanced))
        refresh_rows()

        def parse_value(key, text_value):
            text_value = (text_value or '').strip()
            default = DEFAULT_EXPORT_SETTINGS.get(key)

            if key == 'YAHEI_TEXT_FONT':
                if text_value.startswith('['):
                    return json.loads(text_value)
                return text_value
            if key in ('EXPORT_FONT_FALLBACK_NAMES', 'highlight_box'):
                return json.loads(text_value)
            if key == 'EXPORT_FONT_NAME':
                return text_value
            if key in SPINBOX_KEYS:
                return int(float(text_value)) if text_value not in ('', '-',) else int(default or 0)
            try:
                if '.' in text_value:
                    return float(text_value)
                return int(text_value)
            except Exception:
                return text_value

        # 当前编辑器引用（DEntry 或 DSpinbox）
        editor_ref = [None]

        def is_widget_or_descendant(widget, root_widget):
            """判断 widget 是否为 root_widget 或其子孙."""
            current = widget
            while current is not None:
                if current is root_widget:
                    return True
                current = getattr(current, 'master', None)
                if current is None:
                    break
            return False

        def destroy_editor():
            editor = editor_ref[0]
            editor_ref[0] = None
            if editor is None:
                return
            editor.destroy()

        def on_double_click(event):
            # 已有编辑器时先不重复创建
            if editor_ref[0] is not None:
                return 'break'

            row_id = treeview_advanced.focus()
            if not row_id:
                if hasattr(event, 'y'):
                    row_id = treeview_advanced.identify_row(event.y)
                if not row_id:
                    return
            if hasattr(event, 'x') and event.x > 0:
                column = treeview_advanced.identify_column(event.x)
            else:
                column = '#3'
            if column != '#3':
                return 'break'
            bbox = treeview_advanced.bbox(row_id, column)
            if not bbox:
                return 'break'
            x, y, width, height = bbox
            values = treeview_advanced.item(row_id, 'values')
            current_value = values[2] if len(values) > 2 else ''
            key = row_id

            use_spin = key in SPINBOX_KEYS
            use_combo = (key == 'color_mode')

            if use_spin:
                min_value, max_value = -10 ** 9, 10 ** 9
                if 'MIN' in key:
                    min_value, max_value = 1, 500
                elif 'FONT' in key and 'NAME' not in key:
                    min_value, max_value = 1, 500
                elif 'SPACING' in key or 'GAP' in key:
                    min_value, max_value = 0, 2000
                elif 'MARGIN' in key or '_Y' in key or '_X' in key:
                    min_value, max_value = 0, 5000
                editor = DSpinbox(treeview_advanced, int_only=True, from_=min_value, to=max_value, increment=1)
                editor.delete(0, tk.END)
                try:
                    editor.insert(
                        0,
                        str(int(float(current_value))) if current_value not in ('',) else '0',
                    )
                except (TypeError, ValueError):
                    editor.insert(0, current_value or '0')
                get_text = lambda: editor.get()
                focus_target = editor
            elif use_combo:
                # color_mode 仅允许 system / dark / light
                editor = DCombobutton(
                    treeview_advanced, values=['system', 'dark', 'light'], state='readonly',
                )
                try:
                    editor['state'] = 'normal'
                    editor.delete(0, tk.END)
                    current_mode = (current_value or 'system').strip().lower()
                    if current_mode not in ('system', 'dark', 'light'):
                        current_mode = 'system'
                    editor.insert(0, current_mode)
                    editor['state'] = 'readonly'
                except Exception:
                    editor.insert(0, 'system')
                get_text = lambda: editor.get()
                focus_target = editor
            else:
                editor = DEntry(treeview_advanced)
                editor.insert('end', current_value)
                editor.icursor('end')
                get_text = lambda: editor.get()
                focus_target = editor

            editor.original_value = current_value
            editor.row_id = row_id
            editor_ref[0] = editor

            def apply_edit(event=None):
                editor_widget = editor_ref[0]
                if editor_widget is None:
                    return
                # 若焦点仍在编辑器内部（含 DSpinbox 的 +/- 按钮），不结束编辑
                focus_widget = window_advanced_settings.focus_get()
                if focus_widget is not None and is_widget_or_descendant(focus_widget, editor_widget):
                    return
                _commit_editor()

            def apply_edit_force(event=None):
                """滚动表格/滚动条时强制提交（即使焦点仍在编辑器上）."""
                _commit_editor()

            def _commit_editor():
                editor_widget = editor_ref[0]
                if editor_widget is None:
                    return
                editor_ref[0] = None
                _unbind_scroll()
                new_value = get_text()
                key_local = getattr(editor_widget, 'row_id', None)
                editor_widget.destroy()
                if not key_local:
                    treeview_advanced.focus_set()
                    return
                try:
                    parsed = parse_value(key_local, new_value)
                except Exception as error:
                    MessageBoxModern(
                        parent=window_advanced_settings, title='错误', icon='error',
                        text_blod='值格式错误', text=str(error),
                    )
                    treeview_advanced.focus_set()
                    return
                if key_local == 'highlight_box':
                    if not (isinstance(parsed, (list, tuple)) and len(parsed) >= 4):
                        MessageBoxModern(
                            parent=window_advanced_settings, title='错误', icon='error',
                            text_blod='高亮矩形格式错误',
                            text='需要长度为4的数组: [x, y, 宽, 高]',
                        )
                        treeview_advanced.focus_set()
                        return
                    parsed = [int(parsed[0]), int(parsed[1]), int(parsed[2]), int(parsed[3])]
                work_settings[key_local] = parsed
                treeview_advanced.item(
                    key_local,
                    values=(
                        treeview_advanced.item(key_local, 'values')[0],
                        key_local,
                        value_to_display(parsed),
                    ),
                )
                treeview_advanced.focus_set()

            def cancel_edit(event=None):
                _unbind_scroll()
                destroy_editor()
                treeview_advanced.focus_set()

            editor.place(x=x, y=y, width=width, height=height)
            # 回车确认、Esc 取消
            if use_spin:
                editor.Entry.bind('<Return>', lambda event: apply_edit_force())
                editor.Entry.bind('<Escape>', cancel_edit)
                # FocusOut：若焦点去了 +/- 则不提交
                editor.Entry.bind('<FocusOut>', apply_edit)
                editor.bind('<FocusOut>', apply_edit)
                editor.DButton_up.bind('<FocusOut>', apply_edit)
                editor.DButton_down.bind('<FocusOut>', apply_edit)
            elif use_combo:
                editor.Entry.bind('<Return>', lambda event: apply_edit_force())
                editor.Entry.bind('<Escape>', cancel_edit)
                editor.Entry.bind('<FocusOut>', apply_edit)
                editor.bind('<FocusOut>', apply_edit)
                editor.DButton_show_list.bind('<FocusOut>', apply_edit)
            else:
                editor.bind('<Return>', lambda event: apply_edit_force())
                editor.bind('<Escape>', cancel_edit)
                editor.bind('<FocusOut>', apply_edit)

            # 与 MCLangTool 一致：滚动表格/拖动滚动条时结束编辑
            scroll_bind_ids = [
                (treeview_advanced, '<MouseWheel>', treeview_advanced.bind('<MouseWheel>', apply_edit_force, add='+')),
                (scrollbar_advanced, '<MouseWheel>', scrollbar_advanced.bind('<MouseWheel>', apply_edit_force, add='+')),
                (scrollbar_advanced, '<B1-Motion>', scrollbar_advanced.bind('<B1-Motion>', apply_edit_force, add='+')),
            ]
            editor._scroll_bind_ids = scroll_bind_ids

            def _unbind_scroll():
                for widget, sequence, bind_id in getattr(editor, '_scroll_bind_ids', []) or []:
                    widget.unbind(sequence, bind_id)
                editor._scroll_bind_ids = []

            focus_target.focus_set()
            if use_spin or use_combo:
                editor.Entry.select_range(0, tk.END)
            else:
                editor.select_range(0, tk.END)
            return 'break'

        treeview_advanced.bind('<Double-Button-1>', on_double_click)
        treeview_advanced.bind('<Return>', on_double_click)
        treeview_advanced.bind('<F2>', on_double_click)

        def save_advanced_settings():
            global YAHEI_TEXT_FONT
            # 若仍在编辑，先提交
            if editor_ref[0] is not None:
                editor_widget = editor_ref[0]
                if isinstance(editor_widget, DSpinbox) or isinstance(editor_widget, DCombobutton):
                    text_value = editor_widget.Entry.get()
                else:
                    text_value = editor_widget.get()
                key = editor_widget.row_id
                parsed = parse_value(key, text_value)
                if key == 'highlight_box' and isinstance(parsed, (list, tuple)) and len(parsed) >= 4:
                    parsed = [int(parsed[0]), int(parsed[1]), int(parsed[2]), int(parsed[3])]
                work_settings[key] = parsed
                destroy_editor()

            for key, value in work_settings.items():
                self.settings[key] = value
                if key != 'YAHEI_TEXT_FONT':
                    if not hasattr(self, 'export_cfg'):
                        self.export_cfg = dict(DEFAULT_EXPORT_SETTINGS)
                    self.export_cfg[key] = value
            if 'YAHEI_TEXT_FONT' in work_settings:
                YAHEI_TEXT_FONT = work_settings['YAHEI_TEXT_FONT']
                self.settings['YAHEI_TEXT_FONT'] = YAHEI_TEXT_FONT
            if 'color_mode' in work_settings:
                color_mode_value = str(work_settings['color_mode'] or 'system').strip().lower()
                if color_mode_value not in ('system', 'dark', 'light'):
                    color_mode_value = 'system'
                self.color_mode = color_mode_value
                self.settings['color_mode'] = color_mode_value
                if hasattr(self, 'export_cfg'):
                    self.export_cfg['color_mode'] = color_mode_value
            try:
                with open('homeworktool_settings.json', 'w', encoding='utf-8') as file:
                    json.dump(self.settings, file, ensure_ascii=False, indent=2)
            except Exception:
                MessageBoxModern(
                    parent=window_advanced_settings, title='错误', icon='error',
                    text_blod='保存高级设置失败', text=traceback.format_exc(),
                )
                return
            close_advanced_settings()

        button_ok_advanced = DButton(
            window_advanced_settings, text='确定', default='active', command=save_advanced_settings,
        )
        button_ok_advanced.place(x=700, y=515, width=80, height=30)
        button_ok_advanced.unbind_default_active()

        button_cancel_advanced = DButton(
            window_advanced_settings, text='取消', command=close_advanced_settings,
        )
        button_cancel_advanced.place(x=800, y=515, width=80, height=30)
        button_cancel_advanced.unbind_default_active()

        ConvertPlaceToRelative(window_advanced_settings)
        window_advanced_settings.iconbitmap(f'{libresource}icon.ico')
        window_advanced_settings.wait_window()

    def open_background_image_settings_window(self, parent=None):
        """导出图片背景：纯色 / 图片 + 拉伸模式，写入 settings 并同步 export_cfg."""
        parent = parent or self.root

        def close_background_settings(event=None):
            window_background_settings.destroy()
            parent.focus()

        window_background_settings = tk.Toplevel(parent)
        window_background_settings.title('背景图像设置')
        SetDarkTitleBar(window_background_settings)
        window_width, window_height = 720, 320
        screen_width = window_background_settings.winfo_screenwidth()
        screen_height = window_background_settings.winfo_screenheight()
        window_background_settings.geometry(
            '%dx%d+%d+%d' % (
                window_width, window_height,
                (screen_width - window_width) // 2,
                (screen_height - window_height) // 2,
            )
        )
        window_background_settings['bg'] = WINDOWBG
        window_background_settings.protocol('WM_DELETE_WINDOW', close_background_settings)
        window_background_settings.bind('<Escape>', close_background_settings)
        window_background_settings.focus()

        # 当前值
        current_mode = str(self._cfg('background_mode', '纯色') or '纯色')
        if current_mode not in ('纯色', '图片'):
            current_mode = '纯色'
        current_color = str(self._cfg('background_color', '#FAF9E6') or '#FAF9E6')
        current_path = str(self._cfg('background_image_path', '') or '')
        current_stretch = str(self._cfg('background_stretch_mode', '完全拉伸') or '完全拉伸')
        if current_stretch not in ('完全拉伸', '横向拉伸', '纵向拉伸', '不拉伸'):
            current_stretch = '完全拉伸'

        tk.Label(
            window_background_settings, text='背景图底色:', anchor='w', bg=WINDOWBG, fg=TEXTFG,
        ).place(x=20, y=20, width=120, height=30)
        entry_background_color = DEntry(window_background_settings)
        entry_background_color.insert(0, current_color)
        entry_background_color.place(x=150, y=20, width=150, height=30)

        preview_swatch = tk.Label(
            window_background_settings,
            bg=current_color if current_color.startswith('#') else '#FAF9E6',
            bd=1, relief='solid',
        )
        preview_swatch.place(x=310, y=20, width=40, height=30)

        def update_swatch(event=None):
            color_text = entry_background_color.get().strip()
            rgb = self._parse_bg_color(color_text)
            preview_swatch.config(bg='#{:02x}{:02x}{:02x}'.format(*rgb))
        entry_background_color.bind('<KeyRelease>', update_swatch, add='+')
        entry_background_color.bind('<FocusOut>', update_swatch, add='+')

        def pick_color():
            rgb_tuple, hex_color = colorchooser.askcolor(
                color=preview_swatch.cget('bg'),
                parent=window_background_settings,
                title='选择背景底色',
            )
            if hex_color:
                entry_background_color.delete(0, 'end')
                entry_background_color.insert(0, hex_color.upper())
                update_swatch()

        button_pick_color = DButton(window_background_settings, text='取色', command=pick_color)
        button_pick_color.place(x=360, y=20, width=60, height=30)

        tk.Label(
            window_background_settings, text='背景图模式:', anchor='w', bg=WINDOWBG, fg=TEXTFG,
        ).place(x=20, y=70, width=120, height=30)
        var_background_mode = tk.StringVar(value=current_mode)
        entry_background_mode = DCombobutton(
            window_background_settings, values=['纯色', '图片'],
            textvariable=var_background_mode, state='readonly',
        )
        entry_background_mode.place(x=150, y=70, width=150, height=30)

        tk.Label(
            window_background_settings, text='背景图文件:', anchor='w', bg=WINDOWBG, fg=TEXTFG,
        ).place(x=20, y=120, width=120, height=30)
        entry_background_file = DEntry(window_background_settings)
        entry_background_file.insert(0, current_path)
        entry_background_file.place(x=150, y=120, width=400, height=30)

        def browse_file():
            path = filedialog.askopenfilename(
                parent=window_background_settings,
                title='选择背景图片',
                filetypes=[
                    ('图片文件', '*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.webp'),
                    ('所有文件', '*.*'),
                ],
            )
            if path:
                entry_background_file.delete(0, 'end')
                entry_background_file.insert(0, path)

        button_open_browse_file_dialog = DButton(
            window_background_settings, text='浏览', command=browse_file,
        )
        button_open_browse_file_dialog.place(x=560, y=120, width=60, height=30)

        tk.Label(
            window_background_settings, text='拉伸模式:', anchor='w', bg=WINDOWBG, fg=TEXTFG,
        ).place(x=20, y=170, width=120, height=30)
        var_background_stretch_mode = tk.StringVar(value=current_stretch)
        entry_background_stretch_mode = DCombobutton(
            window_background_settings,
            values=['完全拉伸', '横向拉伸', '纵向拉伸', '不拉伸'],
            textvariable=var_background_stretch_mode,
            state='readonly',
        )
        entry_background_stretch_mode.place(x=150, y=170, width=150, height=30)

        tk.Label(
            window_background_settings, bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor='w',
            text='说明:底色在「纯色」模式下作为整图背景;「图片」模式下作为未铺满区域的填充色.',
        ).place(x=20, y=220, width=680, height=30)

        def refresh_widget_state(event=None, *args):
            if var_background_mode.get() == '图片':
                entry_background_file.config(state='normal')
                entry_background_stretch_mode['state'] = 'readonly'
                button_open_browse_file_dialog.config(state='normal')
            else:
                entry_background_file.config(state='disabled')
                entry_background_stretch_mode['state'] = 'disabled'
                button_open_browse_file_dialog.config(state='disabled')
        var_background_mode.trace_add('write', refresh_widget_state)
        refresh_widget_state()
        update_swatch()

        def save_and_close():
            mode = (var_background_mode.get() or '纯色').strip()
            if mode not in ('纯色', '图片'):
                mode = '纯色'
            color = (entry_background_color.get() or '#FAF9E6').strip()
            # 规范化为 #RRGGBB
            rgb = self._parse_bg_color(color)
            color = '#{:02X}{:02X}{:02X}'.format(*rgb)
            path = (entry_background_file.get() or '').strip()
            stretch = (var_background_stretch_mode.get() or '完全拉伸').strip()
            if stretch not in ('完全拉伸', '横向拉伸', '纵向拉伸', '不拉伸'):
                stretch = '完全拉伸'
            if mode == '图片' and path and not os.path.isfile(path):
                MessageBoxModern(
                    parent=window_background_settings, title='错误', icon='error',
                    text_blod='背景图文件不存在',
                    text=path,
                )
                return
            self.settings['background_mode'] = mode
            self.settings['background_color'] = color
            self.settings['background_image_path'] = path
            self.settings['background_stretch_mode'] = stretch
            if not hasattr(self, 'export_cfg') or not isinstance(self.export_cfg, dict):
                self.export_cfg = dict(DEFAULT_EXPORT_SETTINGS)
            self.export_cfg['background_mode'] = mode
            self.export_cfg['background_color'] = color
            self.export_cfg['background_image_path'] = path
            self.export_cfg['background_stretch_mode'] = stretch
            try:
                with open('homeworktool_settings.json', 'w', encoding='utf-8') as file:
                    json.dump(self.settings, file, ensure_ascii=False, indent=2)
            except Exception:
                MessageBoxModern(
                    parent=window_background_settings, title='错误', icon='error',
                    text_blod='保存背景设置失败',
                    text=traceback.format_exc(),
                )
                return
            close_background_settings()

        button_ok = DButton(
            window_background_settings, text='确定', default='active', command=save_and_close,
        )
        button_ok.place(x=520, y=270, width=80, height=30)
        button_ok.unbind_default_active()
        button_cancel = DButton(
            window_background_settings, text='取消', command=close_background_settings,
        )
        button_cancel.place(x=620, y=270, width=80, height=30)
        button_cancel.unbind_default_active()
        ConvertPlaceToRelative(window_background_settings)
        window_background_settings.iconbitmap(f'{libresource}icon.ico')
        window_background_settings.wait_window()

    def about(self,event=None):
        def set_label_font(label, add_size=3,bold=False):
            old_font = tkfont.Font(font=label.cget("font"))
            new_font = old_font.copy()
            new_font.configure(weight="bold" if bold else "normal", size=old_font.cget("size") + add_size)
            label.configure(font=new_font)

        def close_about_window(event=None):
            self.root.attributes('-disabled', False)
            self.about_window.destroy()
            self.root.focus_set()
        self.root.attributes('-disabled', True)
        self.about_window = tk.Toplevel(self.root)
        self.about_window.title('关于')
        self.about_window.geometry(f'800x570+{(self.about_window.winfo_screenwidth() - 800) // 2}+{(self.about_window.winfo_screenheight() - 570) // 2}')
        self.about_window.resizable(False, False)
        self.about_window['bg'] = WINDOWBG
        self.about_window.protocol('WM_DELETE_WINDOW', close_about_window)
        self.about_window.bind('<Escape>', close_about_window)
        self.about_window.wm_transient(self.root)
        self.about_window.focus()


        label_title=tk.Label(self.about_window,bg=WINDOWBG,text='万岁™作业布置与展示工具',anchor='center',fg=TEXTFG)
        set_label_font(label_title,add_size=18,bold=True)
        label_title.place(x=00,y=20,width=800,height=70)

        tk.Label(self.about_window,bg=TEXTBG,fg=TEXTFG,).place(x=20,y=120,width=760,height=2)

        tk.Label(self.about_window,bg=WINDOWBG,fg=TEXTFG,text='软件概述:',anchor='w').place(x=20,y=140,width=90,height=30)
        label_introduction=tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text='一款专为教室大屏设计的作业布置与展示工具.',anchor='w')
        label_introduction.place(x=110,y=140,height=30)
        BindTipWindow(label_introduction,text='老桃基于「老桃制度 万岁思想 本真观念」所设计的软件.',width=450)


        tk.Label(self.about_window,bg=WINDOWBG,fg=TEXTFG,text='当前版本:',anchor='w').place(x=20,y=180,width=90,height=30)
        tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text=f'{VERSION}',anchor='w').place(x=110,y=180,height=30)

        tk.Label(self.about_window,bg=TEXTBG,fg=TEXTFG,).place(x=20,y=230,width=760,height=2)

        tk.Label(self.about_window,bg=WINDOWBG,fg=TEXTFG,text='著作权:',anchor='w').place(x=20,y=250,width=90,height=30)
        label_copyright=tk.Label(self.about_window,bg=WINDOWBG,fg=TEXTFG,text='Copyright © 2026 炸图监管者 · Licensed under the MIT License.',anchor='w')
        label_copyright.place(x=110,y=250,height=30)
        BindTipWindow(label_copyright,text=MITLICENSE,width=600)

        tk.Label(self.about_window,bg=TEXTBG,fg=TEXTFG,).place(x=20,y=300,width=760,height=2)

        tk.Label(self.about_window,bg=WINDOWBG,fg=TEXTFG,text='相关链接:',anchor='w').place(x=20,y=320,width=90,height=30)

        label_githubpage=tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text='个人主页:',anchor='w',)
        label_githubpage.place(x=60,y=360,width=90,height=30)

        button_githubpage=DAlphaButton(self.about_window,text='https://zhatujianguanzhe.github.io',command=lambda:webbrowser.open_new_tab("https://zhatujianguanzhe.github.io"),fg=HIGHLIGHT,anchor='w')
        button_githubpage.place(x=150,y=360,height=30)



        label_github=tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text='Github:',anchor='w',)
        label_github.place(x=60,y=400,width=90,height=30)

        button_github=DAlphaButton(self.about_window,text='https://github.com/zhatujianguanzhe',command=lambda:webbrowser.open_new_tab("https://github.com/zhatujianguanzhe"),fg=HIGHLIGHT,anchor='w')
        button_github.place(x=150,y=400,height=30)



        label_bilibili=tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text='Bilibili:',anchor='w',)
        label_bilibili.place(x=60,y=440,width=90,height=30)

        button_bilibili=DAlphaButton(self.about_window,text='https://space.bilibili.com/1342104465',command=lambda:webbrowser.open_new_tab("https://space.bilibili.com/1342104465"),fg=HIGHLIGHT,anchor='w')
        button_bilibili.place(x=150,y=440,height=30)

        label_qq=tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text='QQ群:',anchor='w',)
        label_qq.place(x=60,y=480,width=90,height=30)

        button_qq=tk.Label(self.about_window,text='865302820',bg=WINDOWBG,fg=SECONDARYTEXTFG,anchor='w')
        button_qq.place(x=150,y=480,height=30)

        button_close_about=DButton(self.about_window,text='关闭',default='active',command=close_about_window)
        button_close_about.place(x=700,y=520,width=80,height=30)

        SetDarkTitleBar(self.about_window)
        self.about_window.wm_iconbitmap(f"{libresource}icon.ico")
        self.about_window.wait_window()





# ========================= 命令行接口 =========================
CLI_HELP = """作业布置与展示工具 命令行用法

  python homeworktool.py [选项]

选项:
  --assign <科目> <作业内容>     在指定科目下新建一条作业；科目不存在则仅报错
  --notice <内容>                在「班务」科目下新建一条内容（无则自动创建科目）
  --delete <科目> <作业内容>     删除该科目中与内容完全匹配的作业（无匹配则报错）
  --deleteid <科目> <序号>       按 1-based 序号删除该科目作业（越界则报错）
  --attendance <人数>            设置今日实到人数并写入考勤历史
  --render                       生成作业图片（同「生成图片」，命令行跳过密码）
  --help, -h                     显示本帮助

说明:
  · 可一次传入多个选项，按从左到右顺序执行
  · 每个会改数据的操作结束后自动保存历史记录
  · 无任何选项时启动图形界面
"""


def _cli_today():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def _cli_load_json(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except Exception:
        return default


def _cli_save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _cli_load_today_homework(previous, template):
    date = _cli_today()
    today = {}
    if isinstance(previous, dict) and date in previous and isinstance(previous[date], dict):
        for k, v in previous[date].items():
            today[k] = list(v) if isinstance(v, list) else []
    default_subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']
    for s in default_subjects + list((template or {}).keys()):
        today.setdefault(s, [])
    return today


def _cli_save_homework(previous, today_homework):
    date = _cli_today()
    if not isinstance(previous, dict):
        previous = {}
    packed = {s: list(hw) for s, hw in today_homework.items() if hw}
    previous[date] = packed
    _cli_save_json('homeworktool_previous_homework.json', previous)
    return previous


def _cli_save_attendance(attendance_history, actual, settings=None):
    date = _cli_today()
    try:
        expected = int((settings or {}).get('expected_attendance', 50))
    except (TypeError, ValueError):
        expected = 50
    try:
        actual = int(actual)
    except (TypeError, ValueError):
        actual = 0
    if not isinstance(attendance_history, dict):
        attendance_history = {}
    attendance_history[date] = {'expected': int(expected), 'actual': int(actual)}
    _cli_save_json('homeworktool_attendance.json', attendance_history)
    return attendance_history


def _cli_ok(msg):
    print(f'[成功] {msg}')


def _cli_err(msg):
    print(f'[错误] {msg}')


def _cli_subject_exists(subject, today, template):
    default_subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']
    if subject in today:
        return True
    if subject in default_subjects:
        return True
    if isinstance(template, dict) and subject in template:
        return True
    return False


def _cli_do_render(today_homework, settings, template, attendance_history):
    m = object.__new__(Main)
    m._cli_mode = True
    m.settings = settings if isinstance(settings, dict) else {}
    m.homework_template = template if isinstance(template, dict) else {}
    m.previous_homework = {}
    m.attendance_history = attendance_history if isinstance(attendance_history, dict) else {}
    m.root = None
    try:
        m.load_runtime_settings()
    except Exception as e:
        _cli_err(f'加载设置失败: {e}')
        return 1
    m.homework_data = dict(today_homework)
    date = _cli_today()
    rec = m.attendance_history.get(date) if isinstance(m.attendance_history, dict) else None
    actual = 0
    if isinstance(rec, dict):
        try:
            actual = int(rec.get('actual', 0))
        except (TypeError, ValueError):
            actual = 0
    m._get_actual_attendance_from_ui = lambda: actual

    class _V:
        def get(self_inner):
            return bool(getattr(m, 'attendance_enabled', False))

    m.var_attendance_enabled = _V()
    try:
        m.export_homework_image()
        _cli_ok('已生成作业图片（--render）')
        return 0
    except Exception:
        _cli_err(f'生成图片失败:\n{traceback.format_exc()}')
        return 1


def run_cli(argv):
    if not argv or argv[0] in ('-h', '--help') or all(a in ('-h', '--help') for a in argv):
        print(CLI_HELP)
        return 0

    settings = _cli_load_json('homeworktool_settings.json', {})
    if not isinstance(settings, dict):
        settings = {}
    template = _cli_load_json('homeworktool_template.json', {})
    if not isinstance(template, dict):
        template = {}
    previous = _cli_load_json('homeworktool_previous_homework.json', {})
    if not isinstance(previous, dict):
        previous = {}
    attendance_history = _cli_load_json('homeworktool_attendance.json', {})
    if not isinstance(attendance_history, dict):
        attendance_history = {}

    today = _cli_load_today_homework(previous, template)
    exit_code = 0
    i = 0
    n = len(argv)

    while i < n:
        arg = argv[i]
        if arg in ('-h', '--help'):
            print(CLI_HELP)
            i += 1
            continue

        if arg == '--assign':
            if i + 2 >= n:
                _cli_err('--assign 需要参数: <科目> <作业内容>')
                return 2
            subject, content = argv[i + 1], argv[i + 2]
            i += 3
            if not _cli_subject_exists(subject, today, template):
                _cli_err(f'科目不存在，未添加: {subject}')
                exit_code = 1
                continue
            today.setdefault(subject, [])
            today[subject].append(content)
            previous = _cli_save_homework(previous, today)
            _cli_ok(f'已添加 [{subject}] {content}')
            continue

        if arg == '--notice':
            if i + 1 >= n:
                _cli_err('--notice 需要参数: <内容>')
                return 2
            content = argv[i + 1]
            i += 2
            today.setdefault('班务', [])
            today['班务'].append(content)
            previous = _cli_save_homework(previous, today)
            _cli_ok(f'已添加 [班务] {content}')
            continue

        if arg == '--delete':
            if i + 2 >= n:
                _cli_err('--delete 需要参数: <科目> <作业内容>')
                return 2
            subject, content = argv[i + 1], argv[i + 2]
            i += 3
            if subject not in today or content not in today[subject]:
                _cli_err(f'删除失败: 未找到匹配作业 [{subject}] {content}')
                exit_code = 1
                continue
            today[subject].remove(content)
            previous = _cli_save_homework(previous, today)
            _cli_ok(f'已删除 [{subject}] {content}')
            continue

        if arg == '--deleteid':
            if i + 2 >= n:
                _cli_err('--deleteid 需要参数: <科目> <作业序号>')
                return 2
            subject, idx_s = argv[i + 1], argv[i + 2]
            i += 3
            try:
                idx = int(idx_s)
            except (TypeError, ValueError):
                _cli_err(f'删除失败: 序号无效 ({idx_s})')
                exit_code = 1
                continue
            if subject not in today or not today[subject]:
                _cli_err(f'删除失败: 科目无作业或不存在 ({subject})')
                exit_code = 1
                continue
            if idx < 1 or idx > len(today[subject]):
                _cli_err(f'删除失败: 序号越界 ({idx}, 共 {len(today[subject])} 项)')
                exit_code = 1
                continue
            removed = today[subject].pop(idx - 1)
            previous = _cli_save_homework(previous, today)
            _cli_ok(f'已删除 [{subject}] #{idx} {removed}')
            continue

        if arg == '--attendance':
            if i + 1 >= n:
                _cli_err('--attendance 需要参数: <人数>')
                return 2
            num_s = argv[i + 1]
            i += 2
            try:
                num = int(float(num_s))
            except (TypeError, ValueError):
                _cli_err(f'人数无效: {num_s}')
                exit_code = 1
                continue
            attendance_history = _cli_save_attendance(attendance_history, actual=num, settings=settings)
            settings['attendance_enabled'] = True
            _cli_save_json('homeworktool_settings.json', settings)
            _cli_ok(f'已设置今日实到人数: {num}')
            continue

        if arg == '--render':
            i += 1
            rc = _cli_do_render(today, settings, template, attendance_history)
            if rc != 0:
                exit_code = rc
            continue

        _cli_err(f'未知参数: {arg}')
        print(CLI_HELP)
        return 2

    return exit_code


if __name__ == '__main__':
    if len(sys.argv) > 1:
        raise SystemExit(run_cli(sys.argv[1:]))
    Main()
