"""Default thresholds per metric.

Used by AI Processing (Step 3) when user doesn't specify thresholds.
"""

METRIC_DEFAULTS = {
    # RAG — Retriever
    "ContextualRelevancyMetric": 0.6,
    "ContextualPrecisionMetric": 0.6,
    "ContextualRecallMetric": 0.6,
    # RAG — Generator
    "FaithfulnessMetric": 0.7,
    "AnswerRelevancyMetric": 0.6,
    "HallucinationMetric": 0.3,  # Inverse — lower is better
    # Agentic
    "ToolCorrectnessMetric": 0.8,
    "ArgumentCorrectnessMetric": 0.7,
    "TaskCompletionMetric": 0.7,
    "StepEfficiencyMetric": 0.6,
    "PlanQualityMetric": 0.6,
    "PlanAdherenceMetric": 0.7,
    # Conversational
    "KnowledgeRetentionMetric": 0.6,
    "RoleAdherenceMetric": 0.7,
    "ConversationCompletenessMetric": 0.6,
    "ConversationRelevancyMetric": 0.6,
    # Safety — Inverse
    "BiasMetric": 0.3,
    "ToxicityMetric": 0.1,
    "PIILeakageMetric": 0.1,
    # Other
    "JsonCorrectnessMetric": 1.0,
    "SummarizationMetric": 0.6,
}

# Metrics where lower score = better (inverse thresholds)
INVERSE_METRICS = {
    "HallucinationMetric",
    "BiasMetric",
    "ToxicityMetric",
    "PIILeakageMetric",
}

# Required metrics per pipeline type
PIPELINE_METRICS = {
    "RAG": ["FaithfulnessMetric", "ContextualRelevancyMetric", "AnswerRelevancyMetric"],
    "Chat": ["AnswerRelevancyMetric", "HallucinationMetric"],
    "Agent": ["ToolCorrectnessMetric", "TaskCompletionMetric"],
    "Conversational": ["KnowledgeRetentionMetric", "RoleAdherenceMetric"],
    "Codegen": ["GEval"],
    "Custom": ["GEval"],
}
