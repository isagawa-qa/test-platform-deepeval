---
name: on-failure
type: checkpoint
parent: deepeval-management-layer
---

# Failure Diagnosis and Recovery

## Diagnosis Protocol

When any step fails:

1. **Identify the failure layer:**
   | Symptom | Layer | Step |
   |---------|-------|------|
   | Import error | Interface (L1) | Step 4 |
   | Metric returns NaN | Interface (L1) retry | Step 5 |
   | Wrong metrics selected | AI Processing | Step 3 |
   | Missing test case field | Object (L2) validation | Step 4 |
   | Test assertion fails | Test (L5) | Step 5 |
   | Pipeline unreachable | Pre-flight | Step 2 |

2. **Check the most common causes:**
   - **NaN scores:** LLM provider rate-limited or API key invalid. Check `OPENAI_API_KEY`.
   - **Import errors:** Layer generated out of order. Regenerate in order: Interface → Object → Task → Role → Test.
   - **Missing retrieval_context:** Metric requires it but pipeline type doesn't provide it. Check metric selection matrix.
   - **All tests fail:** Pipeline returning empty or error responses. Check pipeline health first.

3. **Fix and record:**
   - Fix the root cause
   - Invoke `/kernel/learn` to record the lesson
   - Re-run the failed step

## Recovery Actions by Step

| Step | Common Failure | Recovery |
|------|---------------|----------|
| 1 | Ambiguous pipeline type | Ask user directly |
| 2 | Missing dependencies | Provide install commands |
| 3 | Wrong metric selection | Re-check metric catalog against pipeline type |
| 4 | Pattern violation in generated code | Re-read reference file, regenerate |
| 5 | All NaN scores | Check API key, provider status, retry with different provider |

## Retry Limits

- Max 3 retries per step
- After 3 failures on same step: skip, log, report to user
- Never retry without fixing the root cause first

## Logging

Log failures to `state/eval_cycle.json`:
```json
{
  "errors": [
    {
      "step": 5,
      "error": "FaithfulnessMetric returned NaN for 3/25 test cases",
      "cause": "OpenAI rate limit hit",
      "fix": "Added 2s delay between eval calls",
      "timestamp": "2026-03-17T14:30:00Z"
    }
  ]
}
```
