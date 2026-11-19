#!/usr/bin/env python3
"""Pre-publish lint for technical blog drafts.

Checks encoding anomalies, AI-ish / marketing phrasing, structure, figure and
code-block hygiene, and desensitization risks. Prints a P0/P1/P2 report.

Usage:
    python blog_lint.py article.md
    python blog_lint.py article.md --deny my-words.txt
    python blog_lint.py article.md --json report.json

Exit code: 0 = 可发布, 1 = 需修复（存在 P0 或 P1）, 2 = 文件错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

# --- rule tables -----------------------------------------------------------

MARKETING = [
    "彻底搞懂", "一文读懂", "一文搞懂", "吊打", "秒杀", "碾压", "颠覆", "革命性",
    "最强", "唯一", "完美解决", "重磅", "炸裂", "必看", "干货满满", "解密",
    "史上最", "全网首发", "天花板", "王炸",
]

AI_PHRASES = [
    "值得注意的是", "需要指出的是", "更微妙的是", "不难发现", "显而易见",
    "综上所述", "总而言之", "由此可见", "总的来说", "换句话说",
    "随着人工智能的快速发展", "随着云计算的快速发展", "随着大模型的快速发展",
    "在当今", "在这个时代", "赋能", "闭环", "抓手", "颗粒度", "底层逻辑",
    "心智", "对齐一下", "组合拳",
]

FLIP_PATTERNS = [
    r"不是[^。；\n]{1,30}?而是",
    r"与其说[^。；\n]{1,30}?不如说",
    r"表面上[^。；\n]{1,30}?实际上",
    r"你以为[^。；\n]{1,30}?其实",
    r"说到底",
]

DEFAULT_DENY = [
    "公司内部", "内部产品", "内部系统",
    "内部文档", "内网", "堡垒机", "生产集群地址",
]

SUSPICIOUS_CATS = {"Cf", "Co", "Cs"}


def load_words(path: str | None) -> list[str]:
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        print(f"警告：deny 文件不存在，已忽略：{p}", file=sys.stderr)
        return []
    return [w.strip() for w in p.read_text(encoding="utf-8").splitlines() if w.strip()]


def check_chars(lines: list[str], issues: list[dict]) -> None:
    for i, line in enumerate(lines, 1):
        for j, ch in enumerate(line, 1):
            code = ord(ch)
            cat = unicodedata.category(ch)
            if code == 0xFFFD:
                issues.append(issue("P0", "ENCODING", i, f"替换符 U+FFFD（第 {j} 列），疑似编码损坏"))
            elif code == 0xFEFF:
                issues.append(issue("P0", "ENCODING", i, f"BOM/零宽无断空格 U+FEFF（第 {j} 列）"))
            elif 0x200B <= code <= 0x200F or 0x2028 <= code <= 0x202E:
                issues.append(issue("P0", "ENCODING", i, f"不可见格式符 U+{code:04X}（第 {j} 列）"))
            elif cat in SUSPICIOUS_CATS:
                issues.append(issue("P1", "ENCODING", i, f"控制/格式字符 U+{code:04X}（第 {j} 列）"))
            elif code < 0x20 and code not in (0x09, 0x0A, 0x0D):
                issues.append(issue("P1", "ENCODING", i, f"控制字符 U+{code:04X}（第 {j} 列）"))


def issue(sev: str, code: str, line: int, msg: str) -> dict:
    return {"severity": sev, "code": code, "line": line, "message": msg}


def check_words(lines: list[str], issues: list[dict]) -> None:
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            continue
        for w in MARKETING:
            if w in line:
                issues.append(issue("P1", "MARKETING", i, f"营销化/夸张表述：「{w}」"))
        for w in AI_PHRASES:
            if w in line:
                sev = "P1" if w not in ("换句话说", "总的来说") else "P2"
                issues.append(issue(sev, "AI_TONE", i, f"AI 味/套路表述：「{w}」"))
        for pat in FLIP_PATTERNS:
            if re.search(pat, line):
                issues.append(issue("P1", "AI_TONE", i, f"翻案腔句式：匹配 /{pat}/"))


def check_structure(lines: list[str], issues: list[dict], stats: dict) -> None:
    levels: list[tuple[int, int]] = []
    in_code = False
    h1_count = 0
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            if in_code and not line.strip().strip("`").strip():
                issues.append(issue("P2", "CODE_FENCE", i, "代码块缺少语言标注（bash/c/go/yaml）"))
            continue
        if in_code:
            continue
        m = re.match(r"^(#{1,6})\s+", line)
        if m:
            lv = len(m.group(1))
            stats["headings"] += 1
            if lv == 1:
                h1_count += 1
            if levels and lv - levels[-1][0] > 1:
                issues.append(issue("P1", "HEADING", i, f"标题层级跳级：H{levels[-1][0]} → H{lv}"))
            levels.append((lv, i))
    if h1_count > 1:
        issues.append(issue("P2", "HEADING", levels[0][1], f"出现 {h1_count} 个 H1，公众号正文建议只用 H2/H3"))


def check_paragraphs(lines: list[str], issues: list[dict], stats: dict) -> None:
    in_code = False
    buf: list[str] = []
    start = 0
    para_lens: list[int] = []

    def flush() -> None:
        nonlocal buf
        if not buf:
            return
        text = "".join(buf)
        n = len(re.findall(r"[\u4e00-\u9fa5]", text))
        if n:
            para_lens.append(n)
            stats["paragraphs"] += 1
            if n > 260:
                issues.append(issue("P1", "PARAGRAPH", start, f"段落 {n} 汉字，手机端一屏放不下，建议拆分"))
            elif n > 180:
                issues.append(issue("P2", "PARAGRAPH", start, f"段落 {n} 汉字，偏长"))
        buf = []

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            flush()
            continue
        if in_code:
            continue
        if not line.strip() or re.match(r"^(#{1,6})\s+", line) or re.match(r"^\s*([-*+]|\d+[.)])\s+", line):
            flush()
            continue
        if not buf:
            start = i
        buf.append(line.strip())
    flush()
    if para_lens:
        stats["avg_paragraph"] = round(sum(para_lens) / len(para_lens), 1)
        stats["max_paragraph"] = max(para_lens)


def check_figures(lines: list[str], issues: list[dict], stats: dict) -> None:
    for i, line in enumerate(lines, 1):
        m = re.match(r"^!\[(.*?)\]\((\S+?)\)", line.strip())
        if not m:
            if "```mermaid" in line:
                stats["mermaid"] += 1
                issues.append(issue("P2", "FIGURE", i, "mermaid 代码块：发布前需渲染为 SVG/PNG"))
            continue
        stats["images"] += 1
        if not m.group(1).strip():
            issues.append(issue("P1", "FIGURE", i, "图片缺少 alt 文本"))
        nxt = ""
        for k in range(i, min(i + 3, len(lines))):
            if lines[k].strip():
                nxt = lines[k].strip()
                break
        if not re.match(r"^(图|表)\s*[0-9０-９一二三四五六七八九十]|^图注|^图表?\s*[:：]", nxt):
            issues.append(issue("P1", "FIGURE", i, "图片后缺少图注（格式：图 N：一句话说明）"))


def check_sensitive(lines: list[str], issues: list[dict], deny: list[str], allow: list[str]) -> None:
    for i, line in enumerate(lines, 1):
        for w in deny:
            if not w or w in allow:
                continue
            if w in line:
                issues.append(
                    issue("P0", "SENSITIVE", i, f"疑似敏感词「{w}」：确认是否可公开；若已授权，用 --allow {w} 放行")
                )
        for m in re.finditer(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", line):
            ip = m.group(0)
            if ip in ("0.0.0.0", "127.0.0.1") or ip.endswith(".0"):
                continue
            issues.append(issue("P0", "SENSITIVE", i, f"疑似 IP 地址：{ip}"))
        for pat in (r"\b(?:10|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.",):
            if re.search(pat, line):
                issues.append(issue("P0", "SENSITIVE", i, "疑似内网网段"))


def check_evidence(text: str, issues: list[dict], stats: dict) -> None:
    stats["fact"] = text.count("【事实】")
    stats["analysis"] = text.count("【分析】")
    stats["guess"] = text.count("【推测】")
    if stats["fact"] + stats["analysis"] + stats["guess"] == 0:
        issues.append(
            issue("P2", "EVIDENCE", 0, "未检测到三级标注（内部稿可用【事实】/【分析】/【推测】；公开稿可用自然语气表达）")
        )
    if re.search(r"(?:性能)?(?:提升|提高|优化|下降|降低)(?:了)?\s*\d+(?:\.\d+)?\s*(?:倍|%|％)", text) and not re.search(
        r"(环境|条件|基线|原始输出|对比|实测)", text
    ):
        issues.append(issue("P1", "EVIDENCE", 0, "出现「提升 N 倍」但未见环境/基线说明"))


def check_stats(text: str, stats: dict) -> None:
    stats["chars"] = len(re.findall(r"[\u4e00-\u9fa5]", text))
    stats["words_en"] = len(re.findall(r"[A-Za-z]+", text))
    stats["read_minutes"] = max(1, round((stats["chars"] + stats["words_en"]) / 400))
    stats["code_blocks"] = len(re.findall(r"^```", text, re.M)) // 2
    stats["tables"] = len(re.findall(r"^\s*\|[\s:|-]+\|\s*$", text, re.M))


SEV_ORDER = {"P0": 0, "P1": 1, "P2": 2}
SEV_LABEL = {"P0": "阻塞", "P1": "必修", "P2": "建议"}


def main() -> int:
    parser = argparse.ArgumentParser(description="技术博客发布前体检")
    parser.add_argument("input", help="Markdown 文件路径")
    parser.add_argument("--deny", help="自定义敏感词文件（每行一个）")
    parser.add_argument("--allow", nargs="*", default=[], help="放行的词（已获授权公开）")
    parser.add_argument("--json", help="输出 JSON 报告的路径")
    parser.add_argument("--quiet", action="store_true", help="只输出汇总与 P0/P1")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"错误：找不到文件 {src}", file=sys.stderr)
        return 2

    raw = src.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        print(f"错误：文件不是合法 UTF-8（{exc}）。请先转码再检查。", file=sys.stderr)
        return 2

    lines = text.split("\n")
    issues: list[dict] = []
    stats = {
        "headings": 0, "paragraphs": 0, "images": 0, "mermaid": 0,
        "avg_paragraph": 0, "max_paragraph": 0,
        "fact": 0, "analysis": 0, "guess": 0,
        "chars": 0, "words_en": 0, "read_minutes": 0, "code_blocks": 0, "tables": 0,
    }

    deny = DEFAULT_DENY + load_words(args.deny)

    check_chars(lines, issues)
    check_words(lines, issues)
    check_structure(lines, issues, stats)
    check_paragraphs(lines, issues, stats)
    check_figures(lines, issues, stats)
    check_sensitive(lines, issues, deny, args.allow)
    check_evidence(text, issues, stats)
    check_stats(text, stats)

    issues.sort(key=lambda x: (SEV_ORDER[x["severity"]], x["line"]))

    counts = {s: sum(1 for it in issues if it["severity"] == s) for s in ("P0", "P1", "P2")}
    verdict = "可发布" if counts["P0"] == 0 and counts["P1"] == 0 else "需修复后重跑"

    print(f"文件：{src}")
    print(
        f"体量：{stats['chars']} 汉字 + {stats['words_en']} 英文词 ≈ {stats['read_minutes']} 分钟阅读"
        f" | 标题 {stats['headings']} · 段落 {stats['paragraphs']}（均 {stats['avg_paragraph']} 字）"
        f" · 代码 {stats['code_blocks']} · 表 {stats['tables']} · 图 {stats['images']}"
    )
    print(
        f"标注：【事实】{stats['fact']} ·【分析】{stats['analysis']} ·【推测】{stats['guess']}"
        f" | mermaid {stats['mermaid']}"
    )
    print(f"问题：P0 {counts['P0']} · P1 {counts['P1']} · P2 {counts['P2']}")
    print("-" * 62)

    if not issues:
        print("未发现问题。发布前仍请人工过一遍 TECH_REVIEW_CHECKLIST 的技术准确性 12 项。")
    else:
        for sev in ("P0", "P1", "P2"):
            group = [it for it in issues if it["severity"] == sev]
            if not group:
                continue
            if args.quiet and sev == "P2":
                print(f"[{sev} {SEV_LABEL[sev]}] 另有 {len(group)} 条建议级问题（--json 查看）")
                continue
            print(f"[{sev} {SEV_LABEL[sev]}] {len(group)} 条")
            for it in group[:40]:
                loc = f"L{it['line']}" if it["line"] else "全文"
                print(f"  {loc:>7}  [{it['code']}] {it['message']}")
            if len(group) > 40:
                print(f"           … 其余 {len(group) - 40} 条省略")

    print("-" * 62)
    print(f"结论：{verdict}")

    if args.json:
        Path(args.json).write_text(
            json.dumps({"file": str(src), "verdict": verdict, "counts": counts, "stats": stats, "issues": issues},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"JSON 报告：{args.json}")

    return 0 if verdict == "可发布" else 1


if __name__ == "__main__":
    raise SystemExit(main())
