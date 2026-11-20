#!/usr/bin/env python3
"""Static audit and registry generator for the personal skill library.

Checks skill structure, frontmatter, local references, workflow/command wiring,
duplicate names, generated-file drift and obvious desensitization risks.

Usage:
    python3 scripts/skill_audit.py --check
    python3 scripts/skill_audit.py --write
    python3 scripts/skill_audit.py --json
    python3 scripts/skill_audit.py --scope hans,personal,workbuddy
    python3 scripts/skill_audit.py --check --strict-cross-repo

Stdlib only. Python 3.9+.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HANS = SCRIPT_DIR.parent
WORKSPACE = HANS.parent
OUT_DIR = HANS / "docs" / "optimization"
REGISTRY_JSON = OUT_DIR / "skill_registry.json"

REPO_ORDER = ["hans", "personal", "workbuddy", "installed"]
SCOPE_DEFAULT = "hans,personal"

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
FENCE_RE = re.compile(r"```.*?```", re.S)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NEAR_MISS_RE = re.compile(r"Not for|不用于|不负责|不适用|不直接")
LOCAL_REF_RE = re.compile(r"^(?:references|scripts|assets|templates|shared)/[A-Za-z0-9._/-]+$")
PARENT_REF_RE = re.compile(r"^\.\./[A-Za-z0-9._/-]+$")
DOC_ROOT_PREFIXES = ("references/", "scripts/", "assets/", "templates/", "shared/", "skills/", "workflows/", "commands/", "docs/")

ALLOWED_FRONTMATTER = {"name", "description", "allowed-tools", "metadata", "license"}


class Audit:
    def __init__(self):
        self.findings = []
        self.errors = 0
        self.warnings = 0

    def add(self, level, check, path, message):
        self.findings.append({"level": level, "check": check, "path": str(path), "message": message})
        if level == "error":
            self.errors += 1
        elif level == "warn":
            self.warnings += 1


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def rel(path, root):
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing frontmatter (first line must be ---)"
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, "unterminated frontmatter"
    data = {}
    i = 1
    while i < end:
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in ("|", ">", "|-", ">-", "|+", ">+"):
            block = []
            i += 1
            while i < end and (lines[i].startswith("  ") or lines[i].strip() == ""):
                block.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            joiner = "\n" if val.startswith("|") else " "
            data[key] = joiner.join(block).strip()
            continue
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        data[key] = val
        i += 1
    return data, None


def repo_root(name):
    if name == "hans":
        return HANS
    if name == "personal":
        return WORKSPACE / "personal-notes"
    if name == "workbuddy":
        return WORKSPACE / "workbuddy-agents"
    return Path.home() / ".claude" / "skills"


def discover_skills(scopes, audit):
    """Return (in_scope, all_skills). all_skills enables cross-repo name resolution."""
    in_scope = []
    all_skills = []
    seen = set()

    def add(scope, root, skill_dir, category):
        skill_md = skill_dir / "SKILL.md"
        key = (scope, skill_md)
        if key in seen:
            return
        seen.add(key)
        item = {"repo_scope": scope, "root": root, "dir": skill_dir, "skill_md": skill_md, "category": category}
        all_skills.append(item)
        if scope in scopes:
            in_scope.append(item)

    hans = repo_root("hans")
    if (hans / "skills").exists():
        for p in sorted((hans / "skills").glob("*/*/SKILL.md")):
            add("hans", hans, p.parent, p.parent.parent.name)

    personal = repo_root("personal")
    if (personal / "skills").exists():
        for p in sorted((personal / "skills").glob("*/SKILL.md")):
            add("personal", personal, p.parent, "project")

    workbuddy = repo_root("workbuddy")
    if (workbuddy / "skills").exists():
        for p in sorted((workbuddy / "skills").glob("*/SKILL.md")):
            add("workbuddy", workbuddy, p.parent, "global")
        for p in sorted((workbuddy / "experts").glob("*/skills/*/SKILL.md")):
            add("workbuddy", workbuddy, p.parent, "expert:" + p.parent.parent.parent.name)

    installed = repo_root("installed")
    if installed.exists():
        for p in sorted(installed.glob("*/SKILL.md")):
            add("installed", installed, p.parent, "installed")

    return in_scope, all_skills


def skill_line_count(path):
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        return 0


def check_frontmatter(audit, item, config):
    path = item["skill_md"]
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        audit.add("error", "frontmatter", path, "cannot read SKILL.md: %s" % exc)
        return None
    data, err = parse_frontmatter(text)
    if err:
        audit.add("error", "frontmatter", path, err)
        return None
    name = data.get("name", "")
    desc = data.get("description", "")
    if not name:
        audit.add("error", "frontmatter", path, "missing name")
    elif not NAME_RE.match(name):
        audit.add("error", "frontmatter", path, "name is not kebab-case: %r" % name)
    elif name != item["dir"].name:
        audit.add("error", "frontmatter", path, "name %r != directory %r" % (name, item["dir"].name))
    if not desc:
        audit.add("error", "frontmatter", path, "missing or empty description")
    else:
        if len(desc) > 1536:
            audit.add("error", "frontmatter", path, "description too long (%d chars, limit 1536)" % len(desc))
        if not NEAR_MISS_RE.search(desc):
            audit.add("warn", "frontmatter", path, "description has no near-miss clause (Not for/不用于/不负责/不适用)")
    for key in data:
        if key not in ALLOWED_FRONTMATTER:
            audit.add("warn", "frontmatter", path, "unknown frontmatter key %r" % key)
    lines = len(text.splitlines())
    if lines > config.get("size", {}).get("skill_warn", 300):
        audit.add("warn", "size", path, "SKILL.md %d lines (> %d)" % (lines, config["size"]["skill_warn"]))
    data["_lines"] = lines
    data["_text"] = text
    return data


def strip_fences(text):
    return FENCE_RE.sub("", text)


def resolve_ref(target, base_dir, hans_root):
    target = target.split("#", 1)[0].strip()
    if not target:
        return None, "empty"
    if target.startswith(("http://", "https://", "mailto:", "/")):
        return None, "external"
    if any(ch in target for ch in ("<", ">", "{", "}", "*", "|")):
        return None, "placeholder"
    if re.match(r"^[A-Za-z]+:", target):
        return None, "uri-like"
    if "@" in target or ":" in target:
        return None, "filename:line or symbol"
    candidate = (base_dir / target).resolve()
    if candidate.exists():
        return candidate, None
    # Reference files often cite sibling assets as if from the skill root
    # (e.g. references/framework.md citing references/verification.md).
    for parent in base_dir.parents:
        if parent == WORKSPACE:
            break
        alt = (parent / target).resolve()
        if alt.exists():
            return alt, None
    # Workflow/docs references to repo-level directories.
    for prefix in DOC_ROOT_PREFIXES:
        if target.startswith(prefix):
            alt = (hans_root / target).resolve()
            if alt.exists():
                return alt, None
    return candidate, "missing"


def check_references(audit, md_files, hans_root):
    for path in md_files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for target in LINK_RE.findall(strip_fences(text)):
            resolved, reason = resolve_ref(target, path.parent, hans_root)
            if reason == "missing":
                audit.add("error", "reference", path, "missing link target: %s" % target)
        for token in BACKTICK_RE.findall(text):
            token = token.strip()
            if not (LOCAL_REF_RE.match(token) or PARENT_REF_RE.match(token)):
                continue
            resolved, reason = resolve_ref(token, path.parent, hans_root)
            if reason == "missing":
                audit.add("error", "reference", path, "missing path reference: %s" % token)


def is_skill_token(token, prefixes):
    return any(token.startswith(p) for p in prefixes) and NAME_RE.match(token) is not None


def check_skill_name_refs(audit, md_files, all_names, prefixes):
    for path in md_files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for token in BACKTICK_RE.findall(text):
            token = token.strip()
            if is_skill_token(token, prefixes) and token not in all_names:
                audit.add("error", "skill-ref", path, "referenced skill does not exist: %s" % token)


def check_workflows(audit, config, all_names, prefixes):
    wf_dir = HANS / "workflows"
    require = config.get("required_workflow_sections", [])
    if not wf_dir.exists():
        audit.add("error", "workflow", wf_dir, "workflows directory missing")
        return []
    workflows = []
    for wf in sorted(wf_dir.glob("*/WORKFLOW.md")):
        try:
            text = wf.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        name = wf.parent.name
        for section in require:
            if section not in text:
                audit.add("error", "workflow", wf, "missing required section/content: %s" % section)
        refs = []
        for token in BACKTICK_RE.findall(text):
            token = token.strip()
            if is_skill_token(token, prefixes):
                refs.append(token)
                if token not in all_names:
                    audit.add("error", "workflow", wf, "references missing skill: %s" % token)
        refs = sorted(set(refs))
        if len(refs) < 2:
            audit.add("warn", "workflow", wf, "references fewer than 2 skills (%d)" % len(refs))
        workflows.append({"name": name, "path": rel(wf, HANS), "skills": refs,
                          "sha256": sha256_bytes(wf.read_bytes())})
    return workflows


def check_commands(audit, workflows):
    cmd_dir = HANS / "commands"
    commands = []
    if not cmd_dir.exists():
        return commands
    wf_names = {w["name"] for w in workflows}
    for cmd in sorted(cmd_dir.glob("*.md")):
        data, err = parse_frontmatter(cmd.read_text(encoding="utf-8"))
        if err:
            audit.add("error", "command", cmd, err)
            continue
        unknown = [k for k in data if k not in ("description", "argument-hint")]
        if unknown:
            audit.add("warn", "command", cmd, "unknown frontmatter key(s): %s" % ", ".join(unknown))
        if cmd.stem not in wf_names:
            audit.add("error", "command", cmd, "no matching workflows/%s/WORKFLOW.md" % cmd.stem)
        commands.append({"name": cmd.stem, "path": rel(cmd, HANS), "workflow": cmd.stem,
                         "sha256": sha256_bytes(cmd.read_bytes())})
    return commands


def check_generated(audit, config, write):
    base = config.get("generated", {})
    canonical_rel = "shared/references/method-and-evidence.md"
    canonical = HANS / canonical_rel
    if not canonical.exists():
        return
    canonical_bytes = canonical.read_bytes()
    canonical_hash = sha256_bytes(canonical_bytes)
    personal_base = config.get("generated_personal", {})
    targets = [(HANS, r) for r in base.get(canonical_rel, [])]
    targets += [(repo_root("personal"), r) for r in personal_base.get(canonical_rel, [])]
    for root, skill_rel in targets:
        target = root / skill_rel / "references" / "shared-method.md"
        if write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(canonical_bytes)
            continue
        if not target.exists():
            audit.add("error", "generated", target, "missing generated copy of %s" % canonical_rel)
            continue
        if sha256_bytes(target.read_bytes()) != canonical_hash:
            audit.add("error", "generated", target, "generated copy drifted from %s" % canonical_rel)


GENERATED_TEMPLATE_HEADER = (
    "<!-- Generated from templates/%s; do not edit. "
    "Run scripts/skill_audit.py --write. -->\n\n"
)


def check_generated_templates(audit, config, write):
    targets = config.get("generated_templates", {}).get("templates", [])
    tpl_dir = HANS / "templates"
    if not targets or not tpl_dir.exists():
        return
    for skill_rel in targets:
        dest_dir = HANS / skill_rel / "assets" / "templates"
        for tpl in sorted(tpl_dir.glob("*.md")):
            expected = (GENERATED_TEMPLATE_HEADER % tpl.name).encode("utf-8") + tpl.read_bytes()
            target = dest_dir / tpl.name
            if write:
                dest_dir.mkdir(parents=True, exist_ok=True)
                target.write_bytes(expected)
                continue
            if not target.exists():
                audit.add("error", "generated", target,
                          "missing generated copy of templates/%s" % tpl.name)
                continue
            if target.read_bytes() != expected:
                audit.add("error", "generated", target,
                          "generated template drifted from templates/%s" % tpl.name)


def check_templates(audit):
    tpl_dir = HANS / "templates"
    if not tpl_dir.exists():
        return []
    templates = []
    search_files = []
    for root in (HANS / "skills", HANS / "workflows", HANS / "commands", HANS / "docs"):
        if root.exists():
            search_files.extend(sorted(root.rglob("*.md")))
    for tpl in sorted(tpl_dir.glob("*.md")):
        cited = []
        needle = tpl.name
        for path in search_files:
            if rel(path, HANS).startswith("docs/optimization/"):
                continue
            try:
                if needle in path.read_text(encoding="utf-8"):
                    cited.append(rel(path, HANS))
            except (OSError, UnicodeDecodeError):
                continue
        if not cited:
            audit.add("warn", "template", tpl, "template is not cited by any skill/workflow/command/doc")
        templates.append({"path": rel(tpl, HANS), "cited_by": sorted(set(cited)),
                          "sha256": sha256_bytes(tpl.read_bytes())})
    return templates


def check_duplicates(audit, all_skills, allowlist):
    by_name = {}
    for item in all_skills:
        # Installed mirror duplicates are expected and skipped.
        if item["repo_scope"] == "installed":
            continue
        name = None
        try:
            data, _ = parse_frontmatter(item["skill_md"].read_text(encoding="utf-8"))
            name = (data or {}).get("name") or item["dir"].name
        except (OSError, UnicodeDecodeError):
            name = item["dir"].name
        by_name.setdefault(name, []).append(item)
    duplicates = []
    for name, items in sorted(by_name.items()):
        scopes = sorted({i["repo_scope"] for i in items})
        if len(scopes) <= 1:
            continue
        classification = "intentional-divergent" if name in allowlist else "unexpected"
        duplicates.append({"name": name, "repos": scopes, "classification": classification})
        if classification == "unexpected":
            audit.add("error", "duplicate", items[0]["skill_md"], "cross-repo duplicate name: %s" % name)
    return duplicates


def check_desensitize(audit, scopes, config):
    ds = config.get("desensitize", {})
    block = [re.compile(p) for p in ds.get("block_patterns", [])]
    warn_terms = ds.get("warn_terms", [])
    allow_prefixes = ds.get("allow_path_prefixes", [])
    scan_roots = []
    if "hans" in scopes:
        scan_roots.append((HANS, ["skills", "templates", "workflows", "commands", "shared", "docs", "CLAUDE.md"]))
    if "personal" in scopes:
        scan_roots.append((repo_root("personal"), ["skills"]))
    # Project terms are legitimate in the internal personal-notes repo; there only
    # credential/identity patterns are blocking.
    secret_patterns = block[:5]
    for root, subpaths in scan_roots:
        patterns = block if root == HANS else secret_patterns
        for sub in subpaths:
            p = root / sub
            files = [p] if p.is_file() else sorted(p.rglob("*.md")) if p.exists() else []
            for f in files:
                r = rel(f, root)
                if any(r.startswith(pref) for pref in allow_prefixes):
                    continue
                try:
                    text = f.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                for lineno, line in enumerate(text.splitlines(), 1):
                    for pat in patterns:
                        if pat.search(line):
                            audit.add("error", "desensitize", f, "line %d matches blocking pattern %s" % (lineno, pat.pattern))
                    for term in warn_terms:
                        if term in line:
                            audit.add("warn", "desensitize", f, "line %d mentions %s" % (lineno, term))


def build_entries(in_scope, config, audit):
    entries = []
    skills_by_dir = {}
    for item in sorted(in_scope, key=lambda i: (REPO_ORDER.index(i["repo_scope"]), rel(i["dir"], i["root"]))):
        data = check_frontmatter(audit, item, config)
        if data is None:
            continue
        files = {}
        for f in sorted(item["dir"].rglob("*")):
            if "__pycache__" in f.parts or f.suffix == ".pyc":
                continue
            if f.is_file():
                files[rel(f, item["dir"])] = sha256_bytes(f.read_bytes())
        entry = {
            "repo": item["repo_scope"],
            "scope": "claude" if item["repo_scope"] in ("hans", "personal") else "workbuddy",
            "category": item["category"],
            "path": rel(item["dir"], item["root"]),
            "name": data.get("name", item["dir"].name),
            "description_sha256": sha256_bytes(data.get("description", "").encode("utf-8")),
            "files": files,
            "authority": "canonical",
            "generated_files": [],
        }
        gen = config.get("generated", {}).get("shared/references/method-and-evidence.md", [])
        if entry["repo"] == "personal":
            gen = config.get("generated_personal", {}).get("shared/references/method-and-evidence.md", [])
        if entry["path"] in gen:
            entry["generated_files"] = ["references/shared-method.md"]
        entries.append(entry)
        skills_by_dir[(item["repo_scope"], entry["path"])] = entry
    return entries


def render_inventory(registry):
    lines = ["# Skill Inventory", "", "> Generated by `scripts/skill_audit.py --write`. Do not hand-edit.", "",
             "| Repo | Scope | Category | Name | Path | SKILL.md lines | Description (trimmed) |",
             "|---|---|---|---|---|---:|---|"]
    for e in registry["skills"]:
        root = repo_root(e["repo"])
        skill_md = root / e["path"] / "SKILL.md"
        n = skill_line_count(skill_md)
        desc = ""
        try:
            data, _ = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
            desc = ((data or {}).get("description") or "").replace("\n", " ")
        except (OSError, UnicodeDecodeError):
            pass
        if len(desc) > 90:
            desc = desc[:87] + "..."
        desc = desc.replace("|", "\\|")
        lines.append("| %s | %s | %s | `%s` | `%s` | %d | %s |" % (
            e["repo"], e["scope"], e["category"], e["name"], e["path"], n, desc))
    lines.append("")
    return "\n".join(lines)


def render_dependencies(registry):
    lines = ["# Skill Dependencies", "", "> Generated by `scripts/skill_audit.py --write`. Do not hand-edit.", "",
             "## Workflow -> Skill", "", "| Workflow | Skills |", "|---|---|"]
    for w in registry["workflows"]:
        lines.append("| `%s` | %s |" % (w["name"], ", ".join("`%s`" % s for s in w["skills"])))
    lines += ["", "## Command -> Workflow", "", "| Command | Workflow |", "|---|---|"]
    for c in registry["commands"]:
        lines.append("| `%s` | `%s` |" % (c["name"], c["workflow"]))
    lines += ["", "## Template -> Citing files", "", "| Template | Cited by |", "|---|---|"]
    for t in registry["templates"]:
        cited = "<br>".join("`%s`" % c for c in t["cited_by"]) or "(none)"
        lines.append("| `%s` | %s |" % (t["path"], cited))
    lines += ["", "## Skill -> Local files", "", "| Skill | Files |", "|---|---|"]
    for e in registry["skills"]:
        names = sorted(e["files"].keys())
        shown = ", ".join("`%s`" % n for n in names if n != "SKILL.md")
        lines.append("| `%s` (%s) | %s |" % (e["name"], e["repo"], shown or "(SKILL.md only)"))
    lines.append("")
    return "\n".join(lines)


def render_registry(registry):
    lines = ["# Skill Registry", "", "> Generated from SKILL.md frontmatter by `scripts/skill_audit.py --write`. Do not hand-edit.", "",
             "| Name | Repo | Category | Path | Files | Description sha256 |",
             "|---|---|---|---|---:|---|"]
    for e in registry["skills"]:
        lines.append("| `%s` | %s | %s | `%s` | %d | `%s` |" % (
            e["name"], e["repo"], e["category"], e["path"], len(e["files"]), e["description_sha256"][:16]))
    lines += ["", "## Cross-repo duplicates", ""]
    if registry["duplicates"]:
        lines.append("| Name | Repos | Classification |")
        lines.append("|---|---|---|")
        for d in registry["duplicates"]:
            lines.append("| `%s` | %s | %s |" % (d["name"], ", ".join(d["repos"]), d["classification"]))
    else:
        lines.append("(none)")
    lines.append("")
    return "\n".join(lines)


def collect_names(items):
    names = set()
    for item in items:
        try:
            data, _ = parse_frontmatter(item["skill_md"].read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        name = (data or {}).get("name")
        if name:
            names.add(name)
    return names


def build_registry(in_scope, config, audit, write):
    entries = build_entries(in_scope, config, audit)
    _, all_skills = discover_skills(set(), audit)
    names = {e["name"] for e in entries} | collect_names(all_skills)
    workflows = check_workflows(audit, config, names, config.get("skill_name_prefixes", []))
    commands = check_commands(audit, workflows)
    templates = check_templates(audit)
    duplicates = check_duplicates(audit, all_skills, set(config.get("duplicate_allowlist", [])))
    registry = {
        "schema_version": config.get("schema_version", 1),
        "roots": ["Hansyangxingxiang", "personal-notes", "workbuddy-agents", "~/.claude/skills"],
        "skills": entries,
        "workflows": workflows,
        "commands": commands,
        "templates": templates,
        "duplicates": duplicates,
        "generated_from": ["SKILL.md frontmatter", "directory layout", "WORKFLOW.md", "commands/*.md"],
        "generated_file_map": config.get("generated", {}),
    }
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        REGISTRY_JSON.write_text(json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (OUT_DIR / "SKILL_INVENTORY.md").write_text(render_inventory(registry), encoding="utf-8")
        (OUT_DIR / "SKILL_DEPENDENCIES.md").write_text(render_dependencies(registry), encoding="utf-8")
        (OUT_DIR / "SKILL_REGISTRY.md").write_text(render_registry(registry), encoding="utf-8")
    return registry


def check_registry_consistency(audit, registry):
    if not REGISTRY_JSON.exists():
        audit.add("error", "registry", REGISTRY_JSON, "registry missing; run --write")
        return
    try:
        committed = json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        audit.add("error", "registry", REGISTRY_JSON, "cannot parse registry: %s" % exc)
        return
    for key in ("skills", "workflows", "commands", "templates", "duplicates"):
        if committed.get(key) != registry.get(key):
            audit.add("error", "registry", REGISTRY_JSON, "%s differs from filesystem; run --write" % key)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit and registry-check the skill library.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="validate and compare against committed registry (default)")
    mode.add_argument("--write", action="store_true", help="regenerate registry, inventory and generated references")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    parser.add_argument("--scope", default=SCOPE_DEFAULT, help="comma list: hans,personal,workbuddy")
    parser.add_argument("--strict-cross-repo", action="store_true", help="treat missing sibling repos as errors")
    args = parser.parse_args(argv)

    scopes = [s.strip() for s in args.scope.split(",") if s.strip()]
    config_path = SCRIPT_DIR / "skill_audit.config.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("config error: %s" % exc, file=sys.stderr)
        return 2

    audit = Audit()
    in_scope, all_skills = discover_skills(scopes, audit)

    if args.strict_cross_repo:
        for scope in scopes:
            if scope in ("personal", "workbuddy") and not repo_root(scope).exists():
                audit.add("error", "scope", repo_root(scope), "missing repo for scope %s" % scope)

    check_generated(audit, config, write=args.write)
    check_generated_templates(audit, config, write=args.write)
    registry = build_registry(in_scope, config, audit, write=args.write)

    md_files = []
    for item in in_scope:
        for md in sorted(item["dir"].rglob("*.md")):
            # Test fixtures deliberately contain broken links.
            if "fixtures" in md.parts:
                continue
            md_files.append(md)
    for base in (HANS / "workflows", HANS / "commands", HANS / "templates", HANS / "shared"):
        if base.exists():
            md_files.extend(sorted(base.rglob("*.md")))
    md_files = sorted(set(md_files))
    check_references(audit, md_files, HANS)
    check_skill_name_refs(audit, md_files, collect_names(all_skills), config.get("skill_name_prefixes", []))
    check_desensitize(audit, scopes, config)

    if not args.write:
        check_registry_consistency(audit, registry)

    if args.json:
        print(json.dumps({"errors": audit.errors, "warnings": audit.warnings, "findings": audit.findings},
                         ensure_ascii=False, indent=2))
    else:
        for f in audit.findings:
            print("[%s] %-12s %s: %s" % (f["level"].upper(), f["check"], f["path"], f["message"]))
        print("\n%d error(s), %d warning(s), %d skill(s) in scope" % (audit.errors, audit.warnings, len(in_scope)))
    return 1 if audit.errors else 0


if __name__ == "__main__":
    sys.exit(main())
