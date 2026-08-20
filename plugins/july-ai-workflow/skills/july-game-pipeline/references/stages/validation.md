# Stage: Validation

Use [../../assets/templates/VALIDATION_REPORT.md](../../assets/templates/VALIDATION_REPORT.md).

## Outcome

Demonstrate that the implemented Product satisfies the approved GDD and the target project's release constraints.

## Work

1. Trace every GDD acceptance scenario to executable or observed evidence.
2. Run focused tests, full Unity compilation, required PlayMode/integration checks, and the target build pipeline at the appropriate non-production setting.
3. Verify Luban generation is reproducible from source inputs and generated outputs are not hand-edited.
4. Verify scenes, launch composition, persistence migration/compatibility where applicable, localization coverage, platform capability behavior, and resource/build completeness.
5. Review generated and modified code against [代码生成质量规则](../code-quality.md). For each added null check, fallback, default object, retry or silent branch, verify the real boundary and required business response. Treat checks that hide required-dependency or internal-invariant violations as failures even when tests otherwise pass.
6. Record failures with reproduction evidence. Fix them through the owning Stage; reopen GDD or MDD when the defect is in the contract rather than merely in implementation.
7. Complete validation only when blockers are closed and the report contains concrete evidence.
