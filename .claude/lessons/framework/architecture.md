# Framework Architecture

<!-- Seeded: expert knowledge for autonomous eval suite generation -->

## The 5-Layer Architecture

All eval code follows a strict 5-layer separation. Each layer has specific responsibilities
and restrictions. The architecture mirrors the QA platform pattern (Selenium/Playwright).

```
Eval Path:  Test → Role → Task → Metric Object → DeepEvalInterface → DeepEval SDK
```

| Layer | Name | Composes | Decorator | Returns |
|-------|------|----------|-----------|---------|
| **DeepEvalInterface** | Wraps DeepEval SDK | Nothing (leaf) | None | Various |
| **Metric Object** | One metric category | DeepEvalInterface (via test case) | None | `self` (fluent) |
| **EvalTask** | One eval operation | Metric Objects | None | `None` |
| **EvalRole** | Pipeline evaluator | EvalTasks | None | `dict` (results) |
| **Test** | Arrange/Act/Assert | Roles or Metric Objects directly | `@pytest.mark.parametrize` | N/A |

## DeepEvalInterface-First Rule (CRITICAL)

**ALL DeepEval SDK calls go through DeepEvalInterface. No exceptions.**

- Never call `deepeval.evaluate()` or `deepeval.assert_test()` directly in Tasks, Roles, or Tests
- Never import `LLMTestCase` or `EvaluationDataset` directly in layers 2-5
- Never construct metric instances outside of Metric Objects (layer 2)
- DeepEvalInterface is at `framework/interfaces/deepeval_interface.py` — NOT in `_reference/`

```python
# WRONG — bypasses DeepEvalInterface
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
test_case = LLMTestCase(input="...", actual_output="...")

# RIGHT — goes through DeepEvalInterface
test_case = deepeval_interface.create_test_case(input="...", actual_output="...")
```

## Composition Over Inheritance

Every layer composes the layer below — never inherits from it.

```python
# WRONG — inheritance
class RAGEvaluator(DeepEvalInterface):
    pass

# RIGHT — composition
class RAGEvaluator:
    def __init__(self, deepeval_interface):
        self.deepeval_interface = deepeval_interface
```

## Metric Object Pattern

Metric Objects are layer 2. They wrap one category of DeepEval metrics.

- **Constants** = threshold values as class attributes
- **State-checks** = `is_above_threshold()`, `get_score()`, `get_detail()`
- **Returns self** = fluent chaining (`metrics.evaluate(test_case).is_above_threshold("X")`)
- **One class per category**: RetrievalMetrics, FaithfulnessMetrics, AgentMetrics, etc.

```python
class RetrievalMetrics:
    CONTEXTUAL_RELEVANCY_THRESHOLD = 0.6

    def evaluate(self, test_case) -> "RetrievalMetrics":
        # Run metrics, store scores
        return self

    def is_above_threshold(self, metric_name) -> bool:
        # Check stored score vs constant
        return self._scores[metric_name] >= threshold
```

## EvalTask Pattern

EvalTasks are layer 3. They compose Metric Objects to run one eval operation.

- **Composes** Metric Objects (imports from `_reference.metrics.*`)
- **Returns None** — results are stored on test case or accessed via Metric Object state-checks
- **One function per pipeline type**: `run_rag_eval()`, `run_agent_eval()`

## EvalRole Pattern

EvalRoles are layer 4. They orchestrate EvalTasks across a dataset.

- **Composes** EvalTasks (imports from `_reference.tasks.*`)
- **Takes** DeepEvalInterface in constructor (for test case creation)
- **Iterates** over golden dataset, creating test cases and running tasks

## Test Pattern

Tests are layer 5. They follow pytest AAA (Arrange/Act/Assert).

- **Fixtures** from `conftest.py`: `deepeval_interface`, `golden_rag_dataset`
- **Parametrize** over golden datasets: `@pytest.mark.parametrize("golden", golden_dataset)`
- **Assert** via Metric Object state-checks: `assert metrics.is_above_threshold("X")`
- **Never** assert on raw scores: `assert score > 0.7` is an anti-pattern
