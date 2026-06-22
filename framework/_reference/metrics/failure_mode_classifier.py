"""FailureModeClassifier — categorizes HOW an agent failed a task.

Layer 2 Metric Object. Deterministic classification based on task completion,
read compliance, and output analysis. Returns self (fluent pattern).

Failure modes:
- correct: Task completed successfully
- silent_drift: Wrong answer with no uncertainty signal
- partial_read: Some required files read, others skipped
- hallucination: Output contains claims absent from all source content
- contradiction_ignored: Contradiction exists but agent didn't flag it
"""

import re


class FailureModeClassifier:
    """Classifies agent failure mode from task execution signals."""

    FAILURE_MODES = [
        "correct",
        "silent_drift",
        "partial_read",
        "hallucination",
        "contradiction_ignored",
    ]

    HEDGING_PATTERNS = [
        r"\b(?:I'm not sure|uncertain|unclear|might be|possibly|I think)\b",
        r"\b(?:note that|however|but|caveat|warning|conflict)\b",
        r"\b(?:contradicts?|inconsisten|disagrees?|differs? from)\b",
    ]

    def __init__(
        self,
        task_completion_score: float,
        read_compliance_score: float,
        agent_output: str,
        source_content: str,
        task_category: str = "general",
        expected_output: str = "",
    ):
        self._task_completion = task_completion_score
        self._read_compliance = read_compliance_score
        self._agent_output = agent_output
        self._source_content = source_content
        self._task_category = task_category
        self._expected_output = expected_output
        self._classification = None
        self._confidence = 0.0
        self._signals = {}

    def evaluate(self) -> "FailureModeClassifier":
        """Classify the failure mode. Returns self for fluent chaining."""
        self._signals = {
            "task_passed": self._task_completion >= 0.9,
            "full_read": self._read_compliance >= 1.0,
            "partial_read": 0.0 < self._read_compliance < 1.0,
            "no_read": self._read_compliance == 0.0,
            "has_hedging": self._detect_hedging(),
            "has_unsourced_claims": self._detect_unsourced_claims(),
            "is_contradiction_task": self._task_category == "contradiction",
            "flags_contradiction": self._detect_contradiction_flagging(),
        }

        self._classification, self._confidence = self._classify()
        return self

    def get_mode(self) -> str:
        """Return the classified failure mode."""
        if self._classification is None:
            raise ValueError("Call evaluate() before get_mode()")
        return self._classification

    def get_confidence(self) -> float:
        """Return classification confidence (0.0-1.0)."""
        if self._classification is None:
            raise ValueError("Call evaluate() before get_confidence()")
        return self._confidence

    def get_signals(self) -> dict:
        """Return the detection signals used for classification."""
        if self._classification is None:
            raise ValueError("Call evaluate() before get_signals()")
        return dict(self._signals)

    def get_detail(self) -> dict:
        """Return full classification detail."""
        if self._classification is None:
            raise ValueError("Call evaluate() before get_detail()")
        return {
            "mode": self._classification,
            "confidence": self._confidence,
            "signals": dict(self._signals),
            "task_category": self._task_category,
            "task_completion": self._task_completion,
            "read_compliance": self._read_compliance,
        }

    def _classify(self) -> tuple[str, float]:
        """Apply classification rules. Returns (mode, confidence)."""
        s = self._signals

        # Correct — task passed
        if s["task_passed"]:
            return ("correct", 1.0)

        # Contradiction ignored — contradiction task, agent didn't flag it
        if s["is_contradiction_task"] and not s["flags_contradiction"]:
            return ("contradiction_ignored", 0.9)

        # Partial read — read some but not all required files
        if s["partial_read"] and not s["task_passed"]:
            return ("partial_read", 0.85)

        # Hallucination — output has unsourced claims
        if s["has_unsourced_claims"] and not s["task_passed"]:
            return ("hallucination", 0.75)

        # Silent drift — wrong answer, no hedging
        if not s["task_passed"] and not s["has_hedging"]:
            return ("silent_drift", 0.8)

        # Fallback — wrong answer with hedging (still silent_drift but lower confidence)
        return ("silent_drift", 0.5)

    def _detect_hedging(self) -> bool:
        """Check if agent output contains hedging/uncertainty language."""
        for pattern in self.HEDGING_PATTERNS:
            if re.search(pattern, self._agent_output, re.IGNORECASE):
                return True
        return False

    def _detect_unsourced_claims(self) -> bool:
        """Check if agent output contains claims not found in source content.

        Simple heuristic: extract sentences from output, check if key phrases
        appear in source. Not exhaustive — serves as a signal, not ground truth.
        """
        if not self._agent_output or not self._source_content:
            return False

        source_lower = self._source_content.lower()
        sentences = re.split(r"[.!?]+", self._agent_output)

        unsourced_count = 0
        total_substantive = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            total_substantive += 1

            # Extract key phrases (3+ word sequences)
            words = sentence.lower().split()
            if len(words) < 3:
                continue

            # Check if any 3-gram from the sentence appears in source
            found = False
            for i in range(len(words) - 2):
                trigram = " ".join(words[i : i + 3])
                if trigram in source_lower:
                    found = True
                    break

            if not found:
                unsourced_count += 1

        if total_substantive == 0:
            return False

        return (unsourced_count / total_substantive) > 0.5

    def _detect_contradiction_flagging(self) -> bool:
        """Check if agent flagged a contradiction in its output."""
        contradiction_signals = [
            r"\bcontradicts?\b",
            r"\binconsisten",
            r"\bconflicts? (?:with|between)\b",
            r"\bdisagrees?\b",
            r"\bdiscrepanc",
            r"\bmismatch",
            r"\bnote:.*(?:different|differs|contrary)\b",
        ]
        for pattern in contradiction_signals:
            if re.search(pattern, self._agent_output, re.IGNORECASE):
                return True
        return False
