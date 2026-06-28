#!/usr/bin/env bash
# 内容宪法审稿（LLM，建议性，不阻塞发布）。
#
# 用无头 claude CLI 复用本机 Claude Code 登录（无需 API key），对照内容宪法审阅文章。
# 审稿纪律单一来源：.claude/agents/content-editor.md 的正文（去掉 frontmatter）。
#
# 用法：
#   bash scripts/publish/review.sh                       # 审本地改动的 content 文章
#   bash scripts/publish/review.sh content/posts/x.md …  # 审指定文章
#
# 设计上这是 workflow / 建议性步骤，不是 pre-push 硬门禁——LLM 审稿主观、可能误报、
# 要联网，硬拦 push 会很难受。

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
AGENT="$REPO_ROOT/.claude/agents/content-editor.md"
CONSTITUTION="$REPO_ROOT/.claude/constitutions/content.md"

command -v claude >/dev/null || { echo "未找到 claude CLI"; exit 127; }
[ -f "$CONSTITUTION" ] || { echo "缺少内容宪法：$CONSTITUTION"; exit 1; }

# 审稿纪律 = content-editor.md 去掉 YAML frontmatter 后的正文
INSTRUCTION="$(awk 'f; /^---$/ {c++; if (c==2) f=1}' "$AGENT")"

# 待审文件：参数优先；否则取相对 HEAD 改动的 content/*.md（跳过 drafts）
# 注：macOS 自带 bash 3.2，不用 mapfile。
files=()
if [ "$#" -gt 0 ]; then
    for a in "$@"; do files+=("$a"); done
else
    while IFS= read -r line; do
        [ -n "$line" ] && files+=("$line")
    done < <(
        { git -C "$REPO_ROOT" diff --name-only HEAD -- content
          git -C "$REPO_ROOT" ls-files --others --exclude-standard -- content
        } | grep -E '\.md$' | grep -v '/drafts/' | sort -u
    )
fi

if [ "${#files[@]}" -eq 0 ]; then
    echo "✓ 无改动文章需审稿。指定文件可：bash scripts/publish/review.sh <file>"
    exit 0
fi

for f in "${files[@]}"; do
    path="$f"; [ -f "$path" ] || path="$REPO_ROOT/$f"
    [ -f "$path" ] || { echo "跳过（不存在）：$f"; continue; }
    echo ""
    echo "════════════════════════════════════════"
    echo "📝 内容审稿：$f"
    echo "════════════════════════════════════════"
    PROMPT="$INSTRUCTION

=== 设计宪法（content.md）===
$(cat "$CONSTITUTION")

=== 待审文章（$f）===
$(cat "$path")"
    claude -p "$PROMPT"
done
