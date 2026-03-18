# Task 030: RAG Pipeline Selects Correct Metrics

## Objective
Verify the RAG pipeline selects Faithfulness and ContextualRelevancy metrics.

## Prerequisites
- `pip install -r requirements.txt` has been run

## Instructions
1. Read fixture at `tests/fixtures/PIPE-01-input.json`
2. From `framework/`, run a Python script that:
   - Imports the RAG eval task from `_reference.tasks.run_rag_eval`
   - Passes `pipeline_type="RAG"` through the metric selection logic
   - Collects the list of metrics selected
3. Write output to `tests/output/PIPE-01-result.json`
4. Compare result against `tests/expected/PIPE-01-expected.json`:
   - Must contain key: `metrics_selected`
   - `metrics_selected` must include `FaithfulnessMetric` and `ContextualRelevancyMetric`

## Acceptance Criteria
- [ ] RAG pipeline selects `FaithfulnessMetric`
- [ ] RAG pipeline selects `ContextualRelevancyMetric`
- [ ] Output written to `tests/output/PIPE-01-result.json`

## Gate
Satisfies: PIPE-01
Method: `mock_data`
