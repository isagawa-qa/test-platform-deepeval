"""RetrievalMetrics — Layer 2: Metric Object for retrieval quality.

Wraps ContextualRelevancyMetric, ContextualPrecisionMetric, ContextualRecallMetric.
Constants = thresholds. State-checks = is_above_threshold(), get_score().
"""

from deepeval.metrics import (
    ContextualRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from deepeval.test_case import LLMTestCase


class RetrievalMetrics:
    """Metric Object for retrieval quality evaluation."""

    # Constants — default thresholds
    CONTEXTUAL_RELEVANCY_THRESHOLD = 0.6
    CONTEXTUAL_PRECISION_THRESHOLD = 0.6
    CONTEXTUAL_RECALL_THRESHOLD = 0.6

    def __init__(self, thresholds: dict = None):
        self._scores = {}
        self._details = {}
        if thresholds:
            self.CONTEXTUAL_RELEVANCY_THRESHOLD = thresholds.get(
                "ContextualRelevancyMetric", self.CONTEXTUAL_RELEVANCY_THRESHOLD
            )
            self.CONTEXTUAL_PRECISION_THRESHOLD = thresholds.get(
                "ContextualPrecisionMetric", self.CONTEXTUAL_PRECISION_THRESHOLD
            )
            self.CONTEXTUAL_RECALL_THRESHOLD = thresholds.get(
                "ContextualRecallMetric", self.CONTEXTUAL_RECALL_THRESHOLD
            )

    def evaluate(self, test_case: LLMTestCase) -> "RetrievalMetrics":
        """Run retrieval metrics and store scores. Returns self."""
        if not test_case.retrieval_context:
            raise ValueError("retrieval_context is required for retrieval metrics")

        metrics = [
            ("ContextualRelevancyMetric", ContextualRelevancyMetric(
                threshold=self.CONTEXTUAL_RELEVANCY_THRESHOLD
            )),
            ("ContextualPrecisionMetric", ContextualPrecisionMetric(
                threshold=self.CONTEXTUAL_PRECISION_THRESHOLD
            )),
            ("ContextualRecallMetric", ContextualRecallMetric(
                threshold=self.CONTEXTUAL_RECALL_THRESHOLD
            )),
        ]

        for name, metric in metrics:
            metric.measure(test_case)
            self._scores[name] = metric.score
            self._details[name] = {"reason": metric.reason}

        return self

    def is_above_threshold(self, metric_name: str) -> bool:
        """Check if specific metric score meets threshold."""
        score = self._scores.get(metric_name)
        if score is None:
            return False
        threshold = getattr(self, f"{self._to_const(metric_name)}_THRESHOLD")
        return score >= threshold

    def get_score(self, metric_name: str) -> float:
        """Get raw score for specific metric."""
        return self._scores.get(metric_name, 0.0)

    def get_detail(self, metric_name: str) -> dict:
        """Get detailed breakdown for specific metric."""
        return self._details.get(metric_name, {})

    @staticmethod
    def _to_const(metric_name: str) -> str:
        """Convert metric name to constant prefix (e.g., ContextualRelevancyMetric → CONTEXTUAL_RELEVANCY)."""
        import re
        name = metric_name.replace("Metric", "")
        # Insert underscore before each uppercase letter (except first)
        name = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name)
        return name.upper()
