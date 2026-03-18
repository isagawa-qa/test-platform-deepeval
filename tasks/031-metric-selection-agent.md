# Task 031: Agent Pipeline Selects Correct Metrics

## Objective
Verify the Agent pipeline selects ToolCorrectness and TaskCompletion metrics.

## Prerequisites
- `pip install -r requirements.txt` has been run

## Instructions
1. Read fixture at `tests/fixtures/PIPE-02-input.json`
2. From `framework/`, run a Python script that:
   - Imports the Agent eval task from `_reference.tasks.run_agent_eval`
   - Passes `pipeline_type="Agent"` through the metric selection logic
   - Collects the list of metrics selected
3. Write output to `tests/output/PIPE-02-result.json`
4. Compare result against `tests/expected/PIPE-02-expected.json`:
   - Must contain key: `metrics_selected`
   - `metrics_selected` must include `ToolCorrectnessMetric` and `TaskCompletionMetric`

## Acceptance Criteria
- [ ] Agent pipeline selects `ToolCorrectnessMetric`
- [ ] Agent pipeline selects `TaskCompletionMetric`
- [ ] Output written to `tests/output/PIPE-02-result.json`

## Gate
Satisfies: PIPE-02
Method: `mock_data`
