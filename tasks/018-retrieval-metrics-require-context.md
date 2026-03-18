# Task 018: Retrieval Metrics Validate retrieval_context

## Objective
Verify that retrieval-type metrics reject test cases missing `retrieval_context`.

## Prerequisites
- `pip install -r requirements.txt` has been run

## Instructions
1. Read fixture at `tests/fixtures/METRIC-05-input.json`
2. From `framework/`, run a Python script that:
   - Imports `RetrievalMetrics` from `_reference.metrics.retrieval_metrics`
   - Creates a test case with `retrieval_context=None` (as specified in fixture)
   - Attempts to evaluate — should raise a validation error or return `valid: false`
3. Write output to `tests/output/METRIC-05-result.json`
4. Compare result against `tests/expected/METRIC-05-expected.json`:
   - Must contain keys: `error`, `valid`
   - `valid` must be `false`

## Acceptance Criteria
- [ ] RetrievalMetrics raises error or returns `valid: false` when `retrieval_context` is null
- [ ] Output written to `tests/output/METRIC-05-result.json`
- [ ] Output matches expected (contains_keys: `error`, `valid`; `valid` = false)

## Gate
Satisfies: METRIC-05
Method: `mock_data`
