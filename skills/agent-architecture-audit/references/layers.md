# Agent Architecture Inspection Layers

Diagnostic reference for auditing compound agent systems across structural tiers.

## 1. System Prompt & Instruction Hierarchy
- **Clarity of Role:** Is the primary directive unambiguous and distinct from subordinate instructions?
- **Negative Constraints:** Are boundaries stated as explicit negatives ("Do NOT invoke X without Y")?
- **Instruction Drift:** Do runtime variable injections override core behavioral fences?

## 2. Tool Definition & Schema Integrity
- **Parameter Precision:** Are arguments strictly typed (enums, explicit strings, numbers) rather than freeform catch-all objects?
- **Description Quality:** Do tool descriptions explicitly specify preconditions, expected side effects, and when NOT to call the tool?
- **Payload Size:** Are return values truncated safely to prevent context blowout?

## 3. Context & Memory Management
- **Token Budget:** Does the system measure context utilization before injecting large file or trace contents?
- **History Pruning:** Is conversation history pruned or summarized before reaching model limits?
- **Idempotent State:** Does the agent maintain a clean external state representation rather than relying purely on model recollection?

## 4. Execution Loop & Convergence
- **Iteration Ceiling:** Is there an enforced hard maximum on loop iterations (e.g. max 10 steps per task)?
- **Progress Verification:** Does the loop verify measurable progress between steps, aborting if the same action repeats without state change?
- **Exit Criteria:** Are completion conditions unambiguously evaluated by objective checks rather than self-attested claims?

## 5. Failure Handling & Resilience
- **Structured Error Feedback:** Do failed tool executions return actionable diagnostic objects?
- **Fallback Pathways:** Does the system degrade gracefully (e.g. falling back to simpler deterministic tools) when an agentic path deadlocks?
