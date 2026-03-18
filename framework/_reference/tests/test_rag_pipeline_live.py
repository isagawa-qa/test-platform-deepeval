"""test_rag_pipeline_live.py — LIVE integration tests with real LLM-as-judge.

No mocks. Real DeepEval metric evaluation via OpenAI.
Asserts via Metric Object state-checks, not raw scores.
"""

import pytest
from _reference.metrics.faithfulness_metrics import FaithfulnessMetrics
from _reference.metrics.retrieval_metrics import RetrievalMetrics
from _reference.metrics.relevancy_metrics import RelevancyMetrics


def _mock_rag_pipeline(input_text, retrieval_context):
    """Simulated RAG pipeline — returns answer grounded in context."""
    return f"According to company policy: {retrieval_context[0]}"


class TestRAGPipelineLive:
    """RAG pipeline evaluation with real LLM-as-judge scoring."""

    def test_faithfulness_live(self, golden, deepeval_interface):
        """Faithfulness metric — real LLM evaluation."""
        # Arrange
        actual_output = _mock_rag_pipeline(golden["input"], golden["retrieval_context"])
        test_case = deepeval_interface.create_test_case(
            input=golden["input"],
            actual_output=actual_output,
            retrieval_context=golden["retrieval_context"],
        )
        metrics = FaithfulnessMetrics()

        # Act — REAL LLM-as-judge call
        metrics.evaluate(test_case)

        # Assert
        score = metrics.get_score("FaithfulnessMetric")
        print(f"\n  Faithfulness: {score:.2f} (threshold: {metrics.FAITHFULNESS_THRESHOLD})")
        assert metrics.is_above_threshold("FaithfulnessMetric"), (
            f"Faithfulness score {score:.2f} below threshold {metrics.FAITHFULNESS_THRESHOLD}"
        )

    def test_retrieval_relevancy_live(self, golden, deepeval_interface):
        """Retrieval metrics — real LLM evaluation."""
        # Arrange
        actual_output = _mock_rag_pipeline(golden["input"], golden["retrieval_context"])
        test_case = deepeval_interface.create_test_case(
            input=golden["input"],
            actual_output=actual_output,
            retrieval_context=golden["retrieval_context"],
            expected_output=golden.get("expected_output"),
        )
        metrics = RetrievalMetrics()

        # Act — REAL LLM-as-judge call
        metrics.evaluate(test_case)

        # Assert
        for metric_name in ["ContextualRelevancyMetric", "ContextualPrecisionMetric", "ContextualRecallMetric"]:
            score = metrics.get_score(metric_name)
            print(f"\n  {metric_name}: {score:.2f}")
        assert metrics.is_above_threshold("ContextualRelevancyMetric"), (
            f"ContextualRelevancy score {metrics.get_score('ContextualRelevancyMetric'):.2f} "
            f"below threshold {metrics.CONTEXTUAL_RELEVANCY_THRESHOLD}"
        )

    def test_answer_relevancy_live(self, golden, deepeval_interface):
        """Answer relevancy — real LLM evaluation."""
        # Arrange
        actual_output = _mock_rag_pipeline(golden["input"], golden["retrieval_context"])
        test_case = deepeval_interface.create_test_case(
            input=golden["input"],
            actual_output=actual_output,
        )
        metrics = RelevancyMetrics()

        # Act — REAL LLM-as-judge call
        metrics.evaluate(test_case)

        # Assert
        score = metrics.get_score("AnswerRelevancyMetric")
        print(f"\n  AnswerRelevancy: {score:.2f} (threshold: {metrics.ANSWER_RELEVANCY_THRESHOLD})")
        assert metrics.is_above_threshold("AnswerRelevancyMetric"), (
            f"Answer relevancy score {score:.2f} below threshold {metrics.ANSWER_RELEVANCY_THRESHOLD}"
        )
