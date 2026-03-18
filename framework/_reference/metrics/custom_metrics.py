"""CustomMetrics — Layer 2: Metric Object for GEval custom criteria.

Wraps GEval for user-defined evaluation criteria via natural language.
"""

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase


class CustomMetrics:
    """Metric Object for custom GEval-based evaluation."""

    # Constants
    DEFAULT_THRESHOLD = 0.6

    def __init__(self, criteria: str, threshold: float = None):
        self._criteria = criteria
        self._threshold = threshold or self.DEFAULT_THRESHOLD
        self._scores = {}
        self._details = {}

    def evaluate(self, test_case: LLMTestCase) -> "CustomMetrics":
        """Run custom GEval metric and store score. Returns self."""
        metric = GEval(
            name="CustomEval",
            criteria=self._criteria,
            threshold=self._threshold,
        )
        metric.measure(test_case)
        self._scores["GEval"] = metric.score
        self._details["GEval"] = {
            "reason": metric.reason,
            "criteria": self._criteria,
        }
        return self

    def is_above_threshold(self, metric_name: str = "GEval") -> bool:
        """Check if custom metric passes."""
        score = self._scores.get(metric_name)
        if score is None:
            return False
        return score >= self._threshold

    def get_score(self, metric_name: str = "GEval") -> float:
        """Get raw score."""
        return self._scores.get(metric_name, 0.0)

    def get_detail(self, metric_name: str = "GEval") -> dict:
        """Get detailed breakdown."""
        return self._details.get(metric_name, {})
