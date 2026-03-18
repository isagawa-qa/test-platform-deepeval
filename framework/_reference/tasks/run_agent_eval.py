"""run_agent_eval — Layer 3: EvalTask for Agent pipeline evaluation.

Composes AgentMetrics.
Returns None.
"""

from _reference.metrics.agent_metrics import AgentMetrics
from deepeval.test_case import LLMTestCase


def run_agent_eval(deepeval_interface, test_case: LLMTestCase,
                   thresholds: dict = None) -> None:
    """Run agent evaluation: tool correctness + task completion.

    Composes AgentMetrics.
    Returns None — results accessed via Metric Object state-checks.
    """
    agent = AgentMetrics(thresholds).evaluate(test_case)

    test_case._eval_results = {
        "agent": agent,
    }
    return None
