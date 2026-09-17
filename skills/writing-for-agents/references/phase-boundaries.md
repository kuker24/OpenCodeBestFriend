# Phase Boundaries

A **phase** is a chunk of work inside a session — the planning interview, the implementation, the QA. A phase ends when the current objective completes.

The **phase boundary** is the gap between two phases, and it is the only place this transition decision belongs. Mid-phase there is no decision to make — continue, or split the work that's left into subagents. Compacting mid-phase causes loss of execution context.

## The Five Options

| Option | What it does |
|---|---|
| **Continue** | Stay in the session. No context switch at all. |
| **`/clear`** | Empty the context window and start from zero. |
| **`/handoff`** | Write a portable markdown file and seed a session anywhere with it. |
| **Subagent** | Send the task to its own context window and get a report back. |
| **`/compact`** | Compress this context and seed a fresh session with the summary. |

## The Decision Tree

Work top to bottom at the boundary. The first **yes** wins:

1. **Can you continue in this session?**
   Two signals make the answer yes: the next phase needs this phase as a **primary source**, or you have enough token budget left (~150k tokens) for the next phase to fit. Planning interview → implementation is the standard yes: implementation requires verbatim reasoning, not a lossy summary. Continue costs nothing and loses nothing.
2. **Is the context irrelevant to what comes next?**
   If exploration, decisions, and dead ends are disposable, use `/clear`.
3. **Do you need to hand off?**
   Only when swapping harnesses, moving repositories, handing off to a colleague, or forking an isolated side task.
4. **Can the task be done AFK?**
   If scoped tightly enough to run without human steering, dispatch a subagent.
5. **Otherwise, `/compact`.**
   Pass an explicit instruction so the summary preserves the exact decisions and open questions the next phase requires.

## Primary vs Secondary Sources

Every transition except **Continue** converts a **primary source** into a **secondary source**:

| Source | Information | Noise | Room to move |
|---|---|---|---|
| Primary (Continue) | Full | Higher | Less |
| Secondary (`/compact`, `/handoff`) | Lossy | Lower | More |
