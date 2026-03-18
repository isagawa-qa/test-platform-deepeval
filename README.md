# platform-deepeval

**LLM Evaluation Codegen Platform** — AI-driven generation of structured DeepEval eval suites.

## What This Is

A domain spec for Claude Code that turns plain English eval descriptions into runnable, maintainable LLM evaluation code. Tell the agent what pipeline to test (RAG, Chat, Agent, Conversational), and it generates a complete eval suite following the 5-layer architecture.

This is to DeepEval what platform-selenium is to Selenium: the codegen layer that eliminates boilerplate and enforces structure.

## Quick Start

1. Install in your project:
   ```bash
   # Copy .claude/ and framework/ directories to your project
   ```

2. Install DeepEval:
   ```bash
   pip install deepeval
   ```

3. Set API keys:
   ```bash
   export OPENAI_API_KEY=your-key-here
   ```

4. Run the eval workflow:
   ```
   /eval-workflow RAG app.rag.query "Evaluate our RAG pipeline for HR policy questions"
   ```

## What It Generates

Given a pipeline type and endpoint, the agent generates:

| Layer | Files | Purpose |
|-------|-------|---------|
| DeepEvalInterface | `deepeval_interface.py` | Wraps DeepEval SDK with retry logic |
| Metric Objects | `metrics/*.py` | Threshold constants + state-checks per metric category |
| EvalTasks | `tasks/*.py` | One eval operation per function |
| EvalRoles | `roles/*.py` | Full eval workflow orchestrator |
| Tests | `tests/*.py` | pytest with parametrize over golden dataset |
| Fixtures | `fixtures/*.json` | Golden datasets for test data |

## Pipeline Types

| Type | What It Tests | Key Metrics |
|------|--------------|-------------|
| RAG | Retrieval + generation quality | Faithfulness, ContextualRelevancy, AnswerRelevancy |
| Chat | Single-turn response quality | AnswerRelevancy, Hallucination |
| Agent | Tool use + task completion | ToolCorrectness, TaskCompletion |
| Conversational | Multi-turn conversation quality | KnowledgeRetention, RoleAdherence |

## Architecture

Based on the isagawa-qa 5-layer test automation framework:

```
Tests → EvalRoles → EvalTasks → Metric Objects → DeepEvalInterface → DeepEval SDK
```

See `FRAMEWORK.md` for detailed architecture documentation.

## Requirements

- Python 3.8+
- DeepEval (`pip install deepeval`)
- LLM provider API key (OpenAI, Anthropic, or Azure)
- Claude Code with kernel

## License

Proprietary — isagawa-co
