# Eval-Driven Development (EDD) Methodology

Operational principles and rubric structures for LLM evaluations.

## 1. The EDD Loop

1. **Specify:** Define task requirements and concrete failure definitions before touching prompts.
2. **Collect:** Gather minimum 20-50 high-diversity test cases (inputs + expected output properties).
3. **Baseline:** Run the test suite against the initial setup and record score `S_0`.
4. **Iterate:** Modify prompt instructions, tool schemas, or examples.
5. **Evaluate:** Re-run suite to calculate score `S_1`. Ensure `S_1 >= S_0` with zero regressions on gold cases.

## 2. Assertion Types & Hierarchy

Always prefer lower-tier assertions when possible:

- **Tier 1 (Deterministic String/Regex):** Verify presence of required keywords, absence of forbidden patterns, or format compliance.
- **Tier 2 (Syntactic/Structural):** Validate JSON schema conformance, Python syntax correctness, or HTML well-formedness.
- **Tier 3 (Functional Execution):** Execute generated code in a sandbox or run tests against the output.
- **Tier 4 (Model-Graded Rubric):** Use an isolated LLM evaluator with an unambiguous scoring rubric.

## 3. Designing Model-Graded Rubrics

Avoid subjective rating scales. Use criteria with concrete binary anchors:

```text
[Criterion: Accuracy of Recommendation]
PASS (1): The response recommends an approach that satisfies all stated constraints in the input prompt.
FAIL (0): The response omits a mandatory constraint or suggests an invalid option.

[Criterion: Negative Constraint Adherence]
PASS (1): The response contains zero forbidden packages or methods.
FAIL (0): The response includes one or more forbidden packages.
```
