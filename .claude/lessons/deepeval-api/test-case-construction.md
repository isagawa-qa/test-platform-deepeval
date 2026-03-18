# Test Case Construction

<!-- Seeded: expert knowledge about LLMTestCase and ConversationalTestCase -->

## LLMTestCase — 9 Parameters

LLMTestCase is the atomic unit of evaluation. It has exactly 9 parameters.

```python
LLMTestCase(
    input="What is the refund policy?",           # Required: user prompt
    actual_output="Our refund policy states...",   # Required: LLM response
    expected_output="Customers can return...",     # Optional: golden answer
    context=["Refund policy document..."],         # Optional: ground truth context
    retrieval_context=["Retrieved chunk 1..."],    # Optional: what RAG retrieved
    tools_called=[{"name": "search"}],             # Optional: agent tool calls
    expected_tools=["search", "lookup"],            # Optional: expected tools
    token_cost=0.002,                              # Optional: cost tracking
    completion_time=1.5,                           # Optional: latency tracking
)
```

## Critical Distinction: context vs retrieval_context

This is the most common source of confusion.

| Field | What It Is | Who Provides It | Used By |
|-------|-----------|-----------------|---------|
| `context` | Ground truth — the correct information | Human / golden dataset | HallucinationMetric |
| `retrieval_context` | What the RAG pipeline actually retrieved | The pipeline under test | Faithfulness, ContextualRelevancy, ContextualPrecision, ContextualRecall |

**Anti-pattern**: Setting `context = retrieval_context`. These are different things.
Context is what SHOULD have been retrieved. Retrieval context is what WAS retrieved.

## ConversationalTestCase

For multi-turn evaluation. Each turn is an LLMTestCase.

```python
ConversationalTestCase(
    turns=[
        LLMTestCase(input="Hi", actual_output="Hello!"),
        LLMTestCase(input="What's my name?", actual_output="I don't know your name yet."),
    ],
    chatbot_role="Customer support agent for an e-commerce platform",
)
```

Used by: KnowledgeRetentionMetric, RoleAdherenceMetric.

## Creating Test Cases from Goldens

The standard pattern uses DeepEvalInterface to create test cases from golden data:

```python
for golden in dataset:
    actual_output = pipeline_fn(golden["input"])
    test_case = deepeval_interface.create_test_case(
        input=golden["input"],
        actual_output=actual_output,
        expected_output=golden.get("expected_output"),
        retrieval_context=golden.get("retrieval_context"),
    )
```

**Never** construct LLMTestCase directly in Tasks, Roles, or Tests.
Always go through DeepEvalInterface.
