"""ReadComplianceEvalTask — Layer 3: Runs read compliance evaluation.

Composes ReadComplianceMetric and ReadTraceParser. Returns None (Layer 3 convention).
"""

from framework._reference.metrics.read_compliance_metrics import ReadComplianceMetric
from framework._reference.metrics.instrumentation import ReadTraceParser


def run_read_compliance_eval(
    required_reads: list[str],
    actual_reads: list[str],
    threshold: float = 1.0,
) -> None:
    """Evaluate read compliance from explicit read lists.

    Args:
        required_reads: Files that should have been read.
        actual_reads: Files that were actually read.
        threshold: Minimum compliance score to pass (default: 1.0).

    Returns:
        None (Layer 3 convention).
    """
    metric = ReadComplianceMetric(required_reads, actual_reads, threshold)
    metric.evaluate()

    score = metric.get_score("compliance")
    coverage = metric.get_score("coverage")
    detail = metric.get_detail("compliance")
    passed = metric.is_above_threshold("compliance")

    print(f"Read Compliance: {score:.2%} ({'PASS' if passed else 'FAIL'})")
    print(f"Read Coverage: {coverage:.2%}")
    if detail.get("missed_reads"):
        print(f"Missed reads: {detail['missed_reads']}")
    if detail.get("extra_reads"):
        print(f"Extra reads: {detail['extra_reads']}")

    return None


def run_read_compliance_from_trace(
    required_reads: list[str],
    trace_source: str,
    threshold: float = 1.0,
) -> None:
    """Evaluate read compliance by parsing an agent trace.

    Args:
        required_reads: Files that should have been read.
        trace_source: Path to actions.jsonl or similar trace file.
        threshold: Minimum compliance score to pass (default: 1.0).

    Returns:
        None (Layer 3 convention).
    """
    parser = ReadTraceParser.from_actions_jsonl(trace_source)
    actual_reads = parser.parse()
    run_read_compliance_eval(required_reads, actual_reads, threshold)
    return None
