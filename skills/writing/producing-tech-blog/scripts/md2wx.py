#!/usr/bin/env python3
"""Markdown -> WeChat Official Account HTML (all inline styles).

Why this exists: WeChat's editor drops <style>, class and most external CSS,
so every element must carry its own inline style. This converter emits a
single wrapper div plus element-level inline styles that follow the blog
visual spec in references/BLOG_IMAGE_GUIDE.md.

Usage:
    python md2wx.py article.md -o article.html
    python md2wx.py article.md -o article.html --accent "#1677FF" --font-size 16
    python md2wx.py article.md --fragment > body.html

No third-party dependency. Python 3.8+.
"""

from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import sys
from pathlib import Path

IMAGE_RE = re.compile(r"^!\[(.*?)\]\((\S+?)(?:\s+\"(.*)\")?\)\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)\s*([\w+-]*)\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
HR_RE = re.compile(r"^\s*((\*\s*){3,}|(-\s*){3,}|(_\s*){3,})$")
QUOTE_RE = re.compile(r"^\s*>\s?(.*)$")
TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]*\|?\s*$")
CAPTION_RE = re.compile(r"^(图|表)\s*[0-9０-９一二三四五六七八九十]|^图注|^图表?\s*[:：]")

CJK_RE = re.compile(r"[\u4e00-\u9fa5]")
WORD_RE = re.compile(r"[A-Za-z]+")


def esc(text: str) -> str:
    """Escape text for an HTML text node; quotes are left alone."""
    return htmllib.escape(text, quote=False)


def esc_attr(text: str) -> str:
    """Escape a raw value (URL, title) for a double-quoted attribute."""
    return htmllib.escape(text, quote=True)


def attr(escaped: str) -> str:
    """Harden already text-escaped output before putting it in an attribute.

    The input has passed through ``esc()``, so ``&``/``<``/``>`` are already
    entities; only quotes can still break out of the attribute value.
    """
    return escaped.replace('"', "&quot;").replace("'", "&#x27;")


class Palette:
    def __init__(self, accent: str, font_size: int, line_height: float, code_bg: str) -> None:
        self.accent = accent
        self.fs = font_size
        self.lh = line_height
        self.code_bg = code_bg
        self.dark = "#0B1F3A"
        self.text = "#333333"
        self.muted = "#8A94A6"
        self.border = "#E6EBF2"
        self.soft = "#F2F7FF"

    def style(self, name: str) -> str:
        fs, lh = self.fs, self.lh
        return {
            "body": (
                "max-width:677px;margin:0 auto;padding:24px 18px 40px;background:#FFFFFF;"
                "font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;"
                f"font-size:{fs}px;line-height:{lh};color:{self.text};letter-spacing:0.4px;"
            ),
            "h1": f"font-size:{fs + 6}px;line-height:1.4;color:{self.dark};font-weight:700;margin:10px 0 22px;",
            "h2": (
                f"font-size:{fs + 4}px;line-height:1.5;color:{self.dark};font-weight:700;"
                f"margin:34px 0 14px;padding-left:10px;border-left:4px solid {self.accent};"
            ),
            "h3": f"font-size:{fs + 1}px;line-height:1.6;color:{self.dark};font-weight:600;margin:24px 0 10px;",
            "h4": f"font-size:{fs}px;line-height:1.6;color:{self.accent};font-weight:600;margin:18px 0 8px;",
            "h5": f"font-size:{fs}px;line-height:1.6;color:{self.dark};font-weight:600;margin:16px 0 8px;",
            "h6": f"font-size:{fs - 1}px;line-height:1.6;color:{self.muted};font-weight:600;margin:14px 0 8px;",
            "p": f"font-size:{fs}px;line-height:{lh};color:{self.text};margin:0 0 16px;text-align:justify;",
            "caption": f"font-size:13px;line-height:{lh};color:{self.muted};text-align:center;margin:6px 0 22px;",
            "ul": f"margin:0 0 16px;padding-left:22px;font-size:{fs}px;line-height:{lh};color:{self.text};",
            "li": f"margin:0 0 8px;font-size:{fs}px;line-height:{lh};color:{self.text};",
            "quote": (
                f"margin:0 0 18px;padding:12px 16px;background:{self.soft};"
                f"border-left:3px solid {self.accent};border-radius:0 4px 4px 0;"
                f"font-size:{fs - 1}px;line-height:{lh};color:#1F3A5F;"
            ),
            "quote_p": f"margin:0;font-size:{fs - 1}px;line-height:{lh};color:#1F3A5F;",
            "pre": (
                f"margin:0 0 18px;padding:14px 16px;background:{self.code_bg};border-radius:6px;"
                "overflow-x:auto;white-space:pre;-webkit-overflow-scrolling:touch;"
            ),
            "code_block": (
                "font-family:Menlo,Consolas,'Courier New',monospace;font-size:13px;"
                f"line-height:1.65;color:#24292F;letter-spacing:0;background:transparent;"
            ),
            "code_inline": (
                f"font-family:Menlo,Consolas,'Courier New',monospace;font-size:0.9em;"
                f"background:{self.code_bg};color:{self.accent};padding:1px 5px;border-radius:3px;"
            ),
            "table_wrap": "margin:0 0 18px;overflow-x:auto;",
            "table": "width:100%;border-collapse:collapse;font-size:14px;line-height:1.6;",
            "th": (
                f"background:{self.soft};color:{self.dark};font-weight:600;text-align:left;"
                f"padding:9px 10px;border-bottom:1px solid {self.border};"
            ),
            "td": f"padding:9px 10px;border-bottom:1px solid {self.border};color:{self.text};vertical-align:top;",
            "img": "max-width:100%;height:auto;display:block;margin:18px auto 8px;border-radius:4px;",
            "hr": f"border:none;border-top:1px solid {self.border};margin:30px 0;",
            "a": f"color:{self.accent};text-decoration:none;",
            "strong": f"color:{self.dark};font-weight:600;",
        }[name]


def inline_format(text: str, pal: Palette) -> str:
    """Escape then apply inline markdown, protecting code spans."""
    text = esc(text)

    codes: list[str] = []

    def stash(match: re.Match) -> str:
        codes.append(match.group(1))
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)

    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        lambda m: f'<a href="{attr(m.group(2))}" style="{pal.style("a")}">{m.group(1)}</a>',
        text,
    )
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: f'<strong style="{pal.style("strong")}">{m.group(1)}</strong>', text)
    text = re.sub(r"__(.+?)__", lambda m: f'<strong style="{pal.style("strong")}">{m.group(1)}</strong>', text)
    text = re.sub(r"(?<![*\w])\*(?!\s)([^*]+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![_\w])_(?!\s)([^_]+?)(?<!\s)_(?![_\w])", r"<em>\1</em>", text)
    text = text.replace("~~", "")

    def unstash(match: re.Match) -> str:
        return f'<code style="{pal.style("code_inline")}">{codes[int(match.group(1))]}</code>'

    return re.sub(r"\x00(\d+)\x00", unstash, text)


def is_block_start(line: str, nxt: str | None) -> bool:
    if not line.strip():
        return True
    if FENCE_RE.match(line) or HEADING_RE.match(line) or HR_RE.match(line) or QUOTE_RE.match(line):
        return True
    if IMAGE_RE.match(line) or LIST_RE.match(line):
        return True
    if "|" in line and nxt is not None and TABLE_SEP_RE.match(nxt):
        return True
    return False


def render_table(rows: list[str], pal: Palette, line_no: int, warns: list[str]) -> str:
    def cells(row: str) -> list[str]:
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        out: list[str] = []
        buf: list[str] = []
        in_code = False
        i = 0
        while i < len(row):
            ch = row[i]
            if ch == "\\" and i + 1 < len(row) and row[i + 1] == "|":
                buf.append("|")
                i += 2
                continue
            if ch == "`":
                in_code = not in_code
            if ch == "|" and not in_code:
                out.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
            i += 1
        out.append("".join(buf).strip())
        return out

    header = cells(rows[0])
    body = [cells(r) for r in rows[2:]]
    width = len(header)
    for row in body:
        if len(row) != width:
            warns.append(f"L{line_no}: 表格列数不一致（表头 {width} 列，数据行 {len(row)} 列）")
    out = [f'<div style="{pal.style("table_wrap")}"><table style="{pal.style("table")}">', "<thead><tr>"]
    out += [f'<th style="{pal.style("th")}">{inline_format(c, pal)}</th>' for c in header]
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        out += [f'<td style="{pal.style("td")}">{inline_format(c, pal)}</td>' for c in row]
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def render_list(items: list[tuple[int, str, str]], pal: Palette) -> str:
    out: list[str] = []
    stack: list[tuple[int, str]] = []
    for indent, marker, text in items:
        tag = "ol" if marker[0].isdigit() else "ul"
        while stack and indent < stack[-1][0]:
            out.append(f"</li></{stack[-1][1]}>")
            stack.pop()
        if not stack or indent > stack[-1][0]:
            out.append(f'<{tag} style="{pal.style("ul")}">')
            stack.append((indent, tag))
        elif stack[-1][1] != tag:
            out.append(f"</li></{stack[-1][1]}>")
            stack.pop()
            out.append(f'<{tag} style="{pal.style("ul")}">')
            stack.append((indent, tag))
        else:
            out.append("</li>")
        out.append(f'<li style="{pal.style("li")}">{inline_format(text, pal)}')
    while stack:
        out.append(f"</li></{stack[-1][1]}>")
        stack.pop()
    return "".join(out)


def convert(md: str, pal: Palette) -> tuple[str, dict, list[str]]:
    lines = md.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    warns: list[str] = []
    stats = {"headings": 0, "paragraphs": 0, "list_items": 0, "code_blocks": 0, "tables": 0, "images": 0, "words": 0}
    heading_levels: list[int] = []
    seen_h1 = 0
    i = 0
    total = len(lines)

    while i < total:
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        fence = FENCE_RE.match(line)
        if fence:
            lang = fence.group(2) or ""
            i += 1
            body: list[str] = []
            while i < total and not FENCE_RE.match(lines[i]):
                body.append(lines[i])
                i += 1
            i += 1  # closing fence
            stats["code_blocks"] += 1
            if not lang:
                warns.append(f"L{i}: 代码块缺少语言标注（建议 ```bash / ```c / ```yaml）")
            if any(re.search(r"mermaid", b) for b in body[:1]):
                warns.append(f"L{i}: 检测到 mermaid 代码块，需先渲染为 SVG/PNG 再嵌入")
            code = esc("\n".join(body))
            out.append(f'<pre style="{pal.style("pre")}"><code style="{pal.style("code_block")}">{code}</code></pre>')
            continue

        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2)
            stats["headings"] += 1
            heading_levels.append(level)
            if level == 1:
                seen_h1 += 1
            if seen_h1 > 1:
                warns.append(f"L{i + 1}: 出现多个 H1，公众号正文建议只用 H2/H3")
            if heading_levels and len(heading_levels) > 1 and level - heading_levels[-2] > 1:
                warns.append(f"L{i + 1}: 标题层级跳级（H{heading_levels[-2]} → H{level}）")
            hstyle = pal.style(f"h{level}")
            out.append(f'<h{level} style="{hstyle}">{inline_format(text, pal)}</h{level}>')
            i += 1
            continue

        if HR_RE.match(line):
            out.append(f'<hr style="{pal.style("hr")}">')
            i += 1
            continue

        if QUOTE_RE.match(line):
            buf: list[str] = []
            j = i
            while j < total and QUOTE_RE.match(lines[j]):
                buf.append(QUOTE_RE.match(lines[j]).group(1))
                j += 1
            inner = "<br>".join(inline_format(b, pal) for b in buf if b.strip())
            out.append(
                f'<blockquote style="{pal.style("quote")}"><p style="{pal.style("quote_p")}">{inner}</p></blockquote>'
            )
            i = j
            continue

        image = IMAGE_RE.match(line)
        if image:
            alt, src, title = image.group(1), image.group(2), image.group(3)
            stats["images"] += 1
            if not alt:
                warns.append(f"L{i + 1}: 图片缺少 alt 文本")
            title_attr = f' title="{attr(esc(title))}"' if title else ""
            out.append(
                f'<img src="{esc_attr(src)}" alt="{attr(esc(alt))}"{title_attr} style="{pal.style("img")}">'
            )
            i += 1
            # caption is expected within the next few non-empty lines
            nxt = ""
            for k in range(i, min(i + 3, total)):
                if lines[k].strip():
                    nxt = lines[k].strip()
                    break
            if not nxt.startswith(("图", "表", "注", "Figure")):
                warns.append(f"L{i}: 图片后未紧跟图注（建议「图 N：说明」）")
            continue

        if "|" in line and i + 1 < total and TABLE_SEP_RE.match(lines[i + 1]):
            rows = [line]
            j = i + 1
            while j < total and "|" in lines[j] and lines[j].strip():
                rows.append(lines[j])
                j += 1
            stats["tables"] += 1
            out.append(render_table(rows, pal, i + 1, warns))
            i = j
            continue

        if LIST_RE.match(line):
            items: list[tuple[int, str, str]] = []
            j = i
            while j < total and LIST_RE.match(lines[j]):
                m = LIST_RE.match(lines[j])
                items.append((len(m.group(1).replace("\t", "    ")), m.group(2), m.group(3)))
                j += 1
                # continuation lines of a list item
                while j < total and lines[j].strip() and not is_block_start(lines[j], lines[j + 1] if j + 1 < total else None):
                    if items:
                        indent, marker, text = items[-1]
                        items[-1] = (indent, marker, text + " " + lines[j].strip())
                    j += 1
            stats["list_items"] += len(items)
            out.append(render_list(items, pal))
            i = j
            continue

        # paragraph
        buf = [line.strip()]
        j = i + 1
        while j < total and not is_block_start(lines[j], lines[j + 1] if j + 1 < total else None):
            buf.append(lines[j].strip())
            j += 1
        text = " ".join(buf)
        stats["paragraphs"] += 1
        if CAPTION_RE.match(text) and len(text) <= 120:
            out.append(f'<p style="{pal.style("caption")}">{inline_format(text, pal)}</p>')
        else:
            if len(CJK_RE.findall(text)) > 220:
                warns.append(f"L{i + 1}: 段落过长（{len(CJK_RE.findall(text))} 汉字），建议拆成两段")
            out.append(f'<p style="{pal.style("p")}">{inline_format(text, pal)}</p>')
        i = j

    body = "".join(out)
    plain = re.sub(r"```.*?```", "", md, flags=re.S)
    stats["words"] = len(CJK_RE.findall(plain)) + len(WORD_RE.findall(plain))
    stats["read_minutes"] = max(1, round(stats["words"] / 400))
    return body, stats, warns


def build_document(body: str, pal: Palette, title: str) -> str:
    return (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{esc(title)}</title>\n</head>\n"
        "<body style=\"margin:0;padding:0;background:#FFFFFF;\">\n"
        f'<div style="{pal.style("body")}">\n{body}\n</div>\n</body>\n</html>\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Markdown -> 公众号内联样式 HTML")
    parser.add_argument("input", help="Markdown 文件路径")
    parser.add_argument("-o", "--output", help="输出 HTML 路径（默认同名 .html）")
    parser.add_argument("--title", default="", help="<title> 内容（默认取首个 H1 或文件名）")
    parser.add_argument("--accent", default="#1677FF", help="强调色，默认 #1677FF")
    parser.add_argument("--font-size", type=int, default=16, help="正文字号，14-17，默认 16")
    parser.add_argument("--line-height", type=float, default=1.8, help="正文行高，1.6-2.0，默认 1.8")
    parser.add_argument("--code-bg", default="#F4F6F8", help="代码块背景色，默认 #F4F6F8")
    parser.add_argument("--fragment", action="store_true", help="只输出 body 片段")
    args = parser.parse_args()

    for name, value in (("--accent", args.accent), ("--code-bg", args.code_bg)):
        if not re.fullmatch(r"#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})", value):
            print(f"错误：{name} 需要 #RGB/#RRGGBB/#RRGGBBAA 形式，收到：{value}", file=sys.stderr)
            return 2

    src = Path(args.input)
    if not src.exists():
        print(f"错误：找不到文件 {src}", file=sys.stderr)
        return 2

    md = src.read_text(encoding="utf-8")
    pal = Palette(args.accent, args.font_size, args.line_height, args.code_bg)
    body, stats, warns = convert(md, pal)

    title = args.title
    if not title:
        m = re.search(r"^#\s+(.+)$", md, re.M)
        title = m.group(1).strip() if m else src.stem

    html_out = body if args.fragment else build_document(body, pal, title)
    out_path = Path(args.output) if args.output else src.with_suffix(".html")
    out_path.write_text(html_out, encoding="utf-8")

    report = {
        "source": str(src),
        "output": str(out_path),
        "title": title,
        "params": {
            "accent": args.accent,
            "font_size": args.font_size,
            "line_height": args.line_height,
            "code_bg": args.code_bg,
        },
        "stats": stats,
        "warnings": warns,
    }
    report_path = out_path.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已生成：{out_path}")
    print(f"报告：  {report_path}")
    print(
        f"统计：  {stats['words']} 字 / 约 {stats['read_minutes']} 分钟 · "
        f"标题 {stats['headings']} · 段落 {stats['paragraphs']} · 代码 {stats['code_blocks']} · "
        f"表格 {stats['tables']} · 图 {stats['images']}"
    )
    if warns:
        print(f"警告 {len(warns)} 条：")
        for w in warns:
            print(f"  - {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
