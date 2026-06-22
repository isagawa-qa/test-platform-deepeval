"""A/B Experiment test harness for tiered indexing validation.

Tests the experiment infrastructure: fixture loading, content parity,
task catalog structure, and metric integration. Does NOT run the actual
LLM experiment (that requires API calls and is triggered separately).
"""

import json
import re
from pathlib import Path

import pytest

from framework._reference.metrics.failure_mode_classifier import FailureModeClassifier
from framework._reference.metrics.read_compliance_metrics import ReadComplianceMetric


EXPERIMENT_DIR = Path(__file__).parent
FIXTURES_DIR = EXPERIMENT_DIR / "fixtures"
FLAT_DIR = FIXTURES_DIR / "flat"
TIERED_DIR = FIXTURES_DIR / "tiered"


# --- Fixture Structure Tests ---


def test_flat_fixtures_exist(flat_fixtures, domain_names):
    """All 5 flat fixture files exist."""
    assert len(flat_fixtures) == 5
    for domain in domain_names:
        assert domain in flat_fixtures, f"Missing flat fixture: {domain}"


def test_tiered_fixtures_exist(tiered_fixtures, domain_names):
    """All 5 tiered fixture directories exist with index + payloads."""
    assert len(tiered_fixtures) == 5
    for domain in domain_names:
        assert domain in tiered_fixtures, f"Missing tiered fixture: {domain}"
        fixture = tiered_fixtures[domain]
        assert fixture["index_content"], f"{domain}: index.md is empty"
        assert len(fixture["payload_paths"]) >= 2, (
            f"{domain}: needs at least 2 payload files, has {len(fixture['payload_paths'])}"
        )


def test_tiered_payloads_under_200_lines(tiered_fixtures):
    """Every tiered payload file is under 200 lines."""
    for domain, fixture in tiered_fixtures.items():
        for payload_path in fixture["payload_paths"]:
            content = payload_path.read_text(encoding="utf-8")
            line_count = len(content.splitlines())
            assert line_count < 200, (
                f"{domain}/{payload_path.name}: {line_count} lines (max 200)"
            )


def test_flat_fixtures_are_substantial(flat_fixtures):
    """Flat fixtures are at least 100 lines (realistic document size)."""
    for domain, fixture in flat_fixtures.items():
        line_count = len(fixture["content"].splitlines())
        assert line_count >= 100, (
            f"{domain}: only {line_count} lines (need at least 100 for realistic flat doc)"
        )


def test_tiered_indexes_have_references(tiered_fixtures):
    """Each tiered index.md references its payload files."""
    for domain, fixture in tiered_fixtures.items():
        index_content = fixture["index_content"]
        for payload_path in fixture["payload_paths"]:
            # Check for wikilink or markdown reference to the payload
            payload_name = payload_path.name
            payload_stem = payload_path.stem
            assert payload_name in index_content or payload_stem in index_content, (
                f"{domain}/index.md doesn't reference {payload_name}"
            )


# --- Content Parity Tests ---


def _extract_substantive_content(text: str) -> set[str]:
    """Extract substantive phrases (3+ word trigrams) from text.

    Strips markdown formatting, headers, and metadata to compare
    raw content between flat and tiered versions.
    """
    # Remove markdown formatting
    text = re.sub(r"^#+\s+.*$", "", text, flags=re.MULTILINE)  # headers
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links
    text = re.sub(r"→\s*\[\[.*?\]\]", "", text)  # wikilinks
    text = re.sub(r"\|.*\|", "", text)  # table rows (topic tables in indexes)
    text = re.sub(r"```[\s\S]*?```", "", text)  # code blocks
    text = re.sub(r"`[^`]+`", "", text)  # inline code
    text = re.sub(r"[*_]{1,2}", "", text)  # bold/italic
    text = re.sub(r"\s+", " ", text).lower().strip()

    # Extract trigrams
    words = text.split()
    trigrams = set()
    for i in range(len(words) - 2):
        trigram = " ".join(words[i : i + 3])
        if len(trigram) > 8:  # skip trivial trigrams
            trigrams.add(trigram)
    return trigrams


def test_content_parity(flat_fixtures, tiered_fixtures, domain_names):
    """Flat and tiered fixtures contain substantially the same content.

    Compares trigram overlap — tiered should contain >80% of flat's
    substantive trigrams (some loss from index metadata is expected).
    """
    for domain in domain_names:
        flat_content = flat_fixtures[domain]["content"]
        tiered_content = tiered_fixtures[domain]["all_content"]

        flat_trigrams = _extract_substantive_content(flat_content)
        tiered_trigrams = _extract_substantive_content(tiered_content)

        if not flat_trigrams:
            continue

        overlap = flat_trigrams & tiered_trigrams
        parity = len(overlap) / len(flat_trigrams)

        assert parity > 0.6, (
            f"{domain}: content parity {parity:.1%} (need >60%). "
            f"Flat has {len(flat_trigrams)} trigrams, tiered has {len(tiered_trigrams)}, "
            f"overlap: {len(overlap)}"
        )


# --- Task Catalog Tests ---


def test_task_catalog_structure(task_catalog):
    """Task catalog has required fields and correct count."""
    assert len(task_catalog) >= 20, f"Need 20+ tasks, have {len(task_catalog)}"

    required_fields = ["task_id", "category", "description", "input", "expected_output"]
    for task in task_catalog:
        for field in required_fields:
            assert field in task, f"Task {task.get('task_id', '???')}: missing field '{field}'"


def test_task_catalog_categories(task_catalog, task_categories):
    """All 6 categories are represented in the task catalog."""
    found_categories = {task["category"] for task in task_catalog}
    for category in task_categories:
        assert category in found_categories, f"Missing category: {category}"


def test_task_catalog_category_balance(task_catalog):
    """Each category has at least 3 tasks."""
    from collections import Counter
    counts = Counter(task["category"] for task in task_catalog)
    for category, count in counts.items():
        assert count >= 3, f"Category '{category}' has only {count} tasks (need 3+)"


def test_task_ids_unique(task_catalog):
    """All task IDs are unique."""
    ids = [task["task_id"] for task in task_catalog]
    assert len(ids) == len(set(ids)), f"Duplicate task IDs found"


# --- Metric Integration Tests ---


def test_failure_mode_classifier_correct():
    """Correct task → mode = 'correct'."""
    classifier = FailureModeClassifier(
        task_completion_score=1.0,
        read_compliance_score=1.0,
        agent_output="The answer is X, as documented in section Y.",
        source_content="Section Y: The answer is X.",
        task_category="single_file_lookup",
    ).evaluate()

    assert classifier.get_mode() == "correct"
    assert classifier.get_confidence() == 1.0


def test_failure_mode_classifier_silent_drift():
    """Wrong answer, no hedging → silent_drift."""
    source = "The recommended retry count is 3 with exponential backoff at 1 second intervals."
    classifier = FailureModeClassifier(
        task_completion_score=0.0,
        read_compliance_score=1.0,
        agent_output="The recommended retry count is 5 with exponential backoff at 1 second intervals.",
        source_content=source,
        task_category="single_file_lookup",
    ).evaluate()

    assert classifier.get_mode() == "silent_drift"


def test_failure_mode_classifier_partial_read():
    """Partial read compliance → partial_read."""
    classifier = FailureModeClassifier(
        task_completion_score=0.3,
        read_compliance_score=0.5,
        agent_output="Based on what I read, the answer seems to be Y.",
        source_content="The full answer requires both X and Y from different sections.",
        task_category="cross_reference",
    ).evaluate()

    assert classifier.get_mode() == "partial_read"


def test_failure_mode_classifier_contradiction_ignored():
    """Contradiction task, no flagging → contradiction_ignored."""
    classifier = FailureModeClassifier(
        task_completion_score=0.0,
        read_compliance_score=1.0,
        agent_output="I've updated the retry count to 5 as requested.",
        source_content="The protocol specifies 3 retries.",
        task_category="contradiction",
    ).evaluate()

    assert classifier.get_mode() == "contradiction_ignored"


def test_failure_mode_classifier_contradiction_detected():
    """Contradiction task, agent flags it → correct (task was to detect it)."""
    classifier = FailureModeClassifier(
        task_completion_score=1.0,
        read_compliance_score=1.0,
        agent_output="Note: this contradicts the existing protocol which specifies 3 retries.",
        source_content="The protocol specifies 3 retries.",
        task_category="contradiction",
    ).evaluate()

    assert classifier.get_mode() == "correct"


def test_failure_mode_classifier_hallucination():
    """Output with unsourced claims → hallucination."""
    classifier = FailureModeClassifier(
        task_completion_score=0.0,
        read_compliance_score=0.0,
        agent_output="The platform leverages quantum mesh networking for distributed consensus. All microservices communicate via holographic state transfer protocol. The zero-knowledge proof layer ensures complete data sovereignty across federated compute nodes.",
        source_content="The system uses REST APIs for communication between services. Authentication uses API keys stored in environment variables.",
        task_category="single_file_lookup",
    ).evaluate()

    assert classifier.get_mode() == "hallucination"


def test_failure_mode_classifier_detail():
    """get_detail returns complete classification info."""
    classifier = FailureModeClassifier(
        task_completion_score=1.0,
        read_compliance_score=1.0,
        agent_output="Correct answer.",
        source_content="Source content.",
        task_category="general",
    ).evaluate()

    detail = classifier.get_detail()
    assert "mode" in detail
    assert "confidence" in detail
    assert "signals" in detail
    assert "task_category" in detail
    assert "task_completion" in detail
    assert "read_compliance" in detail


def test_failure_mode_classifier_evaluate_returns_self():
    """Fluent pattern — evaluate() returns self."""
    classifier = FailureModeClassifier(
        task_completion_score=1.0,
        read_compliance_score=1.0,
        agent_output="test",
        source_content="test",
    )
    result = classifier.evaluate()
    assert result is classifier


def test_failure_mode_classifier_unevaluated_raises():
    """Calling get_mode before evaluate raises ValueError."""
    classifier = FailureModeClassifier(
        task_completion_score=1.0,
        read_compliance_score=1.0,
        agent_output="test",
        source_content="test",
    )
    with pytest.raises(ValueError):
        classifier.get_mode()


# --- ReadComplianceMetric Integration ---


def test_read_compliance_with_tiered_fixture(tiered_fixtures):
    """ReadComplianceMetric works with tiered fixture required_reads."""
    coding = tiered_fixtures["coding-guide"]
    required = ["index.md", "patterns.md"]
    actual = ["index.md", "patterns.md", "testing.md"]

    metric = ReadComplianceMetric(required, actual).evaluate()
    assert metric.get_score("compliance") == 1.0
    assert metric.is_above_threshold("compliance")


def test_read_compliance_partial_with_tiered(tiered_fixtures):
    """Partial read of tiered fixture payloads."""
    required = ["index.md", "patterns.md", "testing.md"]
    actual = ["index.md", "patterns.md"]

    metric = ReadComplianceMetric(required, actual).evaluate()
    score = metric.get_score("compliance")
    assert abs(score - 0.6667) < 0.01
    assert not metric.is_above_threshold("compliance")
