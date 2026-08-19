# Stage: GDD

Use [../../assets/templates/GDD.md](../../assets/templates/GDD.md). For a deliberately small validation product with one core mechanic and no complex progression, use [../../assets/templates/GDD_LITE.md](../../assets/templates/GDD_LITE.md).

## Outcome

Produce the complete player-facing behavior contract from `策划案.md`.

## Work

1. Read `策划案.md` and its open-decision section.
2. Choose full or lite organization based on actual product complexity, not desired document length.
3. Specify core loop, rules, interaction, state transitions, progression/content generation, data concepts, UI/UX, feedback, persistence, failure recovery, localization, analytics intent, and acceptance scenarios.
4. Cross-check every plan goal and constraint against at least one GDD section.
5. Keep the document implementation-free. Describe observable behavior instead of July calls or file structure.
6. Write `GDD.md` in `DesignDoc/<项目名>/`, versioned from `策划案.md`.
7. Complete the Stage only when no blocking `[待确认]` remains.

The next Stage is always GDD review. Do not generate MDD in the same unreviewed step.
