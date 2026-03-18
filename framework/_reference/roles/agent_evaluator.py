"""AgentEvaluator — Layer 4: EvalRole for Agent pipeline evaluation.

Orchestrates Agent EvalTasks across a golden dataset.
"""

from _reference.tasks.run_agent_eval import run_agent_eval


class AgentEvaluator:
    """Orchestrates full Agent pipeline evaluation."""

    def __init__(self, deepeval_interface):
        self.deepeval_interface = deepeval_interface

    def evaluate_pipeline(self, dataset, agent_fn, thresholds=None):
        """Run full Agent eval workflow over dataset.

        Args:
            dataset: List of golden dicts with input, expected_output, expected_tools
            agent_fn: Callable that takes input, returns (output, tools_called)
            thresholds: Optional threshold overrides

        Returns:
            dict with test_cases and summary
        """
        results = []

        for golden in dataset:
            actual_output, tools_called = agent_fn(golden["input"])
            test_case = self.deepeval_interface.create_test_case(
                input=golden["input"],
                actual_output=actual_output,
                expected_output=golden.get("expected_output"),
                tools_called=tools_called,
                expected_tools=golden.get("expected_tools"),
            )
            run_agent_eval(self.deepeval_interface, test_case, thresholds)
            results.append(test_case)

        return {
            "test_cases": results,
            "count": len(results),
            "pipeline_type": "Agent",
        }
