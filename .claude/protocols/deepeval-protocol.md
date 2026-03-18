# DeepEval Protocol

**Domain:** deepeval
**Type:** Indexed
**Created:** 2026-03-18

---

## References

### Code Patterns

| Category | Reference |
|----------|-----------|
| Layer 1 — DeepEvalInterface | `framework/interfaces/deepeval_interface.py` |
| Layer 2 — Metric Objects | `framework/_reference/metrics/` (6 files) |
| Layer 3 — EvalTasks | `framework/_reference/tasks/` |
| Layer 4 — EvalRoles | `framework/_reference/roles/` |
| Layer 5 — Tests | `framework/_reference/tests/` |
| Config defaults | `framework/resources/metric_defaults.py` |
| Config schema | `framework/resources/eval_config.py` |

### Architecture + Patterns

→ `FRAMEWORK.md` — 5-layer architecture, design decisions, pipeline types
→ `.claude/skills/deepeval-management-layer/references/architecture.md` — layer details with examples

### Workflow

| File | Purpose |
|------|---------|
| `.claude/skills/deepeval-management-layer/SKILL.md` | Identity, vocabulary, rules |
| `.claude/skills/deepeval-management-layer/workflow.md` | 5-step pipeline, metric selection matrix |
| `.claude/skills/deepeval-management-layer/gate-contract.md` | Quality gates, HITL protocol |
| `.claude/skills/deepeval-management-layer/steps/` | Step-specific criteria (01-05, pre-eval, on-failure) |
| `.claude/skills/deepeval-management-layer/references/metric-catalog.md` | Complete metric catalog |

### Entry Points

| Command | Purpose |
|---------|---------|
| `/kernel/session-start` | Initialize session, resume if needed |
| `/kernel/anchor` | Re-read protocol, check work |
| `/kernel/learn` | Capture lesson from failure |
| `/kernel/fix` | Impact assessment before fix |
| `/kernel/complete` | Final gate, cycling continuation |
| `/kernel/autonomous-cycle` | Start cycling through tasks |

### Task Queue

→ `tasks/` — 33 numbered task files (001-033)

### Lessons Learned

→ `.claude/lessons/lessons.md` — index of seeded + accumulated lessons

---

*Protocol is an INDEX. Agent reads referenced files during /kernel/anchor.*
