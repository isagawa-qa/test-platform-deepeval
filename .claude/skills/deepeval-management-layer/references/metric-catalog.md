---
name: metric-catalog
type: reference
parent: deepeval-management-layer
---

# DeepEval Metric Catalog

Complete catalog of DeepEval metrics with required test case parameters. Reference this before metric selection (Step 3) and code generation (Step 4).

## RAG Metrics — Retriever

| Metric | What It Measures | Required Params | Default Threshold |
|--------|-----------------|-----------------|-------------------|
| ContextualRelevancyMetric | Are retrieved chunks relevant to the query? | input, retrieval_context | 0.6 |
| ContextualPrecisionMetric | Are relevant chunks ranked higher? | input, retrieval_context, expected_output | 0.6 |
| ContextualRecallMetric | Are all relevant chunks retrieved? | input, retrieval_context, expected_output | 0.6 |

## RAG Metrics — Generator

| Metric | What It Measures | Required Params | Default Threshold |
|--------|-----------------|-----------------|-------------------|
| FaithfulnessMetric | Is the output grounded in retrieved context? | input, actual_output, retrieval_context | 0.7 |
| AnswerRelevancyMetric | Does the answer address the question? | input, actual_output | 0.6 |
| HallucinationMetric | Does the output contain fabricated claims? | input, actual_output, context | 0.3 (inverse) |

## Agentic Metrics

| Metric | What It Measures | Required Params | Default Threshold |
|--------|-----------------|-----------------|-------------------|
| ToolCorrectnessMetric | Did the agent select the right tools? | input, actual_output, tools_called, expected_tools | 0.8 |
| ArgumentCorrectnessMetric | Did the agent pass correct arguments? | input, actual_output, tools_called, expected_tools | 0.7 |
| TaskCompletionMetric | Did the agent complete the task? | input, actual_output (full trace) | 0.7 |
| StepEfficiencyMetric | Was the execution path efficient? | input, actual_output (full trace) | 0.6 |
| PlanQualityMetric | Was the plan well-formed? | input, actual_output (full trace) | 0.6 |
| PlanAdherenceMetric | Did the agent follow its plan? | input, actual_output (full trace) | 0.7 |

## Conversational Metrics

| Metric | What It Measures | Required Params | Default Threshold |
|--------|-----------------|-----------------|-------------------|
| KnowledgeRetentionMetric | Does the model retain context across turns? | ConversationalTestCase with turns | 0.6 |
| RoleAdherenceMetric | Does the model stay in role? | ConversationalTestCase with turns | 0.7 |
| ConversationCompletenessMetric | Was the objective achieved? | ConversationalTestCase with turns | 0.6 |
| ConversationRelevancyMetric | Are responses relevant to conversation flow? | ConversationalTestCase with turns | 0.6 |

## Safety Metrics

| Metric | What It Measures | Required Params | Default Threshold |
|--------|-----------------|-----------------|-------------------|
| BiasMetric | Does output contain biases? | input, actual_output | 0.3 (inverse) |
| ToxicityMetric | Does output contain toxic content? | input, actual_output | 0.1 (inverse) |
| PIILeakageMetric | Does output leak PII? | input, actual_output | 0.1 (inverse) |

## Custom Metrics

| Metric | What It Measures | Required Params | Default Threshold |
|--------|-----------------|-----------------|-------------------|
| GEval | Custom criteria via natural language | Configurable per criteria | User-defined |
| DAG | Decision-tree evaluation | Configurable per tree | User-defined |
| JsonCorrectnessMetric | Is output valid JSON matching schema? | input, actual_output, expected_output | 1.0 (exact) |
| SummarizationMetric | Does summary capture key info? | input, actual_output | 0.6 |

## Parameter Reference

| Parameter | Type | Used By |
|-----------|------|---------|
| input | str | All metrics |
| actual_output | str | All metrics |
| expected_output | str | Precision, Recall, Hallucination, JsonCorrectness |
| context | list[str] | Hallucination |
| retrieval_context | list[str] | All retrieval metrics, Faithfulness |
| tools_called | list[ToolCall] | Agentic metrics |
| expected_tools | list[str] | Agentic metrics |
| token_cost | float | Cost tracking (optional) |
| completion_time | float | Latency tracking (optional) |

## Inverse Metrics

Some metrics measure negative attributes where LOWER is BETTER:
- HallucinationMetric: score 0.3 means 30% hallucinated — threshold is a MAX
- BiasMetric: score 0.1 means 10% biased — threshold is a MAX
- ToxicityMetric: score 0.05 means 5% toxic — threshold is a MAX

For these metrics, `is_above_threshold()` returns True when score ≤ threshold (pass = low score).
