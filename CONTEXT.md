# July AI Workflow language

This glossary keeps product facts, design artifacts, JulyArch roles, and implementation tasks distinct.

**策划案**
The user's product intent and raw requirements. It may be incomplete or ambiguous and must be discussed before technical design.

**GDD**
The current-version product contract: player goals, concepts, rules, complete player flows, visible results, allowed failures, scope, and explicitly deferred nonstructural content. It contains no class names, source directories, July roles, or configuration schemas.

**业务事实**
A fact with exactly one authority. It may be authored configuration, controlled runtime data, a framework-provided value, or a value derived from other authoritative facts.

**业务模块**
A stable, independently nameable product capability. A module owns the runtime state, rules, operations, and authored data needed for that capability. It is not a technical layer, screen step, table collection, or wrapper around generated types.

**View**
A player-visible screen or visual feature. UI Windows and world/scene Views are documented by visual responsibility, without creating separate technical documentation hierarchies.

**索引**
`Design/Docs/MDD/索引.md`, the complete technical map. It records scope coverage, fact ownership, canonical action contracts, product-symbol providers, the complete Module/View dependency graph, MDD links, closure proofs, and the exact topological implementation order. The order does not authorize automatic continuation.

**模块 MDD**
The full implementation contract for one business module: responsibility, facts, roles, data structures, interfaces, algorithms, dependencies, consumers, invariants, configuration, registration, exact file whitelist, and acceptance.

**View MDD**
The full implementation and production contract for one screen or visual feature: visible facts, interactions, Data design, partial refreshes, empty notification events, navigation, Prefab/scene wiring, exact file whitelist, and acceptance.

**Store**
The authoritative owner of controlled runtime business state. Reads are public; mutations are restricted to the owning module's Systems/Procedures. It publishes an empty business event only after a consistent mutation completes.

**System**
A stable runtime capability managed or located through `ArchContext`. It may be simple and may have only one current consumer. It exposes meaningful business operations and may directly complete simple synchronous behavior or start a Procedure.

**Procedure**
One bounded operation, especially a multistep, asynchronous, cancellable, or commit-oriented use case. Windows do not construct or run Procedures directly.

**ordinary type**
A C# type that owns a real algorithm, invariant, or value semantic without needing JulyArch lifecycle or runtime location.

**Luban generated type**
The direct typed contract for static authored facts. A handwritten mirror, definition wrapper, alias enum, or lookup forwarder is not a separate product role.

**WindowData**
Mutable presentation data owned by a Window for its open lifetime. Its constructor obtains complete initial presentation facts through only the required July query interfaces. Targeted refresh methods re-read only the affected facts. It is writable so editor/GM tooling can create representative display data directly.

**empty business event**
A notification that a named business fact changed. It carries no display data. A receiving Window calls the matching WindowData refresh method and then redraws the affected visual region.

**file whitelist**
The complete list of product files an MDD may create or modify. Any additional file or design change requires discussion and an MDD update before implementation continues.

**action contract**
The single authoritative row for one atomic player action: ID, owner, canonical signature, precondition, success/failure, and navigation owner. Every Module/View occurrence references it exactly.

**product symbol provider**
The one MDD that creates a handwritten type/member/event, Luban generated type, Window/Data, Prefab script, resource contract, or registration item used by other MDDs.

**MDD implementation closure**
The guarantee that one MDD can be implemented, compiled, and accepted using only the stable host, fixed package APIs, its own whitelist, and outputs from earlier MDDs in the global topological order.
