# Makefile for chenyang-zheng.github.io Hugo site

.PHONY: check fix drafts preflight preflight-all serve build setup-hooks help

## 安装 git hooks（首次 clone 后执行一次）
setup-hooks:
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-push
	@echo "✅ git hooks 已配置，pre-push 检查已启用"

## 检查所有已发布文章的元数据
check:
	python3 scripts/check_content.py

## 检查并自动补全缺失字段（使用默认占位值）
fix:
	python3 scripts/check_content.py --fix

## 检查所有文章（包括草稿）
drafts:
	python3 scripts/check_content.py --drafts

## 发布硬约束门禁：仅检查改动的文章（同 pre-push）
preflight:
	python3 -m scripts.publish.pregate

## 发布硬约束门禁：全量体检
preflight-all:
	python3 -m scripts.publish.pregate --all

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
	@echo "  make setup-hooks  首次配置：安装 pre-push git hook"
	@echo "  make check        检查所有已发布文章的元数据"
	@echo "  make fix          自动补全缺失的元数据字段"
	@echo "  make drafts       列出所有草稿和问题文章"
	@echo "  make preflight    硬约束门禁：仅查改动的文章"
	@echo "  make preflight-all 硬约束门禁：全量体检"
	@echo "  make serve        本地预览（含草稿）"
	@echo "  make build        构建生产版本"
	@echo ""
	@echo "微信发布：访问文章页点击「微信版」按钮，在预览页复制内容后粘贴到公众号编辑器"
	@echo ""
