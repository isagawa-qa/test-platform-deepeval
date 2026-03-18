---
name: deepeval-management-layer-gates
version: "1.0"
type: gate-contract
parent: deepeval-management-layer
---

# Eval Management Layer Gate Contract

## Verification Methods

| Method | How orchestrator checks |
|--------|------------------------|
| `file_exists` | `test -f {{path}}` — does the file exist? |
| `grep` | Search file content for a specific pattern |
| `run_code` | Execute a command and check exit code (0 = pass) |
| `mock_data` | Read fixture input, process through pipeline step, compare output against expected |
| `manual` | Orchestrator reads content and judges (LLM-evaluated) |

## Structure Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| STRUCT-01 | SKILL.md exists | `file_exists` | `.claude/skills/deepeval-management-layer/SKILL.md` exists | Create SKILL.md |
| STRUCT-02 | Workflow file exists | `file_exists` | `.claude/skills/deepeval-management-layer/workflow.md` exists | Create workflow.md |
| STRUCT-03 | Gate contract exists | `file_exists` | `.claude/skills/deepeval-management-layer/gate-contract.md` exists | Create gate-contract.md |
| STRUCT-04 | All step files exist | `file_exists` | `steps/step-01.md` through `steps/step-05.md` all exist | Create missing steps |
| STRUCT-05 | Metric catalog reference exists | `file_exists` | `references/metric-catalog.md` exists | Create catalog |
| STRUCT-06 | Architecture reference exists | `file_exists` | `references/architecture.md` exists | Create reference |

## Interface Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| IFACE-01 | DeepEvalInterface exists | `file_exists` | `framework/interfaces/deepeval_interface.py` exists | Create interface |
| IFACE-02 | DeepEvalInterface wraps create_test_case | `grep` | `deepeval_interface.py` contains `def create_test_case` | Add method |
| IFACE-03 | DeepEvalInterface wraps run_evaluation | `grep` | `deepeval_interface.py` contains `def run_evaluation` | Add method |
| IFACE-04 | DeepEvalInterface wraps assert_test | `grep` | `deepeval_interface.py` contains `def assert_test` | Add method |
| IFACE-05 | DeepEvalInterface wraps load_dataset | `grep` | `deepeval_interface.py` contains `def load_dataset` | Add method |
| IFACE-06 | DeepEvalInterface has retry logic | `grep` | `deepeval_interface.py` contains `retry` or `max_retries` | Add retry logic |
| IFACE-07 | DeepEvalInterface imports resolve | `run_code` | `python -c "from interfaces.deepeval_interface import DeepEvalInterface"` exits 0 | Fix imports |

## Metric Object Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| METRIC-01 | At least one Metric Object exists | `file_exists` | `framework/_reference/metrics/` contains at least one `.py` file | Create metric objects |
| METRIC-02 | Metric Objects have threshold constants | `grep` | Metric Object files contain `THRESHOLD` or `threshold` constant | Add thresholds |
| METRIC-03 | Metric Objects have state-check methods | `grep` | Metric Object files contain `def is_above_threshold` | Add state-checks |
| METRIC-04 | Metric Objects return self | `grep` | Metric Object files contain `return self` | Fix return pattern |
| METRIC-05 | Retrieval metrics require retrieval_context | `mock_data` | RetrievalMetrics validates that test case has `retrieval_context` field | Add parameter validation |

## Task Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| TASK-01 | At least one EvalTask exists | `file_exists` | `framework/_reference/tasks/` contains at least one `.py` file | Create task |
| TASK-02 | EvalTasks compose Metric Objects | `grep` | Task files import from `metrics/` | Add metric composition |
| TASK-03 | EvalTasks return None | `grep` | Task methods contain `return None` or no return statement | Fix return type |

## Role Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| ROLE-01 | At least one EvalRole exists | `file_exists` | `framework/_reference/roles/` contains at least one `.py` file | Create role |
| ROLE-02 | EvalRoles compose EvalTasks | `grep` | Role files import from `tasks/` | Add task composition |

## Test Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| TEST-01 | Test file exists | `file_exists` | `framework/_reference/tests/test_rag_pipeline.py` exists | Create test file |
| TEST-02 | Tests use pytest parametrize | `grep` | Test files contain `@pytest.mark.parametrize` | Add parametrize |
| TEST-03 | Tests use AAA pattern | `grep` | Test files contain `# Arrange` or clear setup/act/assert sections | Add AAA structure |
| TEST-04 | Tests assert via Metric Object | `grep` | Test files contain `is_above_threshold` or `get_score` | Fix assertions to use Metric Objects |
| TEST-05 | Conftest exists with fixtures | `file_exists` | `framework/_reference/tests/conftest.py` exists | Create conftest |
| TEST-06 | Golden dataset fixture exists | `file_exists` | `framework/_reference/fixtures/golden_rag.json` exists | Create fixture |

## Pipeline Type Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| PIPE-01 | Metric selection covers RAG | `mock_data` | Given pipeline_type="RAG", selected metrics include Faithfulness + ContextualRelevancy | Fix metric selection matrix |
| PIPE-02 | Metric selection covers Agent | `mock_data` | Given pipeline_type="Agent", selected metrics include ToolCorrectness + TaskCompletion | Fix metric selection matrix |
| PIPE-03 | Wrong metrics rejected | `mock_data` | Given pipeline_type="Chat", retrieval metrics are NOT selected (no retrieval_context) | Add pipeline type validation |

## Requirements Registry

| REQ ID | Gate | Behavioral Requirement | Test Name Pattern |
|--------|------|----------------------|-------------------|
| REQ-IF-001 | IFACE-07 | DeepEvalInterface creates valid LLMTestCase with all 9 parameters | `test_create_test_case_REQ_IF_001` |
| REQ-IF-002 | IFACE-06 | DeepEvalInterface retries on LLM-as-judge failure up to 3 times | `test_retry_on_failure_REQ_IF_002` |
| REQ-IF-003 | IFACE-03 | DeepEvalInterface runs batch evaluation and returns results | `test_run_evaluation_REQ_IF_003` |
| REQ-MO-001 | METRIC-05 | Retrieval metrics validate retrieval_context is present | `test_retrieval_requires_context_REQ_MO_001` |
| REQ-MO-002 | METRIC-03 | Metric Objects correctly report pass/fail against threshold | `test_threshold_check_REQ_MO_002` |
| REQ-MO-003 | METRIC-02 | Metric Objects expose configurable thresholds | `test_configurable_threshold_REQ_MO_003` |
| REQ-TK-001 | TASK-02 | EvalTasks compose correct Metric Objects for pipeline type | `test_task_metric_composition_REQ_TK_001` |
| REQ-RL-001 | ROLE-02 | EvalRoles orchestrate Tasks in correct sequence | `test_role_task_sequence_REQ_RL_001` |
| REQ-TS-001 | TEST-02 | Tests parametrize over golden dataset entries | `test_parametrize_goldens_REQ_TS_001` |
| REQ-TS-002 | TEST-04 | Tests assert via Metric Object state-checks not raw scores | `test_assert_via_metric_object_REQ_TS_002` |
| REQ-PP-001 | PIPE-01 | RAG pipeline selects Faithfulness + Retrieval + Relevancy metrics | `test_rag_metric_selection_REQ_PP_001` |
| REQ-PP-002 | PIPE-02 | Agent pipeline selects ToolCorrectness + TaskCompletion metrics | `test_agent_metric_selection_REQ_PP_002` |
| REQ-PP-003 | PIPE-03 | Chat pipeline excludes retrieval metrics | `test_chat_excludes_retrieval_REQ_PP_003` |

## Autonomy Rules

The eval agent operates **fully autonomously** during eval suite generation. HITL only at triage.

| Action | Autonomous? |
|--------|-------------|
| Parse pipeline type and select metrics | Yes |
| Generate eval suite (all 5 layers) | Yes |
| Run evaluation | Yes |
| Retry NaN scores (up to 3x) | Yes |
| Triage failures (recommend fixes) | Yes — present to user |
| Modify pipeline under test | No — agent tests, never modifies the target |
| Change LLM provider | No — requires user config |
| Override user-specified thresholds | No — use user values when provided |

## Stop Conditions

| Condition | Action |
|-----------|--------|
| 3 consecutive failures on same gate | Skip, log, continue to next step |
| DeepEval not installed | Stop, provide `pip install deepeval` |
| No API keys configured | Stop, list required env vars |
| Pipeline unreachable after 3 attempts | Offer mock mode, ask user |
| All metrics return NaN after retries | Stop, report LLM provider issue |

## Domain-Specific Constraints

1. **Never modify the pipeline under test.** The eval agent generates tests and runs them — it never changes the code being evaluated.
2. **API keys are secrets.** Never log, print, or include API keys in generated code. Use `os.environ` references only.
3. **LLM-as-judge costs real money.** Each eval run calls the LLM provider. Report estimated token usage before execution. Batch where possible.
4. **Golden datasets may contain PII.** If user provides real user queries as goldens, treat them as sensitive. Never log full golden content in results — show input truncated to 50 chars.
