---
step: 3
name: AI Processing
requires: validated_environment, parsed_eval_request
produces: eval_plan
requirements: [REQ-PP-001, REQ-PP-002, REQ-PP-003, REQ-MO-003]
---

# Step 3: AI Processing

## Purpose

Select the right metrics for the pipeline type, configure thresholds, and plan the eval suite file structure. This is the intelligence step — where the agent applies domain knowledge about LLM evaluation to produce a concrete build plan. The output is an eval plan that guides all code generation in Step 4.

## Input

- `parsed_eval_request` from Step 1 (pipeline type, eval level, endpoint, description)
- `validated_environment` from Step 2 (provider, dataset info)

## Actions

1. **Select metrics by pipeline type:**

   Read `references/metric-catalog.md` for the full catalog. Apply the selection matrix:

   | Pipeline Type | Required Metrics | Optional Metrics |
   |--------------|-----------------|-----------------|
   | RAG | FaithfulnessMetric, ContextualRelevancyMetric, AnswerRelevancyMetric | ContextualPrecisionMetric, ContextualRecallMetric, HallucinationMetric |
   | Chat | AnswerRelevancyMetric, HallucinationMetric | BiasMetric, ToxicityMetric |
   | Agent | ToolCorrectnessMetric, TaskCompletionMetric | ArgumentCorrectnessMetric, StepEfficiencyMetric, PlanQualityMetric |
   | Conversational | KnowledgeRetentionMetric, RoleAdherenceMetric | ConversationCompletenessMetric, ConversationRelevancyMetric |
   | Codegen | GEval (code correctness criteria) | JsonCorrectnessMetric |
   | Custom | GEval (user-defined criteria) | Any metric |

   **Validation rule:** Never select metrics that require parameters the pipeline can't provide. RAG metrics need `retrieval_context` — if the pipeline doesn't expose retrieval, don't use them.

2. **Configure thresholds:**

   | Metric | Default Threshold | Rationale |
   |--------|------------------|-----------|
   | FaithfulnessMetric | 0.7 | Industry standard for grounding |
   | ContextualRelevancyMetric | 0.6 | Retrieval quality — lower bar, many valid chunks |
   | AnswerRelevancyMetric | 0.6 | Response quality baseline |
   | HallucinationMetric | 0.3 | Inverse — lower is better, 0.3 max acceptable |
   | ToolCorrectnessMetric | 0.8 | Tool selection is critical — high bar |
   | TaskCompletionMetric | 0.7 | Agent must complete tasks reliably |
   | KnowledgeRetentionMetric | 0.6 | Reasonable context retention |
   | RoleAdherenceMetric | 0.7 | Stay in role |
   | BiasMetric | 0.3 | Inverse — lower is better |
   | ToxicityMetric | 0.1 | Very low tolerance |

   If user specifies thresholds → use those. Otherwise → apply defaults.

3. **Determine which Metric Object classes to generate:**

   Map selected metrics to Metric Object classes:
   | Metrics Selected | Metric Object Class Needed |
   |-----------------|---------------------------|
   | FaithfulnessMetric | FaithfulnessMetrics |
   | ContextualRelevancyMetric, ContextualPrecisionMetric, ContextualRecallMetric | RetrievalMetrics |
   | AnswerRelevancyMetric | RelevancyMetrics |
   | HallucinationMetric | HallucinationMetrics |
   | ToolCorrectnessMetric, ArgumentCorrectnessMetric, TaskCompletionMetric, StepEfficiencyMetric | AgentMetrics |
   | KnowledgeRetentionMetric, RoleAdherenceMetric, ConversationCompletenessMetric | ConversationMetrics |
   | BiasMetric, ToxicityMetric, PIILeakageMetric | SafetyMetrics |
   | GEval, DAG | CustomMetrics |

4. **Plan file structure:**

   Based on selected Metric Objects, determine which files to generate:
   ```
   framework/
     interfaces/
       deepeval_interface.py              (always — canonical interface)
     _reference/
       metrics/
         [selected_metric_objects].py  (per pipeline type)
       tasks/
         run_[pipeline_type]_eval.py   (one per pipeline type)
       roles/
         [pipeline_type]_evaluator.py  (one per pipeline type)
       tests/
         test_[pipeline_type]_pipeline.py  (one)
         conftest.py                       (always)
       fixtures/
         golden_[pipeline_type].json       (always)
     resources/
       metric_defaults.py                  (always)
       eval_config.py                      (always)
   ```

5. **Build eval plan:**
   ```json
   {
     "pipeline_type": "RAG",
     "metrics": ["FaithfulnessMetric", "ContextualRelevancyMetric", "AnswerRelevancyMetric"],
     "thresholds": {"FaithfulnessMetric": 0.7, "ContextualRelevancyMetric": 0.6, "AnswerRelevancyMetric": 0.6},
     "metric_objects": ["FaithfulnessMetrics", "RetrievalMetrics", "RelevancyMetrics"],
     "files_to_generate": [
       "deepeval_interface.py", "metrics/faithfulness_metrics.py",
       "metrics/retrieval_metrics.py", "metrics/relevancy_metrics.py",
       "tasks/run_rag_eval.py", "roles/rag_evaluator.py",
       "tests/test_rag_pipeline.py", "tests/conftest.py",
       "fixtures/golden_rag.json"
     ]
   }
   ```

## Requirements

| REQ ID | Behavior | Test Name Convention |
|--------|----------|---------------------|
| REQ-PP-001 | RAG pipeline selects Faithfulness + Retrieval + Relevancy metrics | `test_rag_metric_selection_REQ_PP_001` |
| REQ-PP-002 | Agent pipeline selects ToolCorrectness + TaskCompletion metrics | `test_agent_metric_selection_REQ_PP_002` |
| REQ-PP-003 | Chat pipeline excludes retrieval metrics | `test_chat_excludes_retrieval_REQ_PP_003` |
| REQ-MO-003 | Metric Objects expose configurable thresholds | `test_configurable_threshold_REQ_MO_003` |

## Output

`eval_plan` — JSON with metrics, thresholds, Metric Object classes, and file list. Passed to Step 4.

## Verification

- [ ] Metrics match pipeline type (no retrieval metrics for Chat)
- [ ] Thresholds within valid range (0.0-1.0)
- [ ] At least 2 required metrics selected
- [ ] File plan includes all 5 layers (Interface, Object, Task, Role, Test)
- [ ] Metric Object classes map to selected metrics

## Failure Modes

| Failure | Symptom | Recovery |
|---------|---------|----------|
| Unknown pipeline type | Type not in selection matrix | Fall back to Custom with GEval |
| Metric requires unavailable param | RAG metric on Chat pipeline (no retrieval_context) | Remove metric, warn user |
| No metrics selected | Empty selection after filtering | Default to AnswerRelevancyMetric + HallucinationMetric |
| Conflicting thresholds | User sets threshold > 1.0 or < 0.0 | Clamp to valid range, warn user |

## Examples

**Example 1: RAG Pipeline Plan**
```
Pipeline type: RAG
Metrics selected:
  - FaithfulnessMetric (threshold: 0.7) — required
  - ContextualRelevancyMetric (threshold: 0.6) — required
  - AnswerRelevancyMetric (threshold: 0.6) — required
  - HallucinationMetric (threshold: 0.3) — optional, added

Metric Objects to generate: 4
  FaithfulnessMetrics, RetrievalMetrics, RelevancyMetrics, HallucinationMetrics

Files to generate: 9
  deepeval_interface.py, 4 metric objects, 1 task, 1 role, 1 test, 1 conftest
```

**Example 2: Agent Pipeline Plan**
```
Pipeline type: Agent
Metrics selected:
  - ToolCorrectnessMetric (threshold: 0.8) — required
  - TaskCompletionMetric (threshold: 0.7) — required

Metric Objects to generate: 1
  AgentMetrics

Files to generate: 7
  deepeval_interface.py, 1 metric object, 1 task, 1 role, 1 test, 1 conftest, 1 fixture
```
