#!/usr/bin/env python3
"""技术文章 AI 味量化检测脚本。

移植 human-writing (KKKKhazix/human-writing) 的核心统计检测思路，
适配微信公众号技术文章场景。只报警，不自动改文。

用法：
    python3 check_style.py article.md
    python3 check_style.py -          # 从标准输入读取
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path


# ============================================================
# 词表常量
# ============================================================

# 硬停词：出现在正文中就是 AI 味
HARD_STOPS = (
    "说白了",
    "说穿了",
    "先说结论",
)

# 模型路标词：用来给段落"抬高"的假洞察信号
ROAD_SIGNS = (
    "更微妙的是",
    "还有一层",
    "只说对了一半",
    "值得注意的是",
    "需要指出的是",
    "从某种意义上说",
)

# 翻案腔正则：匹配"先立误解再推翻"的各种变形
PIVOT_PATTERNS = (
    re.compile(r"(?:并)?不是[^。！？\n]{0,90}而是"),
    re.compile(r"并非[^。！？\n]{0,90}而是"),
    re.compile(r"不在于[^。！？\n]{0,90}而在于"),
    re.compile(r"与其说[^。！？\n]{0,90}(?:不如|毋宁|倒不如)"),
    re.compile(r"[。！？!?]\s*而是"),
    re.compile(r"表面(?:上)?[^。！？\n]{0,90}(?:其实|实际|实则)"),
    re.compile(r"看似[^。！？\n]{0,90}(?:其实|实际|实则)"),
)

# 翻案腔语义变形：换字面但做同一个动作
SEMANTIC_PIVOT_PATTERNS = (
    re.compile(r"(?:总|一直|曾|都)?以为[^！？\n]{2,60}?(?:其实|才发现|才明白|才知道|后来才)"),
    re.compile(r"(?:总|都|一直)以为[^！？\n]{2,60}?[。，](?:可|但|其实)"),
    re.compile(r"回头(?:看|一看)?才(?:发现|明白|知道)"),
    re.compile(r"(?:并)?不是[^。！？\n]{1,40}，(?:更|才)?是[^，。！？\n]"),
    re.compile(r"答案(?:是否定的|恰恰相反)|恰恰相反"),
    re.compile(r"[^，。！？\n]{1,12}不重要，(?:重要|要紧)的是"),
    re.compile(r"真正[^，。！？\n]{0,16}的(?:，)?是"),
)

# 名词化句式：动词被压成名词
NOMINALIZATION_PATTERNS = (
    re.compile(r"进行(?:了|一次|一场|着)?[^。，！？\n]{0,10}(?:调整|优化|升级|分析|讨论|梳理|复盘|迭代|探索|尝试|思考|规划|布局)"),
    re.compile(r"实现了?[^。，！？\n]{0,14}的?[^。，！？\n]{0,6}(?:提升|增长|突破|转变|跃升|落地)"),
    re.compile(r"完成了?对[^。，！？\n]{0,16}的"),
    re.compile(r"起到了?[^。，！？\n]{0,12}的?作用"),
    re.compile(r"具有[^。，！？\n]{0,10}(?:意义|价值)"),
)

# 连词列表
CONJUNCTIONS = (
    "因为",
    "所以",
    "但是",
    "然而",
    "同时",
    "此外",
    "而且",
    "并且",
    "因此",
    "不仅",
)

# 段落开场词重复检测
REPEATED_OPENERS = (
    "其实",
    "不过",
    "当然",
    "所以",
    "但是",
    "后来",
    "当时",
    "很多人",
    "问题是",
    "更重要的是",
    "说到这里",
)

# 软标记词（出现过多说明在批量造洞察）
SOFT_MARKERS = (
    "真正",
    "本质上",
    "更深层次",
    "归根结底",
    "换句话说",
    "不可否认",
    "核心是",
    "关键在于",
    "这意味着",
)

# 技术文章常见黑话（AI 味来源）
TECH_JARGON = (
    "赋能",
    "抓手",
    "商业闭环",
    "价值闭环",
    "能力沉淀",
    "拉通",
    "底层逻辑",
    "顶层设计",
    "降本增效",
    "全链路",
    "组合拳",
    "技术底座",
    "核心变量",
)

# 禁止标点
FORBIDDEN_PUNCTUATION = {
    "\u2014": "破折号",
    "\u2013": "连接号式破折号",
}


# ============================================================
# 工具函数
# ============================================================

def han_count(text: str) -> int:
    """统计汉字数量。"""
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def line_number(text: str, position: int) -> int:
    """根据字符位置算行号。"""
    return text.count("\n", 0, position) + 1


def excerpt(value: str, width: int = 60) -> str:
    """截取片段用于显示。"""
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= width else value[: width - 1] + "..."


def mask_non_prose(text: str) -> str:
    """屏蔽代码块、网址、frontmatter 等非正文内容，保留位置和换行。

    支持 HTML 注释排除标记：<!-- check-style: off --> 到 <!-- check-style: on -->
    之间的内容会被屏蔽，用于文章中引用禁令清单等教学性内容。
    """

    def mask(match: re.Match[str]) -> str:
        return "".join("\n" if ch == "\n" else " " for ch in match.group())

    patterns = (
        re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", re.DOTALL),  # frontmatter
        re.compile(r"<!--\s*check-style:\s*off\s*-->.*?<!--\s*check-style:\s*on\s*-->", re.DOTALL),  # 排除标记
        re.compile(r"```.*?```", re.DOTALL),  # 代码块
        re.compile(r"`[^`\n]*`"),  # 行内代码
        re.compile(r"\]\([^\n)]*\)"),  # markdown 链接
        re.compile(r"https?://[^\s)>]+"),  # 网址
        re.compile(r"<[^>\n]+>"),  # HTML 标签
    )
    masked = text
    for pattern in patterns:
        masked = pattern.sub(mask, masked)
    return masked


def non_overlapping_terms(text: str, terms: tuple[str, ...]):
    """查找不重叠的关键词匹配。"""
    matches = []
    occupied = []
    for term in sorted(terms, key=len, reverse=True):
        for match in re.finditer(re.escape(term), text):
            start, end = match.span()
            if any(start < old_end and end > old_start for old_start, old_end in occupied):
                continue
            matches.append((start, term))
            occupied.append((start, end))
    return sorted(matches)


def all_matches(text: str, patterns: tuple[re.Pattern[str], ...]):
    """对所有正则模式做匹配，返回排序后的结果。"""
    matches = []
    for pattern in patterns:
        matches.extend(pattern.finditer(text))
    return sorted(matches, key=lambda m: m.start())


# ============================================================
# 检测函数
# ============================================================

def sentence_length_cv(text: str):
    """句长变异系数。人写的长短句差距大，模型的句长彼此接近。

    Returns:
        (cv, sentence_count) 或 None（句子太少时）
    """
    lengths = [
        han_count(match.group())
        for match in re.finditer(r"[^。！？!?\n]+[。！？!?]", text)
        if han_count(match.group()) >= 4
    ]
    if len(lengths) < 12:
        return None
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return None
    variance = sum((v - mean) ** 2 for v in lengths) / len(lengths)
    return (variance ** 0.5) / mean, len(lengths)


def heavy_de_sentences(text: str):
    """找出一句话里"的"字过多（>=4）的长句。"""
    matches = []
    pattern = re.compile(r"[^。！？!?\n]+(?:[。！？!?]|$)")
    for match in pattern.finditer(text):
        value = match.group()
        if han_count(value) >= 38 and value.count("的") >= 4:
            matches.append(match)
    return matches


def anaphora_runs(text: str, minimum: int = 3):
    """找出同一句里三个以上小句用同一开头的排比。"""
    matches = []
    for sentence in re.finditer(r"[^。！？!?\n]+(?:[。！？!?]|$)", text):
        clauses = [
            clause.strip()
            for clause in re.split(r"[，、；,;]", sentence.group())
            if han_count(clause) >= 3
        ]
        if len(clauses) < minimum:
            continue
        run = 1
        for prev, curr in zip(clauses, clauses[1:]):
            if prev[:2] == curr[:2] and re.match(r"[\u4e00-\u9fff]{2}", curr):
                run += 1
                if run >= minimum:
                    matches.append(sentence)
                    break
            else:
                run = 1
    return matches


def prose_paragraphs(text: str):
    """提取正文段落（跳过标题、列表、代码块）。"""
    paragraphs = []
    cursor = 0
    for block in re.split(r"\n\s*\n", text):
        position = text.find(block, cursor)
        cursor = max(position + len(block), cursor)
        clean = re.sub(r"[>*_`]", "", block).strip()
        if not clean or clean.startswith(("#", "http", "![", "```")):
            continue
        if re.match(r"^(?:[-+*]|\d+[.、])\s", clean):
            continue
        count = han_count(clean)
        if count < 4:
            continue
        sentences = max(1, len(re.findall(r"[。！？!?]", clean)))
        paragraphs.append({
            "position": position,
            "text": clean,
            "han": count,
            "sentences": sentences,
        })
    return paragraphs


def opener_counts(paragraphs: list[dict]):
    """统计段落开场词重复情况。"""
    counts = collections.Counter()
    examples = {}
    for para in paragraphs:
        value = para["text"].lstrip("'\"（(")
        for opener in REPEATED_OPENERS:
            if value.startswith(opener):
                counts[opener] += 1
                examples.setdefault(opener, para["position"])
                break
    return counts, examples


def short_streak(paragraphs: list[dict], limit: int = 4):
    """检测连续出现的短促单句段。"""
    streak = []
    for para in paragraphs:
        if para["han"] <= 24 and para["sentences"] <= 1:
            streak.append(para)
            if len(streak) >= limit:
                return streak
        else:
            streak = []
    return None


# ============================================================
# 主检测逻辑
# ============================================================

def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="技术文章 AI 味量化检测。检查句式、节奏和模型化倾向。"
    )
    parser.add_argument(
        "path",
        help="Markdown 或文本文件路径。使用 - 从标准输入读取",
    )
    args = parser.parse_args()

    try:
        text = read_text(args.path)
    except (OSError, UnicodeError) as error:
        print(f"无法读取稿件：{error}", file=sys.stderr)
        return 2

    prose = mask_non_prose(text)
    total_han = han_count(prose)
    if total_han == 0:
        print("没有检测到汉字。", file=sys.stderr)
        return 2

    failures = []
    warnings = []

    # --- 硬禁令检查 ---

    # 1. 禁止标点（破折号）
    for symbol, label in FORBIDDEN_PUNCTUATION.items():
        matches = list(re.finditer(re.escape(symbol), prose))
        if matches:
            lines = "、".join(str(line_number(text, m.start())) for m in matches[:8])
            failures.append(f"{label}共 {len(matches)} 处，出现在第 {lines} 行。")

    # 2. 硬停词
    stop_matches = non_overlapping_terms(prose, HARD_STOPS)
    for position, phrase in stop_matches:
        failures.append(f"硬停词，第 {line_number(text, position)} 行：{phrase}")

    # 3. 技术黑话
    jargon_matches = non_overlapping_terms(prose, TECH_JARGON)
    for position, phrase in jargon_matches:
        failures.append(f"技术黑话，第 {line_number(text, position)} 行：{phrase}")

    # 4. 模型路标词
    road_sign_patterns = tuple(
        re.compile(
            rf"(?:^|[。！？!?]\s*){re.escape(phrase)}[^。！？!?\n]{{0,24}}",
            re.MULTILINE,
        )
        for phrase in ROAD_SIGNS
    )
    road_signs = all_matches(prose, road_sign_patterns)
    for match in road_signs:
        road_sign_text = match.group().strip("。！？!? \n")
        failures.append(
            f"模型路标，第 {line_number(text, match.start())} 行："
            f"\u201c{excerpt(road_sign_text)}\u201d"
        )

    # 5. 翻案腔（核心变形）
    pivots = all_matches(prose, PIVOT_PATTERNS)
    for match in pivots:
        failures.append(
            f"翻案腔，第 {line_number(text, match.start())} 行："
            f"\u201c{excerpt(match.group())}\u201d"
        )

    # --- 警告层（需人工判断） ---

    # 6. 翻案腔语义变形
    occupied_spans = [m.span() for m in pivots]
    for match in all_matches(prose, SEMANTIC_PIVOT_PATTERNS):
        if any(match.start() < end and match.end() > start for start, end in occupied_spans):
            continue
        occupied_spans.append(match.span())
        warnings.append(
            f"疑似翻案腔变形，第 {line_number(text, match.start())} 行："
            f"\u201c{excerpt(match.group(), 40)}\u201d。"
            f"先立误解再推翻就改成正面陈述，正常用法保留。"
        )

    # 7. 三连以上同构排比
    anaphoras = anaphora_runs(prose)
    for match in anaphoras[:4]:
        warnings.append(
            f"三连以上同构排比，第 {line_number(text, match.start())} 行："
            f"\u201c{excerpt(match.group(), 40)}\u201d。留两项，第三项换说法或删掉。"
        )

    # 8. 名词化句式
    nominalizations = all_matches(prose, NOMINALIZATION_PATTERNS)
    for match in nominalizations[:4]:
        warnings.append(
            f"名词化句式，第 {line_number(text, match.start())} 行："
            f"\u201c{excerpt(match.group(), 36)}\u201d。还原成直接的动词。"
        )

    # 9. 连词密度
    conjunction_hits = non_overlapping_terms(prose, CONJUNCTIONS)
    if total_han >= 600:
        density = len(conjunction_hits) * 1000 / total_han
        if density > 7:
            samples = "、".join(
                f"{term} {count} 次"
                for term, count in collections.Counter(
                    term for _, term in conjunction_hits
                ).most_common(4)
            )
            warnings.append(
                f"连词密度偏高，每千字 {int(density)} 个。{samples}。"
                f"中文小句靠语序和事理相接，删掉一半试试。"
            )

    # 10. 句长变异系数
    cv_result = sentence_length_cv(prose)
    if cv_result and cv_result[0] < 0.42:
        warnings.append(
            f"全文 {cv_result[1]} 个句子长度过于接近（变异系数 {cv_result[0]:.2f}）。"
            f"人写的段落里十个字的句子会挨着四十个字的句子，放开几句，压短几句。"
        )

    # 11. 软标记词密度
    marker_matches = non_overlapping_terms(prose, SOFT_MARKERS)
    marker_limit = max(2, total_han // 900)
    if len(marker_matches) > marker_limit:
        samples = "、".join(dict.fromkeys(term for _, term in marker_matches))
        warnings.append(
            f"洞察路标共 {len(marker_matches)} 处（提醒线 {marker_limit}）。"
            f"检查 {samples}。"
        )

    # 12. 重定语句
    dense_de = heavy_de_sentences(prose)
    dense_de_limit = max(1, total_han // 1500)
    if len(dense_de) > dense_de_limit:
        samples = "；".join(
            f"第 {line_number(text, m.start())} 行\u201c{excerpt(m.group(), 40)}\u201d"
            for m in dense_de[:4]
        )
        warnings.append(
            f"有 {len(dense_de)} 个长句包含四个以上的\u201c的\u201d，可能要先交代人和动作。{samples}"
        )

    # 13. 段落结构检测
    paragraphs = prose_paragraphs(prose)
    if len(paragraphs) >= 10:
        one_sentence = sum(p["sentences"] <= 1 for p in paragraphs)
        ratio = one_sentence / len(paragraphs)
        if ratio >= 0.75:
            warnings.append(
                f"可识别段落中有 {ratio:.0%} 只有一句话，可能形成统一的短段鼓点。"
            )

    # 14. 连续短促单句段
    streak = short_streak(paragraphs)
    if streak:
        first = streak[0]
        warnings.append(
            f"从第 {line_number(text, first['position'])} 行起连续出现 {len(streak)} 个短促单句段，"
            f"检查是否在排队喊结论。"
        )

    # 15. 段落开场重复
    counts, opener_examples = opener_counts(paragraphs)
    repeated = [(opener, count) for opener, count in counts.items() if count >= 4]
    if repeated:
        details = "、".join(f"{opener} {count} 次" for opener, count in repeated)
        first_position = min(opener_examples[opener] for opener, _ in repeated)
        warnings.append(
            f"段落开场重复，从第 {line_number(text, first_position)} 行附近开始。{details}。"
        )

    # --- 输出统计 ---

    print(f"汉字数 {total_han}")
    print(
        f"翻案句 {len(pivots)}，翻案变形 {len(warnings) - len(failures)}，"
        f"同构排比 {len(anaphoras)}，名词化 {len(nominalizations)}，"
        f"黑话 {len(jargon_matches)}，硬停词 {len(stop_matches)}，"
        f"模型路标 {len(road_signs)}"
    )

    if failures:
        print("\n=== 需要修改（硬禁令） ===")
        for item in failures:
            print(f"  [FAIL] {item}")

    if warnings:
        print("\n=== 需要人工判断 ===")
        for item in warnings:
            print(f"  [WARN] {item}")

    if not failures and not warnings:
        print("\n未发现这份检查器覆盖的问题。")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
