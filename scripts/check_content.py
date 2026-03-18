#!/usr/bin/env python3
"""Hugo content pre-publish checker.

Validates frontmatter metadata in all markdown files before push.

Usage:
    python scripts/check_content.py              # check all content/
    python scripts/check_content.py --fix        # auto-fill missing fields
    python scripts/check_content.py --drafts     # also list draft articles
    python scripts/check_content.py content/posts/openai-o1.md  # check one file
"""

from __future__ import annotations

import sys
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent
CONTENT_DIR = REPO_ROOT / "content"

# ── Metadata rules per section ─────────────────────────────────────────────

# For articles with draft = false (ready to publish)
REQUIRED_FIELDS: dict[str, list[str]] = {
    "posts": ["title", "date", "lastmod", "draft", "slug", "description", "summary", "tags", "categories"],
    "read":  ["title", "date", "draft"],
    "invests": ["title", "date", "draft"],
    "careers": ["title", "date", "draft"],
    "cisco": ["title", "date", "draft"],
    "indie_gamer": ["title", "date", "draft"],
    "default": ["title", "date", "draft"],
}

# Recommended (warning, not error) for non-posts sections
RECOMMENDED_FIELDS: dict[str, list[str]] = {
    "posts": [],
    "read":  ["description"],
    "invests": ["description"],
    "careers": ["description"],
    "default": ["description"],
}

# ── Minimal TOML parser ────────────────────────────────────────────────────

_RE_STRING    = re.compile(r"""^["'](.*)["']$""")
_RE_BOOL      = re.compile(r"^(true|false)$", re.I)
_RE_INT       = re.compile(r"^-?\d+$")
_RE_FLOAT     = re.compile(r"^-?\d+\.\d+$")
_RE_DATETIME  = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
_RE_DATE      = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_RE_ARRAY     = re.compile(r"^\[.*\]$", re.DOTALL)


def _parse_toml_value(raw: str):
    raw = raw.strip()
    if m := _RE_STRING.match(raw):
        return m.group(1)
    if _RE_BOOL.match(raw):
        return raw.lower() == "true"
    if _RE_INT.match(raw):
        return int(raw)
    if _RE_FLOAT.match(raw):
        return float(raw)
    if _RE_DATETIME.match(raw) or _RE_DATE.match(raw):
        return raw  # keep as string; we only need the value
    if _RE_ARRAY.match(raw):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        items = re.findall(r"""["']([^"']*)["']""", inner)
        return items
    return raw  # fallback: raw string


def parse_toml_frontmatter(text: str) -> dict | None:
    """Parse TOML frontmatter delimited by +++. Returns None if not found."""
    if not text.startswith("+++"):
        return None
    end = text.find("\n+++", 3)
    if end == -1:
        return None
    toml_block = text[3:end]
    result = {}
    for line in toml_block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        result[key.strip()] = _parse_toml_value(val.strip())
    return result


def split_frontmatter(text: str) -> tuple[str | None, str, str]:
    """Return (toml_block_raw, body, original_text)."""
    if not text.startswith("+++"):
        return None, text, text
    end = text.find("\n+++", 3)
    if end == -1:
        return None, text, text
    toml_raw = text[3:end]          # between the two +++
    body = text[end + 4:]           # after closing +++
    return toml_raw, body, text


# ── Auto-fix helpers ───────────────────────────────────────────────────────

def _toml_value_str(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        items = ", ".join(f'"{i}"' for i in v)
        return f"[{items}]"
    return f'"{v}"'


def _default_value(field: str, meta: dict, path: Path) -> str:
    """Return a sensible default TOML value string for a missing field."""
    if field == "lastmod":
        return meta.get("date", datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"))
    if field == "slug":
        return path.stem
    if field == "draft":
        return "true"   # conservative: mark as draft if missing
    if field in ("tags", "categories"):
        return "[]"
    if field == "description":
        return '"TODO: 添加文章描述"'
    if field == "summary":
        return '"TODO: 添加文章摘要"'
    if field == "date":
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    return '"TODO"'


def apply_fix(path: Path, meta: dict, missing_fields: list[str]) -> None:
    """Insert missing fields into the file's frontmatter and save."""
    original = path.read_text(encoding="utf-8")
    toml_raw, body, _ = split_frontmatter(original)
    if toml_raw is None:
        print(f"    ↳ Cannot fix: no frontmatter found")
        return

    additions = []
    for field in missing_fields:
        val = _default_value(field, meta, path)
        if field in ("lastmod", "date") and not val.startswith('"'):
            # datetime — no quotes
            additions.append(f"{field} = {val}")
        elif field in ("tags", "categories"):
            additions.append(f"{field} = {val}")
        elif field == "draft":
            additions.append(f"{field} = {val}")
        else:
            additions.append(f"{field} = {val}")

    new_toml = toml_raw.rstrip() + "\n" + "\n".join(additions) + "\n"
    new_content = "+++" + new_toml + "+++" + body
    path.write_text(new_content, encoding="utf-8")


# ── Core checker ───────────────────────────────────────────────────────────

def get_section(path: Path) -> str:
    try:
        rel = path.parent.relative_to(CONTENT_DIR)
        parts = rel.parts
        return parts[0] if parts else "default"
    except ValueError:
        return "default"


def check_file(path: Path, fix: bool = False, show_drafts: bool = False) -> list[str]:
    """
    Check a single markdown file. Returns list of issue strings.
    Issues prefixed with '✗' are errors; '⚠' are warnings.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"  ✗  Cannot read file: {e}"]

    meta = parse_toml_frontmatter(text)

    if meta is None:
        return ["  ⚠  缺少 frontmatter（+++...+++）— Hugo 会将此文件作为无元数据页面发布"]

    draft = meta.get("draft")

    # --- Draft articles ---
    if draft is True:
        if show_drafts:
            return ["  ℹ  draft = true (will not be published)"]
        return []   # silently skip drafts

    # --- Missing draft field ---
    if draft is None:
        issues = ["  ⚠  'draft' field missing — Hugo treats this as published"]
        # Still check other required fields
    else:
        issues = []

    section = get_section(path)
    required = REQUIRED_FIELDS.get(section, REQUIRED_FIELDS["default"])
    recommended = RECOMMENDED_FIELDS.get(section, RECOMMENDED_FIELDS["default"])

    missing_required    = [f for f in required    if f not in meta]
    missing_recommended = [f for f in recommended if f not in meta]

    for f in missing_required:
        issues.append(f"  ✗  缺少必填字段: '{f}'")
    for f in missing_recommended:
        issues.append(f"  ⚠  缺少推荐字段: '{f}'")

    if fix and (missing_required or missing_recommended):
        all_missing = missing_required + missing_recommended
        apply_fix(path, meta, all_missing)
        issues.append(f"  ✔  已自动补全: {', '.join(all_missing)}")

    return issues


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Hugo 内容元数据检查器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python scripts/check_content.py               # 检查全部内容
  python scripts/check_content.py --fix         # 自动补全缺失字段
  python scripts/check_content.py --drafts      # 同时显示草稿文章
  python scripts/check_content.py content/posts/openai-o1.md  # 检查单个文件
"""
    )
    parser.add_argument("--fix",    action="store_true", help="自动补全缺失字段（使用默认值）")
    parser.add_argument("--drafts", action="store_true", help="同时列出 draft=true 的文章")
    parser.add_argument("paths",    nargs="*",           help="指定检查的文件（默认检查全部 content/）")
    args = parser.parse_args()

    if args.paths:
        files = [Path(p) for p in args.paths]
    else:
        files = sorted(CONTENT_DIR.rglob("*.md"))

    error_count   = 0
    warning_count = 0
    checked       = 0
    draft_count   = 0

    for filepath in files:
        issues = check_file(filepath, fix=args.fix, show_drafts=args.drafts)
        if not issues:
            checked += 1
            continue

        # Classify
        has_error = any("✗" in i for i in issues)
        has_info  = all("ℹ" in i for i in issues)

        if has_info:
            draft_count += 1
            if args.drafts:
                rel = filepath.relative_to(REPO_ROOT)
                print(f"📝 {rel}")
                for issue in issues:
                    print(issue)
            continue

        rel = filepath.relative_to(REPO_ROOT)
        print(f"\n{'❌' if has_error else '⚠️ '} {rel}")
        for issue in issues:
            print(issue)

        for i in issues:
            if "✗" in i:
                error_count += 1
            elif "⚠" in i:
                warning_count += 1

        checked += 1

    # ── Summary ──
    print()
    total = len(files)
    print(f"共扫描 {total} 个文件 | 草稿 {draft_count} 篇 | "
          f"错误 {error_count} 处 | 警告 {warning_count} 处")

    if error_count == 0 and warning_count == 0:
        print("✅ 所有已发布文章元数据检查通过！")
        return 0

    if error_count > 0:
        if args.fix:
            print("🔧 已自动补全缺失字段，请复核补全内容后再提交。")
        else:
            print("❌ 发现错误，请补全必填字段后再发布。（使用 --fix 可自动补全默认值）")
        return 1

    print("⚠️  发现警告，建议补全推荐字段以提升文章质量。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
