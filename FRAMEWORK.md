# platform-deepeval Framework

## Architecture

The platform-deepeval spec follows the isagawa-qa 5-layer architecture, adapted for LLM output evaluation using DeepEval.

```
Layer 5: Tests          pytest, AAA, @parametrize over goldens
  Layer 4: EvalRoles    RAGEvaluator, AgentEvaluator — workflow orchestrators
    Layer 3: EvalTasks  run_rag_eval, run_agent_eval — one operation, return None
      Layer 2: Metric Objects  FaithfulnessMetrics, RetrievalMetrics — constants + state-checks
        Layer 1: DeepEvalInterface  Wraps DeepEval SDK — evaluate, assert_test, LLMTestCase
```

## Layer Mapping (from QA test automation)

| QA Layer | Eval Layer | Selenium Equivalent | DeepEval Equivalent |
|----------|-----------|--------------------|--------------------|
| Interface | DeepEvalInterface | BrowserInterface (wraps WebDriver) | Wraps DeepEval SDK |
| Object | Metric Object | Page Object (locators, state-checks) | Thresholds, is_above_threshold() |
| Task | EvalTask | Task (login, search) | run_rag_eval, run_agent_eval |
| Role | EvalRole | Role (checkout flow) | RAGEvaluator, AgentEvaluator |
| Test | Test | pytest, AAA, assert via Page Object | pytest, AAA, assert via Metric Object |

## Key Design Decisions

### DD-01: One Metric Object per Category, Not Per Metric
DeepEval has 50+ metrics. Grouping by category (Retrieval, Faithfulness, Agent, Safety) keeps the codebase manageable. Each Metric Object class wraps 2-6 related metrics.

### DD-02: DeepEvalInterface Wraps SDK, Not HTTP
DeepEval is a Python package (`import deepeval`), not a REST API. DeepEvalInterface wraps Python method calls, not HTTP requests.

### DD-03: Retry Logic in Interface Layer
LLM-as-judge calls fail intermittently. Retry logic (3 attempts, exponential backoff) lives in DeepEvalInterface — the only layer that talks to external APIs.

### DD-04: Golden Datasets as Fixtures
Test data comes from JSON fixtures loaded via conftest.py. Tests use `@pytest.mark.parametrize` over the dataset. This matches the data-driven test pattern from the QA platforms.

### DD-05: Metric Selection by Pipeline Type
The agent automatically selects metrics based on pipeline type (RAG, Chat, Agent, Conversational). This eliminates the "metric selection is non-obvious" pain point from the audit.

### DD-06: HITL at Triage Only
The agent autonomously generates the eval suite and runs it. Human-in-the-loop triggers only when results need triage — matching the QA platform pattern.

## File Structure

```
.claude/
  skills/deepeval-management-layer/
    SKILL.md              — Identity, vocabulary, rules
    workflow.md           — 5-step pipeline, metric selection matrix
    gate-contract.md      — Quality gates, HITL protocol
    references/
      metric-catalog.md   — Complete DeepEval metric catalog
      architecture.md     — 5-layer architecture details
    steps/
      step-01.md          — User Input
      step-02.md          — Pre-flight
      step-03.md          — AI Processing
      step-04.md          — Construction
      step-05.md          — Execution
      pre-eval.md         — Pre-construction checkpoint
      on-failure.md       — Failure recovery
  commands/
    eval-workflow.md      — Main eval workflow command
    eval-dev.md           — Dev mode (relaxed gates)
  lessons/
    lessons.md            — Lesson index
    eval/                 — Seeded lessons
framework/
  _reference/             — Reference implementations (all 5 layers)
    deepeval_interface.py     — Layer 1
    metrics/              — Layer 2 (6 Metric Object classes)
    tasks/                — Layer 3 (2 EvalTask functions)
    roles/                — Layer 4 (2 EvalRole classes)
    tests/                — Layer 5 (test files + conftest)
    fixtures/             — Golden datasets (JSON)
  interfaces/             — Canonical DeepEvalInterface
  resources/              — Config and defaults
```

## Pipeline Types Supported

| Type | Level | Metrics | Test Case |
|------|-------|---------|-----------|
| Chat | 1 | AnswerRelevancy, Hallucination | LLMTestCase |
| RAG | 2 | Faithfulness, ContextualRelevancy, AnswerRelevancy | LLMTestCase + retrieval_context |
| Codegen | 3 | GEval (custom criteria) | LLMTestCase |
| Agent | 4 | ToolCorrectness, TaskCompletion | LLMTestCase + tools_called |
| Conversational | 1+ | KnowledgeRetention, RoleAdherence | ConversationalTestCase |
