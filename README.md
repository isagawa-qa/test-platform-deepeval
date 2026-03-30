# Isagawa DeepEval Platform

### AI Execution Management for LLM Evaluation

> AI can generate eval suites. But can you trust it to evaluate correctly?

Most AI tools generate eval code and hope for the best. Isagawa **enforces how AI works** -- gating every action at runtime so the AI can only build evals the right way.

This is not AI governance. It is **AI execution management**.

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

The Isagawa DeepEval Platform combines a **5-layer eval architecture** with the **Isagawa Kernel** -- a self-building, self-improving enforcement system that runs *inside* the AI agent.

---

## 5-Layer Architecture

| Layer | Responsibility | Example |
|-------|---------------|---------|
| **Test** | Asserts eval result | test_rag_faithfulness() |
| **EvalRole** | Coordinates eval workflows | RAGEvaluator.run_full_eval() |
| **EvalTask** | One eval operation | run_rag_eval() |
| **Metric Object** | Thresholds + state-checks | FaithfulnessMetrics.is_above_threshold() |
| **DeepEvalInterface** | Wraps DeepEval SDK | DeepEvalInterface.evaluate() |

```
Test -> EvalRole -> EvalTask -> Metric Object -> DeepEvalInterface -> DeepEval SDK
```

**Key rules:** Thresholds only in Metric Objects. Tasks/Roles never return values. Tests parametrize over golden datasets. Retry logic only in Interface.

---

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

## Project Structure

```
test-platform-deepeval/
  .claude/skills/deepeval-management-layer/  5-step eval workflow
  .claude/commands/kernel/                   Kernel commands
  .claude/hooks/                             Gate enforcer
  framework/_reference/metrics/              7 Metric Object classes
  framework/_reference/tasks/                EvalTask implementations
  framework/_reference/roles/                EvalRole implementations
  framework/interfaces/deepeval_interface.py DeepEvalInterface
  tests/                                     Validation tests + fixtures
  FRAMEWORK.md                               Architecture docs
```

---

## The Bigger Picture

LLM evaluation is one domain. The Isagawa Kernel supports **any** domain:
- **Test automation** -- [platform-selenium](https://github.com/isagawa-qa/platform-selenium), [platform-playwright](https://github.com/isagawa-qa/platform-playwright)
- **Infrastructure** -- [platform-ssh](https://github.com/isagawa-qa/platform-ssh) (STIG, CIS, NIST 800-171)
- **Containers** -- [platform-docker](https://github.com/isagawa-qa/platform-docker)

The [Isagawa Kernel](https://github.com/isagawa-co/isagawa-kernel) is open-source.

---

## AI Execution Management vs AI Governance

| AI Governance (Others) | AI Execution Management (Isagawa) |
|------------------------|-----------------------------------|
| Monitors AI behavior | Controls AI behavior |
| Documents compliance | Enforces compliance |
| Alerts on violations | Prevents violations |
| Audits after execution | Gates during execution |

---

## Services

We build working evals on **YOUR** LLM pipeline in 60 minutes.

**[alain@isagawa.co](mailto:alain@isagawa.co)** | **[DM on LinkedIn](https://www.linkedin.com/in/alain-ignacio-54b9823)**

| Offering | Included | Price |
|----------|----------|-------|
| **Demo** | Live 60-min session | Contact us |
| **Implementation** | Full eval infra + training | USD 15,000 - 50,000 |
| **Retainer** | Ongoing dev + support | USD 1,000 - 3,000/month |
| **Enterprise** | Full + compliance + dedicated | Custom (50K+) |

---

## License

Proprietary -- isagawa-co

---

Built with the [Isagawa Kernel](https://github.com/isagawa-co/isagawa-kernel) -- self-building, self-improving, safety-first.
