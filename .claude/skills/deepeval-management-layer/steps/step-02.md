---
step: 2
name: Pre-flight
requires: parsed_eval_request
produces: validated_environment
requirements: [REQ-IF-001, REQ-IF-002]
---

# Step 2: Pre-flight

## Purpose

Validate that the environment is ready for eval suite generation and execution. Check DeepEval installation, API keys, pipeline connectivity, and golden dataset availability. This step prevents construction failures by catching missing dependencies early.

## Input

`parsed_eval_request` from Step 1 — pipeline type, endpoint, golden dataset path.

## Actions

1. **Verify DeepEval installation:**
   ```python
   python -c "import deepeval; print(deepeval.__version__)"
   ```
   - If fails: report `pip install deepeval` and STOP
   - Minimum version: check against metric requirements (agentic metrics require 1.0+)

2. **Verify LLM provider API keys:**
   | Provider | Env Var | Required For |
   |----------|---------|-------------|
   | OpenAI | `OPENAI_API_KEY` | LLM-as-judge metrics (default provider) |
   | Anthropic | `ANTHROPIC_API_KEY` | Alternative LLM-as-judge |
   | Azure | `AZURE_OPENAI_API_KEY` | Enterprise deployments |

   - Check `os.environ` for at least one provider
   - If none found: report required env vars and STOP
   - Note: some metrics (JsonCorrectness) don't need LLM-as-judge

3. **Verify pipeline reachability:**
   - If Python function: `python -c "from {module} import {function}"`
   - If API URL: basic connectivity check
   - If unreachable after 3 attempts: offer **mock mode**
     - Mock mode: generate eval suite with canned responses for structure validation
     - User can swap mock for real pipeline later

4. **Validate or generate golden dataset:**
   - If path provided:
     - Parse JSON, validate schema (each golden has `input` and `expected_output`)
     - Count entries — warn if < 20
     - Check for required fields per pipeline type:
       - RAG: `input`, `expected_output`, `context` or `retrieval_context`
       - Agent: `input`, `expected_output`, `expected_tools`
       - Chat: `input`, `expected_output`
   - If no path:
     - Flag for synthetic generation via `Synthesizer`
     - Requires source documents (user provides docs path)
     - Or generate minimal dataset from description (5-10 goldens for bootstrapping)

5. **Build validated environment:**
   ```json
   {
     "deepeval_version": "1.3.2",
     "llm_provider": "openai",
     "pipeline_reachable": true,
     "mock_mode": false,
     "golden_dataset": {
       "source": "provided",
       "path": "tests/goldens.json",
       "count": 25,
       "schema_valid": true
     }
   }
   ```

## Requirements

| REQ ID | Behavior | Test Name Convention |
|--------|----------|---------------------|
| REQ-IF-001 | DeepEvalInterface creates valid LLMTestCase with all 9 parameters | `test_create_test_case_REQ_IF_001` |
| REQ-IF-002 | DeepEvalInterface retries on LLM-as-judge failure up to 3 times | `test_retry_on_failure_REQ_IF_002` |

## Output

`validated_environment` — JSON confirming all pre-flight checks passed. Passed to Step 3.

## Verification

- [ ] DeepEval installed and importable
- [ ] At least one LLM provider API key set
- [ ] Pipeline endpoint reachable (or mock mode activated)
- [ ] Golden dataset available with valid schema (or generation planned)
- [ ] Golden count ≥ 20 (or warning issued)

## Failure Modes

| Failure | Symptom | Recovery |
|---------|---------|----------|
| DeepEval not installed | `ModuleNotFoundError: No module named 'deepeval'` | Provide `pip install deepeval` command |
| No API keys | All provider env vars empty | List required env vars per provider |
| Pipeline unreachable | Import error or connection timeout | Offer mock mode, document real endpoint for later |
| Invalid golden schema | JSON parse error or missing required fields | Report which fields are missing, provide schema example |
| Too few goldens | Count < 20 | Warn user, offer Synthesizer generation, proceed with warning |

## Examples

**Example 1: Full Environment Ready**
```
Pre-flight results:
  DeepEval: 1.3.2 ✓
  Provider: OpenAI (OPENAI_API_KEY set) ✓
  Pipeline: app.rag.query importable ✓
  Dataset: tests/goldens.json (25 goldens, schema valid) ✓

All pre-flight checks passed. Proceeding to AI Processing.
```

**Example 2: Missing Dependencies**
```
Pre-flight results:
  DeepEval: NOT INSTALLED ✗
  Provider: No API keys found ✗

STOPPED. Required actions:
  1. pip install deepeval
  2. export OPENAI_API_KEY=your-key-here
```
