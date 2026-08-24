from __future__ import annotations

import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "design_artifacts.py"
SPEC = importlib.util.spec_from_file_location("design_artifacts", SCRIPT)
assert SPEC and SPEC.loader
design_artifacts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(design_artifacts)


def section_document(title: str, headings: tuple[str, ...], extra: str = "") -> str:
    lines = [title, ""]
    for heading in headings:
        section_name = heading.lstrip("# ")
        lines.extend(
            [
                heading,
                "",
                f"{section_name} 描述当前产品的明确事实、责任边界与可审查结果，内容只服务于本章节。",
                "",
            ]
        )
    if extra:
        lines.extend([extra, ""])
    return "\n".join(lines)


def base_contract() -> dict:
    return {
        "schemaVersion": 1,
        "product": "夜市产品",
        "artifacts": [
            {
                "id": "M001",
                "kind": "module",
                "title": "地图生成器",
                "path": "MDD/Modules/M001_地图生成器.md",
                "dependsOn": [],
                "actionsOwned": ["A001"],
                "actionsUsed": [],
                "provides": [
                    {
                        "id": "Product.MapSystem",
                        "kind": "CSharpType",
                        "location": "Assets/Product/Runtime/MapSystem.cs",
                    }
                ],
                "consumes": [],
                "files": {
                    "create": ["Assets/Product/Runtime/MapSystem.cs"],
                    "modify": ["Assets/Product/Runtime/ProductContext.cs"],
                    "generated": [],
                },
            },
            {
                "id": "V001",
                "kind": "view",
                "title": "地图窗口",
                "path": "MDD/Views/V001_地图窗口.md",
                "dependsOn": ["M001"],
                "actionsOwned": [],
                "actionsUsed": ["A001"],
                "provides": [
                    {
                        "id": "Product.MapWindow",
                        "kind": "CSharpType",
                        "location": "Assets/Product/Runtime/UI/MapWindow.cs",
                    }
                ],
                "consumes": [
                    {
                        "symbol": "Product.MapSystem",
                        "provider": "M001",
                        "dependencyType": "compile",
                        "reason": "按钮调用地图业务动作",
                    }
                ],
                "files": {
                    "create": ["Assets/Product/Runtime/UI/MapWindow.cs"],
                    "modify": ["Assets/Product/Runtime/UI/UIContext.cs"],
                    "generated": [],
                },
            },
        ],
        "actions": [
            {
                "id": "A001",
                "intent": "玩家打开地图",
                "kind": "business",
                "owner": "M001",
                "signature": "MapSystem.OpenMap()",
                "precondition": "地图入口可见",
                "success": "地图窗口显示",
                "failure": "无：当前版本没有允许失败",
                "navigationOwner": "MapSystem",
                "navigationTarget": "地图窗口",
                "gdd": "玩家流程",
            }
        ],
        "implementationOrder": ["M001", "V001"],
    }


def gdd_text() -> str:
    lines = ["# 夜市产品 GDD", ""]
    for index, heading in enumerate(design_artifacts.GDD_HEADINGS, 1):
        lines.extend(
            [
                f"## {index}. {heading}",
                "",
                f"{heading}记录第 {index} 类产品事实，描述玩家可感知规则与当前版本明确边界。",
                "",
            ]
        )
    return "\n".join(lines)


def artifact_terms(artifact: dict, actions: list[dict]) -> str:
    terms: list[str] = []
    terms.extend(artifact["dependsOn"])
    terms.extend(item["id"] for item in artifact["provides"])
    terms.extend(item["symbol"] for item in artifact["consumes"])
    for group in design_artifacts.FILE_KEYS:
        terms.extend(artifact["files"][group])
    action_by_id = {item["id"]: item for item in actions}
    for action_id in artifact["actionsOwned"] + artifact["actionsUsed"]:
        terms.extend([action_id, action_by_id[action_id]["signature"]])
    return "合同正文精确引用：" + "；".join(terms)


def index_text(contract: dict) -> str:
    terms: list[str] = []
    for artifact in contract["artifacts"]:
        terms.extend([artifact["id"], artifact["title"], artifact["path"]])
        terms.extend(item["id"] for item in artifact["provides"])
    for action in contract["actions"]:
        terms.extend([action["id"], action["signature"]])
    prose = section_document(
        "# MDD 索引",
        design_artifacts.INDEX_HEADINGS[1:-1],
        "索引正文精确引用：" + "；".join(terms),
    )
    return (
        prose
        + "\n## 11. 结构化设计合同\n\n"
        + "```july-design-contract\n"
        + json.dumps(contract, ensure_ascii=False, indent=2)
        + "\n```\n"
    )


def mdd_text(artifact: dict, actions: list[dict]) -> str:
    headings = (
        design_artifacts.MODULE_HEADINGS
        if artifact["kind"] == "module"
        else design_artifacts.VIEW_HEADINGS
    )
    prose = section_document(
        f"# {artifact['id']}_{artifact['title']}",
        headings[:-1],
        artifact_terms(artifact, actions),
    )
    return (
        prose
        + f"\n{headings[-1]}\n\n"
        + "```july-mdd-contract\n"
        + json.dumps(artifact, ensure_ascii=False, indent=2)
        + "\n```\n"
    )


def write_design(stage: Path, contract: dict, included: set[str] | None = None) -> None:
    (stage / design_artifacts.CONTRACT_FILE).write_text(
        json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (stage / "GDD.md").write_text(gdd_text(), encoding="utf-8")
    (stage / "MDD" / "索引.md").write_text(index_text(contract), encoding="utf-8")
    included = included or {item["id"] for item in contract["artifacts"]}
    for artifact in contract["artifacts"]:
        if artifact["id"] not in included:
            continue
        path = stage.joinpath(*Path(artifact["path"]).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(mdd_text(artifact, contract["actions"]), encoding="utf-8")


class DesignArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="july-plugin-test-"))
        self.stages: list[Path] = []
        self.workspace = self.make_workspace("ProductA")

    def tearDown(self) -> None:
        for stage in self.stages:
            if stage.exists():
                shutil.rmtree(stage)
        shutil.rmtree(self.root)

    def make_workspace(self, name: str) -> Path:
        workspace = self.root / name
        for folder in ("Assets", "Packages", "ProjectSettings", "Design/Docs"):
            (workspace / folder).mkdir(parents=True, exist_ok=True)
        (workspace / "Packages" / "manifest.json").write_text("{}", encoding="utf-8")
        (workspace / "ProjectSettings" / "ProjectVersion.txt").write_text(
            "m_EditorVersion: 6000.0.1f1\n", encoding="utf-8"
        )
        (workspace / "Design" / "Docs" / "策划案.md").write_text(
            "# 策划案\n\n这是明确且稳定的当前版本策划输入。\n", encoding="utf-8"
        )
        return workspace

    def make_stage(self, contract: dict | None = None, included: set[str] | None = None) -> Path:
        stage = design_artifacts.create_stage(self.workspace)
        self.stages.append(stage)
        write_design(stage, contract or base_contract(), included)
        return stage

    def assert_contract_failure(self, callback, contains: str) -> None:
        with self.assertRaises(design_artifacts.ContractFailure) as caught:
            callback()
        self.assertIn(contains, "\n".join(caught.exception.errors))

    def test_valid_partial_full_publish_and_published_validation(self) -> None:
        stage = self.make_stage()
        design_artifacts.validate_artifacts(stage, "partial", "staging", self.workspace)
        design_artifacts.validate_artifacts(stage, "full", "staging", self.workspace)
        design_artifacts.publish(stage, self.workspace)
        docs = self.workspace / "Design" / "Docs"
        design_artifacts.validate_artifacts(docs, "full", "published")
        self.assertFalse((docs / design_artifacts.CONTRACT_FILE).exists())
        self.assertFalse((docs / design_artifacts.STAGE_META_FILE).exists())

    def test_partial_allows_missing_mdd_but_full_rejects_it(self) -> None:
        stage = self.make_stage(included={"M001"})
        design_artifacts.validate_artifacts(stage, "partial", "staging", self.workspace)
        self.assert_contract_failure(
            lambda: design_artifacts.validate_artifacts(stage, "full", "staging", self.workspace),
            "尚未生成",
        )

    def test_staging_is_bound_to_workspace_and_planning_version(self) -> None:
        stage = self.make_stage()
        other = self.make_workspace("ProductB")
        self.assert_contract_failure(
            lambda: design_artifacts.validate_artifacts(stage, "full", "staging", other),
            "其他工作区",
        )
        (self.workspace / "Design" / "Docs" / "策划案.md").write_text(
            "# 策划案\n\n结构已经改变。\n", encoding="utf-8"
        )
        self.assert_contract_failure(
            lambda: design_artifacts.validate_artifacts(stage, "full", "staging", self.workspace),
            "策划案在暂存区创建后已经变化",
        )

    def test_business_generator_title_is_allowed_but_tooling_title_is_not(self) -> None:
        stage = self.make_stage()
        design_artifacts.validate_artifacts(stage, "full", "staging", self.workspace)
        contract = base_contract()
        module = contract["artifacts"][0]
        module["title"] = "每日题目生产与验收"
        module["path"] = "MDD/Modules/M001_每日题目生产与验收.md"
        stage2 = self.make_stage(contract)
        self.assert_contract_failure(
            lambda: design_artifacts.validate_artifacts(stage2, "full", "staging", self.workspace),
            "不是业务能力",
        )

    def test_target_test_file_variants_are_rejected(self) -> None:
        for file_name in ("Assets/Product/Game.Tests.asmdef", "Assets/Product/FooTests.cs", "Assets/Tests/Foo.cs"):
            with self.subTest(file_name=file_name):
                contract = base_contract()
                contract["artifacts"][0]["files"]["create"] = [file_name]
                errors = design_artifacts.validate_schema(contract)
                self.assertTrue(any("目标测试文件" in error for error in errors), errors)
        contract = base_contract()
        contract["artifacts"][0]["files"]["create"] = ["Assets/Product/Contest.cs"]
        self.assertFalse(
            any("目标测试文件" in error for error in design_artifacts.validate_schema(contract))
        )

    def test_prefab_handoff_prose_is_allowed_but_contract_entries_are_rejected(self) -> None:
        prefab_provides = (
            {
                "id": "Prefab.MapWindow",
                "kind": "Resource",
                "location": "Assets/Product/Res/MapWindow.asset",
            },
            {
                "id": "Product.MapWindow",
                "kind": "Prefab",
                "location": "Assets/Product/Res/MapWindow.asset",
            },
            {
                "id": "Product.MapWindow",
                "kind": "Resource",
                "location": "Assets/Product/Res/Prefabs/MapWindow.prefab",
            },
        )
        for prefab_provide in prefab_provides:
            with self.subTest(prefab_provide=prefab_provide):
                contract = base_contract()
                contract["artifacts"][1]["provides"][0] = prefab_provide
                errors = "\n".join(design_artifacts.validate_schema(contract))
                self.assertIn("结构化合同不能声明 Prefab 产物", errors)

        contract = base_contract()
        view = contract["artifacts"][1]
        view["files"]["create"].append("Assets/Product/Res/Prefabs/MapWindow.prefab")
        view["consumes"][0]["dependencyType"] = "prefab"
        errors = "\n".join(design_artifacts.validate_schema(contract))
        self.assertIn("白名单包含 Prefab 文件", errors)
        self.assertIn("Prefab 不进入结构化依赖", errors)

        stage = self.make_stage()
        path = stage / "MDD" / "Views" / "V001_地图窗口.md"
        text = path.read_text(encoding="utf-8")
        handoff = (
            "预期人工交付 `Assets/Product/Res/Prefabs/MapWindow.prefab`，"
            "不进入结构化合同或本 MDD 白名单。"
        )
        text = text.replace("## 8. Prefab、场景与资源", "## 8. Prefab、场景与资源\n\n" + handoff)
        path.write_text(text, encoding="utf-8")
        design_artifacts.validate_artifacts(stage, "full", "staging", self.workspace)

    def test_persistence_type_is_rejected(self) -> None:
        contract = base_contract()
        contract["artifacts"][0]["provides"][0]["id"] = "Product.PuzzleSaveSystem"
        contract["artifacts"][1]["consumes"][0]["symbol"] = "Product.PuzzleSaveSystem"
        stage = self.make_stage(contract)
        self.assert_contract_failure(
            lambda: design_artifacts.validate_artifacts(stage, "full", "staging", self.workspace),
            "持久化实施内容",
        )

    def test_gdd_keywords_in_paragraph_do_not_satisfy_headings(self) -> None:
        stage = self.make_stage()
        paragraph = "、".join(design_artifacts.GDD_HEADINGS)
        (stage / "GDD.md").write_text("# GDD\n\n" + paragraph * 20, encoding="utf-8")
        self.assert_contract_failure(
            lambda: design_artifacts.validate_artifacts(stage, "full", "staging", self.workspace),
            "缺少必需 Markdown 标题",
        )

    def test_duplicate_create_path_and_invalid_enums_are_rejected(self) -> None:
        contract = base_contract()
        contract["artifacts"][1]["files"]["create"] = ["assets/product/runtime/mapsystem.cs"]
        contract["artifacts"][1]["consumes"][0]["dependencyType"] = "magic"
        contract["actions"][0]["kind"] = "command"
        errors = "\n".join(design_artifacts.validate_schema(contract))
        self.assertIn("多个 MDD 声明创建", errors)
        self.assertIn("dependencyType", errors)
        self.assertIn("A001.kind", errors)

    def test_malformed_contract_values_fail_without_validator_crash(self) -> None:
        contract = base_contract()
        contract["artifacts"][0]["dependsOn"] = [[]]
        contract["artifacts"][0]["actionsOwned"] = [[]]
        contract["artifacts"][1]["consumes"][0]["dependencyType"] = []
        contract["actions"][0]["kind"] = []
        contract["actions"][0]["owner"] = {}
        errors = design_artifacts.validate_schema(contract)
        self.assertGreaterEqual(len(errors), 5)

    def test_repeated_boilerplate_sections_are_rejected(self) -> None:
        stage = self.make_stage()
        path = stage / "MDD" / "Modules" / "M001_地图生成器.md"
        text = path.read_text(encoding="utf-8")
        shared = "这一段完全相同并且足够长，用来模拟空洞模板正文。"
        for heading in design_artifacts.MODULE_HEADINGS[:3]:
            pattern = re.escape(heading) + r"\n\n.*?(?=\n## )"
            text = re.sub(pattern, heading + "\n\n" + shared + "\n", text, count=1, flags=re.DOTALL)
        path.write_text(text, encoding="utf-8")
        self.assert_contract_failure(
            lambda: design_artifacts.validate_artifacts(stage, "full", "staging", self.workspace),
            "至少三个章节重复",
        )

    def test_human_body_must_reference_contract_symbols_and_files(self) -> None:
        stage = self.make_stage()
        path = stage / "MDD" / "Views" / "V001_地图窗口.md"
        text = path.read_text(encoding="utf-8")
        marker = "Product.MapSystem"
        prose, contract_block = text.split("```july-mdd-contract", 1)
        path.write_text(prose.replace(marker, "被遗漏的系统") + "```july-mdd-contract" + contract_block, encoding="utf-8")
        self.assert_contract_failure(
            lambda: design_artifacts.validate_artifacts(stage, "full", "staging", self.workspace),
            "正文未引用消费符号",
        )

    def test_publish_rolls_back_if_post_swap_validation_fails(self) -> None:
        stage = self.make_stage()
        marker = self.workspace / "Design" / "Docs" / "existing.txt"
        marker.write_text("keep", encoding="utf-8")
        real_validate = design_artifacts.validate_artifacts
        calls = 0

        def fail_third(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise design_artifacts.ContractFailure(["injected post-swap failure"])
            return real_validate(*args, **kwargs)

        with mock.patch.object(design_artifacts, "validate_artifacts", side_effect=fail_third):
            self.assert_contract_failure(
                lambda: design_artifacts.publish(stage, self.workspace),
                "已尝试回滚",
            )
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
if __name__ == "__main__":
    unittest.main()
