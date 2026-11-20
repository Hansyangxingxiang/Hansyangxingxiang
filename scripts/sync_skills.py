#!/usr/bin/env python3
"""Install repo assets into ~/.claude with an explicit, reviewable diff.

Default is dry-run: nothing is written unless --apply is given. Deletion only
happens with --delete; without it, extra files in the target are left alone.

Usage:
    python3 scripts/sync_skills.py                      # dry-run all Hans skills
    python3 scripts/sync_skills.py --skills design-document humanizer-zh
    python3 scripts/sync_skills.py --commands --workflows
    python3 scripts/sync_skills.py --apply
    python3 scripts/sync_skills.py --repo personal-notes --skills ci-test-case --apply
    python3 scripts/sync_skills.py --apply --delete

Stdlib only. Python 3.9+.
"""
import argparse
import filecmp
import os
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HANS = SCRIPT_DIR.parent
WORKSPACE = HANS.parent

REPO_ROOTS = {
    "hans": HANS,
    "personal-notes": WORKSPACE / "personal-notes",
}


def discover_skills(repo_root):
    skills_root = repo_root / "skills"
    if not skills_root.exists():
        return {}
    found = {}
    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        found[skill_md.parent.name] = skill_md.parent
    return found


def iter_files(base):
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for name in sorted(filenames):
            yield Path(dirpath) / name


def plan_tree(src, dst, delete):
    """Yield (action, src, dst) for one file tree."""
    for src_file in iter_files(src):
        rel = src_file.relative_to(src)
        dst_file = dst / rel
        if not dst_file.exists():
            yield "add", src_file, dst_file
        elif not filecmp.cmp(src_file, dst_file, shallow=False):
            yield "update", src_file, dst_file

    if delete and dst.exists():
        for dst_file in iter_files(dst):
            rel = dst_file.relative_to(dst)
            if not (src / rel).exists():
                yield "delete", None, dst_file


def build_plan(args):
    repo_root = REPO_ROOTS[args.repo]
    plan = []

    if args.skills or not (args.commands or args.workflows):
        available = discover_skills(repo_root)
        names = args.skills or sorted(available)
        unknown = [n for n in names if n not in available]
        if unknown:
            print("unknown skill(s) for %s: %s" % (args.repo, ", ".join(unknown)), file=sys.stderr)
            return None
        for name in names:
            plan.extend(plan_tree(available[name], args.target / "skills" / name, args.delete))

    if args.commands:
        commands_root = repo_root / "commands"
        if commands_root.exists():
            for src_file in sorted(commands_root.glob("*.md")):
                dst_file = args.target / "commands" / src_file.name
                action = "add" if not dst_file.exists() else (
                    "update" if not filecmp.cmp(src_file, dst_file, shallow=False) else "same"
                )
                if action != "same":
                    plan.append((action, src_file, dst_file))

    if args.workflows:
        workflows_root = repo_root / "workflows"
        if workflows_root.exists():
            for wf_dir in sorted(p for p in workflows_root.iterdir() if p.is_dir()):
                plan.extend(plan_tree(wf_dir, args.target / "workflows" / wf_dir.name, args.delete))

    return plan


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sync skills/commands/workflows into ~/.claude (dry-run by default).")
    parser.add_argument("--repo", choices=sorted(REPO_ROOTS), default="hans",
                        help="source repo; personal-notes must be chosen explicitly")
    parser.add_argument("--skills", nargs="*", help="skill directory names; default all in repo")
    parser.add_argument("--commands", action="store_true", help="also sync commands/*.md")
    parser.add_argument("--workflows", action="store_true", help="also sync workflows/<name>/")
    parser.add_argument("--target", type=Path, default=Path.home() / ".claude",
                        help="install directory, default ~/.claude")
    parser.add_argument("--apply", action="store_true", help="actually write; default dry-run")
    parser.add_argument("--delete", action="store_true",
                        help="delete target files absent from source; requires --apply to take effect")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print("target does not exist: %s" % args.target, file=sys.stderr)
        return 2

    plan = build_plan(args)
    if plan is None:
        return 2
    if not plan:
        print("nothing to do")
        return 0

    for action, src_file, dst_file in plan:
        print("%-6s %s" % (action, dst_file))
    if not args.apply:
        print("\ndry-run: %d change(s). Re-run with --apply to write." % len(plan))
        return 0

    for action, src_file, dst_file in plan:
        if action == "delete":
            dst_file.unlink()
            continue
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
    print("\napplied %d change(s) to %s" % (len(plan), args.target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
