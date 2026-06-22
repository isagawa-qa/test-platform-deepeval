"""Tests for ReadComplianceMetric and ReadTraceParser.

Validates scoring logic, edge cases, trace parsing, and golden dataset.
"""

import json
import tempfile
from pathlib import Path

import pytest

from framework._reference.metrics.read_compliance_metrics import ReadComplianceMetric
from framework._reference.metrics.instrumentation import ReadTraceParser


# --- Fixtures ---

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "read-compliance"


@pytest.fixture
def golden_dataset():
    """Load golden dataset from JSON fixture."""
    with open(FIXTURES_DIR / "golden-dataset.json") as f:
        return json.load(f)


@pytest.fixture
def expected_results():
    """Load expected results from JSON fixture."""
    with open(FIXTURES_DIR / "expected-results.json") as f:
        return json.load(f)


# --- ReadComplianceMetric Tests ---


def test_perfect_compliance():
    """All required files read, no extras."""
    metric = ReadComplianceMetric(
        required_reads=["protocol.md", "lessons.md"],
        actual_reads=["protocol.md", "lessons.md"],
    ).evaluate()

    assert metric.get_score("compliance") == 1.0
    assert metric.get_score("coverage") == 1.0
    assert metric.is_above_threshold("compliance")
    detail = metric.get_detail("compliance")
    assert detail["missed_reads"] == []
    assert detail["extra_reads"] == []


def test_missing_reads():
    """Some required files not read."""
    metric = ReadComplianceMetric(
        required_reads=["protocol.md", "lessons.md"],
        actual_reads=["protocol.md"],
    ).evaluate()

    assert metric.get_score("compliance") == 0.5
    assert not metric.is_above_threshold("compliance")
    detail = metric.get_detail("compliance")
    assert "lessons.md" in detail["missed_reads"]


def test_empty_reads():
    """Required files exist but nothing was read."""
    metric = ReadComplianceMetric(
        required_reads=["protocol.md", "lessons.md"],
        actual_reads=[],
    ).evaluate()

    assert metric.get_score("compliance") == 0.0
    assert metric.get_score("coverage") == 0.0
    assert not metric.is_above_threshold("compliance")


def test_extra_reads_still_pass():
    """All required read plus extras — compliance should be 1.0."""
    metric = ReadComplianceMetric(
        required_reads=["protocol.md"],
        actual_reads=["protocol.md", "README.md", "extra.md"],
    ).evaluate()

    assert metric.get_score("compliance") == 1.0
    assert metric.is_above_threshold("compliance")
    assert metric.get_score("coverage") == round(1 / 3, 4)


def test_empty_required():
    """Nothing required — trivially compliant."""
    metric = ReadComplianceMetric(
        required_reads=[],
        actual_reads=["README.md"],
    ).evaluate()

    assert metric.get_score("compliance") == 1.0
    assert metric.is_above_threshold("compliance")


def test_custom_threshold():
    """Partial compliance passes with lowered threshold."""
    metric = ReadComplianceMetric(
        required_reads=["a.md", "b.md"],
        actual_reads=["a.md"],
        threshold=0.5,
    ).evaluate()

    assert metric.get_score("compliance") == 0.5
    assert metric.is_above_threshold("compliance")


def test_evaluate_returns_self():
    """Verify fluent pattern — evaluate() returns self."""
    metric = ReadComplianceMetric(["a.md"], ["a.md"])
    result = metric.evaluate()
    assert result is metric


# --- ReadTraceParser Tests ---


def test_trace_parsing():
    """ReadTraceParser extracts file paths from actions.jsonl format."""
    actions = [
        {"timestamp": "2026-01-01T00:00:00Z", "tool": "Read", "entry": "Read: /path/to/protocol.md"},
        {"timestamp": "2026-01-01T00:00:01Z", "tool": "Read", "entry": "Read: /path/to/lessons.md"},
        {"timestamp": "2026-01-01T00:00:02Z", "tool": "Bash", "entry": "Bash: echo hello"},
        {"timestamp": "2026-01-01T00:00:03Z", "tool": "Write", "entry": "Write: output.md"},
    ]

    parser = ReadTraceParser.from_action_list(actions)
    reads = parser.parse()

    assert "/path/to/protocol.md" in reads
    assert "/path/to/lessons.md" in reads
    assert len(reads) == 2


def test_trace_parsing_deduplicates():
    """Same file read twice should appear once."""
    actions = [
        {"timestamp": "2026-01-01T00:00:00Z", "tool": "Read", "entry": "Read: /path/to/file.md"},
        {"timestamp": "2026-01-01T00:00:01Z", "tool": "Read", "entry": "Read: /path/to/file.md"},
    ]

    parser = ReadTraceParser.from_action_list(actions)
    reads = parser.parse()

    assert len(reads) == 1
    assert reads[0] == "/path/to/file.md"


def test_trace_parsing_from_jsonl():
    """Parse actions from a JSONL file on disk."""
    actions = [
        {"timestamp": "2026-01-01T00:00:00Z", "tool": "Read", "entry": "Read: /path/to/file.md"},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for action in actions:
            f.write(json.dumps(action) + "\n")
        tmppath = f.name

    parser = ReadTraceParser.from_actions_jsonl(tmppath)
    reads = parser.parse()

    assert "/path/to/file.md" in reads
    Path(tmppath).unlink()


def test_trace_parsing_bash_cat():
    """Detect file reads from bash cat commands."""
    actions = [
        {"timestamp": "2026-01-01T00:00:00Z", "tool": "Bash", "entry": "Bash: cat /path/to/config.json"},
    ]

    parser = ReadTraceParser.from_action_list(actions)
    reads = parser.parse()

    assert "/path/to/config.json" in reads


# --- Golden Dataset Tests ---


def test_golden_dataset(golden_dataset, expected_results):
    """Parametrized validation against golden dataset."""
    for case in golden_dataset:
        test_id = case["test_id"]
        expected = expected_results[test_id]

        metric = ReadComplianceMetric(
            required_reads=case["required_reads"],
            actual_reads=case["actual_reads"],
        ).evaluate()

        compliance = metric.get_score("compliance")
        coverage = metric.get_score("coverage")
        passed = metric.is_above_threshold("compliance")
        detail = metric.get_detail("compliance")

        assert abs(compliance - expected["compliance_score"]) < 0.01, (
            f"{test_id}: compliance {compliance} != expected {expected['compliance_score']}"
        )
        assert abs(coverage - expected["coverage_score"]) < 0.01, (
            f"{test_id}: coverage {coverage} != expected {expected['coverage_score']}"
        )
        assert passed == expected["passed"], (
            f"{test_id}: passed {passed} != expected {expected['passed']}"
        )
        assert sorted(detail.get("missed_reads", [])) == sorted(expected["missed_reads"]), (
            f"{test_id}: missed_reads mismatch"
        )
        assert sorted(detail.get("extra_reads", [])) == sorted(expected["extra_reads"]), (
            f"{test_id}: extra_reads mismatch"
        )
