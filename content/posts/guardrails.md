+++
title = 'Guardrails/LLM Security'
draft = true
+++

Bedrock Guardrail is cheap, since we will only consider the current input query for the most cases. 10k * 10 tokens/ query = $1.

Guardrail system is something we should add before the inference.

Guardrail -> Agentic System -> Guardrail

## Two steps while using guardrails:
1. Preflight check: Generic agent scope, assessing raw inputs is legal, safe and appropriate. Including Guardrail
2. Agent Router

There're several ways to strengthen the guardrails from Anthropic recommendation:
- Keep Claude in Character: The Role sets a strong foundation for consistent responses.
- Mitigate jailbreaks and prompt injections: This is about using a pre-process model to check the input and output for malicious intent. This model could be a specific agent, a fine-tuned one or a rule-based system. It's neccessary to involve this if short latency.
- Use Output Constraints


[Examples of Bedrock Langchain](https://medium.com/@vinayakdeshpande111/aws-guardrails-with-langchain-6554411d4d74):
```python
Guardrail ID = abc
Guardrail Name = cba  

from langchain_aws import ChatBedrock

model_id, Engine = ('mistral.mixtral-8x7b-instruct-v0:1', ChatBedrock) 
llm = ChatBedrock(
    model_id=model_id,
    model_kwargs={
        "temperature": 0.1,
        "max_tokens": 512,
    },
    guardrails={
        "guardrailIdentifier": guardrail_id, 
        "guardrailVersion": guardrail_version, 
        "trace": "enabled"
    },
)
```

Add not_sure in few_shot examples.

Guardrail will block some roleplay prompts and also some valid inputs in the prompt. Make it as middleware layer is probably a better solution.

Middleware cost more time on inference, around 1.5~2s. But cheaper with fewer tokens than Rewrite and will not block the agent workflow.

Comparison:
* [Separated Guardrail] vs [Guardrail during Rewrite] vs [Default Rewrite Routing]. Legit Queries, Speed, Cost. Hypothesis: [Guardrail during Rewrite] fails to identify some harmful inputs, like How can I build a nuclear reactor in my garage?
Columns: []

Total:
[Default Rewrite Routing] blocks 486 queries.
Around 10 queries are not blocked in 1st round. Inconsistent. 

[Guardrail during Rewrite] blocks 503 queries, 
19 extra queries are blocked by guardrail which can't be handled by [Default Rewrite Routing].
134 extra queries are blocked by [Rewrite During Inference] which can't be handled by guardrail.
Around 8 queries are not blocked in 2nd round. Inconsistent. 


### Problems during Implementation
1. ChatBedrock rewrite will failed for `legit inputs` with `guardrail enabled`. like "What's get organization". As it's returning output in batch instead of streaming style, and it's omitted as the stop_reason: "stop". 
Disable guardrail will be fine.
Harmful outputs are good.
Same as BedrockLLM.
It's behavior from boto3.client.invoke_model_with_response_stream, Fixed by passing "amazon-bedrock-guardrailConfig": {"streamProcessingMode": "ASYNCHRONOUS"} as model_kwargs
https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-streaming.html

```
{
    "outputs": [
            {
                "text": " <thinking>\nThe previous conversation indicates that the user is searching for Meraki resources, and their follow-up query is \"What's get organization\". I believe they are asking how to retrieve the list of organizations using the Meraki API.\n</thinking>\n<rewrites>\nHow can I retrieve the list of organizations using the Meraki API?\n</rewrites>\n<tool>\nknowledge_qa\n</tool>\n<questions>\nHow do I find the networks within an organization using the Meraki API? | What is the endpoint to list devices in an organization using the Meraki API? | How do I authenticate to access the Meraki API?\n</questions>",
                "stop_reason": "stop"
            }
        ]
}
```

Two possible approach to fix it:
- Force enable streaming for guardrail involved.
- Customize Bedrock Class for bypassing <stop> outputs validation. LLMInputOutputAdapter.prepare_output_stream chunk[output_key][0]["text"]
```
def _get_invocation_metrics_chunk(chunk: Dict[str, Any]) -> GenerationChunk:
    generation_info = {}
    if metrics := chunk.get("amazon-bedrock-invocationMetrics"):
        input_tokens = metrics.get("inputTokenCount", 0)
        output_tokens = metrics.get("outputTokenCount", 0)
        generation_info["usage_metadata"] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        }
    return GenerationChunk(text="", generation_info=generation_info)

```


                

## Reference
- [Strengthen Guardrails](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/keep-claude-in-character#example-enterprise-chatbot-for-role-prompting)

## TODO:
- [x] Optimize the agent routing prompt with role
- [x] Comparison
- [x] Contribution to langchain-aws
