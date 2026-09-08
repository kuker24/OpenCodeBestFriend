# Diagram Archetypes Catalog (39 Types)

Structural blueprints, layout grammars, and when-to-use criteria for editorial technical diagrams.

## I. Architecture & Systems

1. **`architecture` (High-Level System Overview)**
   - *When to use:* Microservice topologies, client-gateway-backend maps, infrastructure boundaries.
   - *Grammar:* Subsystem bounding cards, solid strokes for internal services, dashed for third-party systems.

2. **`high-level` (Executive Architecture)**
   - *When to use:* High-altitude system abstractions for cross-functional stakeholders.
   - *Grammar:* Simplified node shapes, minimal arrows, high semantic color grouping.

3. **`layers` (N-Tier Stack Architecture)**
   - *When to use:* Platform layers (Presentation, API Gateway, Application, Data Storage, Infrastructure).
   - *Grammar:* Horizontal stacked slabs with vertical cross-layer communication pipes.

4. **`nested` (Encapsulated Subsystems)**
   - *When to use:* Cluster architectures (VPC -> Subnets -> Nodes -> Pods/Containers).
   - *Grammar:* Concentric or hierarchical enclosing rounded cards with breadcrumb headers.

5. **`deployment` (Physical & Cloud Deployment)**
   - *When to use:* Kubernetes clusters, multi-region AWS/GCP topology, CDN edge distributions.
   - *Grammar:* Host hardware/VM containers enclosing service processes with network ports.

6. **`medallion` (Data Lake Architecture)**
   - *When to use:* Data lakehouse progression (Bronze raw -> Silver refined -> Gold aggregate).
   - *Grammar:* Three progressive horizontal columns with filtration quality gates.

7. **`dp-integration` (Data Product Integration)**
   - *When to use:* Inter-team data mesh contracts and sharing interfaces.
   - *Grammar:* Domain boundary cards connected via contract-specified endpoints.

8. **`dp-security-matrix` (Security & Data Governance)**
   - *When to use:* Access tier mappings, data sensitivity zones (PII, Confidential, Public).
   - *Grammar:* 2D matrix or overlay fences marking compliance perimeters.

## II. Protocols, Sequence & Flow

9. **`sequence` (UML Protocol / Lifeline Sequence)**
   - *When to use:* Auth handshakes (OAuth, mTLS), distributed RPC calls, order checkout flows.
   - *Grammar:* Vertical participant lifelines, numbered horizontal message arrows, activation boxes.

10. **`flowchart` (Algorithmic Logic Flow)**
    - *When to use:* Conditional logic, business decision rules, execution branches.
    - *Grammar:* Rounded action rectangles, decision diamonds with `Yes`/`No` paths, terminal capsules.

11. **`data-flow` (Data Flow / Pipeline Graph)**
    - *When to use:* ETL pipelines, stream processing (Kafka -> Flink -> S3), event buses.
    - *Grammar:* Data source disks, transformation stages, and directed stream queues.

12. **`loop` (Cyclic Feedback / Control Loop)**
    - *When to use:* CI/CD loops, autonomous feedback loops, reconciliation controllers (Kubelet).
    - *Grammar:* Circular or rounded racetrack directed flows with cycle phase markers.

13. **`process` (Linear Multi-Step Process)**
    - *When to use:* Standard operating procedures, deployment release phases, user onboarding.
    - *Grammar:* Numbered sequential chevron or card chains with milestone milestones.

14. **`swimlane` (Cross-Functional Process Flow)**
    - *When to use:* Workflows crossing actor boundaries (Customer, Frontend, Payment Gateway, Database).
    - *Grammar:* Horizontal or vertical lane partitions with cross-lane handoff arrows.

15. **`journey` (User Experience Journey)**
    - *When to use:* Customer journey mapping, touchpoint sentiment, drop-off phases.
    - *Grammar:* Phase columns tracking user actions, touchpoints, emotions, and pain points.

## III. Data Modeling & State

16. **`er` (Entity-Relationship Diagram)**
    - *When to use:* Relational database models, primary/foreign key connections.
    - *Grammar:* Entity cards with column lists (`PK`, `FK`), cardinalities (1:1, 1:N, M:N).

17. **`db-schema` (Physical Database Schema)**
    - *When to use:* Detailed physical tables, SQL types, index structures, constraints.
    - *Grammar:* Strict tabular cards with exact types (`UUID`, `VARCHAR`, `TIMESTAMPTZ`).

18. **`uml-class` (Object-Oriented Class Hierarchy)**
    - *When to use:* Domain model classes, inheritance, composition, interfaces.
    - *Grammar:* Three-compartment cards (Name, Attributes, Methods) with standard UML arrows.

19. **`state` (State Machine Diagram)**
    - *When to use:* Finite state automata, order lifecycles, connection status transitions.
    - *Grammar:* Rounded state bubbles, initial black circle, final bullseye, event guards `[guard]`.

20. **`it-state` (IT System State Transition)**
    - *When to use:* Migration state transitions (Current State -> Transition Phase -> Target State).
    - *Grammar:* Side-by-side or stacked architectural delta comparisons.

## IV. Organization, Hierarchy & Planning

21. **`tree` (Hierarchical Node Tree)**
    - *When to use:* Directory structures, AST trees, taxonomy classifications.
    - *Grammar:* Root node branching down or right into parent-child edge connections.

22. **`org-chart` (Organizational Hierarchy)**
    - *When to use:* Team structure, reporting lines, squad ownership areas.
    - *Grammar:* Leadership cards at top cascading down through departmental tiers.

23. **`gantt` (Project Timeline / Schedule)**
    - *When to use:* Multi-track project delivery, sprint schedules, resource roadmaps.
    - *Grammar:* Time axis across top, horizontal phase bars with milestone diamonds.

24. **`timeline` (Chronological Milestones)**
    - *When to use:* Incident postmortems, product history, release chronologies.
    - *Grammar:* Central spine line with alternating left/right milestone cards.

25. **`kanban` (Workflow Stage Board)**
    - *When to use:* WIP limit tracking, stage progression (Backlog, In Progress, Review, Done).
    - *Grammar:* Vertical stage columns with prioritized task cards.

26. **`story-map` (Agile User Story Map)**
    - *When to use:* Release slicing, user narrative backbone vs backlog depth.
    - *Grammar:* Horizontal user backbone activities with vertical priority story slices.

27. **`wardley` (Wardley Value Chain Map)**
    - *When to use:* Strategic technology evolution, build-vs-buy decisions, market dynamics.
    - *Grammar:* Y-axis (User Visibility / Value Chain), X-axis (Genesis -> Custom -> Product -> Commodity).

28. **`pyramid` (Hierarchical Priority Pyramid)**
    - *When to use:* Testing pyramid (Unit -> Integration -> E2E), Maslow hierarchies.
    - *Grammar:* Layered triangle with proportional horizontal tiers.

29. **`fishbone` (Ishikawa Cause-and-Effect)**
    - *When to use:* Incident root cause analysis, defect categorization.
    - *Grammar:* Central spine to defect head, angled ribs for categories (People, Process, Tech).

30. **`dependency` (Component Dependency Graph)**
    - *When to use:* Package dependencies, circular import analysis, build DAGs.
    - *Grammar:* Node graph with directional dependency arrows and cluster rings.

## V. Quantitative, Matrix & Analytical

31. **`quadrant` (2x2 Decision Matrix)**
    - *When to use:* Effort vs Impact, Risk vs Value, Gartner-style evaluations.
    - *Grammar:* 4 equal quadrants divided by central crosshairs, labeled axes.

32. **`radar` (Spider / Polar Capability Chart)**
    - *When to use:* Multi-attribute comparisons, team skill matrices, benchmark facets.
    - *Grammar:* Radial spokes from center with polygon overlay polygons.

33. **`sankey` (Flow Distribution / Funnel)**
    - *When to use:* Cost flow allocations, user drop-off funnels, traffic distribution.
    - *Grammar:* Curved ribbons between stages with widths mapped to proportional values.

34. **`bar` (Editorial Bar Chart)**
    - *When to use:* Discrete category metric comparisons, benchmark rankings.
    - *Grammar:* Horizontal or vertical crisp bars with direct numeric labels (no chart junk).

35. **`line` (Trend / Time Series Line)**
    - *When to use:* Latency trends, memory usage over time, growth metrics.
    - *Grammar:* Minimalist grid lines, crisp stroke line, highlighted inflection points.

36. **`scatter` (Correlation Scatter Plot)**
    - *When to use:* Cost vs performance correlation, latency percentile distributions.
    - *Grammar:* Two orthogonal axes with plotted point dots and trend line.

37. **`treemap` (Proportional Hierarchical Squares)**
    - *When to use:* Disk space usage, bundle size breakdown, budget breakdown.
    - *Grammar:* Nested rectangles whose areas are proportional to represented quantities.

38. **`venn` (Set Overlap Diagram)**
    - *When to use:* Conceptual intersections, multi-discipline overlaps (2 or 3 sets).
    - *Grammar:* Overlapping translucent circles with clear zone labels.

39. **`polar` (Cyclic / Angle-Based Distribution)**
    - *When to use:* Periodic cyclic data, directional distributions, angular spreads.
    - *Grammar:* Concentric rings with angular sector wedges.
