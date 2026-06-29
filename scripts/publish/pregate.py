#!/usr/bin/env python3
"""发布前确定性检查（取代旧 check_content.py）。

两种用途，同一套 checks：
  - 门禁（默认 / 指定文件）：只看**改动**的非草稿文章，有硬伤 → 退出 1，拦 push。
  - 全局状态（--all）：扫全部 content，给整体健康度提示 + 列出草稿；用于平时体检，
    不绑定单次发布（push 只 gate 改动文件）。

用法：
    python3 -m scripts.publish.pregate                 # 门禁：相对 HEAD 改动的文章
    python3 -m scripts.publish.pregate path/a.md ...   # 门禁：指定文件（pre-push 用）
    python3 -m scripts.publish.pregate --all           # 全局状态：全量 + 草稿清单

退出码：有 ERROR → 1；否则 0。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from . import checks, frontmatter

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "content"


def _is_draft_dir(path: Path) -> bool:
    """content/drafts/ 已被 gitignore，不发布，跳过。"""
    return "drafts" in path.parts


def _is_draft_meta(path: Path) -> bool:
    """frontmatter 里 draft = true。"""
    try:
        meta = frontmatter.parse(path.read_text(encoding="utf-8"))
    except OSError:
        return False
    return bool(meta) and meta.get("draft") is True


def _rel(path: Path) -> Path:
    return path.relative_to(REPO_ROOT) if path.is_absolute() else path


def _changed_md() -> list[Path]:
    """工作区 + 暂存区相对 HEAD 改动的 content/*.md（仍存在的）。"""
    out: set[str] = set()
    for args in (["diff", "--name-only", "HEAD", "--", "content"],
                 ["diff", "--name-only", "--cached", "--", "content"],
                 ["ls-files", "--others", "--exclude-standard", "--", "content"]):
        try:
            res = subprocess.run(["git", *args], cwd=REPO_ROOT,
                                 capture_output=True, text=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        out.update(res.stdout.split())
    paths = [REPO_ROOT / p for p in out if p.endswith(".md")]
    return sorted(p for p in paths if p.exists())


def _run_checks(files: list[Path]) -> tuple[int, int]:
    """对一组文件跑 checks 并打印，返回 (errors, warns)。"""
    errors = warns = 0
    for path in files:
        issues = checks.run_all(path, CONTENT_DIR)
        if not issues:
            continue
        has_err = any(i.is_error for i in issues)
        print(f"\n{'❌' if has_err else '⚠️ '} {_rel(path)}")
        for i in issues:
            print(f"  {'✗' if i.is_error else '⚠'}  {i.message}")
            errors, warns = (errors + 1, warns) if i.is_error else (errors, warns + 1)
    return errors, warns


def main() -> int:
    ap = argparse.ArgumentParser(description="发布前确定性检查")
    ap.add_argument("paths", nargs="*", help="指定检查的 .md 文件")
    ap.add_argument("--all", action="store_true", help="全局状态：全量扫描 + 草稿清单")
    args = ap.parse_args()

    if args.paths:
        files = [Path(p) for p in args.paths if not _is_draft_dir(Path(p))]
        drafts: list[Path] = []
    elif args.all:
        allmd = [p for p in sorted(CONTENT_DIR.rglob("*.md")) if not _is_draft_dir(p)]
        drafts = [p for p in allmd if _is_draft_meta(p)]
        files = [p for p in allmd if p not in drafts]
    else:
        files = [p for p in _changed_md() if not _is_draft_dir(p)]
        drafts = []

    if not files and not drafts:
        print("✓ 无文章需检查。")
        return 0

    errors, warns = _run_checks(files)

    # 全局状态：列出草稿（不发布，仅提示整体状态）
    if args.all and drafts:
        print(f"\n📝 草稿（draft=true，不发布）共 {len(drafts)} 篇：")
        for d in drafts:
            print(f"  · {_rel(d)}")

    scope = "全局状态" if args.all else "门禁"
    print(f"\n[{scope}] 已发布 {len(files)} 篇 | 硬伤 {errors} | 提示 {warns}"
          + (f" | 草稿 {len(drafts)} 篇" if args.all else ""))
    if errors:
        print("❌ 存在硬伤" + ("。" if args.all else "，已拦截。请修复后重试。"))
        return 1
    if warns:
        print("⚠️  有质量提示（不阻塞）。")
    else:
        print("✅ 通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
