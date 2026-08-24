# July AI Workflow

An explicit-invocation Codex plugin for designing and implementing existing July Framework + Luban Unity products.

The workflow has only two actions:

```text
$july-game-pipeline 完成当前版本的完整项目设计
$july-game-pipeline 按 Design/Docs/MDD/Modules/M003_商品.md 实施
```

The first action discusses unresolved structural decisions without writing project files. It then builds a machine-readable contract and the complete design set in an OS temporary staging directory:

```text
Design/Docs/
├── 策划案.md
├── GDD.md
└── MDD/
    ├── 索引.md
    ├── Modules/
    └── Views/
```

`索引.md` owns scope coverage, business-fact ownership, one canonical contract per atomic player action, one provider per cross-MDD product symbol, the full Module/View dependency graph, and its topological implementation order. Every MDD must be independently compilable and acceptable using only earlier outputs. Module and View MDDs contain concrete data sketches, public interfaces, pseudocode, configuration contracts, exact file whitelists, closure proofs, and acceptance paths.

The staging contract is embedded into the index and each MDD. An ephemeral stage binding prevents publishing a design generated for another workspace or an obsolete planning input. A plugin-side standard-library validator rejects incomplete file sets, duplicate contracts/providers/file creators, forward dependencies, unsupported dependency edges, missing or hollow sections, prose/contract drift, placeholders, tooling disguised as product modules, persistence plans, and target test files. MDDs are generated in bounded batches in staging only. A full validation pass is required before a transactional publisher replaces the product's GDD/MDD set; interrupted generation leaves the product unchanged.

The second action implements exactly the MDD named by the user after verifying its earlier prerequisites from the index. It cannot invent extra product files or silently alter the approved role, ownership, interface, dependency, configuration, or View contracts. A forward reference or contract conflict is reported as a complete-design defect, not treated as a normal reason to wait for later work.

The workflow deliberately excludes progress metadata, extra document categories outside Modules and Views, persistence integration and save/load behavior, target-project test code, automatic next-item selection, and dependencies outside the current product. The validator's own regression suite is plugin tooling and never writes tests into a target product.

## Repository layout

```text
.agents/plugins/marketplace.json
plugins/july-ai-workflow/
├── .codex-plugin/plugin.json
└── skills/july-game-pipeline/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/
    └── scripts/
        ├── design_artifacts.py
        └── tests/test_design_artifacts.py
docs/architecture.md
```

See [docs/architecture.md](docs/architecture.md) for the maintained design.

## Installation

Add this repository as a Codex Marketplace source and install `july-ai-workflow`. Source changes do not modify an installed cache automatically; refresh installation only when explicitly desired.
