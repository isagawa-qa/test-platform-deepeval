# Lessons Learned — Index

<!-- INDEX file — points to payloads. Do not duplicate payload content here. -->
<!-- 200-line threshold: split when exceeded. -->
<!-- Tiered indexing: payload files hold details, this file is the index. -->

## How This Works

The agent reads this index during every `/kernel/anchor`. Each topic folder contains
expert domain knowledge seeded before the first eval run, plus lessons accumulated
from failures during autonomous execution.

- **Index** = points to files. Contains no substantive content.
- **Payload** = contains the knowledge. Pointed to by an index.
- **200-line rule** = any payload exceeding 200 lines splits into a sub-index + sub-payloads.

**Seeded knowledge** = best practices encoded upfront so the agent avoids common mistakes.
**Learned knowledge** = lessons recorded by `/kernel/learn` after real failures.

## Topic Folders

| Topic | Path | Contents |
|-------|------|----------|
| Framework Architecture | `framework/architecture.md` | 5-layer rules, DeepEvalInterface-first, composition over inheritance |
| DeepEval API | `deepeval-api/` | **INDEX** → metrics, test cases, datasets |
| — Metric Patterns | `deepeval-api/metric-patterns.md` | Required params per metric, inverse metrics, threshold ranges, CamelCase→SNAKE_CASE conversion |
| — Test Case Construction | `deepeval-api/test-case-construction.md` | LLMTestCase 9 params, ConversationalTestCase, field requirements |
| — Dataset Management | `deepeval-api/dataset-management.md` | Golden fixtures, Synthesizer, minimum sample sizes |
| Evaluation Strategies | `evaluation/` | **INDEX** → metric selection, LLM-as-judge, CI integration |
| — Metric Selection | `evaluation/metric-selection.md` | Pipeline-to-metric mapping, never mix categories |
| — LLM Judge Failures | `evaluation/llm-judge-failures.md` | NaN handling, retry logic, provider reliability |
| — CI Integration | `evaluation/ci-integration.md` | Cost estimation, batch optimization, threshold tuning |
