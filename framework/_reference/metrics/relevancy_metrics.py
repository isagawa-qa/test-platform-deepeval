"""RelevancyMetrics — Layer 2: Metric Object for answer relevancy.

Wraps AnswerRelevancyMetric. Verifies output addresses the input question.
"""

from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase


class RelevancyMetrics:
    """Metric Object for answer relevancy evaluation."""

    # Constants
    ANSWER_RELEVANCY_THRESHOLD = 0.6

    def __init__(self, thresholds: dict = None):
        self._scores = {}
        self._details = {}
        if thresholds:
            self.ANSWER_RELEVANCY_THRESHOLD = thresholds.get(
                "AnswerRelevancyMetric", self.ANSWER_RELEVANCY_THRESHOLD
            )

    def evaluate(self, test_case: LLMTestCase) -> "RelevancyMetrics":
        """Run relevancy metric and store score. Returns self."""
        metric = AnswerRelevancyMetric(threshold=self.ANSWER_RELEVANCY_THRESHOLD)
        metric.measure(test_case)
        self._scores["AnswerRelevancyMetric"] = metric.score
        self._details["AnswerRelevancyMetric"] = {"reason": metric.reason}
        return self

    def is_above_threshold(self, metric_name: str = "AnswerRelevancyMetric") -> bool:
        """Check if relevancy score meets threshold."""
        score = self._scores.get(metric_name)
        if score is None:
            return False
        return score >= self.ANSWER_RELEVANCY_THRESHOLD

    def get_score(self, metric_name: str = "AnswerRelevancyMetric") -> float:
        """Get raw relevancy score."""
        return self._scores.get(metric_name, 0.0)

    def get_detail(self, metric_name: str = "AnswerRelevancyMetric") -> dict:
        """Get detailed breakdown."""
        return self._details.get(metric_name, {})
