# July Game Delivery

This context describes the reusable delivery language for turning a game idea into a validated July-based Unity product.

## Language

**Product**:
A game in an already-created July Unity project, owned by one project repository.
_Avoid_: Framework package, feature module

**策划案**:
The user-provided workflow input containing confirmed product intent and unresolved product questions before detailed design.
_Avoid_: Prompt, raw idea, requirements dump

**Design Directory**:
The existing `DesignDoc/<product>/` folder selected from the explicit request by exact or uniquely plausible approximate matching. It contains `策划案.md`, workflow state, and authored design artifacts.
_Avoid_: Full user-supplied path, ambiguous guess, generated project root

**GDD**:
The product truth source describing what the game is, how it behaves, and what the player experiences without implementation details.
_Avoid_: Technical design, code plan

**MDD**:
The technical truth source that decomposes an approved GDD into implementable modules, interfaces, dependencies, and acceptance evidence.
_Avoid_: Task list, code sketch

**Stage**:
One ordered part of product delivery with explicit evidence required for completion.
_Avoid_: Step, phase when referring to workflow state

**Gate**:
A verification decision that prevents a downstream Stage from starting until required evidence passes.
_Avoid_: Checklist, suggestion

**Evidence**:
A project-relative artifact or verification result that supports a Stage transition.
_Avoid_: Confidence, expectation

**Project Profile**:
The verified technology and composition constraints of a target July project.
_Avoid_: Host capabilities when referring to the whole project

**Framework Package Change**:
A change to a reusable cross-product capability in the `JulyFramework` package repository, distinct from product-owned gameplay that merely uses JulyArch roles.
_Avoid_: Any game business class using JulyArch

**Reopen**:
Invalidate a completed Stage and its downstream Stages after an upstream truth source changes.
_Avoid_: Reset, silently resync

**Status View**:
The generated `工作流状态.md` projection of `.july-ai-workflow.json`, refreshed after every state mutation.
_Avoid_: Editable state source
