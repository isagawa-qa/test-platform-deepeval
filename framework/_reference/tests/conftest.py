"""conftest.py — Test fixtures for eval suite.

Loads golden datasets and initializes DeepEvalInterface.
"""

import json
import logging
import os
import pytest

from interfaces.deepeval_interface import DeepEvalInterface


def _load_golden_rag():
    """Load RAG golden dataset from fixtures."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), "..", "fixtures", "golden_rag.json"
    )
    with open(fixture_path, "r") as f:
        return json.load(f)


_GOLDEN_RAG_DATA = _load_golden_rag()


@pytest.fixture
def deepeval_interface():
    """Initialize DeepEvalInterface with default config and logger."""
    config = {"max_retries": 3, "retry_delay": 1.0, "results_dir": "eval_results"}
    logger = logging.getLogger("deepeval_interface")
    return DeepEvalInterface(config=config, logger=logger)


@pytest.fixture
def golden_rag_dataset():
    """Load RAG golden dataset from fixtures."""
    return _GOLDEN_RAG_DATA


@pytest.fixture(params=range(len(_GOLDEN_RAG_DATA)), ids=[g["input"][:40] for g in _GOLDEN_RAG_DATA])
def golden(request):
    """Yield individual golden items for parametrized tests."""
    return _GOLDEN_RAG_DATA[request.param]


@pytest.fixture
def golden_agent_dataset():
    """Load Agent golden dataset from fixtures."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), "..", "fixtures", "golden_agent.json"
    )
    if os.path.exists(fixture_path):
        with open(fixture_path, "r") as f:
            return json.load(f)
    return []


def mock_rag_pipeline(input_text):
    """Mock RAG pipeline for testing. Replace with real pipeline."""
    return f"Based on the retrieved documents, {input_text.lower()} The answer is found in the company policy."


def mock_agent_pipeline(input_text):
    """Mock Agent pipeline for testing. Returns (output, tools_called)."""
    return (
        f"I'll help you with that. {input_text}",
        [{"name": "search", "args": {"query": input_text}}],
    )
