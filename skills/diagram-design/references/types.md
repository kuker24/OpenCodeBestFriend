# Diagram Archetypes

Structural blueprints for primary technical diagrams.

## 1. System Architecture / Context (C4-inspired)
- **Use for:** Microservices, deployment boundaries, client-server interactions.
- **Visual Pattern:** Layered cards with clear subsystem bounding boxes. Use dashed stroke for external third-party services and solid stroke for owned systems.
- **Labels:** Service Name (bold 15px), Protocol/Port (muted 12px mono), One-sentence responsibility.

## 2. Sequence & Protocol Flow
- **Use for:** Auth handshakes, distributed RPC transactions, checkout flows, lifecycle events.
- **Visual Pattern:** Vertical lifelines, horizontal message arrows with explicit step numbers (`1.`, `2.`), synchronous return dashes, activation blocks for processing windows.

## 3. Entity-Relationship & Data Models
- **Use for:** Database schemas, relational tables, domain entity graphs.
- **Visual Pattern:** Tabular cards with clear header (Table Name). Rows split into Column Name, Type, and constraint badges (`PK`, `FK`, `UQ`, `NULL`). Direct Crow's Foot or orthogonal connector lines between keys.

## 4. Flowcharts & Decision Trees
- **Use for:** Business rules, approval workflows, failure triage trees.
- **Visual Pattern:** Rounded rectangles for actions, diamonds for branching decisions, pill capsules for terminals (Start/End). Explicit `Yes`/`No` labels on branch edges.

## 5. State Machines
- **Use for:** Order status, connection states, session transitions.
- **Visual Pattern:** Rounded states with self-loops and directed transitions labeled with trigger events and guard conditions `[guard] / action`.

## 6. Wardley Maps
- **Use for:** Strategic technology evolution, build-vs-buy decisions.
- **Visual Pattern:** Two axes (Y: Value Chain / Visibility, X: Evolution from Genesis to Commodity). Components positioned across stages with dependency linkages.

## 7. Sankey & Data Flow Pipelines
- **Use for:** Resource allocation, funnel drops, event ingestion throughput.
- **Visual Pattern:** Flowing ribbons with widths proportional to volume or throughput metrics.
