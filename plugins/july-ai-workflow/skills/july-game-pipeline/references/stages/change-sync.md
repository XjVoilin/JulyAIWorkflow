# Change Sync

Use this flow when confirmed product truth changes after downstream work exists.

## Ownership first

1. Identify the earliest truth source that owns the change: `策划案.md`, GDD, or MDD.
2. Modify only that source first, increment its version, and add a concise change record with reason.
3. Map direct and interface-cascade impact on downstream artifacts and implemented modules.
4. Run `flow.py reopen --stage <earliest-affected-stage> --reason <reason>`. This invalidates that Stage and every downstream Stage while preserving history.
5. Regenerate or patch downstream artifacts in order, verifying each gate again.

## Typical impact

| Change | Earliest Stage to reopen |
|---|---|
| Audience, product promise, core scope | Update `策划案.md`, then reopen `gdd` |
| Player rules, progression, UI flow, win/loss behavior | `gdd` |
| Module ownership, interface, package/config design | `mdd` |
| Code defect with unchanged contracts | `implementation` |
| Missing or invalid acceptance evidence | `validation` |

Do not keep downstream Stages marked complete because a change looks small. State represents validity against the current upstream version, not the amount of editing required.
