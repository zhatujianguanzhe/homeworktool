import  os, sys, win32api, webbrowser, json,  datetime,traceback, ctypes, copy
from laotaoui import *
import tkinter.font as tkfont
from PIL import Image, ImageDraw, ImageFont # 新增这一行
import re


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
    'highlight_box': [0, 0, 0, 0],
    'color_mode':'system'
}

# 高级设置表：说明, 变量名
ADVANCED_SETTING_ROWS = [
    ('科目标题字号', 'EXPORT_FONT_SUBJECT'),
    ('作业内容字号', 'EXPORT_FONT_CONTENT'),
    ('日期字号', 'EXPORT_FONT_DATE'),
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
    ('界面字体(名称或[名称,字号])', 'YAHEI_TEXT_FONT'),

]

# 作业末尾样式标记（保存时保留;导出时解析后去掉）
HOMEWORK_STYLE_MARKERS = frozenset('RGYBO')
HOMEWORK_STYLE_COLORS = {
    'R': (200, 30, 30),
    'G': (0, 110, 40),
    'Y': (180, 140, 0),
    'B': (30, 160, 220),
}




VERSION="1.0.2"
MITLICENSE="""MIT License

Copyright © 2026 炸图监管者

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""



YAHEI_TEXT_FONT = ['微软雅黑', 12]  # 启动时由 settings 覆盖

def parse_homework_style(content):
    """解析作业末尾的 R/G/Y/B/O 标记,返回 (显示文本, 颜色RGB或None, 是否加粗)."""
    if not content:
        return '', None, False
    i = len(content)
    found = []
    while i > 0 and content[i - 1] in HOMEWORK_STYLE_MARKERS:
        i -= 1
        found.append(content[i])
    # found 从右到左,颜色取最靠近正文的那一个之后仍以「最右优先」：从右往左第一个颜色字母
    color = None
    bold = False
    for ch in found:  # 已是从右到左
        if ch == 'O':
            bold = True
        elif ch in HOMEWORK_STYLE_COLORS and color is None:
            color = HOMEWORK_STYLE_COLORS[ch]
    return content[:i], color, bold


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
        
        # 读取配置文件


        try:
            with open('homeworktool_settings.json','r',encoding='utf-8') as f:
                self.settings = json.load(f)
        except:
            if MessageBoxModern(parent=None,title='警告',text=f"{traceback.format_exc()}",text_blod='读取设置文件失败,是否需要重新创建配置文件?',icon='warning',button_mode=2):
                with open('homeworktool_template.json','rw',encoding='utf-8') as f:
                    f.write('{"password":{"admin":"","default":""},"highlight_box":[0,0,0,0],"EXPORT_FONT_SUBJECT":120,"EXPORT_FONT_CONTENT":100,"EXPORT_FONT_DATE":110,"EXPORT_FONT_SUBJECT_MIN":40,"EXPORT_FONT_CONTENT_MIN":32,"EXPORT_FONT_NAME":"宋体","EXPORT_FONT_FALLBACK_NAMES":["宋体","微软雅黑","MicrosoftYaHei","黑体","SimHei","SegoeUISymbol","SegoeUI","ArialUnicodeMS","Arial"],"EXPORT_LINE_SPACING_CONTENT":10,"EXPORT_LINE_SPACING_SUBJECT":15,"EXPORT_SUBJECT_GAP":32,"EXPORT_MARGIN_X":300,"EXPORT_MARGIN_BOTTOM":150,"EXPORT_DATE_Y":120,"EXPORT_START_Y":280,"EXPORT_GAP_CENTER":60,"YAHEI_TEXT_FONT":"TkDefaultFont","disable_highdpi_scaling":true,"auto_set_desktop_background":true}')
                    self.settings = json.load(f)
            else:
                sys.exit()




        try:
            with open('homeworktool_template.json','r',encoding='utf-8') as f:
                self.homework_template = json.load(f)
        except:
            MessageBoxModern(parent=None,title='警告',text=f"{traceback.format_exc()}",text_blod='读取作业模板文件失败,不影响运行.',icon='warning',)      
            self.homework_template = {}
     

        try:
            with open('homeworktool_previous_homework.json','r',encoding='utf-8') as f:
                self.previous_homework = json.load(f)
        except:
            MessageBoxModern(parent=None,title='警告',text=f"{traceback.format_exc()}",text_blod='读取历史记录文件失败,不影响运行.',icon='warning',)
            self.previous_homework = {}




        self.load_runtime_settings()
        
        # 初始化作业数据存储字典,绑定自动刷新回调函数
        self.homework_data = ObservableHomeworkDict(self._update_subject_ui)

        LoadFont(f'{libresource}/WS_Segoe_MDL2_Assets-Regular.ttf')


        self.layout_window()

        self.apply_homework_template()
        self.autoload_homework_histroy()
        self.mainloop()


    def load_runtime_settings(self):
        """从 settings 合并导出/界面常量到 self.export_cfg，并同步全局 YAHEI_TEXT_FONT."""
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
            try:
                SetDPI()
            except Exception:
                pass

        self.auto_set_desktop_background = bool(self.settings.get('auto_set_desktop_background', True))

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

    def export_homework_image(self):

        """将当前作业导出为3840x2160的jpg图片（左右两列,自动换行,字号自适应缩小）"""
        if not self.verify_admin_password():
            return

        # 检查是否有作业
        has_homework = any(len(homework) > 0 for homework in self.homework_data.values())
        if not has_homework:
            MessageBoxModern(self.root, title='错误', icon='error', text_blod='没有作业', text='没有作业可以导出.')
            return

        try:
            img_width, img_height = 3840, 2160
            bg_color = (250, 249, 230)
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
                blocks.append(('subject', f"{subject}:", None, False))
                for index, content in enumerate(homework_list, start=1):
                    body, style_color, style_bold = parse_homework_style(content)
                    blocks.append(('content', f"  {index}.{body}", style_color, style_bold))
                blocks.append(('gap', '', None, False))  # 科目之间的额外间距

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
                except Exception:
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

                def place_line(text, font, extra_after=0, x_offset=0, style_color=None, style_bold=False):
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
                    target.append((base_x + x_offset, y, text, font, style_color, style_bold))
                    y = y + h + extra_after
                    return True

                for kind, text, style_color, style_bold in blocks:
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
                        if not place_line(line, font, after, x_off, style_color, style_bold):
                            return False, None, None
                return True, left_items, right_items

            # 临时 draw 用于测宽（不落在最终图上）
            probe_img = Image.new('RGB', (img_width, img_height), bg_color)
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
            img = Image.new('RGB', (img_width, img_height), bg_color)
            draw = ImageDraw.Draw(img)

            # settings 中的高亮区域：在所有文字之前绘制深绿色矩形 [x, y, 宽, 高]
            try:
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
            except Exception:
                pass

            # 日期居中（缺字回退）
            draw_text_mixed(draw, (center_x, date_y), date, text_color, font_date, anchor='mt')

            # 中间灰色虚线（从内容区顶部到底部）
            dash_len, gap_len = 24, 16
            y = start_y - 20
            while y < img_height - margin_bottom:
                y2 = min(y + dash_len, img_height - margin_bottom)
                draw.line([(center_x, y), (center_x, y2)], fill=divider_color, width=4)
                y = y2 + gap_len

            for x, y, text, font, style_color, style_bold in (final_left or []) + (final_right or []):
                fill = style_color if style_color else text_color
                draw_text_mixed(draw, (x, y), text, fill, font, bold=bool(style_bold))

            filename = f"{date}.jpg"
            filepath = os.path.abspath(filename)
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
                    MessageBoxModern(
                        parent=self.root, title='成功',
                        text=f'图片已保存至: {filepath}\n但设为桌面背景失败,详细信息:\n{wallpaper_err}',
                        text_blod='导出成功,设壁纸失败', icon='warning'
                    )

        except Exception:
            MessageBoxModern(parent=self.root, title='错误', text=traceback.format_exc(), text_blod='导出作业图片失败', icon='error')

    def layout_window(self,):
        self.root=tk.Tk()
        self.root.title('万岁™作业布置工具(合肥一中特供版)')
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


        

        style = ttk.Style()
        style.theme_use("alt")

        style.configure("Treeview", rowheight=40,
                        fieldbackground=WINDOWBG,
                        background=WINDOWBG,
                        foregroung=TEXTFG,
                        borderwidth=0,
                        highlightthickness=0,
                        font=YAHEI_TEXT_FONT ) # 填充背景色
   
        style.configure("Treeview.Heading",
                        background=WINDOWBG,      # 表头背景色
                        foreground=TEXTFG,        # 表头文字颜色
                        borderwidth=0,
                        highlightthickness=0,
                        font=YAHEI_TEXT_FONT)          # 扁平化边框
        # 3. 关键步骤：锁死动态样式（防止鼠标悬停或点击时变回系统默认的灰色）
        
        style.map("Treeview.Heading",
                background=[('active', WIDGETBG),  # 鼠标悬停时的深蓝色
                            ('pressed', WINDOWBG)], # 鼠标点击时的更深蓝色
                foreground=[('active', TEXTFG),
                            ('pressed', TEXTFG)],
                borderwidth=[('active', 0), ('pressed', 0)],    
                highlightthickness=[('active', 0), ('pressed', 0)],   )
        # 配置被选中时的颜色
        style.map("Treeview",
                background=[('selected', AlphaBlend(WINDOWBG,HIGHLIGHT,0.5))],
                foreground=[('selected',TEXTFG )],
                borderwidth=[('active', 0), ('pressed', 0)],    # 外边框宽度设为 0
                highlightthickness=[('active', 0), ('pressed', 0)],)    # 高亮边框宽度设为 0

        self.scrollbar_treeview_y=DScrollbar(self.root)
        self.scrollbar_treeview_y.place(x=870,y=20,width=30,height=760)
        self.treeview_homework= ttk.Treeview(self.root, show="tree headings", columns=["homework"],takefocus=True,
                                          selectmode='browse', yscrollcommand=self.scrollbar_treeview_y.set)
        self.treeview_homework.place(x=20,y=20,width=850,height=760)

        self.scrollbar_treeview_y.config(command=self.treeview_homework.yview)

        self.treeview_homework.heading("#0", text="科目", anchor='center')
        self.treeview_homework.heading("homework", text="作业内容", anchor='center')

        self.treeview_homework.column("#0", width=80, anchor='w')
        self.treeview_homework.column("homework", width=550, anchor='w')
        
        # 绑定展开和收起事件,同时刷新状态文字和行颜色
        def on_treeview_open(event):
            item = self.treeview_homework.focus()
            
            self.root.after_idle(lambda: self._update_subject_state(item))
            self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))

        def on_treeview_close(event):
            item = self.treeview_homework.focus()
            #self._update_subject_state(item)
            self.root.after_idle(lambda: self._update_subject_state(item))
            self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))

        self.treeview_homework.bind('<<TreeviewOpen>>', on_treeview_open)
        self.treeview_homework.bind('<<TreeviewClose>>', on_treeview_close)

        self.treeview_homework.bind('<Double-Button-1>', self.edit_homework)




        self.button_edit_homework=DButton(self.root,text='编辑科目',fg=GREENLIGHT,font=YAHEI_TEXT_FONT,command=self.edit_homework)
        self.button_edit_homework.place(x=920,y=20,width=260,height=60)

        self.button_password_control=DButton(self.root,text='账号密码控制',fg=YELLOWTEXTFG,font=YAHEI_TEXT_FONT,command=self.password_control)
        self.button_password_control.place(x=920,y=100,width=260,height=60)

        self.button_save_homework_file=DButton(self.root,text='写入历史记录',font=YAHEI_TEXT_FONT,command=self.save_homework_history)
        self.button_save_homework_file.place(x=920,y=180,width=260,height=60)

        self.button_load_homework_file=DButton(self.root,text='载入历史记录',font=YAHEI_TEXT_FONT,command=self.load_homework_history)
        self.button_load_homework_file.place(x=920,y=260,width=260,height=60)

        self.button_clear_history=DButton(self.root,text='清理历史记录',font=YAHEI_TEXT_FONT,fg=REDTEXTFG,command=self.clear_homework_history)
        self.button_clear_history.place(x=920,y=340,width=260,height=60)

        self.button_export_image=DButton(self.root,text='生成图片',font=YAHEI_TEXT_FONT,fg=HIGHLIGHT,command=self.export_homework_image)
        self.button_export_image.place(x=920,y=420,width=260,height=60)

        self.button_exit_app=DButton(self.root,text='关闭程序',font=YAHEI_TEXT_FONT,command=self.exit_app,fg=REDTEXTFG)
        self.button_exit_app.place(x=920,y=500,width=260,height=60)

        self.button_settings=DButton(self.root,text='全局设定',font=YAHEI_TEXT_FONT,command=self.open_settings_window,)
        self.button_settings.place(x=920,y=580,width=260,height=60)

        self.button_about=DButton(self.root,text='关于',command=self.about,)
        self.button_about.place(x=1100,y=750,width=80,height=30)

        ConvertPlaceToRelative(self.root)

    def exit_app(self,):
        self.save_homework_history(silent=True)
        self.root.destroy()
        sys.exit()

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

    def edit_homework(self,event=None):
        selected = self.treeview_homework.selection()
        if not selected:
            win32api.MessageBeep()
            return
        item = selected[0]
        parent = self.treeview_homework.parent(item)
        # 选中科目或其子作业,都编辑该科目
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
            try:
                window_homework.destroy()
            except Exception:
                pass
            # 关闭后强制展开主界面对应科目,并刷新行色
            try:
                if self.treeview_homework.exists(subject):
                    self.treeview_homework.item(subject, open=True)
                    self._update_subject_state(subject)
                    self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))
            except Exception:
                pass
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
                            takefocus=True, selectmode='browse',
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
            try:
                t = tree_ref[0]
                if t is not None and t.winfo_exists():
                    SetExpandedTreeviewRowColor(t)
            except Exception:
                pass

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
                try:
                    w = w.master
                except Exception:
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
            """取消本次编辑：丢弃输入,恢复原内容,不改 working_list"""
            if edit_entry[0] is None:
                return
            try:
                edit_entry[0].destroy()
            except Exception:
                pass
            edit_entry[0] = None
            editing_index[0] = None
            editing_item[0] = None
            try:
                button_ok.bind_default_active()
            except Exception:
                pass
            # 原内容仍在 working_list,刷新显示即可
            refresh_tree()

        def commit_edit():
            if edit_entry[0] is None:
                return
            try:
                new_text = edit_entry[0].get()
            except Exception:
                new_text = ''
            idx = editing_index[0]
            try:
                edit_entry[0].destroy()
            except Exception:
                pass
            edit_entry[0] = None
            editing_index[0] = None
            editing_item[0] = None

            if idx is None or idx < 0 or idx >= len(working_list):
                try:
                    button_ok.bind_default_active()
                except Exception:
                    pass
                return
            if new_text.replace('\t', '').replace(' ', '') == '':
                # 空内容视为删除
                del working_list[idx]
            else:
                working_list[idx] = new_text

            try:
                button_ok.bind_default_active()
            except Exception:
                pass
            
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
                try:
                    edit_entry[0].Entry.focus_set()
                except Exception:
                    pass
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
            try:
                if subject in self.homework_template and 'template' in self.homework_template[subject]:
                    entry['values'] = self.homework_template[subject]['template']
            except Exception:
                pass
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
                try:
                    edit_entry[0].destroy()
                except Exception:
                    pass
                edit_entry[0] = None
                editing_index[0] = None
                editing_item[0] = None
                try:
                    button_ok.bind_default_active()
                except Exception:
                    pass
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

        button_number_open_touch_keyboard= DButton(frame_number, text='\uF741', font=self.font_icon, command=OpenTouchKeyboard, takefocus=0)
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
            """在作业末尾切换样式字母：无则追加,有则删除;只处理末尾连续的 RGYBO."""
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
            body, markers = s[:i], list(s[i:])
            if letter in markers:
                markers = [m for m in markers if m != letter]
            else:
                markers.append(letter)
            new_s = body + ''.join(markers)
            try:
                target.delete(0, tk.END)
                target.insert(0, new_s)
                target.Entry.focus_set()
                target.Entry.icursor(tk.END)
            except Exception:
                pass

        try:
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
        except Exception:
            pass

        # 程序级样式标记：R红 G深绿 Y深黄 B天蓝 O加粗（插在配置候选词之后）
        style_btns = [
            ('R', REDTEXTFG),
            ('G', GREENLIGHT),
            ('Y', YELLOWTEXTFG),
            ('B', HIGHLIGHT),
            ('O', TEXTFG),
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
            if result=='':
                win32api.MessageBeep()
            else:
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
        try:
            for subject in self.homework_template.keys():
                if subject not in accounts:
                    accounts.append(subject)
        except Exception:
            pass
        try:
            for key in self.settings.get('password', {}).keys():
                if key not in accounts:
                    accounts.append(key)
        except Exception:
            pass

        # 弹出 PasswordBox：选择账户并输入当前密码
        result = PasswordBox(
            title='账号密码控制',
            text='请选择要修改密码的账户,并输入当前密码进行验证.',
            parent=self.root,
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

        username, password, _ = result

        # 验证密码
        if username == 'admin':
            correct_pwd = self.settings['password'].get('admin', '')
        else:
            correct_pwd = self.settings['password'].get(username, self.settings['password'].get('default', ''))

        if password != correct_pwd:
            MessageBoxModern(
                parent=self.root,
                title='错误',
                icon='error',
                text_blod='密码错误',
                text='密码错误,请重试或咨询课管理员.'
            )
            return

        # 验证通过,提示即将输入新密码
        MessageBoxModern(
            parent=self.root,
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
                parent=self.root,
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
                parent=self.root,
                title='成功',
                icon='correct',
                text_blod='密码修改成功',
                text=f'账户"{username}"的密码已成功修改.'
            )
        except Exception:
            MessageBoxModern(
                parent=self.root,
                title='错误',
                icon='error',
                text_blod='保存设置失败',
                text=traceback.format_exc()
            )

    def save_homework_history(self, silent=False):
        """将当前作业保存到历史记录.成功时不弹窗,按钮短暂显示「成功」."""
        try:
            date = datetime.datetime.now().strftime('%Y-%m-%d')

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
            try:
                btn = self.button_save_homework_file
                old_text = btn['text']
                btn['text'] = '成功'
                def _restore():
                    try:
                        if btn.winfo_exists():
                            btn['text'] = old_text
                            btn._update_border_size()
                    except Exception:
                        pass
                self.root.after(500, _restore)
            except Exception:
                pass
        except:
            if not silent:
                MessageBoxModern(parent=self.root,title='错误',text=traceback.format_exc(),text_blod='写入历史记录文件失败',icon='error')

    def clear_homework_history(self):
        """清空 previous_homework 历史记录（需 admin 密码）"""
        if not self.verify_admin_password():
            return
        confirm = MessageBoxModern(
            parent=self.root,
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
                parent=self.root,
                title='成功',
                icon='correct',
                text_blod='清理完成',
                text='历史记录已全部清空.'
            )
        except Exception:
            MessageBoxModern(
                parent=self.root,
                title='错误',
                icon='error',
                text_blod='清理历史记录失败',
                text=traceback.format_exc()
            )

    def load_homework_history(self):
        """载入历史记录 (控制台输入版)"""
        if not self.verify_admin_password():
            return
        target_date = EntryBox(self.root,title='日期',text_blod="输入要载入的作业历史记录的日期",text="输入要载入的作业历史记录的日期,格式为yyyy-mm-dd,例如2026-08-05,2025-12-01.",entrys=[['日期:',datetime.datetime.now().strftime('%Y-%m-%d')]])
            
        if target_date:
            target_date=target_date[0]
            try:
                # 读取历史记录文件
                with open('homeworktool_previous_homework.json', 'r', encoding='utf-8') as f:
                    history = json.load(f)

                # 检查日期是否存在于历史记录中
                if target_date in history:
                    target_homework = history[target_date]

                    # 1. 清空当前所有科目的作业数据
                    for subject in list(self.homework_data.keys()):
                        self.homework_data[subject] = []
                        self.treeview_homework.item(subject, open=False) # 收起节点

                    # 2. 遍历并加载指定日期的作业数据
                    for subject, homework_list in target_homework.items():
                        if subject in self.homework_data:
                            # 触发字典监听器,自动刷新 UI
                            self.homework_data[subject] = homework_list
                        else:
                            # 如果是新科目,新建父节点并赋值
                            self.treeview_homework.insert('', 'end', iid=subject, text=subject, values=('',))
                            self.homework_data[subject] = homework_list

                    # 3. 展开所有有作业的科目节点并刷新状态
                    for subject in self.homework_data.keys():
                        if self.homework_data[subject]:
                            self.treeview_homework.item(subject, open=True)
                        self._update_subject_state(subject)

                    # 成功提示
                    MessageBoxModern(parent=self.root, title='成功', text=f'已成功载入{target_date}的作业记录.', text_blod='载入历史记录成功', icon='correct')


                else:
                    MessageBoxModern(parent=self.root, title='错误', text=f'找不到{target_date}的作业记录.', text_blod='该日作业的历史记录不存在', icon='error')
                    
            except :
                MessageBoxModern(parent=self.root, title='错误', text=traceback.format_exc(), text_blod='载入历史记录文件失败', icon='error')

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
        except:
            pass  # 静默处理异常,确保即使自动加载失败也不影响程序正常启动

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
            try:
                window_settings.destroy()
            except Exception:
                pass
            try:
                self.root.focus()
            except Exception:
                pass

        window_settings = tk.Toplevel(self.root)
        window_settings.title("软件全局设置")
        SetDarkTitleBar(window_settings)
        width = 920
        height = 550
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

        tk.Label(window_settings, bg=TEXTBG).place(x=20, y=110, width=880, height=2)

        tk.Label(window_settings, bg=WINDOWBG, fg=TEXTFG, text='科目设定:', anchor='w').place(x=20, y=130, height=30)
        listbox_subject = tk.Listbox(
            window_settings, bd=0, bg=TEXTBG, highlightthickness=0, fg=TEXTFG,
            activestyle='none', selectmode='browse', exportselection=0,
            selectbackground=AlphaBlend(HIGHLIGHT, TEXTBG, 0.5), selectforeground=TEXTFG,
        )
        listbox_subject.place(x=20, y=170, width=120, height=310)
        scrollber_y_listbox_subject = DScrollbar(window_settings, command=listbox_subject.yview)
        scrollber_y_listbox_subject.place(x=140, y=170, width=20, height=310)
        listbox_subject.config(yscrollcommand=scrollber_y_listbox_subject.set)

        button_add_subject = DButton(window_settings, text='\uF164', font=self.font_icon)
        button_add_subject.place(x=180, y=170, width=30, height=30)  # 不允许与程序内的默认科目重名.
        BindTipWindow(button_add_subject, text='新增科目')

        button_rename_subject = DButton(window_settings, text='\uED63', font=self.font_icon)
        button_rename_subject.place(x=180, y=220, width=30, height=30)
        # 不允许重命名程序内的默认科目.点击保存配置按钮之后要同步更改程序内数据和三个外部文件的数据,但不更改过去的作业历史记录
        BindTipWindow(button_rename_subject, text='重命名科目(默认九科不可改)')

        button_remove_subject = DButton(window_settings, text='\uF166', font=self.font_icon)
        button_remove_subject.place(x=180, y=270, width=30, height=30)  # 不允许删除程序内的默认科目.点击删除按钮的时候要弹窗疑问.
        BindTipWindow(button_remove_subject, text='删除科目(默认九科不可删)')




        tk.Label(window_settings, bg=TEXTBG).place(x=230, y=130, width=2, height=350)







        tk.Label(window_settings, bg=WINDOWBG, fg=TEXTFG, text='选中的科目相关设定(每行一项,直接编辑):', anchor='w').place(x=250, y=130, height=30)

        def _make_settings_text(parent):
            """样式参考 MCLangTool 主文本框."""
            t = tk.Text(parent, bd=0, highlightthickness=0, bg=TEXTBG, fg=TEXTFG,
                                 font=YAHEI_TEXT_FONT,
                                 insertbackground=GREENLIGHT,
                                 insertontime=500, insertofftime=500, insertwidth=3,
                                 selectforeground=TEXTFG, selectbackground=HIGHLIGHT,)
            SetBorder(t)
            return t

        tk.Label(window_settings, bg=WINDOWBG, fg=TEXTFG, text='作业:', anchor='w').place(x=250, y=170, height=30)
        text_homework = _make_settings_text(window_settings)
        text_homework.place(x=250, y=210, width=250, height=270)
        scrollber_y_text_homework = DScrollbar(window_settings, command=text_homework.yview, bg=WINDOWBG)
        scrollber_y_text_homework.place(x=500, y=210, width=20, height=270)
        text_homework.config(yscrollcommand=scrollber_y_text_homework.set)

        tk.Label(window_settings, bg=WINDOWBG, fg=TEXTFG, text='量词候选词:', anchor='w').place(x=540, y=170, height=30)
        text_measure_word = _make_settings_text(window_settings)
        text_measure_word.place(x=540, y=210, width=150, height=270)
        scrollber_y_text_measure_word = DScrollbar(window_settings, command=text_measure_word.yview, bg=WINDOWBG)
        scrollber_y_text_measure_word.place(x=690, y=210, width=20, height=270)
        text_measure_word.config(yscrollcommand=scrollber_y_text_measure_word.set)

        tk.Label(window_settings, bg=WINDOWBG, fg=TEXTFG, text='其它候选词:', anchor='w').place(x=730, y=170, height=30)
        text_other_word = _make_settings_text(window_settings)
        text_other_word.place(x=730, y=210, width=150, height=270)
        scrollber_y_text_other_word = DScrollbar(window_settings, command=text_other_word.yview, bg=WINDOWBG)
        scrollber_y_text_other_word.place(x=880, y=210, width=20, height=270)
        text_other_word.config(yscrollcommand=scrollber_y_text_other_word.set)

        button_advanced = DButton(window_settings, text='高级设置', command=lambda: self.open_advanced_settings_window(window_settings))
        button_advanced.place(x=20, y=500, width=120, height=30)

        button_ok = DButton(window_settings, text='确定', default='active')
        button_ok.place(x=720, y=500, width=80, height=30)
        button_ok.unbind_default_active()

        button_cancel = DButton(window_settings, text='取消', command=close_window_settings)
        button_cancel.place(x=820, y=500, width=80, height=30)
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
                try:
                    idx = ordered_subjects().index(select_name)
                    listbox_subject.selection_clear(0, tk.END)
                    listbox_subject.selection_set(idx)
                    listbox_subject.activate(idx)
                    listbox_subject.see(idx)
                except ValueError:
                    pass
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
                text='保存后会同步程序数据与配置文件(不改历史记录).',
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

            # 2) 应用科目删除到内存树与 homework_data
            for subj in list(removed_subjects):
                if subj in self.homework_data:
                    try:
                        del self.homework_data[subj]
                    except Exception:
                        self.homework_data.pop(subj, None)
                if self.treeview_homework.exists(subj):
                    try:
                        self.treeview_homework.delete(subj)
                    except Exception:
                        pass
                # settings.password 中对应条目可保留或删除：删除自定义科时一并去掉密码键
                try:
                    if 'password' in self.settings and subj in self.settings['password']:
                        if subj not in DEFAULT_SUBJECTS:
                            del self.settings['password'][subj]
                except Exception:
                    pass

            # 3) 应用重命名（不改历史记录文件）
            # rename_map: old -> new;可能有多条
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
                try:
                    pwd = self.settings.get('password', {})
                    if old_name in pwd:
                        pwd[new_name] = pwd.pop(old_name)
                except Exception:
                    pass

            # 4) 新增科目：确保树与数据存在
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

            try:
                self.root.after_idle(lambda: SetExpandedTreeviewRowColor(self.treeview_homework))
            except Exception:
                pass

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
            'EXPORT_FONT_SUBJECT_MIN', 'EXPORT_FONT_CONTENT_MIN',
            'EXPORT_LINE_SPACING_CONTENT', 'EXPORT_LINE_SPACING_SUBJECT', 'EXPORT_SUBJECT_GAP',
            'EXPORT_MARGIN_X', 'EXPORT_MARGIN_BOTTOM', 'EXPORT_DATE_Y',
            'EXPORT_START_Y', 'EXPORT_GAP_CENTER',
        }

        def close_adv(event=None):
            try:
                win.destroy()
            except Exception:
                pass
            try:
                parent.focus()
            except Exception:
                pass

        win = tk.Toplevel(parent)
        win.title('高级设置')
        SetDarkTitleBar(win)
        w, h = 900, 560
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry('%dx%d+%d+%d' % (w, h, (sw - w) // 2, (sh - h) // 2))
        win['bg'] = WINDOWBG
        win.protocol('WM_DELETE_WINDOW', close_adv)
        win.bind('<Escape>', close_adv)
        win.focus()

        tk.Label(
            win, bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor='w',
            text='双击「值」列编辑,重新打开软件后生效.',
        ).place(x=20, y=10, width=860, height=30)

        style = ttk.Style()
        try:
            style.theme_use('alt')
        except Exception:
            pass
        style.configure(
            'Adv.Treeview', rowheight=28,
            fieldbackground=WINDOWBG, background=WINDOWBG, foreground=TEXTFG,
            borderwidth=0, highlightthickness=0, font=YAHEI_TEXT_FONT,
        )
        style.configure(
            'Adv.Treeview.Heading',
            background=WINDOWBG, foreground=TEXTFG, borderwidth=0, highlightthickness=0,
            font=YAHEI_TEXT_FONT,
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

        scroll = DScrollbar(win, bg=WINDOWBG)
        scroll.place(x=860, y=50, width=20, height=450)
        tree = ttk.Treeview(
            win, show='headings', columns=('desc', 'name', 'value'),
            selectmode='browse', yscrollcommand=scroll.set, style='Adv.Treeview',
        )
        tree.place(x=20, y=50, width=840, height=450)
        scroll.config(command=tree.yview)
        SetBorder(tree)

        tree.heading('desc', text='说明', anchor='center')
        tree.heading('name', text='变量名', anchor='center')
        tree.heading('value', text='值', anchor='center')
        tree.column('desc', width=300, anchor='w')
        tree.column('name', width=240, anchor='w')
        tree.column('value', width=290, anchor='w')

        
        work = {}
        for _desc, key in ADVANCED_SETTING_ROWS:
            if key == 'YAHEI_TEXT_FONT':
                work[key] = copy.deepcopy(self.settings.get(key, YAHEI_TEXT_FONT))
            else:
                work[key] = copy.deepcopy(self._cfg(key, DEFAULT_EXPORT_SETTINGS.get(key)))

        def value_to_display(v):
            if isinstance(v, (list, dict, tuple)):
                try:
                    return json.dumps(v, ensure_ascii=False)
                except Exception:
                    return str(v)
            return str(v)

        def refresh_rows():
            for iid in tree.get_children():
                tree.delete(iid)
            for desc, key in ADVANCED_SETTING_ROWS:
                tree.insert('', 'end', iid=key, values=(desc, key, value_to_display(work.get(key, ''))))
            try:
                win.after_idle(lambda: SetExpandedTreeviewRowColor(tree))
            except Exception:
                pass

        refresh_rows()

        def parse_value(key, text_val):
            text_val = (text_val or '').strip()
            default = DEFAULT_EXPORT_SETTINGS.get(key)

            if key == 'YAHEI_TEXT_FONT':
                if text_val.startswith('['):
                    return json.loads(text_val)
                return text_val
            if key in ('EXPORT_FONT_FALLBACK_NAMES', 'highlight_box'):
                return json.loads(text_val)
            if key == 'EXPORT_FONT_NAME':
                return text_val
            if key in SPINBOX_KEYS:
                return int(float(text_val)) if text_val not in ('', '-',) else int(default or 0)
            try:
                if '.' in text_val:
                    return float(text_val)
                return int(text_val)
            except Exception:
                return text_val

        # 当前编辑器引用（DEntry 或 DSpinbox）
        editor_ref = [None]

        def is_widget_or_descendant(widget, root_widget):
            """判断 widget 是否为 root_widget 或其子孙."""
            w = widget
            while w is not None:
                if w is root_widget:
                    return True
                try:
                    w = w.master
                except Exception:
                    break
            return False

        def destroy_editor():
            ed = editor_ref[0]
            editor_ref[0] = None
            if ed is None:
                return
            try:
                ed.destroy()
            except Exception:
                pass

        def on_double_click(event):
            # 已有编辑器时先不重复创建
            if editor_ref[0] is not None:
                return 'break'

            row_id = tree.focus()
            if not row_id:
                # 鼠标双击时尝试 identify_row
                if hasattr(event, 'y'):
                    row_id = tree.identify_row(event.y)
                if not row_id:
                    return
            if hasattr(event, 'x') and event.x > 0:
                column = tree.identify_column(event.x)
            else:
                column = '#3'
            if column != '#3':
                return 'break'
            bbox = tree.bbox(row_id, column)
            if not bbox:
                return 'break'
            x, y, width, height = bbox
            vals = tree.item(row_id, 'values')
            current_value = vals[2] if len(vals) > 2 else ''
            key = row_id

            use_spin = key in SPINBOX_KEYS
            use_combo = (key == 'color_mode')

            if use_spin:
                # 合理上下限
                lo, hi = -10 ** 9, 10 ** 9
                if 'MIN' in key:
                    lo, hi = 1, 500
                elif 'FONT' in key and 'NAME' not in key:
                    lo, hi = 1, 500
                elif 'SPACING' in key or 'GAP' in key:
                    lo, hi = 0, 2000
                elif 'MARGIN' in key or '_Y' in key or '_X' in key:
                    lo, hi = 0, 5000
                editor = DSpinbox(tree, int_only=True, from_=lo, to=hi, increment=1)
                try:
                    editor.delete(0, tk.END)
                    editor.insert(0, str(int(float(current_value))) if current_value not in ('',) else '0')
                except Exception:
                    editor.delete(0, tk.END)
                    editor.insert(0, current_value or '0')
                get_text = lambda: editor.get()
                focus_target = editor
            elif use_combo:
                # color_mode 仅允许 system / dark / light
                editor = DCombobutton(tree, values=['system', 'dark', 'light'], state='readonly',)
                try:
                    editor['state']='normal'
                    editor.delete(0, tk.END)
                    cur = (current_value or 'system').strip().lower()
                    if cur not in ('system', 'dark', 'light'):
                        cur = 'system'
                    editor.insert(0, cur)
                    editor['state']='readonly'
                except Exception:
                    try:
                        editor.insert(0, 'system')
                    except Exception:
                        pass
                get_text = lambda: editor.get()
                focus_target = editor
            else:
                editor = DEntry(tree)
                editor.insert('end', current_value)
                editor.icursor('end')
                get_text = lambda: editor.get()
                focus_target = editor

            editor.original_value = current_value
            editor.row_id = row_id
            editor_ref[0] = editor

            def apply_edit(event=None):
                ed = editor_ref[0]
                if ed is None:
                    return
                # 若焦点仍在编辑器内部（含 DSpinbox 的 +/- 按钮），不结束编辑
                try:
                    fw = win.focus_get()
                except Exception:
                    fw = None
                if fw is not None and is_widget_or_descendant(fw, ed):
                    return
                # 滚动等外部操作会强制结束：此时用 force 参数
                _commit_editor()

            def apply_edit_force(event=None):
                """滚动表格/滚动条时强制提交（即使焦点仍在编辑器上）."""
                _commit_editor()

            def _commit_editor():
                ed = editor_ref[0]
                if ed is None:
                    return
                editor_ref[0] = None
                try:
                    _unbind_scroll()
                except Exception:
                    pass
                try:
                    new_value = get_text()
                except Exception:
                    new_value = ''
                key_local = getattr(ed, 'row_id', None)
                try:
                    ed.destroy()
                except Exception:
                    pass
                if not key_local:
                    tree.focus_set()
                    return
                try:
                    parsed = parse_value(key_local, new_value)
                except Exception as e:
                    MessageBoxModern(
                        parent=win, title='错误', icon='error',
                        text_blod='值格式错误', text=str(e),
                    )
                    tree.focus_set()
                    return
                if key_local == 'highlight_box':
                    if not (isinstance(parsed, (list, tuple)) and len(parsed) >= 4):
                        MessageBoxModern(
                            parent=win, title='错误', icon='error',
                            text_blod='高亮矩形格式错误',
                            text='需要长度为4的数组: [x, y, 宽, 高]',
                        )
                        tree.focus_set()
                        return
                    parsed = [int(parsed[0]), int(parsed[1]), int(parsed[2]), int(parsed[3])]
                work[key_local] = parsed
                tree.item(key_local, values=(tree.item(key_local, 'values')[0], key_local, value_to_display(parsed)))
                tree.focus_set()

            def cancel_edit(event=None):
                try:
                    _unbind_scroll()
                except Exception:
                    pass
                destroy_editor()
                tree.focus_set()

            editor.place(x=x, y=y, width=width, height=height)
            # 回车确认、Esc 取消
            if use_spin:
                editor.Entry.bind('<Return>', lambda e: apply_edit_force())
                editor.Entry.bind('<Escape>', cancel_edit)
                # FocusOut：若焦点去了 +/- 则不提交
                editor.Entry.bind('<FocusOut>', apply_edit)
                editor.bind('<FocusOut>', apply_edit)
                editor.DButton_up.bind('<FocusOut>', apply_edit)
                editor.DButton_down.bind('<FocusOut>', apply_edit)
            elif use_combo:
                editor.Entry.bind('<Return>', lambda e: apply_edit_force())
                editor.Entry.bind('<Escape>', cancel_edit)
                editor.Entry.bind('<FocusOut>', apply_edit)
                editor.bind('<FocusOut>', apply_edit)
                try:
                    editor.DButton_show_list.bind('<FocusOut>', apply_edit)
                except Exception:
                    pass
            else:
                editor.bind('<Return>', lambda e: apply_edit_force())
                editor.bind('<Escape>', cancel_edit)
                editor.bind('<FocusOut>', apply_edit)

            # 与 MCLangTool 一致：滚动表格/拖动滚动条时结束编辑
            bind_ids = [
                (tree, '<MouseWheel>', tree.bind('<MouseWheel>', apply_edit_force, add='+')),
                (scroll, '<MouseWheel>', scroll.bind('<MouseWheel>', apply_edit_force, add='+')),
                (scroll, '<B1-Motion>', scroll.bind('<B1-Motion>', apply_edit_force, add='+')),
            ]
            editor._scroll_bind_ids = bind_ids

            def _unbind_scroll():
                for widget, seq, fid in getattr(editor, '_scroll_bind_ids', []) or []:
                    try:
                        widget.unbind(seq, fid)
                    except Exception:
                        pass
                try:
                    editor._scroll_bind_ids = []
                except Exception:
                    pass

            focus_target.focus_set()
            try:
                if use_spin or use_combo:
                    editor.Entry.select_range(0, tk.END)
                else:
                    editor.select_range(0, tk.END)
            except Exception:
                pass
            return 'break'

        tree.bind('<Double-Button-1>', on_double_click)
        tree.bind('<Return>', on_double_click)
        tree.bind('<F2>', on_double_click)

        def save_adv():
            global YAHEI_TEXT_FONT
            # 若仍在编辑，先提交
            if editor_ref[0] is not None:
                try:
                    # 强制提交
                    ed = editor_ref[0]
                    if isinstance(ed, DSpinbox) or isinstance(ed, DCombobutton):
                        txt = ed.Entry.get()
                    else:
                        txt = ed.get()
                    key = ed.row_id
                    parsed = parse_value(key, txt)
                    if key == 'highlight_box' and isinstance(parsed, (list, tuple)) and len(parsed) >= 4:
                        parsed = [int(parsed[0]), int(parsed[1]), int(parsed[2]), int(parsed[3])]
                    work[key] = parsed
                except Exception:
                    pass
                destroy_editor()

            for key, val in work.items():
                self.settings[key] = val
                if key != 'YAHEI_TEXT_FONT':
                    if not hasattr(self, 'export_cfg'):
                        self.export_cfg = dict(DEFAULT_EXPORT_SETTINGS)
                    self.export_cfg[key] = val
            if 'YAHEI_TEXT_FONT' in work:
                YAHEI_TEXT_FONT = work['YAHEI_TEXT_FONT']
                self.settings['YAHEI_TEXT_FONT'] = YAHEI_TEXT_FONT
            if 'color_mode' in work:
                cm = str(work['color_mode'] or 'system').strip().lower()
                if cm not in ('system', 'dark', 'light'):
                    cm = 'system'
                self.color_mode = cm
                self.settings['color_mode'] = cm
                if hasattr(self, 'export_cfg'):
                    self.export_cfg['color_mode'] = cm
            try:
                with open('homeworktool_settings.json', 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, ensure_ascii=False, indent=2)
            except Exception:
                MessageBoxModern(
                    parent=win, title='错误', icon='error',
                    text_blod='保存高级设置失败', text=traceback.format_exc(),
                )
                return
            close_adv()

        button_ok_advanced=DButton(win, text='确定', default='active', command=save_adv)
        button_ok_advanced.place(x=700, y=515, width=80, height=30)
        button_ok_advanced.unbind_default_active()

        button_cancel_advanced=DButton(win, text='取消', command=close_adv)
        button_cancel_advanced.place(x=800, y=515, width=80, height=30)
        button_cancel_advanced.unbind_default_active()

        try:
            ConvertPlaceToRelative(win)
        except Exception:
            pass
        try:
            win.iconbitmap(f'{libresource}icon.ico')
        except Exception:
            pass
        win.wait_window()

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


        label_title=tk.Label(self.about_window,bg=WINDOWBG,text='万岁™作业布置工具(合肥一中特供版)',anchor='center',fg=TEXTFG)
        set_label_font(label_title,add_size=18,bold=True)
        label_title.place(x=00,y=20,width=800,height=70)

        tk.Label(self.about_window,bg=TEXTBG,fg=TEXTFG,).place(x=20,y=120,width=760,height=2)

        tk.Label(self.about_window,bg=WINDOWBG,fg=TEXTFG,text='软件概述:',anchor='w').place(x=20,y=140,width=90,height=30)
        label_introduction=tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text='一款专为教室大屏设计的作业布置与展示工具.',anchor='w')
        label_introduction.place(x=110,y=140,height=30)
        BindTipWindow(label_introduction,text='老桃基于「老桃制度 万岁思想 本真观念」所设计的软件.',width=450)


        tk.Label(self.about_window,bg=WINDOWBG,fg=TEXTFG,text='当前版本:',anchor='w').place(x=20,y=180,width=90,height=30)
        tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text=f'V{VERSION}',anchor='w').place(x=110,y=180,height=30)

        tk.Label(self.about_window,bg=TEXTBG,fg=TEXTFG,).place(x=20,y=230,width=760,height=2)

        tk.Label(self.about_window,bg=WINDOWBG,fg=TEXTFG,text='著作权:',anchor='w').place(x=20,y=250,width=90,height=30)
        label_copyright=tk.Label(self.about_window,bg=WINDOWBG,fg=TEXTFG,text='Copyright © 2026 炸图监管者 · Licensed under the MIT License.',anchor='w')
        label_copyright.place(x=110,y=250,height=30)
        BindTipWindow(label_copyright,text=MITLICENSE,width=600)

        tk.Label(self.about_window,bg=TEXTBG,fg=TEXTFG,).place(x=20,y=300,width=760,height=2)

        tk.Label(self.about_window,bg=WINDOWBG,fg=TEXTFG,text='相关链接:',anchor='w').place(x=20,y=320,width=90,height=30)


        label_github=tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text='Github:',anchor='w',)
        label_github.place(x=60,y=360,width=90,height=30)

        button_github=DAlphaButton(self.about_window,text='https://github.com/zhatujianguanzhe',command=lambda:webbrowser.open_new_tab("https://github.com/zhatujianguanzhe"),fg=LINK,anchor='w')
        button_github.place(x=150,y=360,height=30)

        label_discord=tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text='Discord:',anchor='w',)
        label_discord.place(x=60,y=400,width=90,height=30)

        button_discord=DAlphaButton(self.about_window,text='https://discord.gg/Ukr55F2Ypc',command=lambda:webbrowser.open_new_tab("https://discord.gg/Ukr55F2Ypc"),fg=LINK,anchor='w')
        button_discord.place(x=150,y=400,height=30)

        label_bilibili=tk.Label(self.about_window,bg=WINDOWBG,fg=SECONDARYTEXTFG,text='Bilibili:',anchor='w',)
        label_bilibili.place(x=60,y=440,width=90,height=30)

        button_bilibili=DAlphaButton(self.about_window,text='https://space.bilibili.com/1342104465',command=lambda:webbrowser.open_new_tab("https://space.bilibili.com/1342104465"),fg=LINK,anchor='w')
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








if __name__=='__main__':
    Main()