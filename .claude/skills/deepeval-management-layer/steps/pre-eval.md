---
name: pre-eval-checkpoint
type: checkpoint
parent: deepeval-management-layer
---

# Pre-Construction Readiness Checkpoint

Run this checklist before entering Step 4 (Construction).

## Environment

- [ ] DeepEval installed (`python -c "import deepeval"` exits 0)
- [ ] LLM provider API key set (at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY)
- [ ] Pipeline endpoint reachable or mock mode activated

## Plan Completeness

- [ ] Pipeline type resolved (RAG/Chat/Agent/Conversational/Custom)
- [ ] Metrics selected (at least 2 required metrics)
- [ ] Thresholds configured (all within 0.0-1.0)
- [ ] File plan generated (all 5 layers represented)

## Reference Files

- [ ] `references/metric-catalog.md` readable
- [ ] `references/architecture.md` readable
- [ ] `interfaces/deepeval_interface.py` readable
- [ ] At least one `_reference/metrics/*.py` readable
- [ ] At least one `_reference/tasks/*.py` readable
- [ ] At least one `_reference/roles/*.py` readable
- [ ] At least one `_reference/tests/*.py` readable

## Dataset

- [ ] Golden dataset available (provided or generation planned)
- [ ] Golden count ≥ 20 (or warning acknowledged)
- [ ] Golden schema matches pipeline type requirements

## If any check fails

1. Return to the failing step (Step 2 for environment, Step 3 for plan)
2. Fix the issue
3. Re-run this checkpoint
4. Only proceed to Construction when all checks pass
