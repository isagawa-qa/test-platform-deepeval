"""FaithfulnessMetrics — Layer 2: Metric Object for output grounding.

Wraps FaithfulnessMetric. Verifies output is grounded in retrieved context.
"""

from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase


class FaithfulnessMetrics:
    """Metric Object for faithfulness evaluation."""

    # Constants
    FAITHFULNESS_THRESHOLD = 0.7

    def __init__(self, thresholds: dict = None):
        self._scores = {}
        self._details = {}
        if thresholds:
            self.FAITHFULNESS_THRESHOLD = thresholds.get(
                "FaithfulnessMetric", self.FAITHFULNESS_THRESHOLD
            )

    def evaluate(self, test_case: LLMTestCase) -> "FaithfulnessMetrics":
        """Run faithfulness metric and store score. Returns self."""
        if not test_case.retrieval_context:
            raise ValueError("retrieval_context is required for faithfulness metrics")

        metric = FaithfulnessMetric(threshold=self.FAITHFULNESS_THRESHOLD)
        metric.measure(test_case)
        self._scores["FaithfulnessMetric"] = metric.score
        self._details["FaithfulnessMetric"] = {
            "reason": metric.reason,
            "claims": getattr(metric, "claims", []),
            "truths": getattr(metric, "truths", []),
        }
        return self

    def is_above_threshold(self, metric_name: str = "FaithfulnessMetric") -> bool:
        """Check if faithfulness score meets threshold."""
        score = self._scores.get(metric_name)
        if score is None:
            return False
        return score >= self.FAITHFULNESS_THRESHOLD

    def get_score(self, metric_name: str = "FaithfulnessMetric") -> float:
        """Get raw faithfulness score."""
        return self._scores.get(metric_name, 0.0)

    def get_detail(self, metric_name: str = "FaithfulnessMetric") -> dict:
        """Get detailed breakdown."""
        return self._details.get(metric_name, {})
