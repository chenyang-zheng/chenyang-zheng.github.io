"""确定性检查工具库。

每个检查函数接收 (path, text, meta)，返回 list[Issue]。
按严重度分两档：
  - ERROR : 语法级硬伤，pregate 会据此拦 push
  - WARN  : 质量提示，pregate 打印但不阻塞（后续也会被排版/SEO Agent 复用）

无任何第三方依赖。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import fields, frontmatter

# ── 阈值（将来可挪到 config.toml）──────────────────────────────────────────
IMAGE_MAX_BYTES = 1024 * 1024  # 单图 1MB

# 字段口径单一事实源见 fields.py

ERROR = "error"
WARN  = "warn"


@dataclass
class Issue:
    severity: str   # ERROR | WARN
    code: str       # 机器可读的检查名
    message: str    # 人读的说明

    @property
    def is_error(self) -> bool:
        return self.severity == ERROR


# ── 辅助 ────────────────────────────────────────────────────────────────────

_RE_IMG = re.compile(r'!\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+"[^"]*")?\s*\)')
_RE_FENCE = re.compile(r"^\s*```")
_RE_BODY_H1 = re.compile(r"^#\s+\S", re.M)


def _section(path: Path, content_dir: Path) -> str:
    try:
        parts = path.parent.relative_to(content_dir).parts
        return parts[0] if parts else "default"
    except ValueError:
        return "default"


def _image_refs(body: str) -> list[tuple[str, str]]:
    """返回 [(alt, src), ...]，跳过远程图与 data URI。"""
    refs = []
    for alt, src in _RE_IMG.findall(body):
        if src.startswith(("http://", "https://", "data:", "//")):
            continue
        refs.append((alt, src))
    return refs


def _resolve(src: str, md_path: Path) -> Path:
    """把图片引用解析为磁盘路径（相对 md 所在目录）。"""
    return (md_path.parent / src).resolve()


# ── 硬约束（ERROR）─────────────────────────────────────────────────────────

def check_frontmatter_present(path: Path, text: str, meta: dict | None) -> list[Issue]:
    if meta is None:
        return [Issue(ERROR, "no-frontmatter",
                      "缺少 frontmatter（+++...+++），Hugo 会发出无元数据的坏页")]
    return []


def check_required_fields(path: Path, text: str, meta: dict | None,
                          content_dir: Path) -> list[Issue]:
    if meta is None or meta.get("draft") is True:
        return []
    section = _section(path, content_dir)
    issues = [Issue(ERROR, "missing-field", f"缺少必填字段：'{f}'")
              for f in fields.required_for(section) if f not in meta]
    issues += [Issue(WARN, "missing-recommended", f"建议补全字段：'{f}'")
               for f in fields.recommended_for(section) if f not in meta]
    return issues


def check_dead_local_images(path: Path, text: str, meta: dict | None) -> list[Issue]:
    _, body = frontmatter.split_frontmatter(text)
    issues = []
    for _, src in _image_refs(body):
        if not _resolve(src, path).exists():
            issues.append(Issue(ERROR, "dead-image",
                                 f"本地图片不存在，线上会裂图：{src}"))
    return issues


def check_unclosed_code_fence(path: Path, text: str, meta: dict | None) -> list[Issue]:
    _, body = frontmatter.split_frontmatter(text)
    fences = sum(1 for line in body.splitlines() if _RE_FENCE.match(line))
    if fences % 2 != 0:
        return [Issue(ERROR, "unclosed-fence",
                      f"代码块未闭合（``` 出现 {fences} 次，应为偶数），渲染会乱")]
    return []


def check_todo_placeholders(path: Path, text: str, meta: dict | None) -> list[Issue]:
    if meta is None:
        return []
    issues = []
    for field in ("description", "summary"):
        val = meta.get(field)
        # 只认自动填充的占位符（以 TODO 开头），不误伤正文里正当出现的 "TODO" 一词
        if isinstance(val, str) and val.strip().startswith("TODO"):
            issues.append(Issue(ERROR, "todo-placeholder",
                                f"'{field}' 仍是 TODO 占位，会进 SEO/分享卡片：{val!r}"))
    return issues


# ── 质量提示（WARN）────────────────────────────────────────────────────────

def check_image_oversize(path: Path, text: str, meta: dict | None) -> list[Issue]:
    _, body = frontmatter.split_frontmatter(text)
    issues = []
    for _, src in _image_refs(body):
        p = _resolve(src, path)
        if p.exists() and p.stat().st_size > IMAGE_MAX_BYTES:
            kb = p.stat().st_size / 1024
            issues.append(Issue(WARN, "image-oversize",
                                f"图片 {kb:.0f}KB 超过 {IMAGE_MAX_BYTES//1024}KB：{src}"))
    return issues


def check_missing_alt(path: Path, text: str, meta: dict | None) -> list[Issue]:
    _, body = frontmatter.split_frontmatter(text)
    return [Issue(WARN, "missing-alt", f"图片缺 alt 文本（影响 SEO/无障碍）：{src}")
            for alt, src in _image_refs(body) if not alt.strip()]


def check_png_with_webp_sibling(path: Path, text: str, meta: dict | None) -> list[Issue]:
    _, body = frontmatter.split_frontmatter(text)
    issues = []
    for _, src in _image_refs(body):
        if src.lower().endswith((".png", ".jpg", ".jpeg")):
            p = _resolve(src, path)
            if p.with_suffix(".webp").exists():
                issues.append(Issue(WARN, "use-webp",
                                    f"同目录已有 .webp，应改引用：{src}"))
    return issues


def check_body_h1(path: Path, text: str, meta: dict | None) -> list[Issue]:
    _, body = frontmatter.split_frontmatter(text)
    if _RE_BODY_H1.search(body):
        return [Issue(WARN, "body-h1",
                      "正文出现一级标题 '# '（h1 应留给文章标题，正文从 '## ' 起）")]
    return []


# ── 汇总 ────────────────────────────────────────────────────────────────────

HARD_CHECKS = (
    check_frontmatter_present,
    check_dead_local_images,
    check_unclosed_code_fence,
    check_todo_placeholders,
)

SOFT_CHECKS = (
    check_image_oversize,
    check_missing_alt,
    check_png_with_webp_sibling,
    check_body_h1,
)


def run_all(path: Path, content_dir: Path) -> list[Issue]:
    """对单个 md 文件跑全部检查，返回 Issue 列表。"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [Issue(ERROR, "read-error", f"无法读取文件：{e}")]

    meta = frontmatter.parse(text)
    issues: list[Issue] = []
    for check in HARD_CHECKS:
        issues += check(path, text, meta)
    issues += check_required_fields(path, text, meta, content_dir)
    for check in SOFT_CHECKS:
        issues += check(path, text, meta)
    return issues
