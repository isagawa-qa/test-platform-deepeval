"""ReadTraceParser — Extracts actual_reads from agent execution traces.

Parses kernel actions.jsonl format and structured action lists to identify
which files an agent read during task execution.
"""

import json
import re
from pathlib import Path


class ReadTraceParser:
    """Extracts file paths from agent execution traces."""

    # Pattern to match Read tool entries in actions.jsonl
    READ_ENTRY_PATTERN = re.compile(r"^Read:\s+(.+)$")
    # Pattern to match file paths in Bash cat/head/tail commands
    BASH_READ_PATTERN = re.compile(
        r"(?:cat|head|tail|less|more)\s+[\"']?([^\s\"'|>]+)[\"']?"
    )

    def __init__(self, trace_source: "str | list[dict]"):
        if isinstance(trace_source, str):
            self._filepath = trace_source
            self._actions = None
        else:
            self._filepath = None
            self._actions = trace_source

    @classmethod
    def from_actions_jsonl(cls, filepath: str) -> "ReadTraceParser":
        """Create parser from kernel actions.jsonl file path."""
        return cls(filepath)

    @classmethod
    def from_action_list(cls, actions: list[dict]) -> "ReadTraceParser":
        """Create parser from list of action dicts."""
        return cls(actions)

    def parse(self) -> list[str]:
        """Extract file paths from Read tool calls. Returns deduplicated, sorted list."""
        if self._actions is None:
            self._actions = self._load_jsonl()

        reads = set()
        for action in self._actions:
            entry = action.get("entry", "")
            tool = action.get("tool", "")

            if tool == "Read":
                match = self.READ_ENTRY_PATTERN.match(entry)
                if match:
                    reads.add(self._normalize_path(match.group(1)))
                else:
                    # Entry format might be "Read: /path/to/file"
                    if entry.startswith("Read: "):
                        reads.add(self._normalize_path(entry[6:].strip()))

            elif tool == "Bash":
                # Check for cat/head/tail commands that read files
                for match in self.BASH_READ_PATTERN.finditer(entry):
                    path = match.group(1)
                    if self._looks_like_filepath(path):
                        reads.add(self._normalize_path(path))

        return sorted(reads)

    def _load_jsonl(self) -> list[dict]:
        """Load actions from JSONL file."""
        actions = []
        path = Path(self._filepath)
        if not path.exists():
            return actions
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        actions.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return actions

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normalize path separators and strip whitespace."""
        return path.strip().replace("\\", "/")

    @staticmethod
    def _looks_like_filepath(path: str) -> bool:
        """Heuristic: does this string look like a file path?"""
        if not path:
            return False
        # Must contain a dot (extension) or a slash (directory)
        if "." not in path and "/" not in path and "\\" not in path:
            return False
        # Exclude common non-file patterns
        if path.startswith("http") or path.startswith("-"):
            return False
        return True
