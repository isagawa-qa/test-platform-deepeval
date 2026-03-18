# Dataset Management

<!-- Seeded: expert knowledge about golden datasets and synthetic generation -->

## Minimum Sample Sizes

| Purpose | Minimum Goldens | Recommended |
|---------|----------------|-------------|
| Quick smoke test | 5 | 10 |
| Development iteration | 20 | 30 |
| Pre-release eval | 50 | 100 |
| Production monitoring | 100+ | 200+ |

**Anti-pattern**: Creating 3-5 test cases and treating results as reliable. 5 goldens
is an anecdote, not a sample. Eval scores on tiny datasets have extreme variance —
re-running on the same 5 cases can swing ±0.3.

## Golden Dataset Schema

Golden fixtures are JSON arrays. Each entry maps to LLMTestCase parameters.

```json
[
  {
    "input": "What is the vacation policy?",
    "expected_output": "Employees receive 15 days PTO per year.",
    "context": ["HR Policy Document: Section 4.2..."],
    "retrieval_context": ["Retrieved: vacation policy states..."]
  }
]
```

**Required fields** depend on pipeline type:
- RAG: `input`, `expected_output`, `retrieval_context`
- Chat: `input`, `expected_output`
- Agent: `input`, `expected_output`, `expected_tools`

## Synthetic Generation with Synthesizer

When manual golden creation is too slow, use DeepEval's Synthesizer:

```python
dataset = deepeval_interface.generate_synthetic_dataset(
    documents=["Full text of HR policy...", "Employee handbook..."],
    max_goldens_per_document=25,
)
```

**Limitations**:
- Synthesizer requires source documents (not just prompts)
- Generated goldens may not cover edge cases
- Always review and curate synthetic goldens before production use
- Mix synthetic with manually crafted goldens for best coverage

## Fixture Organization

Golden fixtures live in `framework/_reference/fixtures/`:

```
fixtures/
├── golden_rag.json        ← RAG pipeline goldens
├── golden_agent.json      ← Agent pipeline goldens
├── golden_chat.json       ← Chat pipeline goldens
└── golden_conv.json       ← Conversational goldens
```

Loaded via conftest.py fixtures, never hardcoded in test files.

## Edge Cases to Include

Every golden dataset should cover:
- Ambiguous queries (multiple valid answers)
- Multi-hop questions (require combining information)
- Queries with no good answer (tests graceful handling)
- Long-form outputs (tests faithfulness at scale)
- Adversarial inputs (tests safety metrics)
