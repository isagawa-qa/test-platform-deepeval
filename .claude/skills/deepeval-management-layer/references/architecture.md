---
name: architecture
type: reference
parent: deepeval-management-layer
---

# 5-Layer Architecture — Eval Management Layer

## Overview

The eval management layer follows the same 5-layer architecture as the QA management layer (platform-selenium, platform-playwright). Each layer has one responsibility. Layers only depend downward.

```
Layer 5: Tests        — pytest, AAA, parametrize over goldens, assert via Metric Objects
  Layer 4: EvalRoles  — Orchestrate eval workflows (RAGEvaluator, AgentEvaluator)
    Layer 3: EvalTasks  — One eval operation (run_faithfulness, run_retrieval)
      Layer 2: Metric Objects — Constants (thresholds), state-checks, return self
        Layer 1: DeepEvalInterface — Wraps DeepEval SDK (evaluate, assert_test, LLMTestCase)
```

## Layer Details

### Layer 1: DeepEvalInterface

**File:** `framework/interfaces/deepeval_interface.py`
**Responsibility:** Thin wrapper around DeepEval SDK. All DeepEval imports happen here.

| Method | Wraps | Returns |
|--------|-------|---------|
| `create_test_case()` | `LLMTestCase(...)` | LLMTestCase |
| `create_conversation_test_case()` | `ConversationalTestCase(...)` | ConversationalTestCase |
| `run_evaluation()` | `deepeval.evaluate()` | EvaluationResult |
| `assert_test()` | `deepeval.assert_test()` | None (raises on fail) |
| `load_dataset()` | `EvaluationDataset(...)` | EvaluationDataset |
| `generate_synthetic_dataset()` | `Synthesizer(...)` | EvaluationDataset |

**Rules:**
- All retry logic lives here (3 retries, exponential backoff)
- Config-driven (thresholds, provider, model from config dict)
- No business logic — just wrapping

### Layer 2: Metric Objects

**Files:** `framework/_reference/metrics/*.py`
**Responsibility:** One class per metric category. Encapsulate thresholds and evaluation state.

**Pattern:**
```python
class [Category]Metrics:
    # Constants
    [METRIC]_THRESHOLD = 0.7

    def __init__(self, thresholds=None): ...
    def evaluate(self, test_case) -> self: ...      # Run metrics, store scores
    def is_above_threshold(self, metric) -> bool: ... # Check pass/fail
    def get_score(self, metric) -> float: ...         # Raw score
    def get_detail(self, metric) -> dict: ...         # Breakdown
```

**Rules:**
- Constants = threshold values (configurable via constructor)
- `evaluate()` returns `self` (fluent chaining)
- `is_above_threshold()` returns bool
- Validate required test case parameters
- Never call DeepEval directly — use DeepEvalInterface

### Layer 3: EvalTasks

**Files:** `framework/_reference/tasks/*.py`
**Responsibility:** One eval operation per function. Compose Metric Objects.

**Pattern:**
```python
def run_[type]_eval(deepeval_interface, test_case, thresholds=None) -> None:
    metrics_a = MetricsA(thresholds).evaluate(test_case)
    metrics_b = MetricsB(thresholds).evaluate(test_case)
    return None
```

**Rules:**
- Return None (always)
- Compose Metric Objects, never raw metrics
- Pass thresholds through

### Layer 4: EvalRoles

**Files:** `framework/_reference/roles/*.py`
**Responsibility:** Orchestrate full eval workflow. One class per pipeline type.

**Pattern:**
```python
class [Type]Evaluator:
    def __init__(self, deepeval_interface): ...
    def evaluate_pipeline(self, dataset, thresholds=None) -> dict: ...
```

**Rules:**
- Compose EvalTasks
- Handle dataset iteration
- Call pipeline under test to get actual_output
- Return structured results dict

### Layer 5: Tests

**Files:** `framework/_reference/tests/*.py`
**Responsibility:** pytest test files. AAA pattern. Parametrize over goldens.

**Pattern:**
```python
@pytest.mark.parametrize("golden", dataset)
def test_[metric]_REQ_[ID](golden, deepeval_interface):
    # Arrange
    test_case = deepeval_interface.create_test_case(...)
    metrics = MetricObject()
    # Act
    metrics.evaluate(test_case)
    # Assert
    assert metrics.is_above_threshold("MetricName")
```

**Rules:**
- AAA pattern (Arrange/Act/Assert)
- `@pytest.mark.parametrize` over golden dataset
- Assert via Metric Object state-checks (never raw scores)
- Embed REQ IDs in test function names

## Import Direction

```
Tests → Roles → Tasks → Metric Objects → DeepEvalInterface → DeepEval SDK
```

Never import upward. If a lower layer needs something from a higher layer, the design is wrong.
