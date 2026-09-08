---
name: agent-architecture-audit
description: Audit agent system architectures, LLM pipelines, prompt wrapper layers, tool loop boundaries, and context propagation. Use when an agent application exhibits regressions, tool calling failures, context pollution, or infinite repair loops. Not for code-level defensive security or secrets auditing (full-audit-keamanan), web UI (impeccable), or ordinary application bugs (diagnosing-bugs).
compatibility: opencode
license: MIT
---

# Agent Architecture Audit

Diagnostic specialist for LLM application architectures, autonomous agent loops, prompt orchestration wrappers, and tool execution boundaries.

This skill isolates failures in compound AI systems where errors are obscured behind multi-tier wrappers, bloated context windows, recursive retry loops, or degraded tool dispatching.

## Boundaries & Handoffs

| Need | Route |
|---|---|
| Defensive security, secrets scanning, prompt injection attack defense, auth | `full-audit-keamanan` |
| Reproducing ordinary application code defects with red-green tests | `diagnosing-bugs` |
| Measuring agent accuracy, pass@k, and prompt benchmark regressions | `eval-harness` |
| Designing cost-optimized model tiering, token budgets, and prompt caching | `cost-aware-llm-pipeline` |
| Authoring or editing SKILL.md, AGENTS.md, or agent configuration files | `writing-for-agents` |
| **Systematic architectural diagnosis of agent pipelines and failure modes** | **`agent-architecture-audit`** |

## Audit Dimensions

Review [references/layers.md](references/layers.md) for detailed checklists across the primary diagnostic planes:

1. **Wrapper & Transport Layer:**
   - Detect proxy regressions, middleware mutations of tool payloads, and loss of raw error signals.
   - Verify that streaming chunks do not truncate tool argument JSON.

2. **Context & Token Discipline:**
   - Detect runaway conversation history, repeated duplicate system prompts, and memory leaks across turns.
   - Ensure explicit compaction points and sliding context windows with clear eviction policies.

3. **Tool Dispatch & Boundary Discipline:**
   - Verify tool parameter schema conformance, strict types, and robust JSON decoding.
   - Detect tool hallucination, redundant repetitive tool invocations, and missing validation gates.

4. **State Machine & Loop Termination:**
   - Guard every recursive or autonomous repair loop with hard iteration ceilings.
   - Ensure fail-closed terminal states so runaway retries abort cleanly before token exhaustion.

5. **Error Propagation & Recovery:**
   - Verify that tool execution failures return structured, actionable feedback to the model rather than generic exception strings.
   - Distinguish transient infrastructure faults from model reasoning deadlocks.

## Diagnostic Output Format

Produce findings structured by severity:

```markdown
### [CRITICAL | HIGH | MEDIUM | LOW] Layer: <Layer Name>
- **Symptom:** Observed failure or degradation pattern.
- **Root Cause:** Architectural seam or mechanism producing the failure.
- **Evidence:** Concrete log trace, payload snippet, or code location.
- **Remediation:** Code-first architectural fix (e.g. adding hard loop guards, pruning context, schema correction).
```
