"""共享的 Hugo TOML frontmatter 解析。

从原 scripts/check_content.py 抽出，供 pregate、check_content 及未来的
Agent 工具复用，避免各处各写一份解析逻辑（单一职责）。

只做"够用"的解析：frontmatter 里我们关心的都是标量 / 字符串数组，
不需要完整 TOML 实现。
"""

from __future__ import annotations

import re

_RE_STRING   = re.compile(r"""^["'](.*)["']$""")
_RE_BOOL     = re.compile(r"^(true|false)$", re.I)
_RE_INT      = re.compile(r"^-?\d+$")
_RE_FLOAT    = re.compile(r"^-?\d+\.\d+$")
_RE_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
_RE_DATE     = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_RE_ARRAY    = re.compile(r"^\[.*\]$", re.DOTALL)


def _parse_value(raw: str):
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
        return raw  # 保留原字符串，够用
    if _RE_ARRAY.match(raw):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return re.findall(r"""["']([^"']*)["']""", inner)
    return raw


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """返回 (frontmatter 原文, 正文)。无 frontmatter 时返回 (None, 原文)。"""
    if not text.startswith("+++"):
        return None, text
    end = text.find("\n+++", 3)
    if end == -1:
        return None, text
    return text[3:end], text[end + 4:]


def parse(text: str) -> dict | None:
    """解析 +++ 分隔的 TOML frontmatter，返回 dict；没有则返回 None。"""
    raw, _ = split_frontmatter(text)
    if raw is None:
        return None
    result: dict = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        result[key.strip()] = _parse_value(val.strip())
    return result
