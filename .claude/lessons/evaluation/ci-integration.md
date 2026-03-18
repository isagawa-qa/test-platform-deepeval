# CI Integration: Cost, Batching, and Threshold Tuning

<!-- Seeded: expert knowledge about running DeepEval in CI/CD pipelines -->

## Cost Estimation Before Execution

Always report estimated cost before running an eval suite:

```
Eval Plan:
  Test cases: 25
  Metrics: 3 (Faithfulness, ContextualRelevancy, AnswerRelevancy)
  Estimated LLM calls: 75
  Estimated cost: ~$2.25
  Estimated time: ~3-5 minutes

Proceed? [auto-proceed in CI mode]
```

## Batch Optimization

DeepEval's `evaluate()` function batches metric calls more efficiently than
individual `metric.measure()` calls. Use it for CI runs:

```python
# Efficient — batched
results = deepeval_interface.evaluate_batch(test_cases, metrics)

# Less efficient — sequential
for tc in test_cases:
    for metric in metrics:
        deepeval_interface.measure_metric(metric, tc)
```

## Threshold Tuning Strategy

Start loose, tighten over time:

1. **Week 1**: Set thresholds at 0.4-0.5 (baseline — understand your pipeline's range)
2. **Week 2-4**: Analyze score distributions, set thresholds at p25 of scores
3. **Month 2+**: Tighten to target quality level, alert on regressions

**Anti-pattern**: Starting with 0.9 thresholds and wondering why everything fails.
New pipelines rarely score above 0.7 on first eval.

## CI Pipeline Integration

```yaml
# Example: GitHub Actions
eval:
  runs-on: ubuntu-latest
  steps:
    - run: pip install deepeval
    - run: deepeval test run tests/
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

**Rules for CI**:
- Never hardcode API keys — use environment variables
- Set a cost ceiling per run (fail if estimated cost exceeds limit)
- Cache golden datasets — don't regenerate synthetic data on every run
- Run eval on PR branches, not just main (catch regressions early)
- Store eval results as artifacts for trend analysis
