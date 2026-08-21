# Luban Workflow

## Authority

Luban schema workbooks, data workbooks, and configuration under `Tools/Luban/DataTables/` are source inputs. Generated C# and JSON are derived outputs. Never edit derived outputs directly.

## Target-project discovery

Before defining a config change:

1. Read the target project's `Assets/Game/Scripts/Editor/LubanGenerator.cs` and nearby documentation.
2. Inspect existing tables that are closest to the required data shape.
3. Determine whether the project uses a flat `Datas/` layout or discovered module directories.
4. Identify how nearby source workbooks are named and grouped for human authors.
5. Record source path, workbook naming convention, table/bean identity, primary key, mode, consumers, and generated output ownership in MDD.

The inspected seed generator supports both flat and modular layouts. This is current evidence, not permission to assume every July project kept that implementation unchanged.

## Workbook naming

Calibrate workbook names before creating or renaming them. Apply evidence in this order: explicit user direction, a user-designated reference project, established neighboring workbooks in the target project, then the workflow default. A default must not override a clear repository convention.

When the project uses bilingual workbook names and no stronger convention exists, use `<中文业务分类>_<Luban英文类型名>.xlsx`:

- The Chinese prefix exists for human scanning and grouping. Use the narrow business concept represented by the table, such as `摊位`, `摊位等级`, or `每日题目`.
- Do not prepend the same product name, project name, or broad gameplay label to every workbook. A shared prefix that does not distinguish tables defeats its purpose.
- Keep the English type name aligned with the identity referenced by `__tables__.xlsx`; do not invent a second English alias only for the filename.
- Preserve Luban meta workbook names such as `__tables__.xlsx`, `__beans__.xlsx`, and `__enums__.xlsx`.

When a source workbook is renamed, update `__tables__.xlsx` and every maintained source reference in the same change. Treat successful full generation as the validation that the new path is authoritative.

## Generation timing and ownership

- Do not create a table merely because a noun appears in GDD or a future View may need display data.
- During the module stage, create a table only when a stable project capability owns its interpretation and the current scope requires that schema. A configuration-only capability does not need product wrapper code, but its MDD must identify direct consumers and verification evidence.
- Leave fields whose meaning depends on later player-function integration until that integration is designed. Add presentation-only resources during the View stage.
- Do not collect unrelated configuration into a broad `Content` module or give every workbook the same project/gameplay prefix.
- When the schema is still speculative, record the open question in the selected MDD and stop instead of generating a workbook, C#, JSON, or diagnostic sidecar.

## Generated types and product code

- Treat generated enums, beans, and `Tb*` tables as the typed configuration contract. Product consumers should use them directly when doing so preserves the intended business semantics.
- Do not create a product type only to hold the same fields, rename generated properties, forward lookups, or rescan table completeness. Such a type is justified only when it owns independent behavior, runtime state, lifecycle, caching, mutation, or an error contract that the generated configuration cannot express.
- If a calculation also needs board layout, customers, process state, or another future consumer-owned fact, leave it to the module that owns those facts or to the later integration. Do not introduce a partial calculator with placeholder or compressed boolean inputs merely to give the configuration module runtime code.

## Configuration value placement

- Put record-specific values in the table whose record owns their meaning.
- Put a project-wide, designer-tunable scalar in the project's established misc/singleton configuration shape when no narrower table owns it. Do not use a misc table as a container for unrelated values.
- Do not author table row counts, enum item counts, coverage counts, or other values derivable from the source data as duplicate constants.
- Keep a value in product code only when it is an algorithm, protocol, format, or framework invariant rather than authorable game content.

## Editing and generation

- Use the project's approved workbook tooling. If a helper script exists, use it rather than inventing a new writer.
- Meta workbooks such as `__tables__.xlsx`, `__beans__.xlsx`, and `__enums__.xlsx` have special formats. Copying an established project pattern is safer than treating them as ordinary data sheets.
- When a closed value set is consumed by both tables and product code, define it once in the applicable `__enums__.xlsx`, declare table columns with that enum type, author values with enum item aliases when that improves readability, and consume Luban's generated enum in code. Do not maintain a duplicate handwritten enum.
- Invoke the project's full generation entrypoint. In the inspected seed this is `JulyGF/配置表/生成全部`.
- After generation, inspect console errors and verify representative generated data/code consumed by the target module.

## Tool artifact boundary

Workbook inspection and conversion tools must write scratch outputs to an isolated temporary directory, not beside authoring workbooks. Files such as `*.inspect.ndjson`, rendered previews, scratch workbook copies, and generation logs are diagnostic artifacts, not project deliverables.

Before reporting completion, search the Luban authoring directory and the repository working tree for tool-created residue. Remove only artifacts created by the current workflow, preserve unrelated pre-existing files, and verify that no diagnostic sidecar was left in the delivered source directories.

## Failure behavior

Malformed external data should fail at generation or load validation with a precise error. Prefer expressing authoring constraints in Luban schema/generation when supported. Product code must not repeat generated field-type checks, key uniqueness, enum validity, table cardinality, or coverage scans merely because the data originated outside the process; add runtime validation only for a real condition not already established by generation/load and state the required business response. Do not add runtime defaults merely to mask a broken authoring table. Runtime fallback is justified only when the GDD explicitly permits a recoverable business state and defines the observable degraded behavior.
