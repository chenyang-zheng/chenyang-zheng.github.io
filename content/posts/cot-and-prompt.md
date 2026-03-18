+++
title = 'Prompt Engineering for LLM Cot'
date = 2024-08-26T20:02:20+08:00
lastmod = 2024-08-26T20:02:20+08:00
draft = false
slug = 'cot-and-prompt'
description = 'Early notes on prompt engineering, instruction design, and how chain-of-thought can improve LLM reasoning workflows.'
summary = 'This post outlines a simple view of prompt engineering for LLM CoT, arguing that concise instructions, divide-and-conquer task design, and better workflow decomposition can improve reasoning quality.'
tags = ['prompt-engineering', 'chain-of-thought', 'llm', 'instruction-design']
categories = ['AI', 'Context Engineering']
+++

**Some thoughts on Prompt Optimization and Instructional Design for LLM CoT**:

F(Instruction) = P(Chain of Thought) # instruction and rules are designed for LLM CoT

F(CoT) = P(thinking | Instruction) # CoT is the chain of thought, the thinking process of the model

F(Cot) = F(thinking) = P(answer) # After sorted CoT process based on the instruction, the final answer is generated.

Instruction complexity will affect the LLM understand the task, concise one gets better performance.

Divide and conquer is also a good method to optimize the CoT and workflow. Chain of multiple tasks instead of one complex task might be a better idea.
Supported by [Chain complex prompts for stronger performance](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-prompts)

## Reference
- [Chain of Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)
- [Llama 3: How to Prompt LLMs](https://llama.meta.com/docs/how-to-guides/prompting)
- [Jailbreak Prompt](https://github.com/elder-plinius/L1B3RT45)
- [Anthropic Metaprompt](https://github.com/anthropics/anthropic-cookbook/blob/main/misc/metaprompt.ipynb)
- [Claude: Be Clear and Direct](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct)
- [Claude: Prompt Engineering Interactive Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)

## TODO:
- [ ] Read all the reference materials.
- [ ] [Chain of Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)
- [ ] [Llama 3: How to Prompt LLMs](https://llama.meta.com/docs/how-to-guides/prompting)
- [ ] [Jailbreak Prompt](https://github.com/elder-plinius/L1B3RT45)
- [ ] [Anthropic Metaprompt](https://github.com/anthropics/anthropic-cookbook/blob/main/misc/metaprompt.ipynb)
- [ ] [Claude: Be Clear and Direct](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct)
- [ ] [Claude: Prompt Engineering Interactive Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)
