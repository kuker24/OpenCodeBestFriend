---
name: eval-harness
description: Evaluation harness and benchmark design for prompts, agents, and LLM workflows. Implements eval-driven development (EDD), test suite generation, pass@k metrics, and regression testing. Use when validating agent behavior, comparing prompt iterations, or establishing objective quality gates for LLM outputs. Not for standard application unit tests (tdd), exploratory browser testing (playwright-qa), or security auditing (full-audit-keamanan).
compatibility: opencode
license: MIT
---

# Eval Harness

Evaluation and benchmark design specialist for LLM workflows, prompts, and agent configurations.

This skill establishes objective quality gates using Eval-Driven Development (EDD). It constructs ground-truth test datasets, defines deterministic and model-graded evaluation rubrics, computes reliability metrics (`pass@1`, `pass@k`), and guards against prompt regression.

## Boundaries & Handoffs

| Need | Route |
|---|---|
| Project code test-driven development (red-green-refactor) | `tdd` |
| Web application exploratory browser testing and UI flows | `playwright-qa` |
| Application build verification profiles (FAST, STANDARD, RELEASE) | `rules/01-verification.md` |
| Deep architectural failure diagnosis across agent layers | `agent-architecture-audit` |
| Auditing cost tradeoffs across model tiers | `cost-aware-llm-pipeline` |
| **Designing benchmarks, evaluation datasets, rubrics, and regression suites** | **`eval-harness`** |

## Core Methodology

Consult [references/methodology.md](references/methodology.md) for detailed scoring criteria and evaluation templates:

1. **Dataset Construction:**
   - Assemble representative input samples covering canonical happy-paths, subtle boundary conditions, and known failure modes.
   - Separate test sets into Development/Calibration and Held-Out Validation to prevent prompt over-fitting.

2. **Grading Assertions:**
   - **Deterministic Assertions (Fast & Objective):** Exact substring matching, regular expressions, JSON schema validation, AST parsing, and status code verification.
   - **Model-Graded Assertions (Semantic Evaluation):** Structured evaluators using clear, blind rubrics with binary or Likert criteria. Avoid generic "rate 1-5" prompts; use explicit pass/fail definitions per grade.

3. **Metrics & Statistical Rigor:**
   - Measure `pass@1` (single run accuracy) and `pass@k` (probability of at least 1 success in `k` trials for stochastic workflows).
   - Track evaluation latency and token costs alongside accuracy scores.

4. **Regression Gate Workflow:**
   - Establish a baseline score on the current stable prompt or agent setup.
   - Run the eval suite on proposed changes and calculate the score delta.
   - Reject any prompt change that introduces regressions on previously passing test cases.
