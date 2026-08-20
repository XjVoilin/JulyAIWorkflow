# Luban Workflow

## Authority

Luban schema workbooks, data workbooks, and configuration under `Tools/Luban/DataTables/` are source inputs. Generated C# and JSON are derived outputs. Never edit derived outputs directly.

## Target-project discovery

Before defining a config change:

1. Read the target project's `Assets/Game/Scripts/Editor/LubanGenerator.cs` and nearby documentation.
2. Inspect existing tables that are closest to the required data shape.
3. Determine whether the project uses a flat `Datas/` layout or discovered module directories.
4. Record source path, table/bean identity, primary key, mode, consumers, and generated output ownership in MDD.

The inspected seed generator supports both flat and modular layouts. This is current evidence, not permission to assume every July project kept that implementation unchanged.

## Editing and generation

- Use the project's approved workbook tooling. If a helper script exists, use it rather than inventing a new writer.
- Meta workbooks such as `__tables__.xlsx`, `__beans__.xlsx`, and `__enums__.xlsx` have special formats. Copying an established project pattern is safer than treating them as ordinary data sheets.
- When a closed value set is consumed by both tables and product code, define it once in the applicable `__enums__.xlsx`, declare table columns with that enum type, author values with enum item aliases when that improves readability, and consume Luban's generated enum in code. Do not maintain a duplicate handwritten enum.
- Invoke the project's full generation entrypoint. In the inspected seed this is `JulyGF/配置表/生成全部`.
- After generation, inspect console errors and verify representative generated data/code consumed by the target module.

## Failure behavior

Malformed external data should fail at generation or load validation with a precise error. Do not add runtime defaults merely to mask a broken authoring table. Runtime fallback is justified only when the GDD explicitly permits a recoverable business state and defines the observable degraded behavior.
