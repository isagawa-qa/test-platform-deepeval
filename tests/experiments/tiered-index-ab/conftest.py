"""Conftest for tiered-index A/B experiment.

Provides fixtures for loading experiment data: task catalog, flat fixtures,
tiered fixtures, and experiment configuration.
"""

import json
import sys
from pathlib import Path

import pytest

# Add repo root to sys.path so 'framework' imports resolve
_REPO_ROOT = str(Path(__file__).resolve().parents[3])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


EXPERIMENT_DIR = Path(__file__).parent
FIXTURES_DIR = EXPERIMENT_DIR / "fixtures"
FLAT_DIR = FIXTURES_DIR / "flat"
TIERED_DIR = FIXTURES_DIR / "tiered"


@pytest.fixture
def task_catalog():
    """Load the full task catalog."""
    with open(EXPERIMENT_DIR / "task_catalog.json") as f:
        return json.load(f)


@pytest.fixture
def flat_fixtures():
    """Load all flat fixture file paths, keyed by domain."""
    domains = {}
    for md_file in sorted(FLAT_DIR.glob("*.md")):
        domain = md_file.stem
        domains[domain] = {
            "path": md_file,
            "content": md_file.read_text(encoding="utf-8"),
        }
    return domains


@pytest.fixture
def tiered_fixtures():
    """Load all tiered fixture file paths, keyed by domain.

    Each domain has an index and a list of payload files.
    """
    domains = {}
    for domain_dir in sorted(TIERED_DIR.iterdir()):
        if not domain_dir.is_dir():
            continue
        domain = domain_dir.name
        index_file = domain_dir / "index.md"
        payloads = sorted(
            f for f in domain_dir.glob("*.md") if f.name != "index.md"
        )
        domains[domain] = {
            "index_path": index_file,
            "index_content": index_file.read_text(encoding="utf-8") if index_file.exists() else "",
            "payload_paths": payloads,
            "payload_contents": {
                p.stem: p.read_text(encoding="utf-8") for p in payloads
            },
            "all_content": "\n".join(
                p.read_text(encoding="utf-8") for p in [index_file] + payloads if p.exists()
            ),
        }
    return domains


@pytest.fixture
def domain_names():
    """Return the expected domain names."""
    return [
        "coding-guide",
        "contradiction-policy",
        "memory-decisions",
        "research-protocol",
        "workflow-spec",
    ]


@pytest.fixture
def task_categories():
    """Return the expected task categories."""
    return [
        "single_file_lookup",
        "cross_reference",
        "contradiction",
        "multi_step_workflow",
        "memory_retrieval",
        "stress_test",
    ]
