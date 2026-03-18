"""Eval configuration schema.

Defines the structure of eval cycle configuration.
"""


def create_default_config(pipeline_type: str, endpoint: str = None) -> dict:
    """Create default eval config for a pipeline type."""
    from framework.resources.metric_defaults import PIPELINE_METRICS, METRIC_DEFAULTS

    metrics = PIPELINE_METRICS.get(pipeline_type, PIPELINE_METRICS["Custom"])
    thresholds = {m: METRIC_DEFAULTS.get(m, 0.6) for m in metrics}

    return {
        "pipeline_type": pipeline_type,
        "endpoint": endpoint,
        "metrics": metrics,
        "thresholds": thresholds,
        "max_retries": 3,
        "retry_delay": 1.0,
        "golden_min_count": 20,
        "provider": "openai",
    }
