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
        relative_files = [
            "DesignDoc/MyGame/MDD/索引.md",
            "DesignDoc/MyGame/MDD/进度.md",
            "DesignDoc/MyGame/MDD/资源清单.md",
            "DesignDoc/MyGame/MDD/M1_Core.md",
        ]
        for relative in relative_files:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("mdd", encoding="utf-8")

        flow.validate_stage_evidence(self.root, state, "mdd", relative_files)
        with self.assertRaisesRegex(flow.FlowError, "at least one MDD module"):
            flow.validate_stage_evidence(self.root, state, "mdd", relative_files[:3])

    def test_completed_evidence_must_continue_to_exist(self) -> None:
        flow.initialize(self.root, "MyGame")
        flow.start_stage(self.root, "MyGame", "gdd")
        gdd = self.design_dir / "GDD.md"
        gdd.write_text("gdd", encoding="utf-8")
        flow.complete_stage(self.root, "MyGame", "gdd", ["DesignDoc/MyGame/GDD.md"])
        gdd.unlink()
        with self.assertRaisesRegex(flow.FlowError, "not a file"):
            flow.load_state(self.root, "MyGame")


if __name__ == "__main__":
    unittest.main()
