from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import flow


def create_project(root: Path) -> Path:
    (root / "Assets").mkdir(parents=True)
    (root / "Packages").mkdir()
    (root / "ProjectSettings").mkdir()
    (root / "Tools/Luban/DataTables").mkdir(parents=True)
    manifest = {
        "dependencies": {
            "com.july.arch": "test",
            "com.code-philosophy.luban": "test",
        }
    }
    (root / "Packages/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "ProjectSettings/ProjectVersion.txt").write_text(
        "m_EditorVersion: 2022.3.62f2\n", encoding="utf-8"
    )
    design_dir = root / "DesignDoc/MyGame"
    design_dir.mkdir(parents=True)
    (design_dir / "策划案.md").write_text("# 策划案\n", encoding="utf-8")
    return design_dir


class FlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()
        self.design_dir = create_project(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_mdd_bundle(
        self,
        complexity: str = "complex",
        resource_manifest: bool = True,
    ) -> list[str]:
        mdd_dir = self.design_dir / "MDD"
        mdd_dir.mkdir(parents=True, exist_ok=True)
        index_sections = list(flow.MDD_BASE_INDEX_SECTIONS)
        if complexity in {"medium", "complex"}:
            index_sections.extend(flow.MDD_MEDIUM_INDEX_SECTIONS)
        if complexity == "complex":
            index_sections.extend(flow.MDD_COMPLEX_INDEX_SECTIONS)
        index_content = [
            "# index",
            "> 状态：approved",
            "- Architecture Gate：PASS",
            "- Framework Gate：PASS",
            "- Generation Input Boundary：PASS",
            f"- 复杂度：{complexity}",
            "- 参考项目：none",
            f"- 资源清单：{'资源清单.md' if resource_manifest else 'none'}",
            *index_sections,
            "M1_Core.md",
        ]
        (mdd_dir / "索引.md").write_text("\n".join(index_content), encoding="utf-8")
        (mdd_dir / "进度.md").write_text("mdd progress", encoding="utf-8")
        module_content = [
            "# module",
            "> 状态：approved",
            *flow.MDD_MODULE_SECTIONS,
        ]
        (mdd_dir / "M1_Core.md").write_text("\n".join(module_content), encoding="utf-8")

        evidence = [
            "DesignDoc/MyGame/MDD/索引.md",
            "DesignDoc/MyGame/MDD/进度.md",
            "DesignDoc/MyGame/MDD/M1_Core.md",
        ]
        manifest = mdd_dir / "资源清单.md"
        if resource_manifest:
            manifest.write_text("resources", encoding="utf-8")
            evidence.insert(2, "DesignDoc/MyGame/MDD/资源清单.md")
        elif manifest.exists():
            manifest.unlink()
        return evidence

    def test_missing_design_directory_fails(self) -> None:
        with self.assertRaisesRegex(flow.FlowError, "does not exist"):
            flow.initialize(self.root / "missing", "MyGame")

    def test_missing_plan_fails_without_creating_state(self) -> None:
        (self.design_dir / "策划案.md").unlink()
        with self.assertRaisesRegex(flow.FlowError, "missing 策划案.md"):
            flow.initialize(self.root, "MyGame")
        self.assertFalse((self.design_dir / flow.STATE_FILE_NAME).exists())

    def test_missing_named_product_fails_without_guessing(self) -> None:
        with self.assertRaisesRegex(flow.FlowError, "does not exist"):
            flow.initialize(self.root, "Other")

    def test_init_creates_machine_and_readable_state(self) -> None:
        state = flow.initialize(self.root, "MyGame")
        self.assertEqual(flow.STAGES, tuple(state["stages"]))
        self.assertNotIn("brief", state["stages"])
        self.assertTrue((self.design_dir / flow.STATE_FILE_NAME).is_file())
        status = (self.design_dir / flow.STATUS_FILE_NAME).read_text(encoding="utf-8")
        self.assertIn("# 工作流状态", status)
        self.assertIn("`gdd`", status)
        self.assertIn("待开始", status)
        self.assertIsNone(state["stages"]["gdd"]["blocker"])

    def test_product_must_be_one_designdoc_directory_name(self) -> None:
        with self.assertRaisesRegex(flow.FlowError, "one directory name"):
            flow.initialize(self.root, "../MyGame")

    def test_happy_path_and_reopen_refreshes_status_markdown(self) -> None:
        flow.initialize(self.root, "MyGame")
        flow.start_stage(self.root, "MyGame", "gdd")
        status = (self.design_dir / flow.STATUS_FILE_NAME).read_text(encoding="utf-8")
        self.assertIn("| `gdd` | 进行中 |", status)

        gdd = self.design_dir / "GDD.md"
        gdd.write_text("# GDD\n", encoding="utf-8")
        flow.complete_stage(self.root, "MyGame", "gdd", ["DesignDoc/MyGame/GDD.md"])
        status = (self.design_dir / flow.STATUS_FILE_NAME).read_text(encoding="utf-8")
        self.assertIn("| `gdd` | 已完成 |", status)

        state = flow.reopen_stage(self.root, "MyGame", "gdd", "规则改变")
        self.assertEqual("in_progress", state["stages"]["gdd"]["status"])
        self.assertEqual("pending", state["stages"]["gdd_review"]["status"])
        self.assertIn(
            "规则改变",
            (self.design_dir / flow.STATUS_FILE_NAME).read_text(encoding="utf-8"),
        )

    def test_rejects_out_of_order_stage(self) -> None:
        flow.initialize(self.root, "MyGame")
        with self.assertRaisesRegex(flow.FlowError, "Prerequisite"):
            flow.start_stage(self.root, "MyGame", "gdd_review")

    def test_rejects_evidence_outside_project(self) -> None:
        flow.initialize(self.root, "MyGame")
        flow.start_stage(self.root, "MyGame", "gdd")
        outside = self.root.parent / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        with self.assertRaisesRegex(flow.FlowError, "escapes"):
            flow.complete_stage(self.root, "MyGame", "gdd", ["../outside.md"])

    def test_gdd_requires_canonical_artifact(self) -> None:
        state = flow.initialize(self.root, "MyGame")
        other = self.design_dir / "other.md"
        other.write_text("gdd", encoding="utf-8")
        with self.assertRaisesRegex(flow.FlowError, "requires evidence"):
            flow.validate_stage_evidence(
                self.root, state, "gdd", ["DesignDoc/MyGame/other.md"]
            )

    def test_review_report_must_pass_gate(self) -> None:
        state = flow.initialize(self.root, "MyGame")
        review = self.design_dir / "QA_GDD.md"
        review.write_text("- Gate：BLOCKED\n", encoding="utf-8")
        with self.assertRaisesRegex(flow.FlowError, "does not declare PASS"):
            flow.validate_stage_evidence(
                self.root, state, "gdd_review", ["DesignDoc/MyGame/QA_GDD.md"]
            )

    def test_mdd_requires_full_contract_bundle(self) -> None:
        state = flow.initialize(self.root, "MyGame")
        relative_files = self.write_mdd_bundle()

        flow.validate_stage_evidence(self.root, state, "mdd", relative_files)
        with self.assertRaisesRegex(flow.FlowError, "omits module documents"):
            flow.validate_stage_evidence(self.root, state, "mdd", relative_files[:-1])

        second_module = self.root / "DesignDoc/MyGame/MDD/M2_Extra.md"
        second_module.write_text("not yet designed", encoding="utf-8")
        with self.assertRaisesRegex(flow.FlowError, "omits module documents"):
            flow.validate_stage_evidence(self.root, state, "mdd", relative_files)

    def test_mdd_complexity_controls_required_sections(self) -> None:
        state = flow.initialize(self.root, "MyGame")
        small = self.write_mdd_bundle("small", resource_manifest=False)
        flow.validate_stage_evidence(self.root, state, "mdd", small)

        medium = self.write_mdd_bundle("medium", resource_manifest=False)
        index = self.design_dir / "MDD/索引.md"
        index.write_text(
            index.read_text(encoding="utf-8").replace(
                "## 能力树与模块边界", "## omitted capability tree"
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(flow.FlowError, "能力树与模块边界"):
            flow.validate_stage_evidence(self.root, state, "mdd", medium)

        complex_evidence = self.write_mdd_bundle("complex", resource_manifest=False)
        index.write_text(
            index.read_text(encoding="utf-8").replace(
                "## 变化场景 locality", "## omitted locality"
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(flow.FlowError, "变化场景 locality"):
            flow.validate_stage_evidence(self.root, state, "mdd", complex_evidence)

    def test_mdd_resource_manifest_is_explicitly_optional(self) -> None:
        state = flow.initialize(self.root, "MyGame")
        evidence = self.write_mdd_bundle("small", resource_manifest=False)
        flow.validate_stage_evidence(self.root, state, "mdd", evidence)

        manifest = self.design_dir / "MDD/资源清单.md"
        manifest.write_text("unexpected", encoding="utf-8")
        with self.assertRaisesRegex(flow.FlowError, "declares no separate resource manifest"):
            flow.validate_stage_evidence(
                self.root,
                state,
                "mdd",
                [*evidence, "DesignDoc/MyGame/MDD/资源清单.md"],
            )

        evidence = self.write_mdd_bundle("small", resource_manifest=True)
        flow.validate_stage_evidence(self.root, state, "mdd", evidence)

    def test_mdd_templates_match_validator_contract(self) -> None:
        skill_root = Path(__file__).resolve().parent.parent
        index = (skill_root / "assets/templates/MDD_INDEX.md").read_text(encoding="utf-8")
        module = (skill_root / "assets/templates/MDD_MODULE.md").read_text(encoding="utf-8")
        for marker in ("复杂度", "参考项目", "资源清单"):
            self.assertRegex(index, rf"(?m)^- {marker}：")
        for section in (
            *flow.MDD_BASE_INDEX_SECTIONS,
            *flow.MDD_MEDIUM_INDEX_SECTIONS,
            *flow.MDD_COMPLEX_INDEX_SECTIONS,
        ):
            self.assertIn(section, index)
        for section in flow.MDD_MODULE_SECTIONS:
            self.assertIn(section, module)

    def test_completed_evidence_must_continue_to_exist(self) -> None:
        flow.initialize(self.root, "MyGame")
        flow.start_stage(self.root, "MyGame", "gdd")
        gdd = self.design_dir / "GDD.md"
        gdd.write_text("gdd", encoding="utf-8")
        flow.complete_stage(self.root, "MyGame", "gdd", ["DesignDoc/MyGame/GDD.md"])
        gdd.unlink()
        with self.assertRaisesRegex(flow.FlowError, "not a file"):
            flow.load_state(self.root, "MyGame")

        state = flow.reopen_stage(
            self.root,
            "MyGame",
            "gdd",
            "completed evidence was invalidated and must be regenerated",
        )
        self.assertEqual("in_progress", state["stages"]["gdd"]["status"])
        self.assertEqual([], state["stages"]["gdd"]["evidence"])

    def write_framework_gap(self, gate: str = "BLOCKED") -> str:
        relative = "DesignDoc/MyGame/框架缺口/FG-001_SaveContract.md"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(
                [
                    "# FG-001",
                    "",
                    "- 分类：July Framework 缺失",
                    f"- Gate：{gate}",
                    "",
                    "## 缺失判定",
                    "",
                    "## 框架补充方案",
                    "",
                    "## 影响与迁移",
                    "",
                    "## 恢复条件",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return relative

    def test_framework_gap_blocks_until_resolved_with_evidence(self) -> None:
        flow.initialize(self.root, "MyGame")
        flow.start_stage(self.root, "MyGame", "gdd")
        proposal = self.write_framework_gap()

        state = flow.block_stage(
            self.root, "MyGame", "gdd", "Save contract is missing", proposal
        )
        self.assertEqual("blocked", state["stages"]["gdd"]["status"])
        self.assertEqual(proposal, state["stages"]["gdd"]["blocker"]["proposal"])
        status = (self.design_dir / flow.STATUS_FILE_NAME).read_text(encoding="utf-8")
        self.assertIn("框架缺口阻塞", status)
        self.assertIn(proposal, status)

        gdd = self.design_dir / "GDD.md"
        gdd.write_text("gdd", encoding="utf-8")
        with self.assertRaisesRegex(flow.FlowError, "not in progress"):
            flow.complete_stage(self.root, "MyGame", "gdd", ["DesignDoc/MyGame/GDD.md"])
        with self.assertRaisesRegex(flow.FlowError, "resume it first"):
            flow.reopen_stage(self.root, "MyGame", "gdd", "try to bypass")

        integration = self.design_dir / "framework-integration.txt"
        integration.write_text("tests passed", encoding="utf-8")
        evidence = [
            proposal,
            "Packages/manifest.json",
            "DesignDoc/MyGame/framework-integration.txt",
        ]
        with self.assertRaisesRegex(flow.FlowError, "does not declare RESOLVED"):
            flow.resume_stage(
                self.root, "MyGame", "gdd", "framework released", evidence
            )

        self.write_framework_gap("RESOLVED")
        state = flow.resume_stage(
            self.root, "MyGame", "gdd", "framework released", evidence
        )
        self.assertEqual("in_progress", state["stages"]["gdd"]["status"])
        self.assertIsNone(state["stages"]["gdd"]["blocker"])
        self.assertEqual("resume", state["history"][-1]["action"])

    def test_framework_gap_can_be_narrowed_without_false_resolution(self) -> None:
        flow.initialize(self.root, "MyGame")
        flow.start_stage(self.root, "MyGame", "gdd")
        proposal = self.write_framework_gap()
        flow.block_stage(
            self.root,
            "MyGame",
            "gdd",
            "Restore failures must block writes",
            proposal,
        )

        state = flow.block_stage(
            self.root,
            "MyGame",
            "gdd",
            "Write blocking was removed, but restore failures must remain observable",
            proposal,
        )

        self.assertEqual("blocked", state["stages"]["gdd"]["status"])
        self.assertEqual(
            "Write blocking was removed, but restore failures must remain observable",
            state["stages"]["gdd"]["blocker"]["reason"],
        )
        self.assertEqual("reblock", state["history"][-1]["action"])

    def test_framework_gap_requires_designated_proposal(self) -> None:
        flow.initialize(self.root, "MyGame")
        flow.start_stage(self.root, "MyGame", "gdd")
        invalid = self.design_dir / "not-a-gap.md"
        invalid.write_text("- Gate：BLOCKED\n", encoding="utf-8")
        with self.assertRaisesRegex(flow.FlowError, "must be DesignDoc"):
            flow.block_stage(
                self.root,
                "MyGame",
                "gdd",
                "missing framework capability",
                "DesignDoc/MyGame/not-a-gap.md",
            )

    def test_framework_gap_can_resolve_by_confirmed_scope_change(self) -> None:
        flow.initialize(self.root, "MyGame")
        flow.start_stage(self.root, "MyGame", "gdd")
        proposal = self.write_framework_gap()
        flow.block_stage(
            self.root, "MyGame", "gdd", "Cloud storage is missing", proposal
        )

        (self.design_dir / "GDD.md").write_text(
            "# GDD\n\nCloud storage is deferred from this release.\n", encoding="utf-8"
        )
        (self.design_dir / "QA_GDD.md").write_text(
            "# Review\n\n- Gate：PASS\n", encoding="utf-8"
        )
        self.write_framework_gap("RESOLVED")
        evidence = [
            proposal,
            "DesignDoc/MyGame/GDD.md",
            "DesignDoc/MyGame/QA_GDD.md",
        ]

        state = flow.resume_stage(
            self.root,
            "MyGame",
            "gdd",
            "Cloud storage moved out of the current release",
            evidence,
            "scope_change",
        )

        self.assertEqual("in_progress", state["stages"]["gdd"]["status"])
        self.assertEqual("scope_change", state["history"][-1]["resolution_kind"])


if __name__ == "__main__":
    unittest.main()
