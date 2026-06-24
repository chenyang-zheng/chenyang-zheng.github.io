#!/usr/bin/env python3
"""发布前硬约束门禁（极薄）。

只拦"语法级、零主观、修不了就是坏页面"的硬伤；带判断的检查留给 Agent。
默认只检查改动的文章（pre-push / 本地都不必全量扫）。

用法：
    python3 -m scripts.publish.pregate                 # 检查相对 HEAD 改动的文章
    python3 -m scripts.publish.pregate --all           # 检查全部 content/
    python3 -m scripts.publish.pregate path/a.md ...   # 检查指定文件（pre-push 用）

退出码：有 ERROR → 1（拦 push）；只有 WARN 或干净 → 0。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from . import checks

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "content"


def _is_draft_dir(path: Path) -> bool:
    """content/drafts/ 已被 gitignore，不发布，跳过。"""
    return "drafts" in path.parts


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


def main() -> int:
    ap = argparse.ArgumentParser(description="发布前硬约束门禁")
    ap.add_argument("paths", nargs="*", help="指定检查的 .md 文件")
    ap.add_argument("--all", action="store_true", help="检查全部 content/")
    args = ap.parse_args()

    if args.paths:
        files = [Path(p) for p in args.paths]
    elif args.all:
        files = [p for p in sorted(CONTENT_DIR.rglob("*.md")) if not _is_draft_dir(p)]
    else:
        files = [p for p in _changed_md() if not _is_draft_dir(p)]

    if not files:
        print("✓ 无改动文章需检查。")
        return 0

    errors = warns = 0
    for path in files:
        issues = checks.run_all(path, CONTENT_DIR)
        if not issues:
            continue
        rel = path.relative_to(REPO_ROOT) if path.is_absolute() else path
        has_err = any(i.is_error for i in issues)
        print(f"\n{'❌' if has_err else '⚠️ '} {rel}")
        for i in issues:
            mark = "✗" if i.is_error else "⚠"
            print(f"  {mark}  {i.message}")
            if i.is_error:
                errors += 1
            else:
                warns += 1

    print(f"\n扫描 {len(files)} 篇 | 硬伤 {errors} | 提示 {warns}")
    if errors:
        print("❌ 存在硬伤，已拦截。请修复后重试。")
        return 1
    if warns:
        print("⚠️  有质量提示（不阻塞），建议处理后再发布。")
    else:
        print("✅ 通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
