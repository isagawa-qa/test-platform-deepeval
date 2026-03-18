"""run_rag_eval — Layer 3: EvalTask for RAG pipeline evaluation.

Composes FaithfulnessMetrics, RetrievalMetrics, RelevancyMetrics.
Returns None.
"""

from _reference.metrics.faithfulness_metrics import FaithfulnessMetrics
from _reference.metrics.retrieval_metrics import RetrievalMetrics
from _reference.metrics.relevancy_metrics import RelevancyMetrics
from deepeval.test_case import LLMTestCase


def run_rag_eval(deepeval_interface, test_case: LLMTestCase,
                 thresholds: dict = None) -> None:
    """Run full RAG evaluation: faithfulness + retrieval + relevancy.

    Composes Metric Objects for each category.
    Returns None — results accessed via Metric Object state-checks.
    """
    faithfulness = FaithfulnessMetrics(thresholds).evaluate(test_case)
    retrieval = RetrievalMetrics(thresholds).evaluate(test_case)
    relevancy = RelevancyMetrics(thresholds).evaluate(test_case)

    # Store on test_case for later assertion
    test_case._eval_results = {
        "faithfulness": faithfulness,
        "retrieval": retrieval,
        "relevancy": relevancy,
    }
    return None
