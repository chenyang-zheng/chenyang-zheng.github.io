# Makefile for chenyang-zheng.github.io Hugo site

.PHONY: check preflight webp webp-check review serve build setup-hooks help

## 安装 git hooks（首次 clone 后执行一次）
setup-hooks:
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-push .githooks/pre-commit
	@echo "✅ git hooks 已配置：pre-commit（图片转 webp）+ pre-push（硬约束）"

## 全局状态：全量扫描 + 草稿清单（平时体检，不绑定单次发布）
check:
	python3 -m scripts.publish.pregate --all

## 发布硬约束门禁：仅检查改动的文章（同 pre-push）
preflight:
	python3 -m scripts.publish.pregate

## 批量把 content/ 缺失/过期的栅格图转成 webp（检查通过的才转，保留原图）
webp:
	python3 compress_image.py

## 只跑压缩检查：列出该压哪些 + 原因，不写文件
webp-check:
	python3 compress_image.py --check

## 内容宪法审稿（LLM，建议性，不阻塞）。FILE=指定文章，留空则审改动的文章
review:
	bash scripts/publish/review.sh $(FILE)

## 本地预览（含草稿）
serve:
	hugo server -D --bind 0.0.0.0

## 构建生产版本（不含草稿）
build:
	hugo --minify

## 显示帮助
help:
	@echo ""
	@echo "可用命令："
	@echo "  make setup-hooks  首次配置：安装 git hooks（pre-commit 转 webp + pre-push 门禁）"
	@echo "  make check        全局状态：全量扫描 + 草稿清单"
	@echo "  make preflight    硬约束门禁：仅查改动的文章"
	@echo "  make webp         批量转 webp（检查通过的才转，保留原图）"
	@echo "  make webp-check   只跑压缩检查：列出该压哪些，不写文件"
	@echo "  make review       内容宪法审稿（LLM，建议性）；FILE=指定文章"
	@echo "  make serve        本地预览（含草稿）"
	@echo "  make build        构建生产版本"
	@echo ""
	@echo "微信发布：访问文章页点击「微信版」按钮，在预览页复制内容后粘贴到公众号编辑器"
	@echo ""
