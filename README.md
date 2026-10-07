# Isagawa DeepEval Platform

AI-driven LLM and agent evaluation with DeepEval. Describe what to evaluate, and an AI agent builds golden-dataset evaluation suites for RAG, chat, agent, and conversational pipelines, with the right metrics for each pipeline type. Suites run like any other pytest suite and catch regressions when a prompt, model, or tool changes.

---

## Get Started (Step by Step)

### Step 1: Install VS Code
1. Go to https://code.visualstudio.com/ and download

### Step 2: Install Git
1. Go to https://git-scm.com/downloads -- verify with git --version

### Step 3: Install Python (3.10+)
1. Go to https://www.python.org/downloads/ -- check Add Python to PATH

### Step 4: Install Node.js (18+)
1. Go to https://nodejs.org/ and download LTS

### Step 5: Install Claude Code Extension
1. VS Code Extensions -> search Claude Code by Anthropic -> Install

### Step 6: Clone and Open
```bash
git clone https://github.com/isagawa-qa/test-platform-deepeval.git
```
Open in VS Code: File -> Open Folder -> select test-platform-deepeval

### Step 7: Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Add your LLM API key
```

### Step 8: Create Your First Eval Suite
```
/eval-workflow
```
Provide: pipeline type (RAG/Chat/Agent), endpoint, description, golden dataset requirements.

---

## The Problem

AI can generate DeepEval test cases in seconds. But without enforcement:
- Wrong metrics selected for the pipeline type
- Golden datasets poorly constructed
- Thresholds scattered across files instead of centralized
- Same mistakes repeat every session

## The Solution

Every eval suite the agent builds follows one structure, with metrics matched to the pipeline type and thresholds kept in one place. The agent works under guardrails from the [Isagawa Kernel](https://github.com/isagawa-co/isagawa-kernel), so it builds evaluations consistently and does not repeat mistakes it has already made.

## Pipeline Types

| Type | What It Evaluates | Key Metrics |
|------|------------------|-------------|
| **RAG** | Retrieval + generation | Faithfulness, ContextualRelevancy, AnswerRelevancy |
| **Chat** | Single-turn response | AnswerRelevancy, Hallucination, Toxicity |
| **Agent** | Tool use + task completion | ToolCorrectness, TaskCompletion |
| **Conversational** | Multi-turn quality | KnowledgeRetention, RoleAdherence |

---

## Quick Start

```bash
git clone https://github.com/isagawa-qa/test-platform-deepeval.git
cd test-platform-deepeval && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
claude && /eval-workflow
```

---

## Author

Built by Alain Ignacio, QA lead and test automation architect.
Portfolio: [alain-ignacio.github.io](https://alain-ignacio.github.io) · LinkedIn: [linkedin.com/in/alain-ignacio](https://www.linkedin.com/in/alain-ignacio)

## License

Proprietary. Copyright (c) 2025 Isagawa. All rights reserved. Source is available for evaluation only. See [LICENSE](LICENSE).
