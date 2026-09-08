# Prompt Evaluation Rubric

Diagnostic criteria for critiquing and enhancing draft prompts.

## 1. Intent Precision (Weight: 25%)
- Is the desired outcome specified concretely?
- Can the model definitively verify whether it satisfied the user request?
- Are edge cases (empty input, invalid formats, partial data) addressed?

## 2. Structural Partitioning (Weight: 20%)
- Are instructions cleanly separated from background context and user input?
- Are delimiters (tags, headers, fences) used consistently?
- Is the reading order logical and progressive?

## 3. Negative Constraint Firmness (Weight: 25%)
- Are prohibitions unambiguous and enforceable?
- Does the prompt anticipate common model failure modes (e.g. sycophancy, premature completion, ungrounded speculation)?
- Are boundaries between permissible and forbidden actions explicit?

## 4. Output Contract (Weight: 20%)
- Is the exact output syntax described (JSON, Markdown, YAML)?
- Are required keys, types, and value constraints enumerated?
- Is there a clear indicator of where preamble/conversational chatter should be omitted?

## 5. Token Economy (Weight: 10%)
- Is redundant or conversational fluff pruned?
- Are long narrative explanations converted into concise structural bullets?
