# July AI Workflow

An explicit-invocation Codex plugin for designing and implementing existing July Framework + Luban Unity products.

The workflow has only two actions:

```text
$july-game-pipeline 完成当前版本的完整项目设计
$july-game-pipeline 按 Design/Docs/MDD/Modules/M003_商品.md 实施
```

The first action discusses unresolved structural decisions, then produces one complete design set before any product code:

```text
Design/Docs/
├── 策划案.md
├── GDD.md
└── MDD/
    ├── 索引.md
    ├── Modules/
    └── Views/
```

`索引.md` owns scope coverage, business-fact ownership, module boundaries, acyclic dependencies, the full View inventory, and recommended implementation waves. Module and View MDDs contain concrete data sketches, public interfaces, pseudocode, configuration contracts, exact file whitelists, and acceptance paths so design problems can be found before generation.

The second action implements exactly the MDD named by the user. It cannot invent extra product files or silently alter the approved role, ownership, interface, dependency, configuration, or View contracts. When implementation reveals a design change, the workflow stops for discussion and updates the design first.

The workflow deliberately excludes progress metadata, extra document categories outside Modules and Views, persistence design, target-project test code, automatic next-item selection, and dependencies outside the current product.

## Repository layout

```text
.agents/plugins/marketplace.json
plugins/july-ai-workflow/
├── .codex-plugin/plugin.json
└── skills/july-game-pipeline/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
docs/architecture.md
```

See [docs/architecture.md](docs/architecture.md) for the maintained design.

## Installation

Add this repository as a Codex Marketplace source and install `july-ai-workflow`. Source changes do not modify an installed cache automatically; refresh installation only when explicitly desired.
