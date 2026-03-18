---
step: 1
name: User Input
requires: user_request
produces: parsed_eval_request
requirements: []
---

# Step 1: User Input

## Purpose

Parse the user's eval request into a structured format. The user describes what they want to test (pipeline type, endpoint, what to evaluate), and this step resolves it into an eval level, identifies the pipeline type, and prepares the request for pre-flight validation.

## Input

User provides any combination of:
- **Pipeline type** (explicit): "RAG", "Chat", "Agent", "Conversational"
- **Endpoint or function**: Python function, API URL, or module path
- **Description**: Plain English description of what the pipeline does
- **Golden dataset** (optional): Path to existing JSON file with goldens
- **Custom metrics** (optional): Additional GEval criteria

## Actions

1. **Identify pipeline type:**
   - If user specifies type directly → use it
   - If description mentions "retrieval", "context", "documents", "chunks" → RAG (Level 2)
   - If description mentions "tools", "function calling", "agent", "multi-step" → Agent (Level 4)
   - If description mentions "conversation", "multi-turn", "chat history" → Conversational
   - Default → Chat (Level 1)

2. **Resolve eval level:**
   | Pipeline Type | Eval Level | Test Case Type |
   |--------------|-----------|----------------|
   | Chat | 1 | LLMTestCase |
   | RAG | 2 | LLMTestCase (with retrieval_context) |
   | Codegen | 3 | LLMTestCase (with custom GEval) |
   | Agent | 4 | LLMTestCase (with tools_called, expected_tools) |
   | Conversational | 1+ | ConversationalTestCase |

3. **Parse endpoint:**
   - Python function: validate module path (e.g., `app.query_pipeline`)
   - API URL: validate URL format
   - If neither: ask user for clarification

4. **Check for golden dataset:**
   - If path provided → validate file exists, check JSON schema
   - If not → flag for synthetic generation in Step 2

5. **Build parsed eval request:**
   ```json
   {
     "pipeline_type": "RAG",
     "eval_level": 2,
     "endpoint": "app.query_pipeline",
     "description": "RAG pipeline that answers questions about company policies",
     "golden_dataset_path": null,
     "custom_metrics": [],
     "test_case_type": "LLMTestCase"
   }
   ```

## Output

`parsed_eval_request` — structured JSON with all fields resolved. Passed to Step 2.

## Verification

- [ ] Pipeline type resolved to one of: RAG, Chat, Agent, Conversational, Codegen, Custom
- [ ] Eval level assigned (1-4)
- [ ] Endpoint format validated (function path or URL)
- [ ] Test case type determined (LLMTestCase or ConversationalTestCase)
- [ ] Golden dataset path validated or flagged for generation

## Failure Modes

| Failure | Symptom | Recovery |
|---------|---------|----------|
| Ambiguous pipeline type | Description matches multiple types | Ask user to specify: "Is this a RAG pipeline or a Chat pipeline?" |
| Invalid endpoint format | Not a valid Python path or URL | Ask user for the exact function or API to call |
| Corrupt golden dataset | JSON parse error on provided file | Report error, offer to generate synthetic dataset |
| No description provided | User gives only endpoint, no context | Infer from endpoint name, ask for confirmation |

## Examples

**Example 1: RAG Pipeline**
```
User: "Evaluate our RAG pipeline at app.rag.query that answers HR policy questions"

Parsed:
  pipeline_type: RAG
  eval_level: 2
  endpoint: app.rag.query
  description: "RAG pipeline that answers HR policy questions"
  golden_dataset_path: null
  test_case_type: LLMTestCase
```

**Example 2: Agent with Existing Dataset**
```
User: "Test our support agent (app.agent.run) with the goldens in tests/agent_goldens.json"

Parsed:
  pipeline_type: Agent
  eval_level: 4
  endpoint: app.agent.run
  description: "Support agent"
  golden_dataset_path: "tests/agent_goldens.json"
  test_case_type: LLMTestCase
```
