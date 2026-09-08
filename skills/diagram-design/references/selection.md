# Diagram Archetype Selection Guide

How to choose the archetype and scope the complexity budget.

## Decision Matrix

| Question | Recommended Archetype |
|---|---|
| "How do these services communicate?" | System Architecture or Component Diagram |
| "What happens step-by-step during a request?" | Sequence Diagram |
| "How do these data tables relate?" | Entity-Relationship (ER) Diagram |
| "What choices lead to which outcome?" | Decision Tree or Flowchart |
| "What states can this object transition between?" | State Machine |
| "Where are we building custom vs buying commodity?" | Wardley Map |
| "Where is network data or pipeline volume going?" | Sankey or Data Flow Diagram |

## Complexity Budget (The 7±2 Rule)

A diagram that explains everything explains nothing:
- **Maximum visible top-level nodes:** 7 to 9. If a system has 25 services, group them into 3-5 bounded subsystems.
- **Color Palette Budget:** Maximum 3 functional colors (e.g. Primary Navy for core services, Cyan for data stores, Amber for third-party APIs) plus neutral background and border grays.
- **Edge Reduction:** Avoid crossing connector lines. Use orthogonal elbows instead of diagonal spiderwebs.
