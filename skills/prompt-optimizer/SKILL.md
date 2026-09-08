---
name: prompt-optimizer
description: Analyze, critique, and optimize system prompts, task instructions, and agent framing. Enhances structural clarity, edge-case handling, negative constraints, and output schema adherence without executing the underlying task. Advisory only; does not mutate installed skills. Use when refining prompt text, reducing ambiguity, or fixing prompt drift. Not for ordinary coding tasks, prose humanizing (humanizer), or writing agent documentation (writing-for-agents).
compatibility: opencode
license: MIT
---

# Prompt Optimizer

Advisory specialist for analyzing, critiquing, and optimizing prompt engineering artifacts.

This skill reviews draft prompts, user task instructions, and system directives to maximize clarity, predictability, model steering, and constraint adherence.

## Operating Principles

- **Advisory Role Only:** Never execute the task described within the prompt; focus exclusively on analyzing and refining the prompt itself.
- **Zero Auto-Mutation:** This skill does NOT automatically overwrite installed skills or configuration files in `~/.config/opencode/`. It produces recommended prompt text for the user to review and adopt.

## Boundaries & Handoffs

| Need | Route |
|---|---|
| Removing AI-writing tells and polishing natural prose | `humanizer` / `/unslop` |
| Authoring or modifying project SKILL.md, AGENTS.md, or tool definitions | `writing-for-agents` |
| Measuring prompt accuracy across test datasets and computing pass@k | `eval-harness` |
| Structuring system prompts for prefix caching efficiency | `cost-aware-llm-pipeline` |
| **Analyzing and optimizing prompt clarity, constraints, and schemas** | **`prompt-optimizer`** |

## Optimization Framework

Consult [references/rubric.md](references/rubric.md) for quality evaluation criteria:

1. **Role & Objective Framing:**
   - Establish an unambiguous persona and primary mission.
   - Clarify the operational context and assumptions.

2. **Context & Variable Delimiters:**
   - Use clear XML-style tags or markdown blocks (`<context>`, `<input>`, `<instructions>`) to fence user inputs and prevent injection or ambiguity.

3. **Step-by-Step Procedure:**
   - Deconstruct complex tasks into numbered, deterministic phases.
   - Mandate pre-flight checks before destructive actions.

4. **Negative Constraints & Guardrails:**
   - Replace vague warnings ("be careful") with explicit prohibitions ("Do NOT call tool X before tool Y completes").
   - Define fallback behavior when required information is absent.

5. **Output Schema & Format Locks:**
   - Specify exact output formatting (e.g. JSON schema, table columns, markdown headings).
   - Provide minimal, clean few-shot exemplars demonstrating target format.
