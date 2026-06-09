git # Adversarial Scrum Harness：别只让 Agent 重开，要让它记住为什么死

随着Mythos等模型的推出，LLM能力在越来越多的真实任务中展现出超人类的能力，甚至是Claude Code推出了/goal模式，自动化Agent已经变得越来越可靠。

但在实际使用中这类长时Agent仍然没法解决“最后一公里”的问题，花了大量的token和时间进行迭代出的成果却远不如预期，越往后的迭代引入了更多预期外的行为，本应省下的时间反而通过最后的人工微调还了回去。

这种过程让我想起了阿汤哥的电影《明日边缘》。

主角每次死了都会重来。第一次上沙滩，被杂兵打死。第二次知道左边会爆炸。第三次知道该躲哪块钢板。看起来他在进步。

但问题是：如果他只是在沙滩上无限刷经验，他真的能通关吗？

不一定。因为真正的矛盾不在沙滩上的杂兵，而在根本目标Omega。

这也是很多Agent Loop 的问题。它们确实在循环。它们确实在收集失败。它们也确实在更新情景(few shot example)

但 情景(evidence) 不等于 经验(rule)。

一次失败只是一次失败。真正有价值的是从失败中总结出规则：为什么失败？这个失败说明哪条边界不存在？这条边界要不要进入下一轮的约束？

否则我们只是在让 Agent 一遍遍上沙滩。

## Harness 不应该只是让 Agent 重试

传统的 agent harness 关注很多重要问题：

* 下一步写product和designspec
* 如何调用工具
* 如何管理和交接状态
* 如何控制和分解上下文
* 如何做 tracing 和 eval
* 如何管理权限和沙箱
* 如何接入更真实的评测工具

这些都很重要。

但我现在关心的是另一个问题：

> Agent 每一次失败之后，系统有没有能力把失败压缩成规则？

如果没有，它就是在重试。

如果有，它才是在学习。

## 从 Evidence 到 Fence

Evaluator 接上真实工具之后，确实会变强。

它不再只是“我感觉这个功能完成了”，而是能拿到真实反馈：测试失败、页面打不开、API 报错、风格不一致、权限不对。

这有点像给缸中之脑接上神经反馈。

但这里还有一步：

```text
Evidence → Gap Analysis → Fence
```

| Evidence / Example (情景) | Fence (约束边界) |
| :--- | :--- |
| 这次失败了。 | 以后不能越过这条线。 |
| 下次参考这个例子。 | 下次不要犯这一类错。 |

这就是我觉得普通 eval 和 adversarial harness 的差别。

普通 eval 发现失败。

Adversarial harness 要把失败变成约束。

## 为什么是 User Story？

一开始我也以为，问题可以靠更好的 SPEC 解决。

把需求写清楚。把上下文写清楚。把风格写清楚。把验收标准写清楚。最好把 agent 可能犯的错也写清楚。

听起来很合理。

直到你发现，SPEC 越写越像百科全书，agent 越跑越像背着百科全书赶路的人。

它什么都带着。

但不知道现在该看哪一页。

所以我现在更倾向于：计划不要试图定义每一步，而是定义航点。

在这个系统里，`exec-plan` 是阶段目标，`user story` 是这个阶段目标的可观测拆分。

`exec-plan` 太大，难以直接验证。

`code diff` 太小，容易失去业务语义。

`user story` 正好夹在中间。

它足够小，agent 能快速迭代。

它足够语义化，人能监督。

它也足够工程化，可以映射到代码、文档、配置、prompt、UI、测试和运行证据。

所以 user story 不是普通需求卡。

它是最小语义观测点。

## 双层 Loop

这个 harness 里有两层循环。

外层循环：

```text
exec-plan → user story
```

它问的是：

```text
这个 user story 是否真正承载 / 推进 exec-plan？
```

内层循环：

```text
user story → artifacts
```

它问的是：

```text
这些代码、文档、配置、prompt、UI、测试和证据，是否真正实现了 user story？
```

这两层看起来很像。

每层都是：

```text
目标 → 生成 → 判别 → 残差 → 纠偏
```

区别只是对象不同。

外层处理的是目标语言。

内层处理的是实现产物。

## Discriminator 不只是挑刺，它还要还原目标

这里是最关键的地方。

如果 evaluator 只是挑错，它很容易变成一个无限找茬机器。

今天找测试问题。

明天找风格问题。

后天找性能问题。

Generator 就不停打补丁。

这会发散。

所以我们需要让 Discriminator 做一件更像“还原魔方”的事：

> 从产出物反向推导它到底在实现什么目标。

比如内层原始目标是一个 user story：

```text
作为用户，我想搜索 API 文档，并得到和产品相关的结果。
```

Generator 产出了代码、UI、配置、prompt 和文档。

Discriminator 不只是跑测试。

它还要尝试从这些产出物中反向还原：

```text
这个系统看起来是在实现什么？
```

如果它还原出来的是：

```text
用户想和一个通用聊天机器人对话。
```

那就出问题了。

代码可能能跑。

测试可能能过。

UI 可能还挺漂亮。

但目标已经偏了。

## 为什么要压缩回 User Story？

因为目标本身是多维的。

一个 exec-plan 里可能同时包含功能、体验、风格、约束、安全、性能、上下文和业务意图。

而 artifacts 更是多模态的：代码、文档、配置、prompt、UI、日志、测试结果。

这些东西直接比，很难。

所以我们需要把实现结果压缩回一个更小维度的语义表达。

在内层，这个表达就是 user story。

```text
artifacts → reconstructed user story
```

然后比较：

```text
original user story ↔ reconstructed user story
```

这不是为了写作文。

而是为了发现 Generator 在哪里 freestyle 了。

它多做了什么？

少做了什么？

把搜索做成了聊天？

把 API 文档做成了通用帮助中心？

把风格对齐理解成了 UI 炫技？

这些偏差，如果只看代码，很难抓。

但如果把产出物压缩回 user story，就会变得更明显。

## Residual：别只问过没过，要问差在哪里

这个系统不应该只输出 pass / fail。

它应该输出 residual。

```text
R_story    = exec-plan 和 user story 的差距
R_artifact = user story 和 artifacts/evidence 的差距
R_global   = exec-plan 和 artifacts/evidence 的差距
```

其中最危险的是 `R_global`。

因为可能出现这种情况：

```text
user story 看起来对齐 exec-plan
artifacts 也看起来实现了 user story
但最终产物没有推进真正的阶段目标
```

这就是局部正确，全局跑偏。

所以我们需要一个 Cross-alignment Gate。

它不问：

```text
你是不是做完了？
```

它问：

```text
如果从最终产物倒推回去，它还像不像一开始的目标？
```

## 这像 Backpropagation，但不是数学里的那个

正向过程是：

```text
exec-plan → user story → artifacts
```

反向过程是：

```text
artifacts → reconstructed user story → reconstructed exec-plan
```

然后我们比较残差。

如果 `R_artifact` 高，说明 artifacts 没实现 user story，回内层改代码、文档、配置、prompt。

如果 `R_story` 高，说明 user story 没承载 exec-plan，回外层重写或拆分 story。

如果 `R_global` 高，说明局部都对，但组合之后全局不对，要更新 contract、hard fences 或 evidence requirements。

这不是数值梯度反传。

这是语义残差反传。

## 为什么这比单纯 AI 互相挑战更容易收敛？

因为挑战空间是无限的。

如果只是让一个 AI 生成，另一个 AI 挑战，它们很容易陷入一种很累的循环：

```text
Generator: 我完成了。
Verifier: 我找到一个角度说你没完成。
Generator: 我修。
Verifier: 我再换一个角度。
```

这不是收敛。

这是吵架。

我们需要一个共同介质。

这个介质就是每一层的输入目标。

外层用：

```text
exec-plan ↔ user story
```

内层用：

```text
user story ↔ artifacts/evidence
```

跨层用：

```text
exec-plan ↔ evidence
```

Discriminator 的任务不是无限挑战，而是围绕一个问题工作：

```text
这个产出物能否被还原回原目标？
```

能还原，说明信息保住了。

不能还原，说明目标在生成过程中丢了。

## Sprint Contract 仍然有用

如果基座模型已经足够强，是不是就不需要 sprint contract 了？

我暂时不这么认为。

至少在早期实验阶段，sprint contract 仍然是很有用的人类监督接口。

它比 exec-plan 更具体。

比测试用例更抽象。

比代码更可读。

比完整 SPEC 更轻。

它告诉 agent：

```text
这一小段工作，怎样才算真的推进了目标？
```

而不是告诉它每一步怎么写。

## 这个东西叫什么？

我暂时叫它：

```text
Adversarial Scrum Harness
```

这个名字有点中二，但还挺准确。

Scrum 给了我们 user story 和 sprint contract。

GAN 给了我们 generator / discriminator 的对抗精神。

Harness 给了我们 tools、state、context、evidence、checkpoint 和 loop。

合起来就是：

```text
目标被拆成 user story
user story 被实现成 artifacts
artifacts 被 verifier 反向还原成目标
还原失败的部分变成 residual
residual 被路由到该修的层级
成功和失败都沉淀成 fences
```

## 最后

不要把 SPEC 写成百科全书。

把它写成航点。

让 agent 飞。

让 verifier 看它留下的轨迹。

让 residual 告诉你它偏了多少。

让 fences 记住它以前撞过哪堵墙。

然后继续 loop。

不是每一次重开都有意义。

只有当失败变成规则，循环才不是惩罚。

它才是学习。
