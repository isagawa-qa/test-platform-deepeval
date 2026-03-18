"""RAGEvaluator — Layer 4: EvalRole for RAG pipeline evaluation.

Orchestrates RAG EvalTasks across a golden dataset.
"""

from _reference.tasks.run_rag_eval import run_rag_eval


class RAGEvaluator:
    """Orchestrates full RAG pipeline evaluation."""

    def __init__(self, deepeval_interface):
        self.deepeval_interface = deepeval_interface

    def evaluate_pipeline(self, dataset, pipeline_fn, thresholds=None):
        """Run full RAG eval workflow over dataset.

        Args:
            dataset: List of golden dicts with input, expected_output, retrieval_context
            pipeline_fn: Callable that takes input string, returns output string
            thresholds: Optional threshold overrides

        Returns:
            dict with test_cases and summary
        """
        results = []

        for golden in dataset:
            actual_output = pipeline_fn(golden["input"])
            test_case = self.deepeval_interface.create_test_case(
                input=golden["input"],
                actual_output=actual_output,
                expected_output=golden.get("expected_output"),
                retrieval_context=golden.get("retrieval_context"),
                context=golden.get("context"),
            )
            run_rag_eval(self.deepeval_interface, test_case, thresholds)
            results.append(test_case)

        return {
            "test_cases": results,
            "count": len(results),
            "pipeline_type": "RAG",
        }
