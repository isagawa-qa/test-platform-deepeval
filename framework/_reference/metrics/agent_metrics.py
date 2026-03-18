"""AgentMetrics — Layer 2: Metric Object for agentic evaluation.

Wraps ToolCorrectnessMetric, TaskCompletionMetric, ArgumentCorrectnessMetric,
StepEfficiencyMetric.
"""

from deepeval.metrics import (
    ToolCorrectnessMetric,
    TaskCompletionMetric,
)
from deepeval.test_case import LLMTestCase


class AgentMetrics:
    """Metric Object for agentic pipeline evaluation."""

    # Constants
    TOOL_CORRECTNESS_THRESHOLD = 0.8
    TASK_COMPLETION_THRESHOLD = 0.7

    def __init__(self, thresholds: dict = None):
        self._scores = {}
        self._details = {}
        if thresholds:
            self.TOOL_CORRECTNESS_THRESHOLD = thresholds.get(
                "ToolCorrectnessMetric", self.TOOL_CORRECTNESS_THRESHOLD
            )
            self.TASK_COMPLETION_THRESHOLD = thresholds.get(
                "TaskCompletionMetric", self.TASK_COMPLETION_THRESHOLD
            )

    def evaluate(self, test_case: LLMTestCase) -> "AgentMetrics":
        """Run agentic metrics and store scores. Returns self."""
        metrics = [
            ("ToolCorrectnessMetric", ToolCorrectnessMetric(
                threshold=self.TOOL_CORRECTNESS_THRESHOLD
            )),
            ("TaskCompletionMetric", TaskCompletionMetric(
                threshold=self.TASK_COMPLETION_THRESHOLD
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
        if metric_name == "ToolCorrectnessMetric":
            return score >= self.TOOL_CORRECTNESS_THRESHOLD
        elif metric_name == "TaskCompletionMetric":
            return score >= self.TASK_COMPLETION_THRESHOLD
        return False

    def get_score(self, metric_name: str) -> float:
        """Get raw score for specific metric."""
        return self._scores.get(metric_name, 0.0)

    def get_detail(self, metric_name: str) -> dict:
        """Get detailed breakdown for specific metric."""
        return self._details.get(metric_name, {})
