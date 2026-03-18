+++
title = 'RAG Optimization'
date = 2024-08-29T20:02:20+08:00
draft = true
+++

Credit to Richard Feynman, i should apply scientific method on the RAG optimization, not just about prompt engineering, we also need to think about the agentic flow like more query and answer validations during the inference.
The goal is to find the best way to optimize the quality, and then to think about the cost including time and money.

Especially for Observation for Agentic LLM, find inner connection between LLM own knowledge and embedded knowledge database. Loop and reason.

## Goals
not sure if goal is part of scientific method, but it's a good way to guide the hypothesis.

 - Achieve 90% correct on **positive** test datasets.
 - Achieve 90% correct on **negative** test datasets.
 - Time to first token: < 6s
 - Cost: < $0.01 / query
 - Find Devvie style for RAG retrieval, don't be another ChatGPT or Claude, say more meanful and less craps.


## Hypothesis 1: Prompt Optimization

### Hypothesis
QA prompts can be optimized by removing ambiguous words and adding clear Chain of Thought (CoT) instructions.

### Experiment
1. Modify QA prompts: remove ambiguous words, add clear CoT instructions
2. Test against current baseline

### Observation
Long CoT instructions may lead to hallucination. [See more details]({{< ref "hallucination.md" >}})

### Conclusion
Especially for Agentic LLM, find inner connection between LLM own knowledge and embedded knowledge database. Loop and reason.

## Hypothesis 2: Agentic QA with Reranking

### Hypothesis
Self-reflected agentic QA with Reranking and query rewriting based on retrieval will significantly improve answer quality. Original Query -> RAG Retrieval -> Answer not good ->Rewrite Query -> QA

### Experiment
[To be designed]

### Observation
[Pending experiment]

### Conclusion
[Pending results]

## Hypothesis 3: Leveraging LLM and RAG Knowledge

### Hypothesis
We can find a way to leverage both LLM knowledge and RAG knowledge to ensure answers are both correct and specific.

### Experiment
[To be designed]

### Observation
[Pending experiment]

### Conclusion
[Pending results]


## TODO:
- [ ] Check [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html?ref=blog.heim.xyz)
- [ ] Scale AI [Plan Search](https://mp.weixin.qq.com/s/xhV9HoeEP22RjuWTjgbPqg)
