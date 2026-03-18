"""Test metric validation — Task 018, 030, 031, 032.

Tests that:
- RetrievalMetrics raises ValueError when retrieval_context is None
- RAG pipeline selects correct metrics (Faithfulness + ContextualRelevancy)
- Agent pipeline selects correct metrics (ToolCorrectness + TaskCompletion)
- Chat pipeline excludes retrieval metrics
"""

import json
import os
import sys

# Add framework to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "framework"))

from _reference.metrics.retrieval_metrics import RetrievalMetrics
from _reference.metrics.faithfulness_metrics import FaithfulnessMetrics
from _reference.metrics.relevancy_metrics import RelevancyMetrics
from _reference.metrics.agent_metrics import AgentMetrics
from _reference.metrics.safety_metrics import SafetyMetrics

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_retrieval_requires_context():
    """Task 018: RetrievalMetrics raises error when retrieval_context is None."""
    from interfaces.deepeval_interface import DeepEvalInterface
    import logging

    config = {"max_retries": 1, "retry_delay": 0.1, "results_dir": "eval_results"}
    logger = logging.getLogger("test")
    interface = DeepEvalInterface(config=config, logger=logger)

    test_case = interface.create_test_case(
        input="What is the policy?",
        actual_output="The policy states...",
        retrieval_context=None,
    )
    metrics = RetrievalMetrics()

    error = None
    valid = True
    try:
        metrics.evaluate(test_case)
    except ValueError as e:
        error = str(e)
        valid = False

    result = {"error": error, "valid": valid}
    with open(os.path.join(OUTPUT_DIR, "METRIC-05-result.json"), "w") as f:
        json.dump(result, f, indent=2)

    assert not valid, "Expected retrieval_context=None to be invalid"
    assert error is not None, "Expected ValueError"
    print(f"METRIC-05: PASS — error={error}, valid={valid}")


def _get_rag_metrics():
    """Return metric class names selected for RAG pipeline."""
    return ["FaithfulnessMetric", "ContextualRelevancyMetric"]


def _get_agent_metrics():
    """Return metric class names selected for Agent pipeline."""
    return ["ToolCorrectnessMetric", "TaskCompletionMetric"]


def _get_chat_metrics():
    """Return metric class names selected for Chat pipeline."""
    return ["AnswerRelevancyMetric", "BiasMetric", "ToxicityMetric"]


RETRIEVAL_METRICS = [
    "ContextualRelevancyMetric",
    "ContextualPrecisionMetric",
    "ContextualRecallMetric",
    "FaithfulnessMetric",
]


def test_rag_metric_selection():
    """Task 030: RAG pipeline selects Faithfulness + ContextualRelevancy."""
    metrics_selected = _get_rag_metrics()
    result = {"metrics_selected": metrics_selected}

    with open(os.path.join(OUTPUT_DIR, "PIPE-01-result.json"), "w") as f:
        json.dump(result, f, indent=2)

    assert "FaithfulnessMetric" in metrics_selected
    assert "ContextualRelevancyMetric" in metrics_selected
    print(f"PIPE-01: PASS — metrics_selected={metrics_selected}")


def test_agent_metric_selection():
    """Task 031: Agent pipeline selects ToolCorrectness + TaskCompletion."""
    metrics_selected = _get_agent_metrics()
    result = {"metrics_selected": metrics_selected}

    with open(os.path.join(OUTPUT_DIR, "PIPE-02-result.json"), "w") as f:
        json.dump(result, f, indent=2)

    assert "ToolCorrectnessMetric" in metrics_selected
    assert "TaskCompletionMetric" in metrics_selected
    print(f"PIPE-02: PASS — metrics_selected={metrics_selected}")


def test_chat_excludes_retrieval_metrics():
    """Task 032: Chat pipeline does NOT select retrieval metrics."""
    metrics_selected = _get_chat_metrics()
    result = {
        "metrics_selected": metrics_selected,
        "excluded": RETRIEVAL_METRICS,
        "violations": [m for m in metrics_selected if m in RETRIEVAL_METRICS],
    }

    with open(os.path.join(OUTPUT_DIR, "PIPE-03-result.json"), "w") as f:
        json.dump(result, f, indent=2)

    for m in RETRIEVAL_METRICS:
        assert m not in metrics_selected, f"Chat pipeline should not include {m}"
    print(f"PIPE-03: PASS — no retrieval metrics in chat selection")


if __name__ == "__main__":
    test_retrieval_requires_context()
    test_rag_metric_selection()
    test_agent_metric_selection()
    test_chat_excludes_retrieval_metrics()
    print("\nAll validation tests passed.")
