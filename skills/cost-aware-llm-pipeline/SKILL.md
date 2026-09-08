---
name: cost-aware-llm-pipeline
description: Design and optimize cost-efficient LLM application architectures. Covers model tiering, task complexity routing, prompt caching strategies, token budget fences, and retry backoff. Use when reducing API spend, establishing token budgets, or architecting multi-model fallback cascades. Not for client runtime latency/bundle audits (full-performance-audit) or prompt phrasing refinement (prompt-optimizer).
compatibility: opencode
license: MIT
---

# Cost-Aware LLM Pipeline

Specialist for architecting cost-disciplined LLM applications and API integrations.

This skill balances output quality against token expenditure using complexity-based model routing, aggressive prompt caching, token budget ceilings, and graceful degradation cascades.

## Boundaries & Handoffs

| Need | Route |
|---|---|
| Application bundle size, page latency, web vitals, database query profiling | `full-performance-audit` |
| Refining individual prompt wording, instructions, or negative constraints | `prompt-optimizer` |
| Benchmarking accuracy tradeoffs across cheaper models or prompt versions | `eval-harness` |
| Investigating failure loops or context pollution in an agent loop | `agent-architecture-audit` |
| **Engineering cost-optimized LLM architectures, routing, and token budgets** | **`cost-aware-llm-pipeline`** |

## Core Patterns

Consult [references/patterns.md](references/patterns.md) for concrete implementation patterns:

1. **Complexity-Based Model Tiering:**
   - **Tier 1 (Fast/Cheap):** Simple classification, routing, entity extraction, straightforward summarization, unit-test parsing.
   - **Tier 2 (Balanced):** Standard code generation, multi-file refactoring, initial technical writing, triage.
   - **Tier 3 (Frontier Reasoning):** Architectural synthesis, deep multi-hop debugging, security threat modeling, formal verification.
   - *Rule:* Always route to the lowest sufficient tier; escalate only on detected ambiguity or failed evaluation checks.

2. **Prompt Caching Structure:**
   - Organize prompts with invariant static prefixes (system instructions, tool definitions, reference schemas) at the top to maximize prefix-cache hits.
   - Place volatile per-request dynamic data, user queries, and timestamps strictly at the end of the prompt buffer.

3. **Token Budget Fences:**
   - Establish hard limits on max completion tokens per turn.
   - Enforce sliding context compaction thresholds (e.g. compact conversation at 60% of window capacity rather than overflowing at 95%).

4. **Retry Backoff & Fallback Cascades:**
   - Implement exponential backoff with full jitter for rate limits (`429`) and server errors (`5xx`).
   - Cascade down to smaller models or cached responses when upstream limits are encountered.

5. **Cost Telemetry:**
   - Log input tokens, output tokens, cache-read tokens, and calculated cost per transaction.
   - Set automated circuit breakers that halt autonomous loops when a cost threshold is exceeded.
