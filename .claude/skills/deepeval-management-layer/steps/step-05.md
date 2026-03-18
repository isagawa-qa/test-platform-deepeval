---
step: 5
name: Execution
requires: eval_suite
produces: eval_results
requirements: []
---

# Step 5: Execution

## Purpose

Run the generated eval suite against the pipeline under test, parse results, and present findings for human triage. This is where the eval suite proves its value — it either confirms the pipeline meets quality thresholds or identifies specific weaknesses for the team to address.

## Input

`eval_suite` from Step 4 — all generated files, golden dataset, configured metrics with thresholds.

## Actions

1. **Pre-execution check:**
   - Verify all generated files exist
   - Verify golden dataset loadable
   - Verify pipeline endpoint still reachable
   - Estimate token cost (rough: goldens × metrics × ~500 tokens per LLM-as-judge call)
   - Report estimate to user before proceeding

2. **Run eval suite:**
   ```bash
   deepeval test run tests/test_[pipeline_type]_pipeline.py --verbose
   ```

   Alternative (programmatic):
   ```python
   from deepeval import evaluate
   results = evaluate(test_cases, metrics)
   ```

   - Capture stdout/stderr
   - Track per-test-case results
   - Handle NaN scores via DeepEvalInterface retry logic

3. **Parse results:**
   For each metric × test case:
   ```json
   {
     "metric": "FaithfulnessMetric",
     "test_case_input": "What is the vacation policy?",
     "score": 0.82,
     "threshold": 0.70,
     "passed": true,
     "reason": "Output is fully grounded in retrieved context",
     "detail": {
       "claims_count": 3,
       "supported_claims": 3,
       "unsupported_claims": 0
     }
   }
   ```

4. **Compile results summary:**
   - Count pass/fail per metric
   - Identify worst-performing test cases
   - Calculate aggregate scores per metric
   - Flag metrics below threshold

5. **Generate triage report:**
   For each failed metric:
   - Which test cases failed (input truncated to 50 chars)
   - Score vs threshold
   - Possible root causes (based on metric type):
     | Metric | Common Root Causes |
     |--------|-------------------|
     | FaithfulnessMetric low | Hallucination in generation, prompt not grounding |
     | ContextualRelevancyMetric low | Retriever returning irrelevant chunks, chunking too coarse |
     | AnswerRelevancyMetric low | Answer doesn't address the question, too generic |
     | ToolCorrectnessMetric low | Wrong tool selected, tool routing logic broken |
     | TaskCompletionMetric low | Agent stops early, missing final step |
   - Suggested actions (pipeline improvements, NOT eval suite changes)

6. **HITL triage:**
   Present results to user. User decides:
   - **Accept:** Pipeline passes, eval suite is done
   - **Investigate:** User wants to debug specific failures
   - **Adjust thresholds:** User wants different pass/fail boundaries
   - **Expand dataset:** User wants more goldens for edge cases
   - **Re-run:** Fix pipeline, re-run eval suite

## Output

`eval_results` — structured results with pass/fail per metric, triage recommendations.

Output saved to `output/eval-results.md`:

```markdown
# Eval Results: RAG — app.rag.query

**Run date:** 2026-03-17
**Test cases:** 25
**Metrics:** 3

## Results Summary

| Metric | Avg Score | Threshold | Pass Rate | Status |
|--------|-----------|-----------|-----------|--------|
| FaithfulnessMetric | 0.82 | 0.70 | 24/25 (96%) | PASS |
| ContextualRelevancyMetric | 0.54 | 0.60 | 15/25 (60%) | FAIL |
| AnswerRelevancyMetric | 0.71 | 0.60 | 23/25 (92%) | PASS |

## Triage: ContextualRelevancyMetric

**Status:** FAIL — 10/25 test cases below threshold

**Worst cases:**
1. "What are the rules for expense reimburse..." — Score: 0.31
2. "How does the parental leave policy work..." — Score: 0.38
3. "What is the process for internal transfe..." — Score: 0.42

**Root cause analysis:**
- Retriever returning chunks from wrong document sections
- Long-form policy questions retrieve too many irrelevant chunks

**Suggested actions:**
1. Review chunking strategy — consider smaller, more focused chunks
2. Add metadata filtering to retrieval (department, topic)
3. Increase top-k and add re-ranking step

## Overall: 2/3 metrics passing
```

## Verification

- [ ] All test cases executed (no skips)
- [ ] NaN scores retried (up to 3x)
- [ ] Results compiled with per-metric aggregation
- [ ] Failed metrics have triage recommendations
- [ ] Results saved to `output/eval-results.md`
- [ ] User presented with triage options

## Failure Modes

| Failure | Symptom | Recovery |
|---------|---------|----------|
| All metrics NaN | LLM provider returning errors | Check API key, provider status, rate limits |
| Pipeline timeout | Endpoint doesn't respond within timeout | Increase timeout, check pipeline health |
| pytest crash | Import errors in generated code | Return to Step 4, fix imports |
| Token budget exceeded | Too many goldens × metrics | Reduce golden count, run in batches |
| LLM-as-judge inconsistency | Same test case scores differently on re-run | Run 3x and average, report variance |

## Examples

**Example 1: All Pass**
```
Eval Results: RAG — app.rag.query
  FaithfulnessMetric: 0.89 (threshold 0.70) — PASS
  ContextualRelevancyMetric: 0.74 (threshold 0.60) — PASS
  AnswerRelevancyMetric: 0.81 (threshold 0.60) — PASS

All metrics passing. Eval suite complete.
Pipeline quality: GOOD
```

**Example 2: Mixed Results with Triage**
```
Eval Results: Agent — app.agent.run
  ToolCorrectnessMetric: 0.65 (threshold 0.80) — FAIL
  TaskCompletionMetric: 0.78 (threshold 0.70) — PASS

Triage required for ToolCorrectnessMetric.
5/20 test cases selected wrong tool.
Common pattern: agent uses "search" tool when "lookup_order" is more appropriate.
Suggested: improve tool descriptions in agent prompt.
```
