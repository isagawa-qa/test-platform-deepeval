---
name: deepeval-management-layer-workflow
version: "1.0"
type: workflow
parent: deepeval-management-layer
---

# Eval Management Layer Workflow

## Data Flow

```
USER INPUT          PRE-FLIGHT         AI PROCESSING        CONSTRUCTION
{pipeline_type,  -> {deepeval: ok,  -> {metrics[],       -> {eval_suite: {
 endpoint,          api_keys: ok,      thresholds{},        deepeval_interface_cfg,
 description,       pipeline: ok,      file_plan[]}         metric_objects[],
 golden_path?}      dataset: ok|gen}                        tasks[],
                                                             roles[],
                                                             tests[],
                                                             conftest,
                                                             fixtures[]}}
                                                               |
                                                               v
                                                          EXECUTION
                                                          {results: {
                                                            passed: N,
                                                            failed: M,
                                                            scores{},
                                                            triage[]}}
```

## Step Index

| Step | Input | Output | Fail Action |
|------|-------|--------|-------------|
| 1. User Input | Pipeline type, endpoint, description | Parsed eval request with level (1-4) | Ask user to specify pipeline type (RAG/Chat/Agent/Conversational) |
| 2. Pre-flight | Eval request | Validated environment | Install DeepEval (`pip install deepeval`), set API keys, verify endpoint |
| 3. AI Processing | Validated request + metric catalog | Eval plan: metrics, thresholds, file list | Fall back to GEval with custom criteria if metric selection fails |
| 4. Construction | Eval plan + reference files | Generated eval suite (all 5 layers) | Re-read reference files, fix pattern violations |
| 5. Execution | Eval suite | Test results with triage | Retry NaN scores (3x backoff), HITL triage on persistent failures |

## Metric Selection Matrix

Step 3 uses this matrix to auto-select metrics by pipeline type:

| Pipeline Type | Level | Required Metrics | Optional Metrics |
|--------------|-------|-----------------|-----------------|
| RAG | 2 | FaithfulnessMetric, ContextualRelevancyMetric, AnswerRelevancyMetric | ContextualPrecisionMetric, ContextualRecallMetric, HallucinationMetric |
| Chat | 1 | AnswerRelevancyMetric, HallucinationMetric | BiasMetric, ToxicityMetric |
| Agent | 4 | ToolCorrectnessMetric, TaskCompletionMetric | ArgumentCorrectnessMetric, StepEfficiencyMetric, PlanQualityMetric |
| Conversational | 1+ | KnowledgeRetentionMetric, RoleAdherenceMetric | ConversationCompletenessMetric, ConversationRelevancyMetric |
| Custom | Any | GEval (user-defined criteria) | Any metric |

## Construction Build Order

Step 4 generates files in this exact sequence:

```
1. Read _reference/ files for each layer
2. Generate DeepEvalInterface config (eval_config.py)
3. Generate Metric Object classes (one per category needed)
4. Generate EvalTask modules (compose Metric Objects)
5. Generate EvalRole orchestrator (compose EvalTasks)
6. Generate Test file (pytest, parametrize over goldens)
7. Generate conftest.py (fixtures: golden dataset, DeepEvalInterface init)
8. Generate golden dataset fixtures (JSON)
```

**Mandatory rule:** Read `_reference/` implementation for each layer BEFORE generating that layer. Never generate from memory.

## Pre-Step Reads

| Step | Must Read Before Starting |
|------|--------------------------|
| 1 | `SKILL.md` — vocabulary, pipeline types |
| 2 | `references/architecture.md` — verify DeepEvalInterface pattern |
| 3 | `references/metric-catalog.md` — full metric list with required params |
| 4 | `_reference/*.py` — all reference implementations for layers being generated |
| 5 | Generated test files — verify what will run |

## State Persistence

State saved per eval cycle in `state/eval_cycle.json`:

```json
{
  "pipeline_type": "RAG",
  "eval_level": 2,
  "endpoint": "app.query_pipeline",
  "current_step": 4,
  "metrics_selected": ["FaithfulnessMetric", "ContextualRelevancyMetric", "AnswerRelevancyMetric"],
  "thresholds": {
    "FaithfulnessMetric": 0.7,
    "ContextualRelevancyMetric": 0.6,
    "AnswerRelevancyMetric": 0.6
  },
  "files_generated": ["eval_config.py", "metrics/retrieval_metrics.py"],
  "files_remaining": ["tasks/run_rag_eval.py", "roles/rag_evaluator.py", "tests/test_rag.py"],
  "golden_dataset": "fixtures/golden_rag.json",
  "golden_count": 25,
  "errors": []
}
```

Resume: Agent reads `eval_cycle.json`, picks up at `current_step` with `files_remaining`.

## Execution Output

Each eval run produces results at `output/eval-results.md`:

```markdown
# Eval Results: [Pipeline Type] — [Endpoint]

**Run date:** YYYY-MM-DD
**Metrics:** [count]
**Test cases:** [count]

## Results

| Metric | Score | Threshold | Pass/Fail |
|--------|-------|-----------|-----------|
| FaithfulnessMetric | 0.82 | 0.70 | PASS |
| ContextualRelevancyMetric | 0.54 | 0.60 | FAIL |

## Triage Required

### ContextualRelevancyMetric — FAIL (0.54 < 0.60)
- **Worst test cases:** [list with inputs and scores]
- **Possible causes:** Retriever returning irrelevant chunks
- **Suggested actions:** Review chunking strategy, adjust retrieval top-k

## Summary
Passed: 2/3 | Failed: 1/3
```

## Domain-Specific Rules

1. **Never apply metrics to wrong pipeline type.** Retrieval metrics require `retrieval_context` — applying them to a Chat pipeline (no retrieval) causes runtime errors.
2. **Golden datasets must have minimum 20 entries.** Below 20, eval scores are statistically unreliable. Use Synthesizer to generate if user provides fewer.
3. **DeepEvalInterface retry logic is mandatory.** LLM-as-judge calls fail intermittently. 3 retries with exponential backoff (1s, 2s, 4s) before reporting NaN.
4. **Tests use `@pytest.mark.parametrize` over goldens.** Never write one test per golden. Parametrize gives per-case reporting in pytest output.
5. **Construction follows the 5-layer build order.** Interface → Object → Task → Role → Test. Each layer depends on the one below. Never generate out of order.
