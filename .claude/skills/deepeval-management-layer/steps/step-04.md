---
step: 4
name: Construction
requires: eval_plan, reference_files
produces: eval_suite
requirements: [REQ-IF-003, REQ-MO-001, REQ-MO-002, REQ-TK-001, REQ-RL-001, REQ-TS-001, REQ-TS-002]
---

# Step 4: Construction

## Purpose

Generate the complete eval suite — all 5 layers of code, fixtures, and configuration. This is the codegen step. The agent reads reference implementations first, then generates domain-specific code following the exact same patterns. This step produces runnable pytest code that evaluates the user's LLM pipeline.

## Input

- `eval_plan` from Step 3 (metrics, thresholds, file list)
- Reference implementations in `framework/_reference/`

## Actions

### Pre-Construction Gate

Before writing ANY code:
1. Read `references/architecture.md` — understand the 5-layer pattern
2. Read `references/metric-catalog.md` — understand metric parameters
3. Read EVERY `_reference/` file for each layer you will generate
4. **NEVER generate from memory.** The reference IS the pattern.

### Build Order (STRICT — do not reorder)

**Layer 1: DeepEvalInterface**

Read `interfaces/deepeval_interface.py` as reference.

Generate `framework/interfaces/deepeval_interface.py`:
- Wraps `deepeval.evaluate()`, `deepeval.assert_test()`
- Wraps `LLMTestCase` and `ConversationalTestCase` creation
- Wraps `EvaluationDataset` loading and `Golden` construction
- Wraps `Synthesizer` for synthetic dataset generation
- Includes retry logic (3 retries, exponential backoff) for LLM-as-judge calls
- Config-driven: reads thresholds, provider settings from eval config

```python
class DeepEvalInterface:
    def __init__(self, config: dict):
        self.config = config
        self.max_retries = config.get("max_retries", 3)

    def create_test_case(self, input: str, actual_output: str, **kwargs) -> LLMTestCase:
        """Create LLMTestCase with all 9 parameters."""
        ...

    def run_evaluation(self, test_cases: list, metrics: list) -> EvaluationResult:
        """Run batch evaluation with retry logic."""
        ...

    def assert_test(self, test_case: LLMTestCase, metrics: list) -> None:
        """Assert single test case against metrics."""
        ...

    def load_dataset(self, path: str) -> EvaluationDataset:
        """Load golden dataset from JSON file."""
        ...

    def generate_synthetic_dataset(self, docs: list, count: int) -> EvaluationDataset:
        """Generate synthetic goldens via Synthesizer."""
        ...
```

**Layer 2: Metric Objects**

Read `_reference/metrics/*.py` first.

Generate one file per Metric Object class from eval plan. Each follows the pattern:

```python
class RetrievalMetrics:
    """Metric Object for retrieval quality evaluation."""

    # Constants
    CONTEXTUAL_RELEVANCY_THRESHOLD = 0.6
    CONTEXTUAL_PRECISION_THRESHOLD = 0.6
    CONTEXTUAL_RECALL_THRESHOLD = 0.6

    def __init__(self, thresholds: dict = None):
        self._scores = {}
        if thresholds:
            self.CONTEXTUAL_RELEVANCY_THRESHOLD = thresholds.get(
                "ContextualRelevancyMetric", self.CONTEXTUAL_RELEVANCY_THRESHOLD
            )
        return  # __init__ doesn't return self

    def evaluate(self, test_case: LLMTestCase) -> "RetrievalMetrics":
        """Run retrieval metrics and store scores. Returns self."""
        # Validate retrieval_context exists
        if not test_case.retrieval_context:
            raise ValueError("retrieval_context is required for retrieval metrics")
        # Run metrics, store scores
        ...
        return self

    def is_above_threshold(self, metric_name: str) -> bool:
        """Check if specific metric score meets threshold."""
        ...

    def get_score(self, metric_name: str) -> float:
        """Get raw score for specific metric."""
        ...

    def get_detail(self, metric_name: str) -> dict:
        """Get detailed breakdown for specific metric."""
        ...
```

**Key rules:**
- Constants = threshold values
- State-checks = `is_above_threshold()`, `get_score()`, `get_detail()`
- All methods return `self` (except `is_above_threshold` → bool, `get_score` → float)
- Validate required test case parameters (e.g., retrieval_context for retrieval metrics)

**Layer 3: EvalTasks**

Read `_reference/tasks/*.py` first.

Generate one file per pipeline type eval task:

```python
def run_rag_eval(deepeval_interface: DeepEvalInterface, test_case: LLMTestCase,
                 thresholds: dict = None) -> None:
    """Run RAG evaluation: faithfulness + retrieval + relevancy."""
    faithfulness = FaithfulnessMetrics(thresholds).evaluate(test_case)
    retrieval = RetrievalMetrics(thresholds).evaluate(test_case)
    relevancy = RelevancyMetrics(thresholds).evaluate(test_case)
    # Store results for assertion in test layer
    return None
```

**Key rules:**
- One eval operation per function
- Compose Metric Objects
- Return None
- Pass thresholds through to Metric Objects

**Layer 4: EvalRoles**

Read `_reference/roles/*.py` first.

Generate one file per pipeline type evaluator:

```python
class RAGEvaluator:
    """Orchestrates full RAG pipeline evaluation."""

    def __init__(self, deepeval_interface: DeepEvalInterface):
        self.deepeval_interface = deepeval_interface

    def evaluate_pipeline(self, dataset: EvaluationDataset,
                         thresholds: dict = None) -> dict:
        """Run full RAG eval workflow."""
        results = []
        for golden in dataset:
            test_case = self.deepeval_interface.create_test_case(
                input=golden.input,
                actual_output=self._call_pipeline(golden.input),
                expected_output=golden.expected_output,
                retrieval_context=golden.retrieval_context
            )
            run_rag_eval(self.deepeval_interface, test_case, thresholds)
            results.append(test_case)
        return {"test_cases": results, "count": len(results)}
```

**Layer 5: Tests**

Read `_reference/tests/*.py` first.

Generate pytest test file:

```python
import pytest
from conftest import golden_dataset, deepeval_interface

class TestRAGPipeline:
    """RAG pipeline evaluation tests."""

    @pytest.mark.parametrize("golden", golden_dataset)
    def test_faithfulness_REQ_MO_002(self, golden, deepeval_interface):
        # Arrange
        test_case = deepeval_interface.create_test_case(
            input=golden["input"],
            actual_output=call_pipeline(golden["input"]),
            retrieval_context=golden["retrieval_context"]
        )
        metrics = FaithfulnessMetrics()

        # Act
        metrics.evaluate(test_case)

        # Assert
        assert metrics.is_above_threshold("FaithfulnessMetric")
```

Generate `conftest.py`:
```python
import pytest
import json

@pytest.fixture
def golden_dataset():
    with open("fixtures/golden_rag.json") as f:
        return json.load(f)

@pytest.fixture
def deepeval_interface():
    from interfaces.deepeval_interface import DeepEvalInterface
    import logging
    return DeepEvalInterface(config={"max_retries": 3}, logger=logging.getLogger("eval"))
```

Generate golden dataset fixture (JSON):
```json
[
  {
    "input": "What is the company vacation policy?",
    "expected_output": "Employees receive 15 days of PTO per year...",
    "context": ["HR Policy Manual, Section 4.2: Vacation..."],
    "retrieval_context": ["Section 4.2: All full-time employees receive..."]
  }
]
```

### Post-Construction

After all files generated:
1. Verify each file follows its layer's pattern
2. Check imports resolve between layers
3. Verify golden dataset has required fields for selected metrics

## Requirements

| REQ ID | Behavior | Test Name Convention |
|--------|----------|---------------------|
| REQ-IF-003 | DeepEvalInterface runs batch evaluation and returns results | `test_run_evaluation_REQ_IF_003` |
| REQ-MO-001 | Retrieval metrics validate retrieval_context is present | `test_retrieval_requires_context_REQ_MO_001` |
| REQ-MO-002 | Metric Objects correctly report pass/fail against threshold | `test_threshold_check_REQ_MO_002` |
| REQ-TK-001 | EvalTasks compose correct Metric Objects for pipeline type | `test_task_metric_composition_REQ_TK_001` |
| REQ-RL-001 | EvalRoles orchestrate Tasks in correct sequence | `test_role_task_sequence_REQ_RL_001` |
| REQ-TS-001 | Tests parametrize over golden dataset entries | `test_parametrize_goldens_REQ_TS_001` |
| REQ-TS-002 | Tests assert via Metric Object state-checks not raw scores | `test_assert_via_metric_object_REQ_TS_002` |

## Output

`eval_suite` — complete set of generated files covering all 5 layers. Passed to Step 5.

## Verification

- [ ] All files from eval plan generated
- [ ] DeepEvalInterface wraps all required DeepEval methods
- [ ] Metric Objects have constants + state-checks + return self
- [ ] EvalTasks compose Metric Objects and return None
- [ ] EvalRoles compose EvalTasks
- [ ] Tests use AAA pattern with `@pytest.mark.parametrize`
- [ ] Tests assert via Metric Object state-checks, not raw scores
- [ ] Golden dataset has required fields per pipeline type
- [ ] Reference files were read before generation (check action log)

## Failure Modes

| Failure | Symptom | Recovery |
|---------|---------|----------|
| Reference file missing | `FileNotFoundError` on `_reference/` read | Generate from SKILL.md patterns (degraded) |
| Import cycle | Layer N imports from Layer N+1 | Fix: layers only import downward (Test → Role → Task → Object → Interface) |
| Wrong metric parameters | Test case missing required field for metric | Check metric catalog, add missing field to test case creation |
| Golden schema mismatch | Fields don't match selected metrics | Regenerate golden fixture with correct fields |

## Examples

**Example: RAG Construction Output**
```
Files generated (9):
  ✓ framework/interfaces/deepeval_interface.py (180 lines)
  ✓ framework/_reference/metrics/faithfulness_metrics.py (65 lines)
  ✓ framework/_reference/metrics/retrieval_metrics.py (75 lines)
  ✓ framework/_reference/metrics/relevancy_metrics.py (55 lines)
  ✓ framework/_reference/tasks/run_rag_eval.py (45 lines)
  ✓ framework/_reference/roles/rag_evaluator.py (60 lines)
  ✓ framework/_reference/tests/test_rag_pipeline.py (70 lines)
  ✓ framework/_reference/tests/conftest.py (35 lines)
  ✓ framework/_reference/fixtures/golden_rag.json (50 lines)

All layers follow 5-layer architecture. Imports resolve downward.
```
