# Tiered Index A/B Experiment — Design Document

## Hypothesis

**H1:** Agent tasks performed against tiered-indexed documentation (index/payload split, each file < 200 lines) will produce higher task completion scores and fewer silent-drift failures than identical tasks performed against flat documentation (single large files, 300-800 lines).

**H0 (null):** There is no statistically significant difference in task completion or failure mode distribution between flat and tiered documentation structures.

## Variables

### Independent Variable
- **Documentation structure:** flat (single file) vs tiered (index + payloads)
- Content is identical across both conditions — only structure differs

### Dependent Variables
- **Task completion score** (0.0-1.0) — did the agent produce the correct output?
- **Read compliance score** (0.0-1.0) — did the agent read the right files? (ReadComplianceMetric from backlog 143)
- **Failure mode classification** — HOW did the agent fail? (4 categories)
- **Answer relevancy score** (0.0-1.0) — does the output address the question?

### Controlled Variables
- Model (held constant per run — default: claude-sonnet-4-5-20250514)
- Prompt template (identical across conditions)
- Content (identical — only structure differs)
- Task definitions (identical)

## Fixture Design

### Flat Fixtures (Group A)
- 5 domains: coding, research, workflow, memory, contradiction
- Each domain: single markdown file, 300-500 lines
- Content covers multiple topics within the domain

### Tiered Fixtures (Group B)
- Same 5 domains, same content
- Each domain: index.md (< 100 lines) + 2-4 payload files (each < 200 lines)
- Index files contain topic headings with file references
- Payload files contain the actual content

### Content Parity Guarantee
A structural test (`test_fixture_parity`) strips all index metadata and verifies that the raw content in flat fixtures matches the combined content in tiered fixtures. This is a prerequisite gate — the experiment cannot run if parity fails.

## Task Categories

| Category | Count | Tests | Flat Expectation | Tiered Expectation |
|----------|-------|-------|-----------------|-------------------|
| Single-file lookup | 4 | Find specific fact | May miss buried info | Index directs to correct payload |
| Cross-reference | 4 | Combine 2+ sources | May miss one source | Index links both payloads |
| Contradiction | 4 | Detect conflict | May skip conflicting section | Focused payload makes conflict visible |
| Multi-step workflow | 4 | Follow ordered steps | May skip/reorder steps | Index enforces sequence |
| Memory retrieval | 4 | Recall prior decision | May miss in large file | Focused payload is findable |
| Stress test | 4 | 500+ line content | Likely attention loss | 3-level split maintains focus |

Total: 24 tasks (4 per category × 6 categories)

## Metric Battery

Per task execution, collect:

| Metric | Source | Type |
|--------|--------|------|
| task_completion | Custom — exact match or rubric | Deterministic |
| read_compliance | ReadComplianceMetric (backlog 143) | Deterministic |
| failure_mode | FailureModeClassifier (new) | LLM-as-judge |
| answer_relevancy | Keyword/pattern match | Deterministic |

## Failure Mode Taxonomy

| Mode | Definition | Detection Method |
|------|-----------|-----------------|
| silent_drift | Wrong answer, no uncertainty signal | Output incorrect + no hedging language |
| partial_read | Read some required files, skipped others | ReadComplianceMetric < 1.0 + task_completion < 1.0 |
| hallucination | Content not in any source file | Output contains claims absent from all fixtures |
| contradiction_ignored | Conflict exists, agent didn't flag it | Contradiction task + no conflict mention in output |
| correct | Task completed correctly | task_completion == 1.0 |

## Statistical Method

- **Comparison:** Paired comparison per task (flat score vs tiered score for same task)
- **Metric:** Mean difference in task_completion between groups
- **Significance:** Report effect size (Cohen's d) and confidence intervals
- **Minimum meaningful difference:** 15% improvement in task_completion to reject H0
- **Sample size:** 24 tasks × 2 conditions = 48 data points per run

## Execution Protocol

1. Load fixture set (flat or tiered)
2. For each task in catalog:
   a. Construct prompt from template + task input
   b. Provide fixture files as context
   c. Collect agent output
   d. Score with metric battery
3. Repeat for other condition
4. Aggregate and compare

## Cost Estimate

- 24 tasks × 2 conditions = 48 executions
- Estimated ~2000 tokens per execution (prompt + context + output)
- Total: ~96K tokens per full run
- At typical rates: < $1 per full experiment run
