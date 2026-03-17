+++
title = 'OpenClaw：AI OS与Personal的早期实验？'
date = 2026-03-17T20:02:20+08:00
draft = false
slug = 'openclaw-personal-agent'
description = 'OpenClaw同时踩在AI OS与personal memory两条线上，也因此成为观察个性化AI早期形态的一个好样本。'
summary = 'OpenClaw把runtime、plugins、system calling和local-first memory放进同一个框架里，既回应了AI Agent工程化落地的需求，也开始触及个性化AI的方向。本文讨论它已经做对了什么、为什么这仍然只是早期实验，以及AI OS与personal memory未来可能如何分工。'
tags = ['openclaw', 'personal-agent', 'agent-memory', 'ai-os']
categories = ['AI', 'Agents']
+++

OpenClaw最有意思的地方，在于它同时回应了两类正在变强的需求：AI Agent的工程化落地和个性化AI。前者关心的不是单纯把agent快速跑起来，而是把工具接入、系统调用、调度编排和运行时管理一起做实；后者关心的则是agent能不能真正贴着某个人的上下文长期工作。

OpenClaw已经同时踩在这两条线上。runtime、plugins、system calling这些能力，让它很像一个轻量的AI OS；local-first memory这条线，又让它开始具备personal的雏形。

也正因为如此，我更关心的问题不是它像不像AI OS，而是它离真正personal还有多远。一个真正的personal agent，不只是能替我完成任务，还得能把分散的输入、阶段性的判断和长期偏好，慢慢收成一套不断线的个人语境。

## 我们缺的不是Agent，而是一条不断线的上下文

很多现成AI agent可以覆盖单点需求，比如总结文章、搜索资料、整理会议纪要、调用日历或待办工具。它们完成一次任务通常没有问题，问题出在连续性上。

这里的连续性，不只是“记住你上次说过什么”，而是三层能力同时成立：

- 信息连续性：它知道你看过什么、记过什么、做过什么。
- 语义连续性：它知道这些信息之间的关系，哪些是长期兴趣，哪些只是偶然路过。
- 决策连续性：它知道对你来说，什么该归档，什么该提醒，什么该变成一个后续动作。

这种连续性不是附属feature，而是agent能否形成稳定行为的前提。[Generative Agents](https://arxiv.org/abs/2304.03442) 用memory stream、reflection和planning去维持角色一致性。[Evaluating Very Long-Term Conversational Memory of LLM Agents](https://aclanthology.org/2024.acl-long.747/) 也说明了，即便引入long context和RAG，模型在very long-term dialogue memory上仍明显落后于人类。[MemGPT](https://arxiv.org/abs/2310.08560) 则把长期交互中的memory管理类比为操作系统问题。换句话说，personal agent真正稀缺的不是一次任务的执行能力，而是长期上下文的维护能力。

多数cloud AI agent最多做到第一层的一部分。它们可能有聊天记忆，也可能能接一些外部工具，但很少真正成为你的`system of record`。原因不完全是技术能力不足，而是产品形态决定了它们很难承担这个角色。

首先，用户与AI的入口是分散的。聊天窗口、邮件、浏览器插件、微信群、语音入口、各种SaaS里的Copilot，都可能是单独的交互点。即使这些入口背后都是同一类模型，它们通常也没有统一的记忆写入路径，更谈不上稳定的长期上下文。

其次，写入长期记忆远比检索困难。RAG很擅长“把相关资料找回来”，但personal agent真正需要回答的是另一类问题：什么值得被记住？应该记成什么结构？旧的判断什么时候该被更新？如果这一步做错，后面的所有检索和自动化都会被污染。

再进一步，通用云产品往往不会为单个用户维护一套强个性化、强可审计的长期记忆。因为它们优化的是通用用户的即时成功率，而不是某一个人的长期复利。对于产品方来说，过度主动地推断、归类和记忆用户偏好，本身就伴随着隐私、责任和解释权问题。

所以personal agent的必要性，不在于“云上的agent不够智能”，而在于你的长期上下文，通常并不真正掌握在你自己手里。

## Personal Agent的分水岭，在记忆归谁所有

如果说OpenClaw解决的是执行门槛，那么personal agent更想解决的是记忆归属。

所谓记忆主权，不是简单地把模型跑在本地，而是让下面这些东西由你来定义和控制：

- 什么信息允许进入长期记忆
- 长期记忆如何组织
- 哪些偏好和判断会影响后续行为
- 什么内容可以发往云端，什么必须留在本地

这也是为什么personal agent往往更适合做成`local-first / hybrid`。[Local-first software: You own your data, in spite of the cloud](https://www.inkandswitch.com/essay/local-first/)讲得很清楚：关键不在某个云服务是否足够强，而在用户是否还拥有对自身数据和长期状态的控制权。与此同时，[Unveiling Privacy Risks in LLM Agent Memory](https://aclanthology.org/2025.acl-long.1227/)也提醒了另一面：一旦长期记忆成为agent的核心能力，记忆泄露和可审计性就不再是附属问题。

- 本地保存原始资料、长期记忆、偏好画像、项目状态
- 云端模型负责高质量推理、摘要、规划和执行
- 是否出端、出端到什么粒度，由用户定义policy

从这个角度看，personal agent不该只是另一个“更会调用工具的聊天机器人”。它更像一个统一入口：持续接住分散的信息输入，再根据你的上下文做过滤、分类、关联和行动判断。

## 真正稀缺的，是一套统一记忆

如果没有稳定记忆，任何agent都很容易退化成一次性工作流。它可以帮你完成一次摘要、一次搜索、一次整理，但很难知道哪些主题是长期追踪对象，哪些结论已经出现过，哪些想法值得转成后续动作。

所以统一入口的意义，不只是减少切换成本，更是让所有分散输入最终汇入同一个记忆系统。

## Personal Agent的记忆，不该只是一座向量库

这类系统最容易踩的坑，就是把“个人记忆”做成一个更大的RAG仓库。只要文章、链接、聊天记录都进embedding，然后靠语义检索调用，看上去像有记忆，实际上很快会失控。

原因很简单：个人记忆不只是在回答“哪些内容和当前问题相似”，还在回答“什么值得被长期保留”“它和我正在做的事是什么关系”“是否应该触发下一步动作”。

因此，personal agent的memory更适合分层设计，而不是只依赖向量检索。这里沿用较常见的口径：`working memory`、`episodic memory`、`semantic memory`和`procedural memory`。参考 [CoALA](https://collaborate.princeton.edu/en/publications/cognitive-architectures-for-language-agents/)。

### 1. Working Memory：维持眼前的任务上下文

这是当前正在被模型“拿在手里”的那部分信息。它的作用是服务当前任务，保证agent知道自己此刻在处理什么、刚刚发生了什么、下一步要做什么。它不是长期保存层，而是一块容量有限、不断刷新的工作台。

### 2. Episodic Memory：保留经历与时间线

这一层保存的是具体事件、交互过程和带时间顺序的经验。它回答的不是“世界上有什么事实”，而是“我曾经经历过什么”。对personal agent来说，聊天记录、操作轨迹、失败案例、某次研究过程中的关键片段，都更接近episodic memory。

### 3. Semantic Memory：沉淀稳定事实与偏好

这一层保存的是经过整理之后仍然成立的知识、偏好和长期状态。用户画像、稳定兴趣、正在推进的项目、已经确认过的判断，更适合归到`semantic memory`。它不是原始日志的堆积，而是从经历里提炼出来、可以在未来反复使用的长期知识。

### 4. Procedural Memory：保存规则、技能与做事方式

这一层对应的是agent“怎么做事”。SOP、工具使用规则、长期形成的工作习惯、某些被验证过的处理流程，都更接近`procedural memory`。它保存的不是世界知识，而是行动方式。

## 写入策略比检索策略更重要

如果要让personal agent长期可用，最关键的设计不是“用哪种embedding model”，而是“什么值得被写进长期记忆”。

至少有几条规则是必要的：

- 所有输入都可以先进入`episodic memory`，但不是所有内容都应该升级为`semantic memory`。
- 只有在被重复提及、与当前项目强相关、产生行动、可用于未来比较，或被用户显式确认有价值时，才值得沉淀为长期记忆。
- 每条长期记忆都应该带有来源、时间和置信度，避免把事实与判断混在一起。
- 尽量更新已有的`semantic memory`，而不是不断append新碎片。
- 显式记录负反馈，例如“这类信息不重要”或“这条价格虽然低，但时间不合适”，因为忽略规则本身也是记忆的一部分。

从工程角度看，personal agent的难点不是能不能把知识塞进去，而是能不能持续维护一套干净、可演化、可审计的长期状态。

## OpenClaw现在把personal memory做到了哪一步

如果只看OpenClaw当前公开文档，它已经有一套相当明确的personal memory管理方式，而且整体上偏`local-first`。[OpenClaw的memory文档](https://docs.openclaw.ai/concepts/memory)直接把工作区里的Markdown文件定义为memory的source of truth：只有写入磁盘的内容，才算真正进入记忆。

按上面的记忆口径来看，OpenClaw现在的大致对应关系已经比较清楚：

- 会话里的当前上下文，更接近`working memory`
- `memory/YYYY-MM-DD.md`更接近`episodic memory`，承担每天的运行记录和近场上下文
- `MEMORY.md`更接近`semantic memory`，存放整理后的长期记忆，而且官方文档明确说它只会在主私人会话中加载，不进入群组等共享上下文
- `USER.md` / `SOUL.md`这类文件，一部分更接近关于用户和代理关系的`semantic memory`，另一部分则带有`procedural memory`的味道，因为它们也在规定长期相处方式和行为边界

在retrieval层，OpenClaw提供`memory_search`和`memory_get`；默认由`memory-core`提供搜索能力，也可以切换到官方的`memory-lancedb`插件，获得自动recall/capture这类更像长期记忆插件的行为。参考 [CLI Memory](https://docs.openclaw.ai/cli/memory)、[Plugins](https://docs.openclaw.ai/plugins)、[Agent Runtime](https://docs.openclaw.ai/concepts/agent)、[USER.md 模板](https://docs.openclaw.ai/reference/templates/USER)。

和很多cloud assistant的黑箱式memory相比，OpenClaw这套设计已经往前走了几步：

- 记忆是可见、可编辑、可审计的，不是平台内部一层不可见的personalization
- 它至少把`episodic memory`和`semantic memory`初步分开了，而不是只给一个模糊的“记忆开关”
- 它明确划出了隐私边界，`MEMORY.md`不进入群组上下文，这比“默认所有入口共享同一份个人记忆”更克制
- 它把retrieval做成了插件槽位，说明memory被视为系统层能力，而不是一个临时patch

但如果从personal agent的目标往回看，OpenClaw现在这套memory还只是走到中段。下面几条判断里，有一部分是基于官方行为边界做的推断：

- 它现在更像`file-centric memory`，而不是`typed memory`。也就是说，它能很好地管理文件中的个人上下文，但还没有把topic、decision、task、preference这些对象变成一等公民
- 它已经有了episodic与semantic的分层，但“什么内容应该从经历沉淀为长期记忆”仍然主要依赖人工整理或agent自觉写入，治理层还不够强
- `MEMORY.md`只在主私人会话中加载，这个设计保护了隐私，但也意味着personal context在群组、子代理和异步任务之间仍然可能出现断裂。这一点是我根据官方加载规则做的推断
- `procedural memory`在OpenClaw里还比较分散，更多体现在文件、模板和运行时约束里，而不是一个显式、统一的记忆层

所以更准确的说法不是“OpenClaw还没有personal memory”，而是：它已经把personal memory做成了一套明确的`local-first file-based memory system`，而且比很多云端产品更可控；但离成熟的personal memory runtime，仍然还有一段路。

## OpenClaw：AI OS与Personal的早期实验？

某种意义上，OpenClaw已经很像AI OS了：它有runtime、memory、plugins、跨平台gateway和系统调用能力，更像一个轻量的AI OS，而不只是一个聊天助手。参考 [OpenClaw Docs: Memory](https://docs.openclaw.ai/concepts/memory)、[OpenClaw Docs: Agent Runtime](https://docs.openclaw.ai/concepts/agent)、[OpenClaw Docs: Plugins](https://docs.openclaw.ai/plugins)。

同时，它又已经开始兼顾personal memory：memory是可见、可编辑、可审计的，而且已经开始区分会话上下文、日常记录和长期记忆。也正因为两条线被提前放进了同一个框架里，OpenClaw才更像一个很有潜力的早期实验。

问题也正出在这里。要真正走向personal，OpenClaw还需要更强的记忆治理能力，比如更清楚地决定什么内容应该沉淀为长期记忆、如何跨群组和异步任务保持连续性、以及怎样让personal memory真正可迁移、可治理，而不只是存在于一组文件里。换句话说，它现在已经证明了AI OS能力和personal memory可以被放进同一个框架，但更理想的形态，未必是把两者永久绑死在一起。

我甚至更倾向于另一种分工：AI OS不一定直接拥有personal memory，它更像权限、调度和执行平面；personal memory则更像一层独立的用户应用或vault。OS负责把邮件、文件、浏览器、日历等能力标准化暴露出来，memory层负责长期记忆的写入、整理、授权和审计。这样personal memory既能最大化利用OS能力，又不必被OS本身吞掉。

所以从这个角度看，OpenClaw的价值不只是它已经很像AI OS，而是它把AI OS和personal memory这两条线提前拉到了一起，也因此把它们之间未来可能需要怎样解耦，提前暴露了出来。

## References

- Park, J. S., et al. [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442)
- Packer, C., et al. [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560)
- Li, J., et al. [Evaluating Very Long-Term Conversational Memory of LLM Agents](https://aclanthology.org/2024.acl-long.747/)
- Wang, W., et al. [Unveiling Privacy Risks in LLM Agent Memory](https://aclanthology.org/2025.acl-long.1227/)
- Sumers, T. R., et al. [Cognitive Architectures for Language Agents](https://collaborate.princeton.edu/en/publications/cognitive-architectures-for-language-agents/)
- Kleppmann, M., et al. [Local-first software: You own your data, in spite of the cloud](https://www.inkandswitch.com/essay/local-first/)
- OpenClaw Docs. [Memory](https://docs.openclaw.ai/concepts/memory)
