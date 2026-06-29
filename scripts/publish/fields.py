"""各 section 的 frontmatter 字段定义（单一事实源）。

抽出来单独管理，供 checks.py / pregate 使用，避免散落多处各写一份。
字段口径沿用原 check_content.py。

- REQUIRED_FIELDS    : 缺了算硬伤（pregate 拦截）。draft=true 的文章跳过。
- RECOMMENDED_FIELDS : 缺了只警告，建议补全以提升质量。
"""

from __future__ import annotations

REQUIRED_FIELDS: dict[str, list[str]] = {
    "posts":       ["title", "date", "lastmod", "draft", "slug",
                    "description", "summary", "tags", "categories"],
    "read":        ["title", "date", "draft"],
    "invests":     ["title", "date", "draft"],
    "careers":     ["title", "date", "draft"],
    "cisco":       ["title", "date", "draft"],
    "indie_gamer": ["title", "date", "draft"],
    "default":     ["title", "date", "draft"],
}

RECOMMENDED_FIELDS: dict[str, list[str]] = {
    "posts":   [],
    "read":    ["description"],
    "invests": ["description"],
    "careers": ["description"],
    "default": ["description"],
}


def required_for(section: str) -> list[str]:
    return REQUIRED_FIELDS.get(section, REQUIRED_FIELDS["default"])


def recommended_for(section: str) -> list[str]:
    return RECOMMENDED_FIELDS.get(section, RECOMMENDED_FIELDS["default"])
