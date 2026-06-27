# SEO 宪法（DRAFT v0）

> Claude 从现有文章 frontmatter 与站点配置反推的偏好初稿，**待作者定稿**。
> SEO Agent 调用确定性工具（长度/唯一性/meta 检测）+ 对照本文件给改进建议，
> 每条 finding 标明依据 + 引用证据。

## description / summary 必须自包含（踩过的坑）
- description、summary、任何 SEO 文案**必须脱离正文也能看懂**：不得引用正文才建立的隐喻、代号或电影例（如用"无限刷沙滩"而非"低效循环"——前者只有读过正文才懂，不可取）。
- 自检：读者没读正文，这句话能不能独立看懂？

## description（进搜索结果 + 分享卡片）
- 长度 **50–160 字符**；过短信息不足，过长被截断。
- **概括、不夸张、不标题党**——准确传达文章讲什么，自然包含关键词，别堆砌。
- 全站尽量唯一，不同文章别用雷同 description。
- 现有文章是好范本（如 OpenAI-o1、对抗式敏捷闭环那种"一句话点明主题 + 角度"）。

## summary（站内列表 / 摘要卡片）
- 比 description 长、更完整：讲清文章的脉络与价值（看现有文章的 summary 写法）。
- 是给"已经点进来或在列表浏览"的读者，可以更有信息量。

## title
- 真实贴合内容，不党、不悬念营销。
- 理想 < 60 字符（搜索结果标题截断点附近）。

## slug
- 英文 kebab-case（`adversarial-agile-loop`、`peter-lynch-investing`）。
- **一旦发布尽量不改**：giscus 评论按 `pathname` 绑定，改 slug 会丢评论关联。

## tags / categories
- **不做硬限制**（已决策）；但建议复用已有标签、避免越分越碎或近义重复（"Agent" vs "Agents"）。

## 内链与图片
- 相关文章之间适当互链，减少孤儿页。
- 图片 alt 兼顾 SEO 与无障碍（与排版宪法一致）。

## 模板层（阶段五补，Agent 先报缺）
- Open Graph / Twitter Card meta：缺了分享（尤其微信）无缩略图。
- JSON-LD `Article` 结构化数据、`robots.txt`（Hugo 默认不生成）。

## 不要做
- 不为 SEO 牺牲标题/描述的真实与体面；宁可朴素，不要标题党。
