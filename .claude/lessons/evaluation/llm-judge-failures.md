# LLM-as-Judge: Handle NaN Scores Gracefully

<!-- Seeded: expert knowledge about LLM-as-judge reliability and failure modes -->

## The Problem

Running an eval suite and having it crash when the LLM-as-judge returns NaN or errors.
No retry logic, no error handling. One bad API call kills the entire eval run.

## Why It Fails

LLM-as-judge metrics call an LLM (usually GPT-4) to evaluate another LLM's output.
These calls fail for many reasons:

| Failure Mode | Frequency | Impact |
|-------------|-----------|--------|
| Rate limits (429) | Common | Temporary — retryable |
| Timeout | Occasional | Temporary — retryable |
| Malformed response | Rare | Permanent — record NaN |
| Provider downtime | Rare | Permanent — abort run |
| Context too long | Occasional | Permanent — truncate or skip |
| Auth error (401) | Setup | Permanent — wrong/expired API key. Validate before run |

A 25-golden eval with 3 metrics = 75 LLM calls. Even at 99% reliability, you'll see
~1 failure per run.

## Correct Approach

DeepEvalInterface includes retry logic: 3 retries with exponential backoff (1s, 2s, 4s).

```python
def _run_with_retry(self, metric, test_case):
    for attempt in range(self.max_retries):
        try:
            metric.measure(test_case)
            return metric.score
        except Exception:
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                time.sleep(delay)
            else:
                return None  # Record NaN, don't crash
```

**Rules**:
- If all retries fail → record NaN for that metric-case pair, continue the run
- Report NaN count in results summary
- If >10% of scores are NaN → flag the LLM provider as unreliable
- If ALL scores are NaN → stop the run, report provider issue

## Cost Awareness

Each eval run costs real money. Estimate before running:

| Metric Type | Approx Cost per Test Case |
|-------------|--------------------------|
| Simple (Bias, Toxicity) | ~$0.01 |
| Medium (Faithfulness, Relevancy) | ~$0.03 |
| Complex (GEval with long criteria) | ~$0.05 |

25 goldens × 3 metrics × $0.03 = ~$2.25 per run. Report this before execution.

## Source

DeepEval GitHub issues: multiple reports of NaN scores during eval runs. Audit finding:
"LLM-as-judge failures (NaN scores) crash eval runs" (pain point severity: Medium).
