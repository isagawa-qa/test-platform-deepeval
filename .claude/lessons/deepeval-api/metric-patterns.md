# DeepEval Metric Patterns

<!-- Seeded: expert knowledge about DeepEval metric requirements and behavior -->

## Required Test Case Parameters Per Metric

Every DeepEval metric requires specific fields on the LLMTestCase. Missing a required
field causes a crash or meaningless score. This is the #1 source of eval failures.

| Metric | Required Fields | Optional Fields |
|--------|----------------|-----------------|
| FaithfulnessMetric | `input`, `actual_output`, `retrieval_context` | `context` |
| ContextualRelevancyMetric | `input`, `actual_output`, `retrieval_context` | — |
| ContextualPrecisionMetric | `input`, `actual_output`, `retrieval_context`, `expected_output` | — |
| ContextualRecallMetric | `input`, `actual_output`, `retrieval_context`, `expected_output` | — |
| AnswerRelevancyMetric | `input`, `actual_output` | — |
| HallucinationMetric | `input`, `actual_output`, `context` | — |
| SummarizationMetric | `input`, `actual_output` | — |
| BiasMetric | `input`, `actual_output` | — |
| ToxicityMetric | `input`, `actual_output` | — |
| ToolCorrectnessMetric | `input`, `actual_output`, `tools_called`, `expected_tools` | — |
| TaskCompletionMetric | `input`, `actual_output` | `expected_output` |
| GEval | `input`, `actual_output` | Depends on `evaluation_params` |
| KnowledgeRetentionMetric | ConversationalTestCase with turns | `chatbot_role` |
| RoleAdherenceMetric | ConversationalTestCase with turns | `chatbot_role` |

## Inverse Metrics

Most metrics: higher score = better. Some metrics are **inverse** — lower = better.

| Metric | Direction | Pass Condition |
|--------|-----------|----------------|
| BiasMetric | Inverse | score ≤ threshold |
| ToxicityMetric | Inverse | score ≤ threshold |
| HallucinationMetric | Inverse | score ≤ threshold |
| All others | Normal | score ≥ threshold |

**Anti-pattern**: Using `is_above_threshold()` with the same logic for all metrics.
Safety/bias metrics need inverted comparison: `score <= threshold` means passing.

## Threshold Ranges

Sensible defaults based on DeepEval docs and production experience:

| Category | Metric | Default | Tight | Loose |
|----------|--------|---------|-------|-------|
| RAG Core | FaithfulnessMetric | 0.7 | 0.85 | 0.5 |
| RAG Core | ContextualRelevancyMetric | 0.6 | 0.8 | 0.4 |
| RAG Core | ContextualPrecisionMetric | 0.6 | 0.8 | 0.4 |
| RAG Core | ContextualRecallMetric | 0.6 | 0.8 | 0.4 |
| General | AnswerRelevancyMetric | 0.6 | 0.8 | 0.4 |
| Safety | BiasMetric | 0.3 | 0.1 | 0.5 |
| Safety | ToxicityMetric | 0.1 | 0.05 | 0.3 |
| Agent | ToolCorrectnessMetric | 0.8 | 0.95 | 0.6 |
| Agent | TaskCompletionMetric | 0.7 | 0.85 | 0.5 |

## Metric Name to Constant Conversion (Learned: 2026-03-18)

**Anti-pattern**: Using simple `.replace("Metric", "").upper()` to convert CamelCase metric names to SNAKE_CASE constants.

`ContextualRelevancyMetric` → `.replace("Metric","").upper()` → `CONTEXTUALRELEVANCY` (WRONG)
`ContextualRelevancyMetric` → CamelCase split + upper → `CONTEXTUAL_RELEVANCY` (CORRECT)

**Fix**: Use `re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name)` before `.upper()` to insert underscores at CamelCase boundaries.

**Rule**: Any `_to_const()` or similar name-conversion helper in Metric Objects MUST handle CamelCase → SNAKE_CASE properly. Test with multi-word metric names (ContextualRelevancy, ContextualPrecision, ContextualRecall, ToolCorrectness, TaskCompletion, KnowledgeRetention, RoleAdherence, AnswerRelevancy).

## Metric Categories by Pipeline Type

| Pipeline | Required Metrics | Optional Metrics |
|----------|-----------------|------------------|
| RAG | Faithfulness, ContextualRelevancy | ContextualPrecision, ContextualRecall, AnswerRelevancy |
| Chat | AnswerRelevancy, Bias, Toxicity | Hallucination, GEval (custom) |
| Agent | ToolCorrectness, TaskCompletion | GEval (custom criteria) |
| Conversational | KnowledgeRetention, RoleAdherence | GEval (custom criteria) |
