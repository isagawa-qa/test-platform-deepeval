"""ConversationMetrics — Layer 2: Metric Object for conversational evaluation.

Wraps KnowledgeRetentionMetric, RoleAdherenceMetric.
"""

from deepeval.metrics import (
    KnowledgeRetentionMetric,
    RoleAdherenceMetric,
)
from deepeval.test_case import ConversationalTestCase


class ConversationMetrics:
    """Metric Object for conversational pipeline evaluation."""

    # Constants
    KNOWLEDGE_RETENTION_THRESHOLD = 0.6
    ROLE_ADHERENCE_THRESHOLD = 0.7

    def __init__(self, thresholds: dict = None):
        self._scores = {}
        self._details = {}
        if thresholds:
            self.KNOWLEDGE_RETENTION_THRESHOLD = thresholds.get(
                "KnowledgeRetentionMetric", self.KNOWLEDGE_RETENTION_THRESHOLD
            )
            self.ROLE_ADHERENCE_THRESHOLD = thresholds.get(
                "RoleAdherenceMetric", self.ROLE_ADHERENCE_THRESHOLD
            )

    def evaluate(self, test_case: ConversationalTestCase) -> "ConversationMetrics":
        """Run conversational metrics and store scores. Returns self."""
        metrics = [
            ("KnowledgeRetentionMetric", KnowledgeRetentionMetric(
                threshold=self.KNOWLEDGE_RETENTION_THRESHOLD
            )),
            ("RoleAdherenceMetric", RoleAdherenceMetric(
                threshold=self.ROLE_ADHERENCE_THRESHOLD
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
        if metric_name == "KnowledgeRetentionMetric":
            return score >= self.KNOWLEDGE_RETENTION_THRESHOLD
        elif metric_name == "RoleAdherenceMetric":
            return score >= self.ROLE_ADHERENCE_THRESHOLD
        return False

    def get_score(self, metric_name: str) -> float:
        """Get raw score."""
        return self._scores.get(metric_name, 0.0)

    def get_detail(self, metric_name: str) -> dict:
        """Get detailed breakdown."""
        return self._details.get(metric_name, {})
