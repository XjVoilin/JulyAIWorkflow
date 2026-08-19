# Architecture

## External interface

The repository is a Git-backed marketplace containing one plugin, `july-ai-workflow`. The plugin exposes one explicitly invoked skill, `july-game-pipeline`, and one deterministic command module:

- `flow.py`: resolve `DesignDoc/<product>/` from the current July Unity project, then initialize, inspect, advance, reopen, and validate workflow state.

`.agents/plugins/marketplace.json` is the distribution boundary and maps the marketplace entry to `plugins/july-ai-workflow`. `.codex-plugin/plugin.json` owns the plugin identity and exposes the plugin-local `skills/` directory. Target product repositories do not receive a copied workflow Skill.

Stage instructions, templates, state rules, and project-profile checks remain inside that interface. Deleting this module would force every product repository to rediscover state ordering, evidence rules, artifact formats, July ownership, and Luban generation constraints.

## Stage model

```text
策划案.md（前置输入）
       ↓
gdd → gdd_review → mdd → implementation → validation
 ↑                         |
 └──── reopen on change ───┘
```

Each Stage is completed by `flow.py complete` with project-relative Evidence. The command rejects missing prerequisites, nonexistent evidence, absolute evidence paths, and paths outside the target project.

## Seams

- `.july-ai-workflow.json` is the machine-state interface; `工作流状态.md` is its automatically refreshed human-readable projection.
- The product name and target Unity project are external seams. The name resolves only to `DesignDoc/<product>/`; its existence, required `策划案.md`, project markers, dependencies, and evidence paths are validated there.
- No framework adapter seam exists yet: this repository intentionally supports one Project Profile, standalone July. Add another profile only when a second real target differs.

## Artifact ownership

- `策划案.md` owns confirmed intent and open product decisions.
- GDD owns player-facing behavior.
- GDD review owns the gate decision and issue evidence.
- MDD owns technical decomposition and interfaces.
- Code, Luban source data, tests, and reports own implementation evidence.
- `DesignDoc/<product>/.july-ai-workflow.json` owns Stage state and transition history.
- `工作流状态.md` contains no independent truth and is regenerated after every mutation.
