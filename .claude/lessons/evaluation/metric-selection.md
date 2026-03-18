# Metric Selection: Pipeline-to-Metric Mapping

<!-- Seeded: expert knowledge about matching metrics to pipeline types -->

## The Problem

Applying all available metrics to every pipeline type. "More metrics = more thorough."
Developer selects FaithfulnessMetric + ContextualRelevancyMetric for a simple chatbot
with no retrieval component.

## Why It Fails

Retrieval metrics require `retrieval_context` in the test case. A Chat pipeline doesn't
have retrieval. The eval either crashes (missing field) or returns meaningless scores
(empty context → 0.0 for everything). Developer wastes time debugging "failures" that
are actually misconfiguration.

## Correct Approach

Match metrics to pipeline type using this selection matrix:

| Pipeline Type | Required Metrics | Why |
|--------------|-----------------|-----|
| RAG | Faithfulness, ContextualRelevancy | Measures grounding + retrieval quality |
| Chat | AnswerRelevancy, Bias, Toxicity | Measures relevance + safety |
| Agent | ToolCorrectness, TaskCompletion | Measures tool use + task success |
| Conversational | KnowledgeRetention, RoleAdherence | Measures memory + persona consistency |

**Never mix categories.** If a pipeline has no retrieval, it gets no retrieval metrics.
If it has no tool calls, it gets no agent metrics.

## Edge Cases

- **RAG + Chat hybrid**: Use RAG metrics (retrieval is the differentiator)
- **Agent + RAG**: Use both Agent AND RAG metrics (test case has both fields)
- **Custom pipeline**: Use GEval with natural language criteria
- **Safety always**: Bias + Toxicity can be added to ANY pipeline type as optional

## Source

DeepEval docs: each metric's "Required Parameters" section. Audit finding: "Metric
selection is non-obvious for beginners" (pain point severity: High).
