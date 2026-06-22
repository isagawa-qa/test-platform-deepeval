"""ReadComplianceMetric — Layer 2: Measures whether required files were read before generation.

Deterministic set-comparison metric. No LLM judge dependency.
Scores compliance (required reads covered) and coverage (read efficiency).
"""


class ReadComplianceMetric:
    """Metric Object for read compliance evaluation."""

    # Constants
    DEFAULT_THRESHOLD = 1.0  # All required files must be read

    def __init__(
        self,
        required_reads: list[str],
        actual_reads: list[str],
        threshold: float = None,
    ):
        self._required = set(required_reads)
        self._actual = set(actual_reads)
        self._threshold = threshold or self.DEFAULT_THRESHOLD
        self._scores = {}
        self._details = {}

    def evaluate(self) -> "ReadComplianceMetric":
        """Compute compliance and coverage scores. Returns self."""
        if not self._required:
            # Nothing required — trivially compliant
            self._scores["compliance"] = 1.0
            self._scores["coverage"] = 1.0 if not self._actual else 0.0
            self._details["compliance"] = {
                "reason": "No required reads specified — trivially compliant",
                "missed_reads": [],
                "extra_reads": sorted(self._actual),
            }
            return self

        intersection = self._required & self._actual
        missed = self._required - self._actual
        extra = self._actual - self._required

        # Compliance: what fraction of required files were actually read
        compliance = len(intersection) / len(self._required)
        self._scores["compliance"] = round(compliance, 4)

        # Coverage: what fraction of actual reads were required (noise detection)
        if self._actual:
            coverage = len(intersection) / len(self._actual)
        else:
            coverage = 0.0
        self._scores["coverage"] = round(coverage, 4)

        self._details["compliance"] = {
            "reason": self._build_reason(compliance, missed, extra),
            "missed_reads": sorted(missed),
            "extra_reads": sorted(extra),
            "required_count": len(self._required),
            "actual_count": len(self._actual),
            "intersection_count": len(intersection),
        }

        return self

    def is_above_threshold(self, metric_name: str = "compliance") -> bool:
        """Check if metric passes threshold."""
        score = self._scores.get(metric_name)
        if score is None:
            return False
        return score >= self._threshold

    def get_score(self, metric_name: str = "compliance") -> float:
        """Get raw score."""
        return self._scores.get(metric_name, 0.0)

    def get_detail(self, metric_name: str = "compliance") -> dict:
        """Get detailed breakdown."""
        return self._details.get(metric_name, {})

    def _build_reason(self, compliance: float, missed: set, extra: set) -> str:
        """Build human-readable reason string."""
        if compliance == 1.0 and not extra:
            return "Perfect compliance — all required files read, no extras"
        if compliance == 1.0 and extra:
            return f"Full compliance — all required files read, {len(extra)} extra file(s) read"
        if compliance == 0.0:
            return f"Zero compliance — none of {len(self._required)} required files were read"
        return (
            f"Partial compliance ({compliance:.0%}) — "
            f"{len(missed)} required file(s) not read: {sorted(missed)}"
        )
