VERSION = "1.1.1"
# coding=utf-8
"""字形台 - 只读字体预览.


    python 字形台.py
    python 字形台.py some.ttf

"""

import io
import math
import struct
import sys
import zlib
import threading
import traceback
import webbrowser
import tkinter.font as tkfont


APP_NAME = "万岁™字形台"
APP_NAME_SHORT = "字形台"


# ---------------------------------------------------------------------------
# 字体解析（不依赖 fontTools）
# ---------------------------------------------------------------------------

def _u16(b, o):
    return struct.unpack_from(">H", b, o)[0]


def _i16(b, o):
    return struct.unpack_from(">h", b, o)[0]


def _u32(b, o):
    return struct.unpack_from(">I", b, o)[0]


MAC_NAMES = (
    ".notdef", ".null", "nonmarkingreturn", "space", "exclam", "quotedbl", "numbersign",
    "dollar", "percent", "ampersand", "quotesingle", "parenleft", "parenright", "asterisk",
    "plus", "comma", "hyphen", "period", "slash", "zero", "one", "two", "three", "four",
    "five", "six", "seven", "eight", "nine", "colon", "semicolon", "less", "equal",
    "greater", "question", "at",
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
    "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "bracketleft", "backslash", "bracketright",
    "asciicircum", "underscore", "grave",
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q",
    "r", "s", "t", "u", "v", "w", "x", "y", "z", "braceleft", "bar", "braceright", "asciitilde",
    "Adieresis", "Aring", "Ccedilla", "Eacute", "Ntilde", "Odieresis", "Udieresis", "aacute",
    "agrave", "acircumflex", "adieresis", "atilde", "aring", "ccedilla", "eacute", "egrave",
    "ecircumflex", "edieresis", "iacute", "igrave", "icircumflex", "idieresis", "ntilde",
    "oacute", "ograve", "ocircumflex", "odieresis", "otilde", "uacute", "ugrave", "ucircumflex",
    "udieresis", "dagger", "degree", "cent", "sterling", "section", "bullet", "paragraph",
    "germandbls", "registered", "copyright", "trademark", "acute", "dieresis", "notequal",
    "AE", "Oslash", "infinity", "plusminus", "lessequal", "greaterequal", "yen", "mu",
    "partialdiff", "summation", "product", "pi", "integral", "ordfeminine", "ordmasculine",
    "Omega", "ae", "oslash", "questiondown", "exclamdown", "logicalnot", "radical", "florin",
    "approxequal", "Delta", "guillemotleft", "guillemotright", "ellipsis", "nbspace", "Agrave",
    "Atilde", "Otilde", "OE", "oe", "endash", "emdash", "quotedblleft", "quotedblright",
    "quoteleft", "quoteright", "divide", "lozenge", "ydieresis", "Ydieresis", "fraction",
    "currency", "guilsinglleft", "guilsinglright", "fi", "fl", "daggerdbl", "periodcentered",
    "quotesinglbase", "quotedblbase", "perthousand", "Acircumflex", "Ecircumflex", "Aacute",
    "Edieresis", "Egrave", "Iacute", "Icircumflex", "Idieresis", "Igrave", "Oacute",
    "Ocircumflex", "apple", "Ograve", "Uacute", "Ucircumflex", "Ugrave", "dotlessi",
    "circumflex", "tilde", "macron", "breve", "dotaccent", "ring", "cedilla", "hungarumlaut",
    "ogonek", "caron",
)

BLOCKS = (
    (0x0000, 0x007F, "基本拉丁字母", "Basic Latin"),
    (0x0080, 0x00FF, "拉丁字母-1 补充", "Latin-1 Supplement"),
    (0x0100, 0x017F, "拉丁字母扩展-A", "Latin Extended-A"),
    (0x0180, 0x024F, "拉丁字母扩展-B", "Latin Extended-B"),
    (0x0250, 0x02AF, "国际音标扩展", "IPA Extensions"),
    (0x02B0, 0x02FF, "间距修饰字母", "Spacing Modifier Letters"),
    (0x0300, 0x036F, "组合附加符号", "Combining Diacritical Marks"),
    (0x0370, 0x03FF, "希腊文和科普特文", "Greek and Coptic"),
    (0x0400, 0x04FF, "西里尔文", "Cyrillic"),
    (0x0500, 0x052F, "西里尔文补充", "Cyrillic Supplement"),
    (0x0530, 0x058F, "亚美尼亚文", "Armenian"),
    (0x0590, 0x05FF, "希伯来文", "Hebrew"),
    (0x0600, 0x06FF, "阿拉伯文", "Arabic"),
    (0x0900, 0x097F, "天城文", "Devanagari"),
    (0x0E00, 0x0E7F, "泰文", "Thai"),
    (0x1100, 0x11FF, "谚文声母", "Hangul Jamo"),
    (0x1E00, 0x1EFF, "拉丁字母扩展附加", "Latin Extended Additional"),
    (0x2000, 0x206F, "常用标点", "General Punctuation"),
    (0x2070, 0x209F, "上标和下标", "Superscripts and Subscripts"),
    (0x20A0, 0x20CF, "货币符号", "Currency Symbols"),
    (0x2100, 0x214F, "字母式符号", "Letterlike Symbols"),
    (0x2150, 0x218F, "数字形式", "Number Forms"),
    (0x2190, 0x21FF, "箭头", "Arrows"),
    (0x2200, 0x22FF, "数学运算符", "Mathematical Operators"),
    (0x2300, 0x23FF, "杂项技术符号", "Miscellaneous Technical"),
    (0x2460, 0x24FF, "带圈字母数字", "Enclosed Alphanumerics"),
    (0x2500, 0x257F, "制表符", "Box Drawing"),
    (0x2580, 0x259F, "方块元素", "Block Elements"),
    (0x25A0, 0x25FF, "几何图形", "Geometric Shapes"),
    (0x2600, 0x26FF, "杂项符号", "Miscellaneous Symbols"),
    (0x2700, 0x27BF, "装饰符号", "Dingbats"),
    (0x2800, 0x28FF, "盲文", "Braille Patterns"),
    (0x2E80, 0x2EFF, "中日韩部首补充", "CJK Radicals Supplement"),
    (0x2F00, 0x2FDF, "康熙部首", "Kangxi Radicals"),
    (0x3000, 0x303F, "中日韩符号和标点", "CJK Symbols and Punctuation"),
    (0x3040, 0x309F, "平假名", "Hiragana"),
    (0x30A0, 0x30FF, "片假名", "Katakana"),
    (0x3100, 0x312F, "注音", "Bopomofo"),
    (0x31A0, 0x31BF, "注音扩展", "Bopomofo Extended"),
    (0x3400, 0x4DBF, "中日韩统一表意文字扩展 A", "CJK Extension A"),
    (0x4E00, 0x9FFF, "中日韩统一表意文字", "CJK Unified Ideographs"),
    (0xAC00, 0xD7AF, "谚文音节", "Hangul Syllables"),
    (0xE000, 0xF8FF, "私用区", "Private Use Area"),
    (0xF900, 0xFAFF, "中日韩兼容表意文字", "CJK Compatibility Ideographs"),
    (0xFB00, 0xFB4F, "字母表达形式", "Alphabetic Presentation Forms"),
    (0xFE00, 0xFE0F, "变体选择符", "Variation Selectors"),
    (0xFE30, 0xFE4F, "中日韩兼容形式", "CJK Compatibility Forms"),
    (0xFF00, 0xFFEF, "半角及全角形式", "Halfwidth and Fullwidth Forms"),
    (0x1F300, 0x1F5FF, "杂项符号和象形文字", "Misc Symbols and Pictographs"),
    (0x1F600, 0x1F64F, "表情符号", "Emoticons"),
    (0x20000, 0x2A6DF, "中日韩统一表意文字扩展 B", "CJK Extension B"),
    (0xF0000, 0xFFFFD, "补充私用区-A", "Supplementary Private Use Area-A"),
    (0x100000, 0x10FFFD, "补充私用区-B", "Supplementary Private Use Area-B"),
)


def find_block(cp):
    lo, hi = 0, len(BLOCKS) - 1
    while lo <= hi:
        mid = (lo + hi) >> 1
        start, end = BLOCKS[mid][0], BLOCKS[mid][1]
        if cp < start:
            hi = mid - 1
        elif cp > end:
            lo = mid + 1
        else:
            return BLOCKS[mid]
    return None


def fmt_cp(cp):
    hex_ = format(cp, "X")
    if len(hex_) < 4:
        hex_ = hex_.zfill(4)
    return "$" + hex_


def fmt_cps(codes):
    return ",".join(fmt_cp(cp) for cp in codes)


def _sfnt_tables(data, origin=0):
    scaler = data[origin:origin + 4]
    if scaler == b"wOFF":
        return _woff_tables(data)
    if scaler == b"ttcf":
        count = _u32(data, 8)
        if count < 1:
            raise ValueError("字体集合是空的")
        origin = _u32(data, 12)
        scaler = data[origin:origin + 4]
    if scaler not in (b"\x00\x01\x00\x00", b"OTTO", b"true", b"typ1"):
        raise ValueError("不是 TrueType /OpenType 字体")
    num = _u16(data, origin + 4)
    tables = {}
    for i in range(num):
        rec = origin + 12 + i * 16
        tag = data[rec:rec + 4].decode("latin1")
        off = _u32(data, rec + 8)
        length = _u32(data, rec + 12)
        tables[tag] = data[off:off + length]
    return tables


def _woff_tables(data):
    num = _u16(data, 12)
    tables = {}
    for i in range(num):
        rec = 44 + i * 20
        tag = data[rec:rec + 4].decode("latin1")
        off = _u32(data, rec + 4)
        comp = _u32(data, rec + 8)
        orig = _u32(data, rec + 12)
        blob = data[off:off + comp]
        if comp < orig:
            blob = zlib.decompress(blob)
        tables[tag] = blob
    return tables


def _parse_cmap(cmap):
    if len(cmap) < 4:
        return {}
    num = _u16(cmap, 2)
    chosen = []
    for i in range(num):
        rec = 4 + i * 8
        plat = _u16(cmap, rec)
        enc = _u16(cmap, rec + 2)
        off = _u32(cmap, rec + 4)
        if plat in (0, 3):
            chosen.append((0 if plat == 3 and enc == 10 else 1, off))
    chosen.sort()
    mapping = {}
    seen = set()
    for _, off in chosen:
        if off in seen or off + 2 > len(cmap):
            continue
        seen.add(off)
        fmt = _u16(cmap, off)
        if fmt == 4:
            mapping.update(_cmap4(cmap, off))
        elif fmt == 12:
            mapping.update(_cmap12(cmap, off))
        elif fmt == 6:
            mapping.update(_cmap6(cmap, off))
    return mapping


def _cmap4(cmap, off):
    seg_count = _u16(cmap, off + 6) // 2
    end_at = off + 14
    start_at = end_at + 2 * seg_count + 2
    delta_at = start_at + 2 * seg_count
    range_at = delta_at + 2 * seg_count
    out = {}
    for i in range(seg_count):
        end = _u16(cmap, end_at + 2 * i)
        start = _u16(cmap, start_at + 2 * i)
        delta = _i16(cmap, delta_at + 2 * i)
        range_off = _u16(cmap, range_at + 2 * i)
        if start == 0xFFFF:
            continue
        for cp in range(start, end + 1):
            if range_off == 0:
                gid = (cp + delta) & 0xFFFF
            else:
                pos = range_at + 2 * i + range_off + 2 * (cp - start)
                if pos + 2 > len(cmap):
                    continue
                gid = _u16(cmap, pos)
                if gid:
                    gid = (gid + delta) & 0xFFFF
            if gid:
                out[cp] = gid
    return out


def _cmap12(cmap, off):
    groups = _u32(cmap, off + 12)
    out = {}
    pos = off + 16
    for _ in range(groups):
        if pos + 12 > len(cmap):
            break
        start = _u32(cmap, pos)
        end = _u32(cmap, pos + 4)
        gid = _u32(cmap, pos + 8)
        span = end - start + 1
        if 0 < span <= 200000:
            for n in range(span):
                out[start + n] = gid + n
        pos += 12
    return out


def _cmap6(cmap, off):
    first = _u16(cmap, off + 6)
    count = _u16(cmap, off + 8)
    out = {}
    for i in range(count):
        gid = _u16(cmap, off + 10 + 2 * i)
        if gid:
            out[first + i] = gid
    return out


def _decode_name(raw, platform):
    if platform == 3:
        return raw.decode("utf-16-be", "ignore").strip("\x00")
    if platform == 1:
        return raw.decode("latin1", "ignore")
    return raw.decode("utf-8", "ignore")


def _names(table):
    found = {}
    if len(table) < 6:
        return found
    count = _u16(table, 2)
    store = _u16(table, 4)
    best = {}
    for i in range(count):
        rec = 6 + 12 * i
        if rec + 12 > len(table):
            break
        plat = _u16(table, rec)
        name_id = _u16(table, rec + 6)
        length = _u16(table, rec + 8)
        noff = _u16(table, rec + 10)
        lang = _u16(table, rec + 4)
        raw = table[store + noff:store + noff + length]
        text = _decode_name(raw, plat).strip()
        if not text:
            continue
        rank = 0
        if plat == 3 and lang in (0x804, 0x404, 0x409):
            rank = 3 if lang == 0x804 else 2
        elif plat == 3:
            rank = 1
        prev = best.get(name_id)
        if prev is None or rank >= prev[0]:
            best[name_id] = (rank, text)
    for key, val in best.items():
        found[key] = val[1]
    return found


def _post_names(post, count):
    names = [""] * count
    if not post or len(post) < 32:
        return names
    fmt = _u32(post, 0)
    if fmt == 0x00010000:
        for i in range(min(count, len(MAC_NAMES))):
            names[i] = MAC_NAMES[i]
        return names
    if fmt != 0x00020000 or len(post) < 34:
        return names
    num = _u16(post, 32)
    indexes = []
    pos = 34
    for i in range(min(num, count)):
        if pos + 2 > len(post):
            break
        indexes.append(_u16(post, pos))
        pos += 2
    strings = []
    end = len(post)
    while pos < end:
        n = post[pos]
        pos += 1
        strings.append(post[pos:pos + n].decode("latin1", "ignore"))
        pos += n
    for i, idx in enumerate(indexes):
        if idx < len(MAC_NAMES):
            names[i] = MAC_NAMES[idx]
        else:
            custom = idx - 258
            if 0 <= custom < len(strings):
                names[i] = strings[custom]
    return names


def _glyph_bounds(tables, count):
    empty = [False] * count
    bounds = [None] * count
    head = tables.get("head")
    loca = tables.get("loca")
    glyf = tables.get("glyf")
    if not (head and loca and glyf) or len(head) < 52:
        return empty, bounds
    short = _i16(head, 50) == 0
    offsets = []
    if short:
        n = len(loca) // 2
        for i in range(n):
            offsets.append(_u16(loca, i * 2) * 2)
    else:
        n = len(loca) // 4
        for i in range(n):
            offsets.append(_u32(loca, i * 4))
    limit = min(count, max(0, len(offsets) - 1))
    for i in range(limit):
        a, b = offsets[i], offsets[i + 1]
        if b <= a or a < 0 or b > len(glyf):
            empty[i] = True
            continue
        if b - a < 10:
            empty[i] = True
            continue
        contours = _i16(glyf, a)
        if contours == 0:
            empty[i] = True
            continue
        bounds[i] = (_i16(glyf, a + 2), _i16(glyf, a + 4), _i16(glyf, a + 6), _i16(glyf, a + 8))
    for i in range(limit, count):
        empty[i] = True
    return empty, bounds


def _hmtx(tables, count):
    hhea = tables.get("hhea", b"")
    hmtx = tables.get("hmtx", b"")
    metrics = [(0, 0)] * count
    if len(hhea) < 36 or len(hmtx) < 4:
        return metrics, 0, 0, 0
    asc = _i16(hhea, 4)
    desc = _i16(hhea, 6)
    gap = _i16(hhea, 8)
    nmetrics = _u16(hhea, 34)
    advances = []
    bearings = []
    pos = 0
    for _ in range(min(nmetrics, count)):
        if pos + 4 > len(hmtx):
            break
        advances.append(_u16(hmtx, pos))
        bearings.append(_i16(hmtx, pos + 2))
        pos += 4
    last_adv = advances[-1] if advances else 0
    while len(advances) < count:
        if pos + 2 <= len(hmtx):
            bearings.append(_i16(hmtx, pos))
            pos += 2
        else:
            bearings.append(0)
        advances.append(last_adv)
    for i in range(count):
        metrics[i] = (advances[i], bearings[i])
    return metrics, asc, desc, gap


def read_font(path):
    with open(path, "rb") as handle:
        data = handle.read()
    if len(data) < 12:
        raise ValueError("文件太小")
    if data[:4] == b"wOF2":
        raise ValueError("暂不能解析 WOFF2,请打开 .ttf,.otf 或 .woff")
    tables = _sfnt_tables(data)
    head = tables.get("head", b"")
    maxp = tables.get("maxp", b"")
    if len(maxp) < 6:
        raise ValueError("字体缺少 maxp 表")
    count = _u16(maxp, 4)
    upem = _u16(head, 18) if len(head) >= 20 else 1000
    names = _names(tables.get("name", b""))
    cmap = _parse_cmap(tables.get("cmap", b""))
    post = _post_names(tables.get("post", b""), count)
    empty, bounds = _glyph_bounds(tables, count)
    metrics, asc, desc, gap = _hmtx(tables, count)
    weight = 400
    os2 = tables.get("OS/2", b"")
    if len(os2) >= 6:
        weight = _u16(os2, 4)

    is_cff = "glyf" not in tables and ("CFF " in tables or "CFF2" in tables)

    by_gid = {}
    for cp, gid in cmap.items():
        if gid <= 0 or gid >= count:
            continue
        by_gid.setdefault(gid, []).append(cp)
    for gid in by_gid:
        by_gid[gid].sort()

    glyphs = []
    skipped = 0
    for index in range(count):
        if empty[index]:
            skipped += 1
            continue
        box = bounds[index]
        advance, lsb = metrics[index]
        if box:
            xmin, ymin, xmax, ymax = box
            ink_w = xmax - xmin
        else:
            xmin = ymin = xmax = ymax = 0
            ink_w = 0

        unicodes = by_gid.get(index, [])
        name = post[index] or f"glyph{index}"

        if box is None and not unicodes:
            if is_cff:
                if not name or name.startswith("glyph") or name in (".notdef", ".null", "nonmarkingreturn"):
                    skipped += 1
                    continue
            else:
                skipped += 1
                continue

        if box is not None and ink_w == 0 and (ymax - ymin) == 0:
            skipped += 1
            continue

        rsb = advance - lsb - ink_w
        glyphs.append({
            "index": index,
            "name": name,
            "unicodes": unicodes,
            "advance": advance,
            "lsb": lsb,
            "rsb": rsb,
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax,
        })

    block_chars = {}
    char_count = 0
    seen = set()
    for glyph in glyphs:
        for cp in glyph["unicodes"]:
            if cp in seen:
                continue
            seen.add(cp)
            char_count += 1
            block = find_block(cp)
            key = block[0] if block else -1
            block_chars[key] = block_chars.get(key, 0) + 1

    blocks = []
    for start, end, name, en in BLOCKS:
        chars = block_chars.get(start, 0)
        if chars <= 0:
            continue
        blocks.append({
            "start": start,
            "end": end,
            "name": name,
            "en": en,
            "chars": chars,
            "total": end - start + 1,
        })
    other = block_chars.get(-1, 0)
    if other:
        blocks.append({
            "start": -1, "end": -1, "name": "其他", "en": "Other",
            "chars": other, "total": other,
        })

    unmapped = sum(1 for g in glyphs if not g["unicodes"])
    return {
        "path": path,
        "file": path.replace("\\", "/").split("/")[-1],
        "family": names.get(16) or names.get(1) or "",
        "subfamily": names.get(17) or names.get(2) or "",
        "full": names.get(4) or "",
        "version": names.get(5) or "",
        "ps": names.get(6) or "",
        "designer": names.get(9) or "",
        "copyright": names.get(0) or "",
        "trademark": names.get(7) or "",
        "manufacturer": names.get(8) or "",
        "description": names.get(10) or "",
        "license": names.get(13) or "",
        "upem": upem or 1000,
        "ascender": asc,
        "descender": desc,
        "line_gap": gap,
        "weight": weight,
        "glyphs": glyphs,
        "skipped": skipped,
        "char_count": char_count,
        "unmapped": unmapped,
        "blocks": blocks,
        "is_cff": is_cff,
    }


def parse_query(text):
    """解析搜索串. 字码点可带 $ / U+ / 0x,也可不带;同时支持名称与索引."""
    raw = text.strip()
    if not raw:
        return None
    body = raw
    prefixed = False
    for prefix in ("$", "U+", "u+", "0x", "0X", "\\u", "\\U"):
        if body.startswith(prefix):
            body = body[len(prefix):].strip()
            prefixed = True
            break
    # 纯十六进制:带前缀任意长度,或不带前缀且长度 2~6
    if body and all(c in "0123456789abcdefABCDEF" for c in body):
        if prefixed or 2 <= len(body) <= 6:
            try:
                cp = int(body, 16)
                if 0 <= cp <= 0x10FFFF:
                    return ("cp", cp, body.lower())
            except ValueError:
                pass
    if raw.isdigit():
        return ("index", int(raw))
    return ("text", raw.lower())


# ---------------------------------------------------------------------------
# 界面
# ---------------------------------------------------------------------------


def _checksum(data):
    """OpenType table checksum (sum of ULONG big-endian, pad to 4)."""
    if len(data) % 4:
        data = data + b"\x00" * (4 - len(data) % 4)
    total = 0
    for i in range(0, len(data), 4):
        total = (total + _u32(data, i)) & 0xFFFFFFFF
    return total


def _encode_name_utf16(text):
    return (text or "").encode("utf-16-be", "ignore")


def _build_name_table(names_map):
    """
    names_map: {name_id: str} 仅平台 3 (Windows) 语言 0x0409.
    生成 name 表二进制.
    """
    records = []
    store = b""
    for name_id in sorted(names_map.keys()):
        raw = _encode_name_utf16(names_map[name_id])
        records.append((3, 1, 0x0409, name_id, len(raw), len(store)))
        store += raw
    count = len(records)
    header = struct.pack(">HHH", 0, count, 6 + 12 * count)
    body = b""
    for plat, enc, lang, nid, length, noff in records:
        body += struct.pack(">HHHHHH", plat, enc, lang, nid, length, noff)
    return header + body + store


def _replace_sfnt_table(data, tag, new_blob):
    """
    在 sfnt 字体二进制中替换一张表,重算偏移与 head checkSumAdjustment.
    仅支持单字体 (非 TTC / 非 WOFF).
    """
    if data[:4] in (b"wOFF", b"wOF2", b"ttcf"):
        raise ValueError("暂不支持向 WOFF/TTC 写回,请使用 .ttf/.otf")
    if data[:4] not in (b"\x00\x01\x00\x00", b"OTTO", b"true", b"typ1"):
        raise ValueError("不是可写回的 TrueType/OpenType 字体")

    num = _u16(data, 4)
    records = []
    for i in range(num):
        rec = 12 + i * 16
        t = data[rec:rec + 4]
        off = _u32(data, rec + 8)
        length = _u32(data, rec + 12)
        records.append([t, data[off:off + length]])

    tag_b = tag.encode("latin1") if isinstance(tag, str) else tag
    found = False
    for r in records:
        if r[0] == tag_b:
            r[1] = new_blob
            found = True
            break
    if not found:
        records.append([tag_b, new_blob])
        num = len(records)

    pot = 1
    while pot * 2 <= num:
        pot *= 2
    search_range = pot * 16
    entry_selector = int(math.log2(pot)) if pot else 0
    range_shift = num * 16 - search_range

    header = data[:4] + struct.pack(">HHHH", num, search_range, entry_selector, range_shift)
    # 先按目录长度算表数据起点
    cursor = len(header) + 16 * num
    if cursor % 4:
        cursor += 4 - (cursor % 4)

    dir_bin = b""
    table_blobs = b""
    for t, blob in records:
        if cursor % 4:
            pad = 4 - (cursor % 4)
            table_blobs += b"\x00" * pad
            cursor += pad
        check = _checksum(blob)
        dir_bin += t + struct.pack(">III", check, cursor, len(blob))
        table_blobs += blob
        cursor += len(blob)

    out = bytearray(header + dir_bin)
    while len(out) % 4:
        out.append(0)
    # 若 header+dir 对齐后长度与第一条表 offset 不一致,补齐
    first_off = _u32(bytes(dir_bin), 8) if dir_bin else len(out)
    while len(out) < first_off:
        out.append(0)
    out.extend(table_blobs)

    # head.checkSumAdjustment
    num2 = _u16(out, 4)
    head_off = head_len = None
    head_rec = None
    for i in range(num2):
        rec = 12 + i * 16
        if out[rec:rec + 4] == b"head":
            head_off = _u32(out, rec + 8)
            head_len = _u32(out, rec + 12)
            head_rec = rec
            break
    if head_off is not None and head_off + 12 <= len(out):
        out[head_off + 8:head_off + 12] = b"\x00\x00\x00\x00"
        whole = _checksum(bytes(out))
        adjust = (0xB1B0AFBA - whole) & 0xFFFFFFFF
        out[head_off + 8:head_off + 12] = struct.pack(">I", adjust)
        if head_len:
            head_blob = bytes(out[head_off:head_off + head_len])
            out[head_rec + 4:head_rec + 8] = struct.pack(">I", _checksum(head_blob))

    return bytes(out)


def write_font_metadata(path, updates):
    """
    将 updates 写入字体文件的 name 表 (及可选 OS/2 字重).
    updates 键: family, subfamily, full, ps, version, designer, copyright, weight
    """
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] in (b"wOFF", b"wOF2", b"ttcf"):
        raise ValueError("暂不支持向 WOFF/TTC 写回,请另存或使用 .ttf/.otf")

    tables = _sfnt_tables(data)
    name_blob = tables.get("name", b"")
    existing = _names(name_blob)

    # name id 映射
    id_map = {
        "copyright": 0,
        "family": 1,
        "subfamily": 2,
        "full": 4,
        "version": 5,
        "ps": 6,
        "trademark": 7,
        "manufacturer": 8,
        "designer": 9,
        "description": 10,
        "license": 13,
    }
    # 合并: 保留原有 id,覆盖 updates
    names_map = dict(existing)
    for key, nid in id_map.items():
        if key in updates and updates[key] is not None:
            names_map[nid] = str(updates[key])
    # 同时写 Typographic Family/Subfamily,避免读回仍命中 16/17 旧值
    if "family" in updates and updates["family"] is not None:
        names_map[16] = str(updates["family"])
    if "subfamily" in updates and updates["subfamily"] is not None:
        names_map[17] = str(updates["subfamily"])

    new_name = _build_name_table(names_map)
    data2 = _replace_sfnt_table(data, "name", new_name)

    if "weight" in updates and updates["weight"] is not None:
        tables2 = _sfnt_tables(data2)
        os2 = bytearray(tables2.get("OS/2", b""))
        if len(os2) >= 6:
            w = int(updates["weight"])
            os2[4:6] = struct.pack(">H", max(1, min(1000, w)))
            data2 = _replace_sfnt_table(data2, "OS/2", bytes(os2))

    import os
    import stat

    # 尽量解除只读属性，然后直接写入原文件
    try:
        if os.path.isfile(path):
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
    except Exception:
        pass

    # 直接覆盖原字体文件
    with open(path, "r+b") as f:
        f.seek(0)
        f.write(data2)
        f.truncate()
        f.flush()
    return path



def main():
    import tkinter as tk
    import tkinter.font as tkfont
    import tkinter.ttk as ttk
    from tkinter import filedialog
    import os

    from laotaoui import (
        AlphaBlend, BDCOLOR, BindTipWindow, DAlphaButton, DButton, DCombobutton, DEntry,
        DScrollbar, DSpinbox, GREENLIGHT, GetWorkArea, HIGHLIGHT, IsDarkMode,
        LoadFont, MessageBoxModern, SECONDARYTEXTFG, SetBorder, SetDPI,
        SetDarkTitleBar, SetExpandedTreeviewRowColor, TEXTBG, TEXTFG, WIDGETBG, WINDOWBG, libresource,
    )
    from PIL import Image, ImageDraw, ImageFont, ImageTk

    SetDPI()
    ink = (241, 241, 241, 255) if IsDarkMode() else (20, 20, 20, 255)
    code_color = "#5FD0D8" if IsDarkMode() else "#0B6A72"
    cell_bg = TEXTBG
    head_bg = AlphaBlend(HIGHLIGHT, WINDOWBG, 0.10)
    select_bg = AlphaBlend(HIGHLIGHT, TEXTBG, 0.28)
    CELL_MIN, CELL_MAX = 48, 320  # 缩放按 10% 步进

    # ---------- ttk.Treeview 主题样式（对齐 MCLangTool / laotaoui 配色） ----------
    def setup_treeview_style():
        """与 homeworktool 高级设置 Adv.Treeview 一致."""
        style = ttk.Style()
        try:
            style.theme_use("alt")
        except Exception:
            pass
        style.configure(
            "Glyph.Treeview",
            rowheight=28,
            fieldbackground=WINDOWBG,
            background=WINDOWBG,
            foreground=TEXTFG,
            borderwidth=0,
            highlightthickness=0,
        )
        style.configure(
            "Glyph.Treeview.Heading",
            background=WINDOWBG,
            foreground=TEXTFG,
            borderwidth=0,
            highlightthickness=0,
        )
        style.map(
            "Glyph.Treeview.Heading",
            background=[("active", WIDGETBG), ("pressed", WINDOWBG)],
            foreground=[("active", TEXTFG), ("pressed", TEXTFG)],
        )
        style.map(
            "Glyph.Treeview",
            background=[("selected", AlphaBlend(WINDOWBG, HIGHLIGHT, 0.5))],
            foreground=[("selected", TEXTFG)],
        )
        # 信息页同款
        style.configure(
            "Info.Treeview",
            rowheight=28,
            fieldbackground=WINDOWBG,
            background=WINDOWBG,
            foreground=TEXTFG,
            borderwidth=0,
            highlightthickness=0,
        )
        style.configure(
            "Info.Treeview.Heading",
            background=WINDOWBG,
            foreground=TEXTFG,
            borderwidth=0,
            highlightthickness=0,
        )
        style.map(
            "Info.Treeview.Heading",
            background=[("active", WIDGETBG), ("pressed", WINDOWBG)],
            foreground=[("active", TEXTFG), ("pressed", TEXTFG)],
        )
        style.map(
            "Info.Treeview",
            background=[("selected", AlphaBlend(WINDOWBG, HIGHLIGHT, 0.5))],
            foreground=[("selected", TEXTFG)],
        )

    def center_window(win, w=None, h=None, parent=None):
        """把窗口居中到父窗口或屏幕工作区。"""
        win.update_idletasks()
        if w is None:
            w = win.winfo_reqwidth()
        if h is None:
            h = win.winfo_reqheight()
        if parent is not None:
            try:
                px = parent.winfo_rootx()
                py = parent.winfo_rooty()
                pw = max(parent.winfo_width(), 1)
                ph = max(parent.winfo_height(), 1)
                x = px + (pw - w) // 2
                y = py + (ph - h) // 2
            except Exception:
                area = GetWorkArea()
                x = area[0] + (area[2] - w) // 2
                y = area[1] + (area[3] - h) // 2
        else:
            area = GetWorkArea()
            x = area[0] + (area[2] - w) // 2
            y = area[1] + (area[3] - h) // 2
        # 防止跑出屏幕
        area = GetWorkArea()
        x = max(area[0], min(x, area[0] + area[2] - w))
        y = max(area[1], min(y, area[1] + area[3] - h))
        win.geometry(f"{w}x{h}+{x}+{y}")

    # 窗口顺序: 实例化 → geometry → 内部控件&其它 → 图标 → 展示
    root = tk.Tk()
    root.withdraw()
    root.title(APP_NAME)
    area = GetWorkArea()
    width, height = min(1280, area[2] - 40), min(820, area[3] - 60)
    root.minsize(860, 560)
    root.configure(bg=WINDOWBG, bd=0, highlightthickness=0)
    root.geometry(f"{width}x{height}")
    SetDarkTitleBar(root)
    setup_treeview_style()  # 必须在 Tk() 之后

    # 符号字体 — 必须在 Tk() 之后 (与 homeworktool / MCLangTool 一致)
    LoadFont(f'{libresource}/WS_Segoe_MDL2_Assets-Regular.ttf')
    icon_font = tkfont.Font(family='WS_Segoe_MDL2_Assets', size=12)

    # state / 控件在下方创建; 图标与 deiconify 在 mainloop 前

    state = {
        "doc": None,
        "view": [],
        "filter": ("all",),
        "selected": None,
        "cell": 112,
        "mode": "grid",
        "show_code": True,
        "show_name": True,
        "cache": {},
        "pil": {},
        "photos": [],
        "_redrawing": False,
        "_layouting": False,
        "_search_after": None,
        "_scroll_after": None,
        "_loading": False,
        "_detail_win": None,   # 当前打开的小预览窗
        "_precache_after": None,
        "cached_px": None,     # 已全量缓存的像素尺寸
    }

    def tell(title, bold, text, icon="info"):
        try:
            MessageBoxModern(parent=root, title=title, text_blod=bold, text=text, icon=icon, title_icon="icon")
        except Exception:
            tk.messagebox.showinfo(title, bold + "\n" + text)

    def pil_font(px):
        """只用内存中的 font_bytes 加载,绝不让 FreeType 打开磁盘路径."""
        path = (state["doc"] or {}).get("path") or ""
        key = (path, px)
        if key not in state["pil"]:
            data = state.get("font_bytes")
            if not data:
                with open(path, "rb") as f:
                    data = f.read()
                state["font_bytes"] = data
            state["pil"][key] = ImageFont.truetype(io.BytesIO(data), px)
        return state["pil"][key]

    def grid_px():
        """当前网格模式下字形渲染像素大小 (与 draw_cell 一致)."""
        if state["mode"] == "list":
            return 18
        ch = int(state["cell"] * 0.86)
        head_h = 22
        return max(18, ch - head_h - 8)

    def raster(glyph, px):
        """返回 PIL Image;全量缓存,一个都不丢."""
        codes = glyph["unicodes"]
        if not codes:
            return None
        key = (state["doc"]["path"], glyph["index"], px, ink[0])
        if key in state["cache"]:
            return state["cache"][key]
        try:
            font = pil_font(px)
            ch = chr(codes[0])
            bbox = font.getbbox(ch)
            if not bbox or bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
                state["cache"][key] = None
                return None
            w = bbox[2] - bbox[0] + 2
            h = bbox[3] - bbox[1] + 2
            image = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
            ImageDraw.Draw(image).text((1 - bbox[0], 1 - bbox[1]), ch, font=font, fill=ink)
            state["cache"][key] = image
            return image
        except Exception:
            state["cache"][key] = None
            return None

    def photo_of(glyph, px):
        """返回 PhotoImage,同样全量缓存."""
        if not state["doc"]:
            return None
        key = (state["doc"]["path"], glyph["index"], px, ink[0], "photo")
        if key in state["cache"]:
            return state["cache"][key]
        image = raster(glyph, px)
        if image is None:
            state["cache"][key] = None
            return None
        try:
            photo = ImageTk.PhotoImage(image)
            state["cache"][key] = photo
            return photo
        except Exception:
            state["cache"][key] = None
            return None

    CACHE_SOFT = 6000   # 超过此数只优先缓存当前区
    CACHE_HARD = 8000   # 缓存条目上限

    def _cache_entry_count():
        # cache 里 raster 与 photo 各一,按 key 数 /2 估字形数
        return max(0, len(state["cache"]) // 2)

    def _trim_cache(keep_glyphs=None, px=None):
        """缓存超过 CACHE_HARD 时剔除不在 keep 集合内的项."""
        if _cache_entry_count() <= CACHE_HARD:
            return
        keep = set()
        if keep_glyphs and px is not None:
            for g in keep_glyphs:
                keep.add(("r", g["index"], px))
                keep.add(("p", g["index"], px))
        # 先删非 keep
        for key in list(state["cache"].keys()):
            if key not in keep:
                try:
                    del state["cache"][key]
                except Exception:
                    pass
                if _cache_entry_count() <= CACHE_HARD:
                    return
        # 仍超则继续删 keep 以外已空,再 FIFO 砍
        while _cache_entry_count() > CACHE_HARD and state["cache"]:
            try:
                state["cache"].pop(next(iter(state["cache"])))
            except Exception:
                break

    def precache_all(glyphs=None, px=None, done=None):
        """
        预缓存策略:
        - 字体总字形 <= 6000: 尽量缓存全部 (上限 8000)
        - 字体总字形 > 6000: 只优先缓存当前选中区/当前 view
        - 任何时候缓存字形数不超过 8000
        """
        if not state["doc"]:
            return
        doc_glyphs = state["doc"]["glyphs"]
        total_font = len(doc_glyphs)
        if px is None:
            px = grid_px()

        # 选源列表
        if glyphs is not None:
            source = list(glyphs)
        elif total_font > CACHE_SOFT:
            # 大字体:只缓存当前视图区
            source = list(state["view"] or [])
            if not source:
                source = list(doc_glyphs[:CACHE_HARD])
        else:
            source = list(doc_glyphs)

        # 硬上限
        if len(source) > CACHE_HARD:
            source = source[:CACHE_HARD]

        # 取消上一次未完成的预缓存
        if state.get("_precache_after"):
            try:
                root.after_cancel(state["_precache_after"])
            except Exception:
                pass
            state["_precache_after"] = None

        todo = list(source)
        total = len(todo)
        if total == 0:
            if done:
                done()
            return
        idx = [0]
        BATCH = 40

        def step():
            if not state["doc"]:
                return
            end = min(idx[0] + BATCH, total)
            for i in range(idx[0], end):
                g = todo[i]
                raster(g, px)
                photo_of(g, px)
            idx[0] = end
            if end < total:
                tip = "当前区" if total_font > CACHE_SOFT else ""
                status_mid.config(text=f"缓存{tip}字形 {end}/{total}")
                state["_precache_after"] = root.after(1, step)
            else:
                state["_precache_after"] = None
                _trim_cache(todo, px)
                update_status_mid()
                if done:
                    done()
                schedule_redraw()

        state["_precache_after"] = root.after(1, step)

    # ----- 菜单 -----
    # ========== 顶栏 (仿 MCLangTool): y=20 导航; y=70 操作; 无文档蓝条 ==========
    # 不要默认 tk.Menu; 不要 docbar
    NAV_H = 70    # 导航行 (控件 y=20)
    TOOL_H = 50   # 操作行 (绝对 y=70)
    TOP_CHROME = NAV_H + TOOL_H

    nav_bar = tk.Frame(root, bg=WINDOWBG, bd=0, highlightthickness=0)
    tool_bar = tk.Frame(root, bg=WINDOWBG, bd=0, highlightthickness=0)

    def icon_button(parent, glyph, command, tip):
        """MCLangTool 同款: DAlphaButton + 符号字体,不使用汉字兜底."""
        btn = DAlphaButton(
            parent,
            text=glyph,
            command=command,
            bg=WINDOWBG,
            font=icon_font,
            takefocus=0,
        )
        BindTipWindow(btn, text=tip)
        return btn

    def nav_back():
        if state["nav_index"] <= 0:
            return
        state["_nav_lock"] = True
        try:
            state["nav_index"] -= 1
            g = state["nav_history"][state["nav_index"]]
            if state["doc"] and g in state["doc"]["glyphs"]:
                select_glyph(g, reveal=True)
        finally:
            state["_nav_lock"] = False

    def nav_forward():
        if state["nav_index"] < 0 or state["nav_index"] >= len(state["nav_history"]) - 1:
            return
        state["_nav_lock"] = True
        try:
            state["nav_index"] += 1
            g = state["nav_history"][state["nav_index"]]
            if state["doc"] and g in state["doc"]["glyphs"]:
                select_glyph(g, reveal=True)
        finally:
            state["_nav_lock"] = False

    def push_nav(glyph):
        if state.get("_nav_lock") or not glyph:
            return
        hist = state["nav_history"]
        idx = state["nav_index"]
        if idx >= 0 and idx < len(hist) and hist[idx] is glyph:
            return
        if idx < len(hist) - 1:
            state["nav_history"] = hist[: idx + 1]
        state["nav_history"].append(glyph)
        if len(state["nav_history"]) > 80:
            state["nav_history"] = state["nav_history"][-80:]
        state["nav_index"] = len(state["nav_history"]) - 1

    def push_search_history(text):
        """历史只保留字码点 ($XXXX),不记字形名."""
        text = (text or "").strip()
        if not text:
            return
        # 统一成 $HEX
        raw = text[1:] if text.startswith("$") else text
        try:
            cp = int(raw, 16)
            if cp < 0 or cp > 0x10FFFF:
                return
            text = fmt_cp(cp)
        except Exception:
            return  # 非字码点不入历史
        try:
            hist = state["search_history"]
        except Exception:
            hist = []
        if text in hist:
            hist.remove(text)
        hist.insert(0, text)
        # 去重后只留字码点
        cleaned = []
        for h in hist:
            if h not in cleaned:
                cleaned.append(h)
        state["search_history"] = cleaned[:30]
        try:
            search_combo.values = list(state["search_history"])
        except Exception:
            pass

    # y=20: 后退/前进 (间距0) | 文件框 | 搜索
    btn_back = icon_button(nav_bar, "\uE72B", nav_back, "后退")
    btn_fwd = icon_button(nav_bar, "\uE72A", nav_forward, "前进")

    # 文件路径: 只读 DEntry (不是下拉/Spin)
    file_path_entry = DEntry(nav_bar)
    file_path_entry.insert(0, "")
    file_path_entry.config(state="readonly")
    BindTipWindow(file_path_entry, "当前字体路径")

    search_var = tk.StringVar()
    try:
        search_combo = DCombobutton(nav_bar, values=[], state="normal")
        search_entry = search_combo.Entry
    except Exception:
        search_combo = DEntry(nav_bar, textvariable=search_var)
        search_entry = search_combo
    BindTipWindow(search_combo, "搜索名称或字码点")
    search = search_entry

    def get_search_text():
        try:
            return search_entry.get().strip()
        except Exception:
            return (search_var.get() or "").strip()

    def set_search_text(t):
        try:
            search_entry.delete(0, "end")
            search_entry.insert(0, t)
        except Exception:
            search_var.set(t)

    # y=70: 操作 — 相近的成组间距0,组与组间距20
    
    btn_open = icon_button(tool_bar, "\uE8E5", lambda: open_font(), "打开字体 (Ctrl+O)")
    zoom_spin = DSpinbox(
        tool_bar, int_only=True, increment=10,
        from_=CELL_MIN, to=CELL_MAX,
    )
    zoom_spin.delete(0, "end")
    zoom_spin.insert(0, "112")
    BindTipWindow(zoom_spin, "网格边长")
    btn_grid = icon_button(tool_bar, "\uE138", lambda: set_mode("grid"), "网格视图")
    btn_list = icon_button(tool_bar, "\uE7C4", lambda: set_mode("list"), "列表视图")
    btn_info = icon_button(tool_bar, "\uE946", lambda: show_info(), "字体信息")
    btn_help = icon_button(tool_bar, "\uE897", lambda: show_help(), "字码点说明 (F1)")
    btn_about = icon_button(tool_bar, "\uE9CE", lambda: show_about(), "关于")
    btn_exit = icon_button(tool_bar, "\uE711", lambda: root.destroy(), "退出")

    # ----- 左树（ttk.Treeview） / 网格 / 属性 -----
    # 间距统一 20
    MARGIN = 20
    TREE_W = 300
    PROP_W = 300
    BTN_H = 30
    BTN_W_2_4 = 80   # 2-4 字
    BTN_W_5_6 = 120  # 5-6 字
    SB_W = 20        # 滚动条宽度必须 20

    tree_scroll = DScrollbar(root, bg=WINDOWBG, width=SB_W)
    tree_scroll_x = DScrollbar(root, bg=WINDOWBG, orient="horizontal")
    tree = ttk.Treeview(
        root,
        columns=("count",),
        show="tree headings",
        selectmode="browse",
        style="Glyph.Treeview",
        yscrollcommand=tree_scroll.set,
        xscrollcommand=tree_scroll_x.set,
    )
    tree.heading("#0", text="分类", anchor="center")
    tree.heading("count", text="数量", anchor="center")
    tree.column("#0", width=160, minwidth=120, anchor="w", stretch=True)
    tree.column("count", width=70, minwidth=50, anchor="e", stretch=False)
    tree_scroll.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)
    SetBorder(tree)

    grid_scroll = DScrollbar(root, bg=WINDOWBG, width=SB_W)
    canvas = tk.Canvas(root, bg=cell_bg, bd=0, highlightthickness=0, takefocus=True)
    grid_scroll.config(command=canvas.yview)
    SetBorder(canvas)

    props = tk.Frame(root, bg=WINDOWBG, bd=0, highlightthickness=0)
    SetBorder(props, mode="place")

    # 右侧：统一「控件高 30 + 间距 20」→ 行步进 50
    # 边距 20
    _px = MARGIN // 2          # 左右内边距约 10，与面板边框配合
    _row_h = BTN_H             # 30
    _row_gap = MARGIN          # 20
    _step = _row_h + _row_gap  # 50
    _y0 = MARGIN               # 标题从 20 开始

    prop_title = tk.Label(props, text="字形属性", bg=WINDOWBG, fg=TEXTFG, anchor="w")
    prop_title.place(x=_px, y=_y0, width=PROP_W - MARGIN, height=_row_h)

    fields = {}

    def add_field(row, label):
        y = _y0 + _step + row * _step   # 标题后再空一行间距，然后每行 +50
        # 标签与输入框间距加大 (标签宽 80, 输入从 100 起)
        tk.Label(props, text=label, bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="w").place(
            x=_px, y=y, width=80, height=_row_h
        )
        entry = DEntry(props)
        entry.place(x=100, y=y, width=PROP_W - 100 - _px, height=_row_h)
        entry.insert(0, "")
        entry.config(state="readonly")
        fields[label] = entry
        return entry

    add_field(0, "名称:")
    code_entry = add_field(1, "字码点:")
    code_entry.config(fg=code_color, font=("Consolas", 12, "bold"))
    # 双击字码点框也复制
    def _copy_code_entry(_e=None):
        t = fields["字码点:"].get()
        if t:
            copy_text(t)
    code_entry.bind("<Double-Button-1>", _copy_code_entry)
    add_field(2, "OT类别:")
    add_field(3, "左线:")
    add_field(4, "右线:")
    add_field(5, "字宽:")

    # 6 个字段后：区段说明
    _after_fields = _y0 + _step + 6 * _step
    aside = tk.Label(props, text="", bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="w")
    aside.place(x=100, y=_after_fields - 18, width=PROP_W - 100 - _px, height=16)
    block_label = tk.Label(props, text="", bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="w", justify="left")
    block_label.place(x=_px, y=_after_fields, width=PROP_W - MARGIN, height=36)

    # 轮廓标题 + 详细查看按钮（同一行，高 30）
    _preview_head_y = _after_fields + 36 + _row_gap
    preview_title = tk.Label(props, text="轮廓", bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="w")
    preview_title.place(x=_px, y=_preview_head_y, width=100, height=_row_h)
    # 「详细查看」4 字 → 宽 80，高 30
    btn_detail = DButton(props, text="详细查看", command=lambda: open_detail())
    btn_detail.place(x=PROP_W - _px - BTN_W_2_4, y=_preview_head_y, width=BTN_W_2_4, height=_row_h)

    # 预览图：再空 20
    _preview_y = _preview_head_y + _row_h + _row_gap
    preview = tk.Label(props, bg=cell_bg, bd=0)
    preview.place(x=_px, y=_preview_y, width=PROP_W - MARGIN, height=150)
    SetBorder(preview, mode="place")

    status = tk.Label(root, text="未打开字体", bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="w")
    status_mid = tk.Label(root, text="", bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="center")
    status_right = tk.Label(root, text="只读", bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="e")

    def set_readonly(entry, value, color=None):
        entry.config(state="normal")
        entry.delete(0, "end")
        entry.insert(0, value)
        if color:
            entry.config(fg=color)
        entry.config(state="readonly")

    def current():
        return state["selected"]

    def fill_props():
        glyph = current()
        doc = state["doc"]
        if not glyph or not doc:
            prop_title.config(text="字形属性")
            for entry in fields.values():
                set_readonly(entry, "")
            aside.config(text="")
            block_label.config(text="")
            preview.config(image="")
            preview.image = None
            return
        prop_title.config(text=f"字形属性 (#{glyph['index']} {glyph['name']})")
        set_readonly(fields["名称:"], glyph["name"])
        codes = fmt_cps(glyph["unicodes"])
        set_readonly(fields["字码点:"], codes, code_color)
        if glyph["unicodes"]:
            set_readonly(fields["OT类别:"], "自动")
            aside.config(text="未分配")
        else:
            set_readonly(fields["OT类别:"], "")
            aside.config(text="")
        set_readonly(fields["左线:"], str(int(glyph["lsb"])))
        set_readonly(fields["右线:"], str(int(glyph["rsb"])))
        set_readonly(fields["字宽:"], str(int(glyph["advance"])))
        if glyph["unicodes"]:
            block = find_block(glyph["unicodes"][0])
            if block:
                block_label.config(text=f"{block[2]}  ({block[3]})\nU+{block[0]:04X}–U+{block[1]:04X}")
            else:
                block_label.config(text="未归类码位")
        else:
            block_label.config(text="")
        image = raster(glyph, 96)
        if image is None:
            preview.config(image="")
            preview.image = None
        else:
            photo = ImageTk.PhotoImage(image)
            preview.config(image=photo)
            preview.image = photo
        codes_text = fmt_cps(glyph["unicodes"])
        status.config(text=("1 个字形被选择" + (f"  ·  {codes_text}" if codes_text else "")))

    def match_glyph(glyph, query):
        """名称与字码点同时匹配.字码点可写 $E881 或 E881."""
        kind = parse_query(query)
        if kind is None:
            return True
        name_l = (glyph["name"] or "").lower()
        codes_disp = fmt_cps(glyph["unicodes"]).lower()  # $e881,$e8c4
        codes_bare = codes_disp.replace("$", "")

        if kind[0] == "cp":
            cp = kind[1]
            hex_body = kind[2] if len(kind) > 2 else format(cp, "x")
            if cp in glyph["unicodes"]:
                return True
            # 部分匹配:输入 E88 能扫到 $E881
            if hex_body and (hex_body in codes_bare or hex_body in codes_disp):
                return True
            # 同时允许名称碰巧包含该串
            if hex_body in name_l or query.strip().lower() in name_l:
                return True
            return False
        if kind[0] == "index":
            if glyph["index"] == kind[1]:
                return True
            # 数字也可能是名称/码点片段
            needle = str(kind[1])
            return needle in name_l or needle in codes_bare or needle in codes_disp
        needle = kind[1]
        if needle in name_l:
            return True
        if needle in codes_disp or needle in codes_bare:
            return True
        # 去掉 $ 后再比一次
        if needle.lstrip("$").lower() in codes_bare:
            return True
        return False

    def rebuild_view(keep=True):
        doc = state["doc"]
        if not doc:
            state["view"] = []
            return
        kind, value = state["filter"][0], state["filter"][1] if len(state["filter"]) > 1 else None
        view = doc["glyphs"]
        if kind == "mapped":
            view = [g for g in view if g["unicodes"]]
        elif kind == "unmapped":
            view = [g for g in view if not g["unicodes"]]
        elif kind == "block":
            picked = []
            for glyph in view:
                for cp in glyph["unicodes"]:
                    block = find_block(cp)
                    start = block[0] if block else -1
                    if start == value:
                        picked.append(glyph)
                        break
            view = picked
        query = get_search_text()
        if query:
            view = [g for g in view if match_glyph(g, query)]
        state["view"] = view
        # 仅当当前选中已不在视图里时清空;绝不自动挑第一个
        if current() is not None and current() not in view:
            state["selected"] = None
        schedule_redraw()
        fill_props()
        update_status_mid()
        # 预缓存:大字体只缓存当前 view
        px = grid_px()
        state["cached_px"] = px
        if state["doc"]:
            precache_all(None, px)

    def update_status_mid():
        doc = state["doc"]
        if not doc:
            status_mid.config(text="")
            return
        kind = state["filter"][0]
        if kind == "block":
            start = state["filter"][1]
            block = next((b for b in doc["blocks"] if b["start"] == start), None)
            name = block["name"] if block else "区段"
            status_mid.config(text=f"{name}  ·  {len(state['view'])} 个字形")
        elif kind == "unmapped":
            status_mid.config(text=f"未编码  ·  {len(state['view'])} 个字形")
        else:
            status_mid.config(text=f"显示 {len(state['view'])} 个字形")
        extra = f"已忽略 {doc['skipped']} 个空字形" if doc["skipped"] else ""
        right = f"{len(doc['glyphs'])} 个字形"
        if extra:
            right += "  ·  " + extra
        if doc.get("is_cff"):
            right += "  ·  CFF"
        status_right.config(text=right )

    def rebuild_tree():
        for item in tree.get_children():
            tree.delete(item)
        doc = state["doc"]
        if not doc:
            return
        tree.insert("", "end", iid="all", text="字形", values=(str(len(doc["glyphs"])),), open=False)
        tree.insert("", "end", iid="mapped", text="字符", values=(str(doc["char_count"]),))
        if doc["unmapped"]:
            tree.insert("", "end", iid="unmapped", text="未编码", values=(str(doc["unmapped"]),))
        tree.insert("", "end", iid="unicode", text="Unicode", values=(str(doc["char_count"]),), open=True)
        for block in doc["blocks"]:
            iid = f"block:{block['start']}"
            tree.insert("unicode", "end", iid=iid, text=f"{block['name']} ({block['en']})",
                        values=(f"{block['chars']}/{block['total']}",))
        select_tree_node()

    def select_tree_node():
        kind = state["filter"][0]
        iid = "all" if kind == "all" else "mapped" if kind == "mapped" else "unmapped" if kind == "unmapped" else f"block:{state['filter'][1]}"
        if tree.exists(iid):
            tree.selection_set(iid)
            tree.focus(iid)
            tree.see(iid)

    def on_tree_click(_event=None):
        root.after_idle(apply_tree_selection)

    def apply_tree_selection():
        picked = tree.selection()
        if not picked:
            return
        iid = picked[0]
        if iid == "unicode":
            return
        old_filter = state["filter"]
        if iid == "all":
            new_filter = ("all",)
        elif iid == "mapped":
            new_filter = ("mapped",)
        elif iid == "unmapped":
            new_filter = ("unmapped",)
        elif iid.startswith("block:"):
            new_filter = ("block", int(iid.split(":", 1)[1]))
        else:
            return
        # 同一项重复点不重置滚动
        if new_filter == old_filter:
            return
        state["filter"] = new_filter
        rebuild_view(keep=False)
        canvas.yview_moveto(0)

    tree.bind("<ButtonRelease-1>", on_tree_click)
    # 不用 <<TreeviewSelect>> 避免重复触发导致滚动跳动
    # tree.bind("<<TreeviewSelect>>", on_tree_click)

    def columns():
        width = max(1, canvas.winfo_width())
        if state["mode"] == "list":
            return 1
        return max(1, width // state["cell"])

    def cell_size():
        if state["mode"] == "list":
            return max(1, canvas.winfo_width()), 28
        return state["cell"], int(state["cell"] * 0.86)

    def schedule_redraw():
        if state["_redrawing"]:
            return
        if state.get("_scroll_after"):
            try:
                root.after_cancel(state["_scroll_after"])
            except Exception:
                pass
        state["_scroll_after"] = root.after(16, _do_redraw)

    def _do_redraw():
        state["_scroll_after"] = None
        redraw()

    def _safe_scroll_set(first, last):
        grid_scroll.set(first, last)
        schedule_redraw()

    canvas.configure(yscrollcommand=_safe_scroll_set)

    def redraw(_event=None):
        if state["_redrawing"] or state["_loading"]:
            return
        state["_redrawing"] = True
        try:
            canvas.delete("g")
            state["photos"] = []
            view = state["view"]
            if not view:
                canvas.configure(scrollregion=(0, 0, 1, 1))
                if state["doc"]:
                    canvas.create_text(20, 24, anchor="w", text="这个范围里没有字形.", fill=SECONDARYTEXTFG, tags="g")
                else:
                    canvas.create_text(20, 24, anchor="w", text="打开一个字体,查看字形,私用区和$码位.", fill=SECONDARYTEXTFG, tags="g")
                return
            cw, ch = cell_size()
            cols = columns()
            rows = math.ceil(len(view) / cols) if cols else 0
            total_h = max(1, rows * ch)
            total_w = cols * cw if state["mode"] == "grid" else max(canvas.winfo_width(), 1)
            canvas.configure(scrollregion=(0, 0, total_w, total_h))
            y0 = canvas.canvasy(0)
            height = max(canvas.winfo_height(), 1)
            # 多预画几行,拖动滚动条时更不容易露白
            r0 = max(0, int(y0 // ch) - 3)
            r1 = min(rows, int((y0 + height) // ch) + 5)
            selected = current()
            for row in range(r0, r1):
                for col in range(cols):
                    pos = row * cols + col
                    if pos >= len(view):
                        break
                    glyph = view[pos]
                    x, y = col * cw, row * ch
                    on = selected is glyph
                    if state["mode"] == "list":
                        draw_row(glyph, x, y, total_w, ch, on, pos)
                    else:
                        draw_cell(glyph, x, y, cw, ch, on)
        finally:
            state["_redrawing"] = False

    def draw_cell(glyph, x, y, cw, ch, on):
        body = select_bg if on else cell_bg
        head_h = 22  # 字码点区加高
        canvas.create_rectangle(x, y, x + cw, y + ch, fill=body, outline=HIGHLIGHT if on else BDCOLOR, width=2 if on else 1, tags=("g", "hit"))
        canvas.create_rectangle(x + 1, y + 1, x + cw - 1, y + head_h, fill=head_bg if not on else AlphaBlend(HIGHLIGHT, head_bg, 0.35), outline="", tags="g")
        if state["show_name"]:
            canvas.create_text(x + 4, y + head_h // 2, anchor="w", text=glyph["name"], fill=SECONDARYTEXTFG, font=("微软雅黑", 9), tags="g")
        if state["show_code"]:
            primary = glyph["unicodes"][0] if glyph["unicodes"] else None
            label = "" if primary is None else fmt_cp(primary) + ("+" if len(glyph["unicodes"]) > 1 else "")
            if label:
                # 字码点加大;点右上角可复制 (on_click)
                canvas.create_text(x + cw - 4, y + head_h // 2, anchor="e", text=label, fill=code_color, font=("Consolas", 11, "bold"), tags=("g", "code"))
        photo = photo_of(glyph, max(18, ch - head_h - 8))
        if photo is not None:
            state["photos"].append(photo)
            canvas.create_image(x + cw / 2, y + head_h + (ch - head_h) / 2, image=photo, tags="g")
        canvas.create_rectangle(x, y, x + cw, y + ch, outline="", tags=("g", f"id:{glyph['index']}"))

    def draw_row(glyph, x, y, width, ch, on, pos):
        bg = select_bg if on else (TEXTBG if pos % 2 else WINDOWBG)
        canvas.create_rectangle(x, y, x + width, y + ch, fill=bg, outline="", tags=("g", "hit", f"id:{glyph['index']}"))
        codes = fmt_cps(glyph["unicodes"])
        canvas.create_text(x + 8, y + ch / 2, anchor="w", text=str(glyph["index"]), fill=TEXTFG, font=("Consolas", 10), tags="g")
        canvas.create_text(x + 56, y + ch / 2, anchor="w", text=glyph["name"], fill=TEXTFG, font=("微软雅黑", 10), tags="g")
        if codes:
            canvas.create_text(x + 240, y + ch / 2, anchor="w", text=codes, fill=code_color, font=("Consolas", 11, "bold"), tags="g")
        canvas.create_text(x + 430, y + ch / 2, anchor="w", text=str(glyph["advance"]), fill=SECONDARYTEXTFG, font=("Consolas", 10), tags="g")

    def hit_glyph(event):
        if not state["view"]:
            return None
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        cw, ch = cell_size()
        cols = columns()
        col = int(x // cw) if state["mode"] == "grid" else 0
        row = int(y // ch)
        pos = row * cols + col
        if 0 <= pos < len(state["view"]):
            return state["view"][pos]
        return None

    def select_glyph(glyph, reveal=False):
        state["selected"] = glyph
        push_nav(glyph)
        schedule_redraw()
        fill_props()
        if reveal and glyph in state["view"]:
            pos = state["view"].index(glyph)
            cw, ch = cell_size()
            cols = columns()
            row = pos // cols
            top = canvas.canvasy(0)
            bottom = top + canvas.winfo_height()
            y = row * ch
            if y < top or y + ch > bottom:
                total = float(canvas.cget("scrollregion").split()[3] or 1)
                canvas.yview_moveto(max(0, y - 20) / total)

    def on_click(event):
        glyph = hit_glyph(event)
        if not glyph:
            canvas.focus_set()
            return
        # 点在格子顶部字码点区域 (右上)->直接复制字码点
        if state["mode"] == "grid" and state["show_code"] and glyph.get("unicodes"):
            cw, ch = cell_size()
            lx = canvas.canvasx(event.x)
            ly = canvas.canvasy(event.y)
            cols = columns()
            col = int(lx // cw) if cols else 0
            row = int(ly // ch)
            cell_x = col * cw
            cell_y = row * ch
            # 顶部 22px 且偏右半边视为点字码点 → 只复制第一个字码点
            if ly - cell_y <= 22 and lx - cell_x >= cw * 0.4:
                copy_text(fmt_cp(glyph["unicodes"][0]))
                select_glyph(glyph)
                canvas.focus_set()
                return
        select_glyph(glyph)
        canvas.focus_set()

    def on_double(event):
        glyph = hit_glyph(event)
        if glyph:
            select_glyph(glyph)
            open_detail()

    def on_menu(event):
        glyph = hit_glyph(event)
        if not glyph:
            return
        select_glyph(glyph)
        menu = tk.Menu(root, tearoff=0)
        codes = fmt_cps(glyph["unicodes"])
        if codes:
            menu.add_command(label="复制字码点", command=lambda: copy_text(codes))
        menu.add_command(label="复制名称", command=lambda: copy_text(glyph["name"]))
        if glyph["unicodes"]:
            menu.add_command(label="复制字符", command=lambda: copy_text("".join(chr(cp) for cp in glyph["unicodes"])))
        menu.add_command(label="详细查看", command=open_detail)
        menu.tk_popup(event.x_root, event.y_root)

    def copy_text(text):
        if not text:
            return
        root.clipboard_clear()
        root.clipboard_append(text)
        status.config(text=f"已复制: {text}")

    def on_wheel(event):
        # Ctrl + 滚轮 → 缩放；普通滚轮 → 滚动
        if event.state & 0x4:  # Control
            zoom(1 if event.delta > 0 else -1)
            return "break"
        canvas.yview_scroll(int(-event.delta / 120), "units")
        return "break"

    canvas.bind("<Button-1>", on_click)
    canvas.bind("<Double-Button-1>", on_double)
    canvas.bind("<Button-3>", on_menu)
    canvas.bind("<MouseWheel>", on_wheel)
    canvas.bind("<Control-MouseWheel>", on_wheel)
    root.bind("<Control-MouseWheel>", on_wheel)
    canvas.bind("<Configure>", lambda e: schedule_redraw())
    canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    def move(delta):
        view = state["view"]
        if not view:
            return
        glyph = current()
        pos = view.index(glyph) if glyph in view else 0
        pos = max(0, min(len(view) - 1, pos + delta))
        select_glyph(view[pos], reveal=True)

    def zoom(direction):
        """每次约 10% 放大/缩小."""
        current_size = state["cell"]
        if direction > 0:
            nxt = int(round(current_size * 1.1))
            if nxt <= current_size:
                nxt = current_size + 1
        else:
            nxt = int(round(current_size / 1.1))
            if nxt >= current_size:
                nxt = current_size - 1
        nxt = max(CELL_MIN, min(CELL_MAX, nxt))
        if nxt == current_size:
            return
        state["cell"] = nxt
        zoom_spin.delete(0, "end")
        zoom_spin.insert(0, str(nxt))
        state["cached_px"] = None  # 强制按新尺寸重缓存
        schedule_redraw()
        if state["doc"]:
            state["cached_px"] = grid_px()
            precache_all(None, state["cached_px"])
        # 缩放后把当前选中项滚到中间可见
        root.after(20, _center_selected)

    def apply_cell_size(value=None, recenter=True):
        """把格子边长设为 value (px),并刷新缓存."""
        if value is None:
            try:
                value = int(str(zoom_spin.get()).strip())
            except Exception:
                return
        try:
            value = int(value)
        except Exception:
            return
        value = max(CELL_MIN, min(CELL_MAX, value))
        if value == state["cell"]:
            zoom_spin.delete(0, "end")
            zoom_spin.insert(0, str(value))
            return
        state["cell"] = value
        zoom_spin.delete(0, "end")
        zoom_spin.insert(0, str(value))
        state["cached_px"] = None
        schedule_redraw()
        if state["doc"]:
            state["cached_px"] = grid_px()
            precache_all(None, state["cached_px"])
        if recenter:
            root.after(20, _center_selected)

    def _spin_commit(event=None):
        apply_cell_size()
        return None

    zoom_spin.Entry.bind("<Return>", _spin_commit, add="+")
    zoom_spin.Entry.bind("<FocusOut>", _spin_commit, add="+")
    zoom_spin.DButton_up.bind("<ButtonRelease-1>", lambda e: root.after(1, _spin_commit), add="+")
    zoom_spin.DButton_down.bind("<ButtonRelease-1>", lambda e: root.after(1, _spin_commit), add="+")


    def _center_selected():
        glyph = current()
        view = state["view"]
        if not glyph or glyph not in view:
            return
        pos = view.index(glyph)
        cw, ch = cell_size()
        cols = columns()
        if cols < 1 or ch < 1:
            return
        row = pos // cols
        total_h = max(1.0, float(canvas.cget("scrollregion").split()[3] or 1))
        view_h = max(canvas.winfo_height(), 1)
        # 目标: 选中行出现在视口中间
        target_y = row * ch - (view_h - ch) / 2
        frac = max(0.0, min(1.0, target_y / total_h))
        canvas.yview_moveto(frac)

    def set_mode(mode):
        state["mode"] = mode
        canvas.yview_moveto(0)
        schedule_redraw()

    def on_search(*_):
        if state["_search_after"]:
            try:
                root.after_cancel(state["_search_after"])
            except Exception:
                pass
        state["_search_after"] = root.after(280, _do_search)

    def _do_search():
        state["_search_after"] = None
        query = get_search_text()
        if not query:
            search.config(bg=TEXTBG)
        else:
            hit = any(match_glyph(g, query) for g in (state["doc"]["glyphs"] if state["doc"] else []))
            search.config(bg=AlphaBlend(GREENLIGHT if hit else "#C42B1C", TEXTBG, 0.25))
            if hit:
                push_search_history(query)
        rebuild_view(keep=False)
        canvas.yview_moveto(0)

    search_var.trace_add("write", on_search)
    search_entry.bind("<KeyRelease>", lambda e: on_search())
    search_entry.bind("<Return>", lambda e: (_do_search(), push_search_history(get_search_text())))

    def jump_search(_event=None):
        if state["view"]:
            select_glyph(state["view"][0], reveal=True)
        return "break"

    search.bind("<Return>", jump_search)

    def open_font(path=None):
        if state["_loading"]:
            return
        if not path:
            path = filedialog.askopenfilename(
                parent=root,
                title="打开字体",
                filetypes=[("字体", "*.ttf *.otf *.woff *.ttc *.otc"), ("所有文件", "*.*")],
            )
        if not path:
            return

        state["_loading"] = True
        root.config(cursor="watch")
        status.config(text="正在解析字体...")
        status_mid.config(text="")
        status_right.config(text="")
        root.update_idletasks()

        def worker():
            try:
                doc = read_font(path)
            except Exception as exc:
                root.after(0, lambda: _load_failed(str(exc)))
                return
            root.after(0, lambda: _load_ok(doc))

        threading.Thread(target=worker, daemon=True).start()

    def _load_failed(msg):
        state["_loading"] = False
        root.config(cursor="")
        status.config(text="未打开字体")
        tell("错误", "字体没有载入", msg, "error")

    def _load_ok(doc):
        state["_loading"] = False
        root.config(cursor="")
        if not doc["glyphs"]:
            status.config(text="未打开字体")
            tell("信息", "这个字体里没有可预览的字形", "空字形已全部略过.", "info")
            return
        state["doc"] = doc
        state["cache"].clear()
        state["pil"].clear()
        state["cached_px"] = None
        # 整文件读入内存,后续渲染不再占磁盘句柄
        try:
            with open(doc["path"], "rb") as f:
                state["font_bytes"] = f.read()
        except Exception:
            state["font_bytes"] = None
        state["filter"] = ("all",)
        pua = next((b for b in doc["blocks"] if b["start"] == 0xE000), None)
        if pua:
            state["filter"] = ("block", 0xE000)
        title_name = doc["full"] or doc["family"] or doc["file"]
        root.title(f"{APP_NAME} - {doc['file']}")
        status.config(text=f"{doc['file']}  ·  {title_name}")
        file_path_entry.config(state="normal")
        file_path_entry.delete(0, "end")
        file_path_entry.insert(0, doc.get("path") or doc.get("file") or "")
        file_path_entry.config(state="readonly")
        state["nav_history"] = []
        state["nav_index"] = -1
        rebuild_tree()
        rebuild_view(keep=False)
        hero = next((g for g in state["view"] if 0xE169 in g["unicodes"]), None)
        if hero:
            select_glyph(hero, reveal=True)

    def show_info():
        doc = state["doc"]
        if not doc:
            return

        # (iid, 说明, 初值, 可编辑, doc键)
        rows = [
            ("file", "文件", doc.get("file") or "", False, None),
            ("path", "路径", doc.get("path") or "", False, None),
            ("full", "全名/标题", doc.get("full") or "", True, "full"),
            ("family", "家族/说明", doc.get("family") or "", True, "family"),
            ("subfamily", "子族", doc.get("subfamily") or "", True, "subfamily"),
            ("ps", "PostScript", doc.get("ps") or "", True, "ps"),
            ("version", "版本", doc.get("version") or "", True, "version"),
            ("designer", "设计/作者", doc.get("designer") or "", True, "designer"),
            ("manufacturer", "厂商/公司", doc.get("manufacturer") or "", True, "manufacturer"),
            ("copyright", "著作权", doc.get("copyright") or "", True, "copyright"),
            ("trademark", "合法商标", doc.get("trademark") or "", True, "trademark"),
            ("description", "文件说明", doc.get("description") or "", True, "description"),
            ("license", "许可证描述", doc.get("license") or "", True, "license"),
            ("glyphs", "字形数", str(len(doc.get("glyphs") or [])), False, None),
            ("chars", "字符数", str(doc.get("char_count") or 0), False, None),
            ("unmapped", "未编码", str(doc.get("unmapped") or 0), False, None),
            ("skipped", "空字形", str(doc.get("skipped") or 0), False, None),
            ("upem", "单位/Em", str(doc.get("upem") or ""), False, None),
            ("ascdesc", "上升/下降", "%s/%s" % (doc.get("ascender", ""), doc.get("descender", "")), False, None),
            ("weight", "字重", str(doc.get("weight") if doc.get("weight") not in (None, "") else ""), True, "weight"),
            ("format", "格式", "CFF" if doc.get("is_cff") else "TrueType", False, None),
        ]
        work = {r[0]: r[2] for r in rows}
        editable = {r[0]: r[3] for r in rows}
        key_of = {r[0]: r[4] for r in rows}
        result = {"ok": False}
        editor_ref = [None]

        def close_info(ok=False):
            result["ok"] = ok
            root.attributes("-disabled", False)
            win.destroy()
            root.focus_set()

        def on_cancel(event=None):
            close_info(False)
            return "break"

        def on_ok(event=None):
            if editor_ref[0] is not None:
                _commit_editor()
            d = state["doc"]
            if not d:
                close_info(False)
                return "break"
            changed = {}
            for iid, is_edit in editable.items():
                if not is_edit:
                    continue
                k = key_of.get(iid)
                if not k:
                    continue
                new_v = (work.get(iid) or "").strip()
                old_v = d.get(k)
                if old_v is None:
                    old_v = ""
                if str(old_v) != new_v:
                    if k == "weight":
                        try:
                            changed[k] = int(new_v) if new_v else 400
                        except Exception:
                            changed[k] = new_v
                    else:
                        changed[k] = new_v
            if not changed:
                close_info(True)
                return "break"
            try:
                ans = MessageBoxModern(
                    parent=win, title="疑问", icon="question",
                    text_blod="将修改写入字体文件?",
                    text="将会写入.name表相关字段.",
                    button_mode=2,
                )
            except Exception:
                ans = True
            if not ans:
                for k, v in changed.items():
                    d[k] = v
                title_name = d.get("full") or d.get("family") or d.get("file") or ""
                root.title("%s - %s" % (APP_NAME, d.get("file", "")))
                status.config(text="%s  ·  %s" % (d.get("file", ""), title_name))
                close_info(True)
                return "break"
            font_path = d.get("path") or ""

            def release_font_handles():
                # 丢弃所有可能间接引用 FreeType face 的对象
                state["pil"].clear()
                state["cache"].clear()
                state["photos"] = []
                canvas.delete("all")
                preview.delete("all")
                import gc
                gc.collect()

            release_font_handles()
            root.update_idletasks()
            try:
                write_font_metadata(font_path, changed)
            except Exception:
                err = traceback.format_exc()
                try:
                    MessageBoxModern(
                        parent=win, title="错误", icon="error",
                        text_blod="无法写入字体文件", text=err, button_mode=1,
                    )
                except Exception:
                    tell("错误", "无法写入字体文件", err, "error")
                return "break"

            for k, v in changed.items():
                d[k] = v
            with open(font_path, "rb") as f:
                state["font_bytes"] = f.read()
            release_font_handles()
            status.config(text="已写入字体文件")
            schedule_redraw()
            close_info(True)
            return "break"

        root.attributes("-disabled", True)

        win = tk.Toplevel(root)
        win.withdraw()
        win.title("字体信息")
        win.configure(bg=WINDOWBG, bd=0, highlightthickness=0)
        win.transient(root)
        win.resizable(False, False)
        win.protocol("WM_DELETE_WINDOW", on_cancel)
        win.bind("<Escape>", on_cancel)
        SetDarkTitleBar(win)

        WIN_W, WIN_H = 720, 560
        tip_lbl = tk.Label(
            win, bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="w",
            text="双击「值」列编辑可改项;只读项不可改.确定后询问是否写入字体文件.",
        )
        tip_lbl.place(x=MARGIN, y=MARGIN, width=WIN_W - 2 * MARGIN, height=30)

        scroll_y = DScrollbar(win, bg=WINDOWBG, width=SB_W)

        info_tree = ttk.Treeview(
            win, show="headings", columns=("desc", "value"),
            selectmode="browse", style="Info.Treeview",
            yscrollcommand=scroll_y.set,
        )
        tree_x, tree_y = MARGIN, MARGIN + 40
        tree_w = WIN_W - 2 * MARGIN - SB_W
        tree_h = WIN_H - tree_y - MARGIN - BTN_H - MARGIN 
        info_tree.place(x=tree_x, y=tree_y, width=tree_w, height=tree_h)
        scroll_y.place(x=tree_x + tree_w, y=tree_y, width=SB_W, height=tree_h)
   
        scroll_y.config(command=info_tree.yview)

        SetBorder(info_tree)
        info_tree.heading("desc", text="属性", anchor="center")
        info_tree.heading("value", text="值", anchor="center")
        info_tree.column("desc", width=180, minwidth=100, anchor="w")
        info_tree.column("value", width=max(200, tree_w - 190), minwidth=200, anchor="w")

        def refresh_rows():
            for iid in info_tree.get_children():
                info_tree.delete(iid)
            for iid, desc, _val, is_edit, _k in rows:
                mark = "" if is_edit else "  [只读]"
                info_tree.insert("", "end", iid=iid, values=(desc + mark, work.get(iid, "")))
            win.after_idle(lambda: SetExpandedTreeviewRowColor(info_tree))

        refresh_rows()

        def destroy_editor():
            ed = editor_ref[0]
            editor_ref[0] = None
            if ed is None:
                return
            ed.destroy()

        def _commit_editor():
            ed = editor_ref[0]
            if ed is None:
                return
            iid = getattr(ed, "row_id", None)
            new_value = ed.get()
            destroy_editor()
            if not iid:
                return
            work[iid] = new_value
            is_edit = editable.get(iid, False)
            desc = next((r[1] for r in rows if r[0] == iid), iid)
            mark = "" if is_edit else "  [只读]"
            info_tree.item(iid, values=(desc + mark, new_value))
            info_tree.focus_set()

        def on_double_click(event=None):
            if editor_ref[0] is not None:
                _commit_editor()
            sel = info_tree.selection()
            if not sel:
                return "break"
            iid = sel[0]
            if not editable.get(iid, False):
                return "break"
            bbox = info_tree.bbox(iid, "value")
            if not bbox:
                return "break"
            x, y, w, h = bbox
            editor = DEntry(info_tree)
            editor.insert(0, work.get(iid, ""))
            editor.row_id = iid
            editor_ref[0] = editor

            def apply_edit(event=None):
                fw = win.focus_get()
                if fw is not None:
                    wdg = fw
                    while wdg is not None:
                        if wdg is editor:
                            return
                        wdg = getattr(wdg, "master", None)
                _commit_editor()

            def cancel_edit(event=None):
                destroy_editor()
                info_tree.focus_set()
                return "break"

            editor.place(x=x, y=y, width=w, height=h)
            editor.bind("<Return>", lambda e: (_commit_editor(), "break")[1])
            editor.bind("<Escape>", cancel_edit)
            editor.bind("<FocusOut>", apply_edit)
            editor.focus_set()
            editor.select_range(0, "end")
            return "break"

        info_tree.bind("<Double-Button-1>", on_double_click)
        info_tree.bind("<Return>", on_double_click)
        info_tree.bind("<F2>", on_double_click)

        ok_btn = DButton(win, text="确定", command=on_ok, default="active")
        cancel_btn = DButton(win, text="取消", command=on_cancel)
        ok_btn.place(x=WIN_W - MARGIN - BTN_W_2_4 * 2 - 20, y=WIN_H - MARGIN - BTN_H, width=BTN_W_2_4, height=BTN_H)
        cancel_btn.place(x=WIN_W - MARGIN - BTN_W_2_4, y=WIN_H - MARGIN - BTN_H, width=BTN_W_2_4, height=BTN_H)

        center_window(win, WIN_W, WIN_H, parent=root)
        try:
            win.wm_iconbitmap(f"{libresource}icon.ico")
        except Exception:
            pass
        win.update_idletasks()
        win.deiconify()
        ok_btn.focus_set()
        win.wait_window()
        return result["ok"]


        return result["ok"]


    def show_help():
        tell(
            "信息",
            "字码点写成 $ 加十六进制",
            "例如 $E169,$E8C4.同一个字形占多个码位时写成 $E169,$E8C4.\n"
            "私用区是 Unicode 留给私人约定的区段,图标字体几乎都放在这里.\n"
            "BMP 私用区 U+E000-U+F8FF,共 6400 个码位.左侧点 [私用区] 只看这些字形.\n"
            "空字形和没有字形的区段会自动略过.双击格子打开小预览窗 (Esc 或双击关闭).\n"
            "Ctrl+滚轮 或 +/- 缩放.查找框接受 $E169 或字形名.",
            "info",
        )

    def show_about(event=None):
        """关于页,风格对齐 homeworktool."""
        def set_label_font(label, add_size=3, bold=False):
            old_font = tkfont.Font(font=label.cget("font"))
            new_font = old_font.copy()
            new_font.configure(weight="bold" if bold else "normal", size=old_font.cget("size") + add_size)
            label.configure(font=new_font)

        def close_about(event=None):
            
            root.attributes("-disabled", False)
            about_win.destroy()
            root.focus_set()
          

       
        root.attributes("-disabled", True)


        about_win = tk.Toplevel(root)
        about_win.withdraw()
        about_win.title("关于")
        about_win.resizable(False, False)
        about_win.configure(bg=WINDOWBG)
        about_win.protocol("WM_DELETE_WINDOW", close_about)
        about_win.bind("<Escape>", close_about)
        about_win.wm_transient(root)
        SetDarkTitleBar(about_win)

        W, H = 800, 600
        about_win.geometry(f"{W}x{H}")

        label_title = tk.Label(about_win, bg=WINDOWBG, text=APP_NAME, anchor="center", fg=TEXTFG)
        set_label_font(label_title, add_size=16, bold=True)
        label_title.place(x=0, y=20, width=W, height=60)

        tk.Label(about_win, bg=TEXTBG, fg=TEXTFG).place(x=20, y=100, width=W - 40, height=2)

        tk.Label(about_win, bg=WINDOWBG, fg=TEXTFG, text="软件概述:", anchor="w").place(x=20, y=120, width=90, height=30)
        tk.Label(
            about_win, bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="w",
            text="只读字体预览工具,可以查看字形网格,私用区与$码位.",
        ).place(x=110, y=120, height=30)

        tk.Label(about_win, bg=WINDOWBG, fg=TEXTFG, text="当前版本:", anchor="w").place(x=20, y=160, width=90, height=30)
        tk.Label(about_win, bg=WINDOWBG, fg=SECONDARYTEXTFG, text=VERSION, anchor="w").place(x=110, y=160, height=30)

        tk.Label(about_win, bg=WINDOWBG, fg=TEXTFG, text="实际开发者:", anchor="w").place(x=20, y=200, width=90, height=30)
        tk.Label(
            about_win, bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="w",
            text="GROK AI",
        ).place(x=110, y=200, height=30)

        tk.Label(about_win, bg=TEXTBG, fg=TEXTFG).place(x=20, y=250, width=W - 40, height=2)

        tk.Label(about_win, bg=WINDOWBG, fg=TEXTFG, text="著作权:", anchor="w").place(x=20, y=270, width=90, height=30)
        tk.Label(
            about_win, bg=WINDOWBG, fg=TEXTFG, anchor="w",
            text="Copyright © 2026 炸图监管者.Licensed under the MIT License.",
        ).place(x=110, y=270, height=30)

        tk.Label(about_win, bg=TEXTBG, fg=TEXTFG).place(x=20, y=320, width=W - 40, height=2)

        tk.Label(about_win, bg=WINDOWBG, fg=TEXTFG, text="相关链接:", anchor="w").place(x=20, y=340, width=90, height=30)

        tk.Label(about_win, bg=WINDOWBG, fg=SECONDARYTEXTFG, text="个人主页:", anchor="w").place(x=60, y=380, width=90, height=30)
    
        btn_home = DAlphaButton(
                about_win, text="https://zhatujianguanzhe.github.io",
                command=lambda: webbrowser.open_new_tab("https://zhatujianguanzhe.github.io"),
                fg=HIGHLIGHT, anchor="w",)
        btn_home.place(x=150, y=380, height=30)
   

        tk.Label(about_win, bg=WINDOWBG, fg=SECONDARYTEXTFG, text="Github:", anchor="w").place(x=60, y=420, width=90, height=30)
        
        btn_gh = DAlphaButton(
                about_win, text="https://github.com/zhatujianguanzhe",
                command=lambda: webbrowser.open_new_tab("https://github.com/zhatujianguanzhe"),
                fg=HIGHLIGHT, anchor="w", )
        btn_gh.place(x=150, y=420, height=30)

      
        tk.Label(about_win, bg=WINDOWBG, fg=SECONDARYTEXTFG, text="Bilibili:", anchor="w").place(x=60, y=460, width=90, height=30)
        btn_gh = DAlphaButton(
                about_win, text="https://space.bilibili.com/1342104465",
                command=lambda: webbrowser.open_new_tab("https://space.bilibili.com/1342104465"),
                fg=HIGHLIGHT, anchor="w", )
        btn_gh.place(x=150, y=460, height=30)

        label_qq=tk.Label(about_win,bg=WINDOWBG,fg=SECONDARYTEXTFG,text='QQ群:',anchor='w',)
        label_qq.place(x=60,y=500,width=90,height=30)

        button_qq=tk.Label(about_win,text='865302820',bg=WINDOWBG,fg=SECONDARYTEXTFG,anchor='w')
        button_qq.place(x=150,y=500,height=30)

        close_btn = DButton(about_win, text="关闭", default="active", command=close_about)
        close_btn.place(x=W -100, y=H - 50, width=80, height=30)
    
        close_btn.unbind_default_active()
      
        center_window(about_win, W, H, parent=root)
      
        about_win.wm_iconbitmap(f"{libresource}icon.ico")
    
        about_win.update_idletasks()
        about_win.deiconify()
        close_btn.focus_set()
        about_win.wait_window()

    # ---------- 小预览窗: 双击打开, Esc / 双击关闭 ----------
    def open_detail():
        glyph = current()
        doc = state["doc"]
        if not glyph or not doc:
            return
        # 若已有小窗，先关掉
        if state["_detail_win"] is not None:
            try:
                state["_detail_win"].destroy()
            except Exception:
                pass
            state["_detail_win"] = None

        # 双击查看:历史只记首字码点
        if glyph.get("unicodes"):
            push_search_history(fmt_cp(glyph["unicodes"][0]))
        win = tk.Toplevel(root)
        win.withdraw()
        state["_detail_win"] = win
        win.title(f"#{glyph['index']} {glyph['name']}")
        win.configure(bg=WINDOWBG)
        win.transient(root)
        win.resizable(False, False)
        SetDarkTitleBar(win)

        # 左侧大图
        stage = tk.Canvas(win, bg=cell_bg, bd=0, highlightthickness=0)
        stage.place(x=MARGIN, y=MARGIN, width=360, height=320)
        SetBorder(stage, mode="place")
        image = raster(glyph, 240)
        if image is not None:
            photo = ImageTk.PhotoImage(image)
            stage.create_image(180, 160, image=photo)
            stage.image = photo
            stage.create_line(20, 280, 340, 280, fill="#D13438")
            stage.create_text(24, 292, anchor="w", text="基线示意", fill="#D13438", font=("微软雅黑", 8))

        # 右侧信息: 字码点用 DEntry 可横滚/选中复制,不被裁切
        codes = fmt_cps(glyph["unicodes"]) or "(无码位)"
        info_x = MARGIN + 360 + MARGIN
        info_w = 240
        info_y = MARGIN
        LABEL_STEP = 5
        code_entry = DEntry(win, font=("Consolas", 11))
        code_entry.place(x=info_x, y=info_y, width=info_w, height=30)
        code_entry.insert(0, codes)
        try:
            code_entry.config(fg=code_color, state="readonly")
        except Exception:
            code_entry.config(state="readonly")
        info_y += 30 + LABEL_STEP
        for key, val in (
            ("字宽:", glyph["advance"]),
            ("左线:", glyph["lsb"]),
            ("右线:", glyph["rsb"]),
            ("单位/Em:", doc["upem"]),
        ):
            tk.Label(win, text=key, bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="w").place(
                x=info_x, y=info_y, width=80, height=22)
            val_entry = DEntry(win)
            val_entry.place(x=info_x + 80, y=info_y, width=info_w - 80, height=30)
            val_entry.insert(0, str(int(val)))
            val_entry.config(state="readonly")
            info_y += 30 + LABEL_STEP

        tip = tk.Label(win, text="Esc 或双击此窗口关闭", bg=WINDOWBG, fg=SECONDARYTEXTFG, anchor="w")
        tip.place(x=info_x, y=MARGIN + 320 - 20, width=info_w, height=20)

        win_w = info_x + info_w + MARGIN
        win_h = MARGIN + 320 + MARGIN
        center_window(win, win_w, win_h, parent=root)
        try:
            win.wm_iconbitmap(f"{libresource}icon.ico")
        except Exception:
            pass
        win.update_idletasks()
        win.deiconify()

        def close_detail(event=None):
            try:
                win.destroy()
            except Exception:
                pass
            state["_detail_win"] = None
            return "break"

        win.bind("<Escape>", close_detail)
        win.bind("<Double-Button-1>", close_detail)
        stage.bind("<Double-Button-1>", close_detail)
        # 让整个小窗区域都能双击关闭
        for child in win.winfo_children():
            child.bind("<Double-Button-1>", close_detail)
        win.focus_set()
        win.protocol("WM_DELETE_WINDOW", close_detail)

    def on_key(event):
        if event.widget in (search,):
            return
        cols = columns()
        if event.keysym == "Right":
            move(1)
        elif event.keysym == "Left":
            move(-1)
        elif event.keysym == "Down":
            move(1 if state["mode"] == "list" else cols)
        elif event.keysym == "Up":
            move(-1 if state["mode"] == "list" else -cols)
        elif event.keysym == "Return":
            open_detail()
        elif event.keysym in ("plus", "equal", "KP_Add"):
            zoom(1)
        elif event.keysym in ("minus", "KP_Subtract"):
            zoom(-1)

    root.bind("<Control-o>", lambda e: open_font())
    root.bind("<Control-f>", lambda e: (search.focus_set(), (search.select_range(0, "end") if hasattr(search, "select_range") else None)))
    root.bind("<F1>", lambda e: show_help())
    root.bind("<Key>", on_key)
    # 全局 ESC：如果有小窗就关小窗
    def global_esc(event):
        if state["_detail_win"] is not None:
            try:
                state["_detail_win"].destroy()
            except Exception:
                pass
            state["_detail_win"] = None
            return "break"
    root.bind("<Escape>", global_esc)


    def toggle(key):
        state[key] = not state[key]
        schedule_redraw()

    def layout(event=None):
        if event is not None and event.widget is not root:
            return
        if state["_layouting"]:
            return
        state["_layouting"] = True
        try:
            width = root.winfo_width()
            height = root.winfo_height()
            if width < 200 or height < 200:
                return
            M = MARGIN  # 20
            top = TOP_CHROME + M
            bottom = height - 24 - M
            # 左树
            tree_h = max(40, bottom - top - SB_W)  # 底部横滚高度 20
            tree.place(x=M, y=top, width=TREE_W - SB_W, height=tree_h)
            tree_scroll.place(x=M + TREE_W - SB_W, y=top, width=SB_W, height=tree_h)
            tree_scroll_x.place(x=M, y=top + tree_h, width=TREE_W - SB_W, height=SB_W)
            # 预览左缘
            canvas_left = M + TREE_W + M
            # 右属性: 与滚动条间距 20
            # [canvas][SB_W][M=20][props][M]
            props_x = width - PROP_W - M
            grid_w = max(80, props_x - M - SB_W - canvas_left)
            canvas.place(x=canvas_left, y=top, width=grid_w, height=bottom - top)
            grid_scroll.place(x=canvas_left + grid_w, y=top, width=SB_W, height=bottom - top)
            props.place(x=props_x, y=top, width=PROP_W, height=bottom - top)

            # ---- 导航 y=20: 导航按钮左缘 = 预览左缘; 按钮间距0; 与搜索间距10 ----
            nav_bar.place(x=0, y=0, width=width, height=NAV_H)
            nav_x = canvas_left  # 与中心预览框左对齐
            btn_back.place(x=nav_x, y=20, width=30, height=30)
            btn_fwd.place(x=nav_x + 30, y=20, width=30, height=30)  # 两按钮间距 0
            search_x = nav_x + 60 + 10  # 与导航按钮组间距 10
            search_w = min(200, max(120, width // 6))
            # 路径框右移并加宽,吃掉右侧剩余
            path_x = search_x + search_w + M
            path_w = max(180, width - path_x - M)
            search_combo.place(x=search_x, y=20, width=search_w, height=30)
            file_path_entry.place(x=path_x, y=20, width=path_w, height=30)

            # ---- 操作栏 y=70: 保持原样,从左边距起,不跟预览对齐 ----
            tool_bar.place(x=0, y=NAV_H, width=width, height=TOOL_H)
            x = M
            btn_open.place(x=x, y=10, width=30, height=30)
            x += 30 + M
            zoom_spin.place(x=x, y=10, width=100, height=30)
            x += 100 + M
            btn_grid.place(x=x, y=10, width=30, height=30)
            btn_list.place(x=x + 30, y=10, width=30, height=30)
            x += 60 + M
            btn_info.place(x=x, y=10, width=30, height=30)
            btn_help.place(x=x + 30, y=10, width=30, height=30)
            btn_about.place(x=x + 60, y=10, width=30, height=30)
            x += 90 + M
            btn_exit.place(x=x, y=10, width=30, height=30)
            status.place(x=M, y=height - 22, width=width // 3 - M, height=20)
            status_mid.place(x=width // 3, y=height - 22, width=width // 3, height=20)
            status_right.place(x=2 * width // 3, y=height - 22, width=width // 3 - M, height=20)
        finally:
            state["_layouting"] = False

    root.bind("<Configure>", layout)
    root.after(30, layout)

    if len(sys.argv) > 1:
        root.after(120, lambda: open_font(sys.argv[1]))

    # 图标 → 居中 → 展示
    try:
        root.wm_iconbitmap(f"{libresource}icon.ico")
    except Exception:
        pass
    root.update_idletasks()
    center_window(root, width, height)
    root.deiconify()
    root.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
