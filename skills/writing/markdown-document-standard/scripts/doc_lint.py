#!/usr/bin/env python3
"""Static Markdown checks for technical documents.

Stdlib only. Parses a CommonMark subset: ATX headings, fenced code,
inline links, GFM-style tables. It cannot validate technical correctness,
diagram semantics, or rendered output.
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

SCHEMA_VERSION = 1

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([^`~]*)$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SEP_CELL_RE = re.compile(r"^:?-{3,}:?$")
NUMBER_RE = re.compile(r"^(\d+)(?:\.(\d+))?\.\s")
CAPTION_RE = re.compile(r"^\s*(?:\*\*)?\s*(?:图\s*[0-9０-９一二三四五六七八九十]+|图注|图表?\s*[:：]|表\s*[0-9０-９一二三四五六七八九十]+)")
UNICODE_BOX_CHARS = set("┌┐└┘├┤┬┴┼─│")
ARROW_CHARS = set("▼▲◀▶→←↑↓")
PLACEHOLDER_RE = re.compile(r"<[^<>\n]+>|待补充|未核验")

CHECK_REGISTRY = {
    "MD001": ("error", "new", "文档必须恰好有一个 H1"),
    "MD002": ("error", "new", "标题层级不得跳级"),
    "MD003": ("warn", "all", "标题 slug 不得重复"),
    "MD004": ("warn", "all", "编号章节必须连续"),
    "MD005": ("error", "all", "代码围栏必须闭合"),
    "MD006": ("warn", "all", "代码围栏应有语言标识"),
    "MD007": ("error", "all", "表格分隔行必须合法"),
    "MD008": ("error", "new", "表格各行列数必须一致"),
    "MD009": ("warn", "all", "非代码区域不得有行尾空格"),
    "MD010": ("warn", "all", "代码区域外不得使用 Tab"),
    "MD011": ("warn", "all", "不得连续出现超过两个空行"),
    "MD012": ("error", "all", "相对链接目标必须存在"),
    "MD013": ("warn", "all", "链接锚点必须能匹配目标标题"),
    "MD014": ("error", "new", "ASCII 图显示宽度不得超过限制"),
    "MD015": ("error", "new", "ASCII 图内不得使用 Tab"),
    "MD016": ("warn", "all", "ASCII 图不得混用框线风格"),
    "MD017": ("warn", "all", "ASCII 图应有图注"),
    "MD018": ("warn", "all", "指定文档类型时必需元数据键应齐全"),
    "MD019": ("info", "all", "元数据或正文存在占位符"),
    "MD020": ("info", "all", "出现 Mermaid 图，需确认是否为显式要求"),
}

LEGACY_DOWNGRADE = {"MD001", "MD002", "MD008", "MD014", "MD015"}

METADATA_KEYS = {
    "design": ["文档类型", "状态", "适用版本", "证据基线", "最后核验"],
    "plan": ["文档类型", "状态", "适用版本", "证据基线", "计划范围", "最后核验"],
    "rca": ["文档类型", "状态", "适用版本", "证据基线", "事件日期", "处置状态", "最后核验"],
    "review": ["文档类型", "状态", "适用版本", "证据基线", "评审对象", "评审结论", "最后核验"],
}


@dataclass
class Finding:
    code: str
    severity: str
    line: int
    column: int
    message: str


@dataclass
class Fence:
    start: int          # 1-based opening fence line
    end: Optional[int]  # 1-based closing fence line, None if unclosed
    marker: str
    info: str
    content: List[str] = field(default_factory=list)


@dataclass
class Config:
    profile: str = "new"
    max_ascii_width: int = 100
    require_ascii_caption: bool = True
    doctype: Optional[str] = None
    root: Optional[Path] = None
    strict: bool = False
    ignore: Set[str] = field(default_factory=set)


class Linter:
    def __init__(self, path: Path, cfg: Config):
        self.path = path
        self.cfg = cfg
        self.lines = read_document(path)
        self.findings: List[Finding] = []
        self.fences = scan_fences(self.lines)
        self.fence_mask = fence_mask(self.lines, self.fences)
        self.frontmatter_end = frontmatter_length(self.lines)
        self.headings = parse_headings(self.lines, self.fence_mask, self.frontmatter_end)

    def add(self, code: str, line: int, column: int, message: str) -> None:
        if code in self.cfg.ignore:
            return
        severity = CHECK_REGISTRY[code][0]
        if self.cfg.profile == "legacy" and code in LEGACY_DOWNGRADE:
            severity = "warn"
        self.findings.append(Finding(code, severity, max(1, line), max(0, column), message))

    def run(self) -> List[Finding]:
        self.check_headings()
        self.check_numbering()
        self.check_fences()
        self.check_tables()
        self.check_whitespace()
        self.check_links()
        self.check_ascii()
        self.check_metadata()
        self.findings.sort(key=lambda f: (f.line, f.column, f.code))
        return self.findings

    # ---- headings -------------------------------------------------------

    def check_headings(self) -> None:
        h1 = [h for h in self.headings if h[1] == 1]
        if len(h1) != 1:
            self.add("MD001", h1[1][0] if len(h1) > 1 else 1, 0,
                     "found %d H1 headings; exactly one is required" % len(h1))
        prev_level = 0
        for line, level, text in self.headings:
            if prev_level and level > prev_level + 1:
                self.add("MD002", line, 0,
                         "heading jumps from H%d to H%d" % (prev_level, level))
            prev_level = level
        seen: Dict[str, int] = {}
        for line, level, text in self.headings:
            slug = slugify(text)
            if slug in seen:
                self.add("MD003", line, 0,
                         "duplicate heading slug %r (first at line %d)" % (slug, seen[slug]))
            else:
                seen[slug] = line

    def check_numbering(self) -> None:
        h2_numbers = []
        for line, level, text in self.headings:
            m = NUMBER_RE.match(text)
            if level == 2 and m and m.group(2) is None:
                h1_n = int(m.group(1))
                h2_numbers.append((line, h1_n))
            elif level == 3 and m and m.group(2) is not None:
                pass
        expected = None
        for line, n in h2_numbers:
            if expected is None:
                expected = n + 1
            elif n != expected:
                self.add("MD004", line, 0,
                         "H2 numbering is %d, expected %d" % (n, expected))
                expected = n + 1
            else:
                expected += 1
        # H3 continuity grouped by major number.
        current_major = None
        expected_minor = None
        for line, level, text in self.headings:
            m = NUMBER_RE.match(text)
            if level != 3 or not m or m.group(2) is None:
                continue
            major, minor = int(m.group(1)), int(m.group(2))
            if major != current_major:
                current_major, expected_minor = major, minor + 1
            elif minor != expected_minor:
                self.add("MD004", line, 0,
                         "H3 numbering is %d.%d, expected %d.%d" % (major, minor, major, expected_minor))
                expected_minor = minor + 1
            else:
                expected_minor += 1

    # ---- fences ---------------------------------------------------------

    def check_fences(self) -> None:
        for fence in self.fences:
            if fence.end is None:
                self.add("MD005", fence.start, 0, "unclosed code fence")
                continue
            info = fence.info.strip().split()[0].lower() if fence.info.strip() else ""
            if not info:
                self.add("MD006", fence.start, 0, "code fence has no language identifier")
            if info == "mermaid":
                self.add("MD020", fence.start, 0,
                         "Mermaid diagram present; confirm explicit user request or platform requirement")

    # ---- tables ---------------------------------------------------------

    def check_tables(self) -> None:
        i = 0
        n = len(self.lines)
        while i < n:
            if self.fence_mask[i] or i <= self.frontmatter_end:
                i += 1
                continue
            line = self.lines[i]
            if "|" not in line:
                i += 1
                continue
            nxt = self.lines[i + 1] if i + 1 < n else ""
            if i + 1 < n and not self.fence_mask[i + 1] and "|" in nxt and "---" in nxt:
                sep_cells = split_table_cells(nxt)
                if not sep_cells or not all(SEP_CELL_RE.match(c.strip()) for c in sep_cells):
                    self.add("MD007", i + 2, 0, "malformed table separator row")
                    i += 1
                    continue
                header = split_table_cells(line)
                if len(header) != len(sep_cells):
                    self.add("MD008", i + 1, 0,
                             "header has %d columns, separator has %d" % (len(header), len(sep_cells)))
                j = i + 2
                while j < n and not self.fence_mask[j] and self.lines[j].strip() and "|" in self.lines[j]:
                    if self.lines[j].lstrip().startswith("#"):
                        break
                    cells = split_table_cells(self.lines[j])
                    if len(cells) != len(sep_cells):
                        self.add("MD008", j + 1, 0,
                                 "row has %d columns, separator has %d" % (len(cells), len(sep_cells)))
                    j += 1
                i = j
            else:
                i += 1

    # ---- whitespace -----------------------------------------------------

    def check_whitespace(self) -> None:
        blanks = 0
        for idx, raw in enumerate(self.lines):
            line_no = idx + 1
            if raw.strip() == "":
                blanks += 1
                if blanks > 2 and not self.fence_mask[idx]:
                    self.add("MD011", line_no, 0, "more than two consecutive blank lines")
                continue
            blanks = 0
            if self.fence_mask[idx]:
                continue
            if raw.rstrip("\n") != raw.rstrip():
                self.add("MD009", line_no, len(raw.rstrip()), "trailing whitespace")
            if "\t" in raw:
                self.add("MD010", line_no, raw.index("\t") + 1, "tab outside code")

    # ---- links ----------------------------------------------------------

    def check_links(self) -> None:
        for idx, raw in enumerate(self.lines):
            if self.fence_mask[idx] or idx <= self.frontmatter_end:
                continue
            visible = re.sub(r"`[^`]*`", "", raw)
            for m in LINK_RE.finditer(visible):
                target = m.group(1).strip()
                self._check_link(target, idx + 1, m.start())

    def _check_link(self, target: str, line: int, column: int) -> None:
        if not target:
            return
        target = target.split()[0].strip("<>")
        if not target or target.startswith("#"):
            if target.startswith("#") and len(target) > 1:
                self._check_anchor(target[1:], self.path, line, column)
            return
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            return
        if target.startswith("/") or any(ch in target for ch in "<>{}*|"):
            return
        path_part, _, anchor = target.partition("#")
        path_part = path_part.split("?")[0]
        if not path_part:
            return
        base = self.cfg.root or self.path.parent
        resolved = (base / path_part).resolve()
        if not resolved.exists():
            self.add("MD012", line, column, "relative link target not found: %s" % path_part)
            return
        if anchor and resolved.suffix.lower() == ".md":
            self._check_anchor(anchor, resolved, line, column)

    def _check_anchor(self, anchor: str, md_path: Path, line: int, column: int) -> None:
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError:
            return
        lines = text.splitlines()
        fences = scan_fences(lines)
        mask = fence_mask(lines, fences)
        headings = parse_headings(lines, mask, frontmatter_length(lines))
        slugs = {slugify(h[2]) for h in headings}
        if anchor.lower() not in slugs:
            self.add("MD013", line, column,
                     "anchor #%s not found in %s" % (anchor, md_path.name))

    # ---- ASCII diagrams -------------------------------------------------

    def check_ascii(self) -> None:
        for fence in self.fences:
            if fence.end is None or not is_ascii_diagram(fence):
                continue
            self._check_ascii_fence(fence)

    def _check_ascii_fence(self, fence: Fence) -> None:
        max_width = 0
        max_line = fence.start
        has_unicode = False
        has_ascii_box = False
        for offset, text in enumerate(fence.content):
            line_no = fence.start + 1 + offset
            if "\t" in text:
                self.add("MD015", line_no, text.index("\t") + 1, "tab inside ASCII diagram")
            width = display_width(text)
            if width > max_width:
                max_width, max_line = width, line_no
            if any(ch in UNICODE_BOX_CHARS for ch in text):
                has_unicode = True
            if re.search(r"\+[-=]{2,}\+", text):
                has_ascii_box = True
        if max_width > self.cfg.max_ascii_width:
            self.add("MD014", max_line, 0,
                     "ASCII diagram width %d exceeds %d columns" % (max_width, self.cfg.max_ascii_width))
        if has_unicode and has_ascii_box:
            self.add("MD016", fence.start, 0, "ASCII diagram mixes Unicode and ASCII box styles")
        if self.cfg.require_ascii_caption and not has_caption(self.lines, fence):
            self.add("MD017", fence.start, 0, "ASCII diagram has no caption")

    # ---- metadata -------------------------------------------------------

    def check_metadata(self) -> None:
        if not self.cfg.doctype:
            return
        required = METADATA_KEYS[self.cfg.doctype]
        found = collect_metadata_keys(self.lines, self.frontmatter_end, self.headings)
        missing = [k for k in required if k not in found]
        if missing:
            self.add("MD018", 1, 0, "missing metadata keys: %s" % ", ".join(missing))
        for idx, raw in enumerate(self.lines[:40]):
            if PLACEHOLDER_RE.search(raw):
                self.add("MD019", idx + 1, 0, "placeholder remains: %s" % raw.strip()[:60])
                break


# ---- parsing helpers ----------------------------------------------------

def read_document(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8-sig")
    return text.splitlines()


def frontmatter_length(lines: Sequence[str]) -> int:
    if not lines or lines[0].strip() != "---":
        return -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() in ("---", "..."):
            return idx
    return -1


def scan_fences(lines: Sequence[str]) -> List[Fence]:
    fences: List[Fence] = []
    open_fence: Optional[Fence] = None
    for idx, raw in enumerate(lines):
        m = FENCE_RE.match(raw)
        if not m:
            if open_fence is not None:
                open_fence.content.append(raw)
            continue
        marker = m.group(1)
        info = m.group(2).strip()
        if open_fence is None:
            open_fence = Fence(start=idx + 1, end=None, marker=marker, info=info)
            fences.append(open_fence)
        elif marker[0] == open_fence.marker[0] and len(marker) >= len(open_fence.marker):
            open_fence.end = idx + 1
            open_fence = None
        else:
            open_fence.content.append(raw)
    return fences


def fence_mask(lines: Sequence[str], fences: Sequence[Fence]) -> List[bool]:
    mask = [False] * len(lines)
    for fence in fences:
        end = fence.end if fence.end is not None else len(lines)
        for idx in range(fence.start - 1, min(end, len(lines))):
            mask[idx] = True
    return mask


def parse_headings(lines: Sequence[str], mask: Sequence[bool], fm_end: int) -> List[Tuple[int, int, str]]:
    headings = []
    for idx, raw in enumerate(lines):
        if idx <= fm_end or mask[idx]:
            continue
        m = HEADING_RE.match(raw)
        if m:
            headings.append((idx + 1, len(m.group(1)), m.group(2).strip()))
    return headings


def slugify(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w一-鿿\-\s]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return re.sub(r"-{2,}", "-", text)


def split_table_cells(line: str) -> List[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells: List[str] = []
    buf: List[str] = []
    in_code = False
    escaped = False
    for ch in s:
        if escaped:
            buf.append(ch)
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            buf.append(ch)
            continue
        if ch == "`":
            in_code = not in_code
            buf.append(ch)
            continue
        if ch == "|" and not in_code:
            cells.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    cells.append("".join(buf).strip())
    return cells


def display_width(text: str) -> int:
    width = 0
    for ch in text:
        if ch == "\t":
            width += 4
        elif unicodedata.combining(ch):
            continue
        else:
            width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def is_ascii_diagram(fence: Fence) -> bool:
    info = fence.info.strip().split()[0].lower() if fence.info.strip() else ""
    if info in ("ascii", "diagram"):
        return True
    if info not in ("", "text", "plain", "plaintext"):
        return False
    joined = "\n".join(fence.content)
    return any(ch in UNICODE_BOX_CHARS for ch in joined) or any(ch in ARROW_CHARS for ch in joined) or bool(
        re.search(r"\+[-=]{2,}\+", joined)
    )


def has_caption(lines: Sequence[str], fence: Fence) -> bool:
    end = fence.end if fence.end is not None else fence.start
    before = lines[max(0, fence.start - 3):fence.start - 1]
    after = lines[end:min(len(lines), end + 4)]
    return any(CAPTION_RE.match(line) for line in list(before) + list(after))


def collect_metadata_keys(lines: Sequence[str], fm_end: int, headings: Sequence[Tuple[int, int, str]]) -> Set[str]:
    keys: Set[str] = set()
    start = fm_end + 1
    end = min(len(lines), start + 40)
    for idx in range(start, end):
        raw = lines[idx].strip()
        if raw.startswith("|"):
            cells = split_table_cells(raw)
            if len(cells) >= 2:
                keys.add(cells[0].strip())
        if raw.startswith(">"):
            body = raw.lstrip(">").strip()
            for part in re.split(r"[\s　]+(?=[^\s：:]+[：:])", body):
                m = re.match(r"([^：:]+)[：:]\s*(.*)", part)
                if m:
                    keys.add(m.group(1).strip())
    return keys


# ---- reporting ----------------------------------------------------------

def lint_file(path: Path, cfg: Config) -> List[Finding]:
    try:
        return Linter(path, cfg).run()
    except (OSError, UnicodeDecodeError) as exc:
        return [Finding("IO", "error", 1, 0, "cannot read %s: %s" % (path, exc))]


def collect_files(paths: Sequence[str]) -> List[Path]:
    files: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for child in sorted(p.rglob("*.md")):
                if any(part.startswith(".") for part in child.parts):
                    continue
                if "__pycache__" in child.parts:
                    continue
                files.append(child)
        elif p.is_file():
            files.append(p)
        else:
            raise FileNotFoundError(str(p))
    return files


def render_text(results: Sequence[Tuple[Path, List[Finding]]], quiet: bool) -> str:
    out: List[str] = []
    total_err = total_warn = 0
    for path, findings in results:
        for f in findings:
            if f.severity == "error":
                total_err += 1
            elif f.severity == "warn":
                total_warn += 1
            if quiet and f.severity != "error":
                continue
            out.append("%s:%d:%d: %s %s %s" % (path, f.line, f.column, f.severity, f.code, f.message))
    out.append("%d error(s), %d warning(s), %d file(s)" % (total_err, total_warn, len(results)))
    out.append("static checks finished; human review is still required")
    return "\n".join(out)


def render_json(results: Sequence[Tuple[Path, List[Finding]]], cfg: Config) -> str:
    files = []
    total_err = total_warn = 0
    for path, findings in results:
        errors = sum(1 for f in findings if f.severity == "error")
        warnings = sum(1 for f in findings if f.severity == "warn")
        total_err += errors
        total_warn += warnings
        files.append({
            "path": str(path),
            "errors": errors,
            "warnings": warnings,
            "findings": [
                {"code": f.code, "severity": f.severity, "line": f.line,
                 "column": f.column, "message": f.message}
                for f in findings
            ],
        })
    payload = {
        "schema_version": SCHEMA_VERSION,
        "profile": cfg.profile,
        "files": files,
        "summary": {"files": len(files), "errors": total_err, "warnings": total_warn},
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Static Markdown checks for technical documents. "
                    "Cannot validate technical correctness or rendered output.",
    )
    parser.add_argument("paths", nargs="*", help="Markdown files or directories")
    parser.add_argument("--profile", choices=["new", "legacy"], default="new")
    parser.add_argument("--strict", action="store_true", help="warnings also cause exit 1")
    parser.add_argument("--json", nargs="?", const="-", metavar="PATH",
                        help="write JSON report to PATH ('-' for stdout)")
    parser.add_argument("--doctype", choices=sorted(METADATA_KEYS))
    parser.add_argument("--ascii-max-width", type=int, default=100)
    parser.add_argument("--root", metavar="DIR", help="base directory for relative links")
    parser.add_argument("--ignore", default="", help="comma-separated check codes to ignore")
    parser.add_argument("--list-checks", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if args.list_checks:
        for code, (severity, profile, desc) in sorted(CHECK_REGISTRY.items()):
            print("%s\t%s\t%s\t%s" % (code, severity, profile, desc))
        return 0
    if not args.paths:
        print("error: no input files", file=sys.stderr)
        return 2
    if args.ascii_max_width < 20:
        print("error: --ascii-max-width must be >= 20", file=sys.stderr)
        return 2
    cfg = Config(
        profile=args.profile,
        max_ascii_width=args.ascii_max_width,
        doctype=args.doctype,
        root=Path(args.root).resolve() if args.root else None,
        strict=args.strict,
        ignore={c.strip() for c in args.ignore.split(",") if c.strip()},
    )
    try:
        files = collect_files(args.paths)
    except FileNotFoundError as exc:
        print("error: path not found: %s" % exc, file=sys.stderr)
        return 2
    results = [(path, lint_file(path, cfg)) for path in files]
    if args.json:
        payload = render_json(results, cfg)
        if args.json == "-":
            print(payload)
        else:
            Path(args.json).write_text(payload + "\n", encoding="utf-8")
    else:
        print(render_text(results, args.quiet))
    errors = sum(1 for _, fs in results for f in fs if f.severity == "error")
    warnings = sum(1 for _, fs in results for f in fs if f.severity == "warn")
    if errors:
        return 1
    if cfg.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
