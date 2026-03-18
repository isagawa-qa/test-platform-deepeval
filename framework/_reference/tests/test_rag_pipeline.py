"""test_rag_pipeline.py — Layer 5: Tests for RAG pipeline evaluation.

Uses AAA pattern. Parametrizes over golden dataset.
Asserts via Metric Object state-checks, not raw scores.
Real LLM-as-judge evaluation — requires OPENAI_API_KEY.
"""

import pytest
from _reference.metrics.faithfulness_metrics import FaithfulnessMetrics
from _reference.metrics.retrieval_metrics import RetrievalMetrics
from _reference.metrics.relevancy_metrics import RelevancyMetrics


def _mock_rag_pipeline(input_text):
    """Mock RAG pipeline (system under test). Simulates retrieval-augmented generation."""
    return f"Based on the retrieved documents, {input_text.lower()} The answer is found in the company policy."


class TestRAGPipeline:
    """RAG pipeline evaluation tests — real LLM-as-judge."""

    @pytest.mark.parametrize("metric_name,threshold", [
        ("FaithfulnessMetric", 0.7),
    ])
    def test_faithfulness_REQ_MO_002(self, golden, deepeval_interface, metric_name, threshold):
        """Faithfulness metric passes threshold for RAG output."""
        # Arrange
        actual_output = _mock_rag_pipeline(golden["input"])
        test_case = deepeval_interface.create_test_case(
            input=golden["input"],
            actual_output=actual_output,
            retrieval_context=golden["retrieval_context"],
        )
        metrics = FaithfulnessMetrics()

        # Act
        metrics.evaluate(test_case)

        # Assert
        assert metrics.is_above_threshold(metric_name), (
            f"Faithfulness score {metrics.get_score(metric_name):.2f} "
            f"below threshold {metrics.FAITHFULNESS_THRESHOLD}"
        )

    def test_retrieval_relevancy_REQ_MO_001(self, golden, deepeval_interface):
        """Retrieval relevancy passes threshold — validates retrieval_context required."""
        # Arrange
        actual_output = _mock_rag_pipeline(golden["input"])
        test_case = deepeval_interface.create_test_case(
            input=golden["input"],
            actual_output=actual_output,
            retrieval_context=golden["retrieval_context"],
            expected_output=golden.get("expected_output"),
        )
        metrics = RetrievalMetrics()

        # Act
        metrics.evaluate(test_case)

        # Assert
        assert metrics.is_above_threshold("ContextualRelevancyMetric"), (
            f"ContextualRelevancy score {metrics.get_score('ContextualRelevancyMetric'):.2f} "
            f"below threshold {metrics.CONTEXTUAL_RELEVANCY_THRESHOLD}"
        )

    def test_answer_relevancy_REQ_TS_002(self, golden, deepeval_interface):
        """Answer relevancy passes — asserts via Metric Object, not raw score."""
        # Arrange
        actual_output = _mock_rag_pipeline(golden["input"])
        test_case = deepeval_interface.create_test_case(
            input=golden["input"],
            actual_output=actual_output,
        )
        metrics = RelevancyMetrics()

        # Act
        metrics.evaluate(test_case)

        # Assert
        assert metrics.is_above_threshold("AnswerRelevancyMetric")


class TestRetrievalContextValidation:
    """Verify retrieval metrics require retrieval_context."""

    def test_retrieval_requires_context_REQ_MO_001(self, deepeval_interface):
        """RetrievalMetrics raises ValueError when retrieval_context is missing."""
        # Arrange
        test_case = deepeval_interface.create_test_case(
            input="What is the policy?",
            actual_output="The policy states...",
            retrieval_context=None,
        )
        metrics = RetrievalMetrics()

        # Act & Assert
        with pytest.raises(ValueError, match="retrieval_context is required"):
            metrics.evaluate(test_case)
