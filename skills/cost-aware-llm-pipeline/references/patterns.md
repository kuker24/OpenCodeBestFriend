# Cost-Aware LLM Implementation Patterns

Concrete architectural formulas and recipes for token discipline and budget control.

## 1. Static Prefix Cache Optimization

Structure request payloads so the cacheable prefix remains identical across calls:

```text
[STATIC PREFIX - Cached]
├── Core System Instructions (Identical for all sessions)
├── Global Style & Policy Directives
└── Static Tool Definitions & Output JSON Schemas

[DYNAMIC SUFFIX - Ephemeral]
├── Project-Specific Delta Context
├── Most Recent Conversation Window (Pruned)
└── Current User Request
```

*Cache Break Prevention:* Never inject dynamic timestamps, randomized session UUIDs, or rotating nonces into the system prompt prefix.

## 2. Dynamic Model Routing Gate

Heuristic scoring to assign queries to the most cost-effective model tier:

```python
def select_model_tier(query: str, context_len: int) -> str:
    # Quick deterministic fast-path for lightweight tasks
    if len(query) < 120 and not any(k in query.lower() for k in ["architect", "audit", "refactor", "security"]):
        return "tier-1-fast"
    
    # Moderate tasks with bounded context
    if context_len < 16_000 and "explain" in query.lower():
        return "tier-2-balanced"
    
    # Complex multi-step reasoning
    return "tier-3-frontier"
```

## 3. Token Budget Circuit Breakers

Define hard ceiling limits per workflow:

- **Single Turn Max:** Cap `max_tokens` (e.g. 2,048 tokens unless streaming large files).
- **Session Budget:** If cumulative cost exceeds configured budget (e.g. $1.50 per task), halt execution and request user approval before continuing.
- **Compaction Threshold:** Trigger semantic history summarization when conversation history reaches 50% of the maximum window.
