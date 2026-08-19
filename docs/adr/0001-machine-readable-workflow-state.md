# 0001: Keep workflow state in a machine-readable file

- Status: accepted
- Date: 2026-08-19

## Context

An earlier project-local workflow stored pipeline and wave state in editable Markdown. This is readable but permits a stage to be marked complete without its required artifact, allows invalid downstream completion, and makes state parsing depend on table wording.

## Decision

`DesignDoc/<product>/.july-ai-workflow.json` is the workflow state truth source. `flow.py` is the only supported writer. After every state mutation, it also regenerates `工作流状态.md` as a human-readable projection. Human-authored Markdown files remain Evidence, not state.

## Consequences

- State transitions and prerequisite ordering are deterministic and testable.
- Upstream changes can invalidate downstream state without rewriting product documents.
- Users should not hand-edit the JSON file; damaged state fails validation instead of being guessed back into shape.
- `工作流状态.md` makes progress readable without becoming a second state truth source; it is replaced from JSON after every mutation.
