# Task 032: Chat Pipeline Excludes Retrieval Metrics

## Objective
Verify the Chat pipeline does not select retrieval-specific metrics.

## Prerequisites
- `pip install -r requirements.txt` has been run

## Instructions
1. Read fixture at `tests/fixtures/PIPE-03-input.json`
2. From `framework/`, run a Python script that:
   - Passes `pipeline_type="Chat"` through the metric selection logic
   - Collects the list of metrics selected
3. Write output to `tests/output/PIPE-03-result.json`
4. Compare result against `tests/expected/PIPE-03-expected.json`:
   - Must contain keys: `metrics_selected`, `excluded_metrics`
   - `metrics_selected` must NOT include any of: `ContextualRelevancyMetric`, `ContextualPrecisionMetric`, `ContextualRecallMetric`, `FaithfulnessMetric`

## Acceptance Criteria
- [ ] Chat pipeline does NOT select `FaithfulnessMetric`
- [ ] Chat pipeline does NOT select `ContextualRelevancyMetric`
- [ ] Chat pipeline does NOT select `ContextualPrecisionMetric`
- [ ] Chat pipeline does NOT select `ContextualRecallMetric`
- [ ] Output written to `tests/output/PIPE-03-result.json`

## Gate
Satisfies: PIPE-03
Method: `mock_data`
