#!/usr/bin/env python3
"""Validate and transactionally publish July game design artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCHEMA_VERSION = 1
CONTRACT_FILE = ".july-design-contract.json"
STAGE_META_FILE = ".july-design-stage.json"
INDEX_BLOCK = "july-design-contract"
MDD_BLOCK = "july-mdd-contract"
STAGE_META_KEYS = {
    "schemaVersion",
    "workspace",
    "planningSha256",
    "projectVersion",
    "createdAtUtc",
}

TOP_LEVEL_KEYS = {
    "schemaVersion",
    "product",
    "artifacts",
    "actions",
    "implementationOrder",
}
ARTIFACT_KEYS = {
    "id",
    "kind",
    "title",
    "path",
    "dependsOn",
    "actionsOwned",
    "actionsUsed",
    "provides",
    "consumes",
    "files",
}
ACTION_KEYS = {
    "id",
    "intent",
    "kind",
    "owner",
    "signature",
    "precondition",
    "success",
    "failure",
    "navigationOwner",
    "navigationTarget",
    "gdd",
}
PROVIDE_KEYS = {"id", "kind", "location"}
CONSUME_KEYS = {"symbol", "provider", "dependencyType", "reason"}
FILE_KEYS = {"create", "modify", "generated"}

INDEX_HEADINGS = (
    "# MDD 索引",
    "## 1. 设计基线",
    "## 2. GDD 范围覆盖",
    "## 3. 业务事实所有权",
    "## 4. 全局动作合同",
    "## 5. Module 与 View 清单",
    "## 6. 产品符号唯一提供表",
    "## 7. 全产物实施依赖图",
    "## 8. 精确实施顺序",
    "## 9. 单份 MDD 闭包证明",
    "## 10. 完整性结论",
    "## 11. 结构化设计合同",
)
MODULE_HEADINGS = (
    "## 1. 能力定义",
    "## 2. 完整业务流程",
    "## 3. 事实与数据所有权",
    "## 4. 实施依赖与消费者",
    "## 5. 角色清单",
    "## 6. C# 数据结构草图",
    "## 7. 公共接口合同",
    "## 8. 核心算法伪代码",
    "## 9. 业务事件",
    "## 10. Luban 配置合同",
    "## 11. 注册与初始化",
    "## 12. 新类型必要性审查",
    "## 13. 精确文件白名单",
    "## 14. 单份 MDD 闭包证明",
    "## 15. 验收",
    "## 16. 明确不实施",
    "## 17. 结构化 MDD 合同",
)
VIEW_HEADINGS = (
    "## 1. 视觉责任",
    "## 2. 可见事实",
    "## 3. 玩家交互",
    "## 4. WindowData 合同",
    "## 5. Window 合同",
    "## 6. 业务事件",
    "## 7. GameView 合同",
    "## 8. Prefab、场景与资源",
    "## 9. 精确文件白名单",
    "## 10. 单份 MDD 闭包证明",
    "## 11. 验收",
    "## 12. 明确不实施",
    "## 13. 结构化 MDD 合同",
)
GDD_HEADINGS = (
    "产品定位",
    "当前版本范围",
    "玩家目标",
    "核心循环",
    "业务词汇",
    "规则",
    "运行时事实",
    "玩家流程",
    "约束",
)

UNRESOLVED_PATTERNS = (
    re.compile(r"A___"),
    re.compile(r"\[TODO", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"实施时决定|待补充"),
    re.compile(r"<(?:逐个|玩家|能力|视觉功能|MDD|业务能力)[^>\n]*>"),
)
PERSISTENCE_PATTERNS = (
    re.compile(
        r"\b(?:SaveAsync|LoadAsync|\w*Repository|\w*SaveSystem|\w*LoadSystem|"
        r"Persistence|Persistent|Persistable)\b",
        re.IGNORECASE,
    ),
    re.compile(r"存档|持久化|跨启动|本地存储|服务器存储|云存档"),
)
NON_BUSINESS_TITLE = re.compile(
    r"验收|验证器|编辑器|(?:测试|发布|验证)(?:工具|流程|管线|系统)|"
    r"(?:工具|流程|管线)(?:验证|发布|测试)"
)
ACTION_KINDS = {"business", "navigation", "view-local"}
DEPENDENCY_TYPES = {
    "compile",
    "luban-authoring",
    "registration",
    "prefab",
    "runtime-contract",
}
TEST_DIRECTORY_NAMES = {"test", "tests", "mocks", "fakes", "fixtures"}
TEST_FILE_STEM = re.compile(r"(?i:^test)|(?:Test|Tests)$|(?i:[._-]tests?$)")


class ContractFailure(Exception):
    def __init__(self, errors: Iterable[str]):
        self.errors = list(errors)
        super().__init__("\n".join(self.errors))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise ContractFailure([f"无法读取文本文件：{path}：{exc}"]) from exc


def load_json(path: Path) -> Any:
    try:
        return json.loads(read_text(path))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractFailure([f"无法读取 JSON：{path}：{exc}"]) from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_is_link(path: Path) -> bool:
    is_junction = getattr(os.path, "isjunction", lambda _: False)
    return path.is_symlink() or is_junction(path)


def tree_contains_links(root: Path) -> bool:
    if path_is_link(root):
        return True
    pending = [root]
    while pending:
        current = pending.pop()
        with os.scandir(current) as entries:
            for entry in entries:
                path = Path(entry.path)
                if path_is_link(path):
                    return True
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
    return False


def is_target_test_path(value: str) -> bool:
    path = PurePosixPath(value)
    lowered_parts = [part.casefold() for part in path.parts]
    if any(part in TEST_DIRECTORY_NAMES for part in lowered_parts[:-1]):
        return True
    return bool(TEST_FILE_STEM.search(path.stem))


def load_stage_metadata(staging: Path, workspace: Path | None = None) -> dict[str, Any]:
    temp_root = Path(tempfile.gettempdir()).resolve()
    if staging.parent != temp_root or not staging.name.startswith("july-design-"):
        raise ContractFailure([f"暂存目录不是本工具创建的系统临时目录：{staging}"])
    metadata_path = staging / STAGE_META_FILE
    if not metadata_path.is_file():
        raise ContractFailure([f"暂存目录缺少工作区绑定信息：{metadata_path}"])
    metadata = load_json(metadata_path)
    errors: list[str] = []
    if not require_exact_keys(metadata, STAGE_META_KEYS, "暂存区元数据", errors):
        raise ContractFailure(errors)
    if metadata["schemaVersion"] != SCHEMA_VERSION:
        errors.append(f"暂存区 schemaVersion 必须为 {SCHEMA_VERSION}")
    for key in STAGE_META_KEYS - {"schemaVersion"}:
        require_string(metadata[key], f"暂存区.{key}", errors)
    if errors:
        raise ContractFailure(errors)
    if workspace is not None:
        workspace = validate_workspace(workspace)
        expected_workspace = os.path.normcase(str(workspace))
        actual_workspace = os.path.normcase(str(Path(metadata["workspace"]).resolve()))
        if actual_workspace != expected_workspace:
            errors.append(
                f"暂存区属于其他工作区：{metadata['workspace']}，当前目标为 {workspace}"
            )
        planning = workspace / "Design" / "Docs" / "策划案.md"
        if metadata["planningSha256"] != sha256_file(planning):
            errors.append("策划案在暂存区创建后已经变化，必须重新讨论并创建暂存区")
        project_version = read_text(workspace / "ProjectSettings" / "ProjectVersion.txt").strip()
        if metadata["projectVersion"] != project_version:
            errors.append("Unity 项目版本在暂存区创建后已经变化，必须重新创建暂存区")
    if errors:
        raise ContractFailure(errors)
    return metadata


def extract_block(text: str, language: str, source: Path) -> Any:
    pattern = re.compile(
        rf"```{re.escape(language)}[ \t]*\r?\n(.*?)\r?\n```", re.DOTALL
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise ContractFailure(
            [f"{source} 必须且只能包含一个 ```{language} 结构化合同块"]
        )
    try:
        return json.loads(matches[0])
    except json.JSONDecodeError as exc:
        raise ContractFailure([f"{source} 的 {language} 不是有效 JSON：{exc}"]) from exc


def normalized_relative_path(value: Any, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} 必须是非空相对路径")
        return None
    if "\\" in value:
        errors.append(f"{label} 必须使用 /：{value}")
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value != path.as_posix():
        errors.append(f"{label} 必须是规范且不越界的相对路径：{value}")
        return None
    return value


def require_exact_keys(value: Any, keys: set[str], label: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} 必须是对象")
        return False
    actual = set(value)
    if actual != keys:
        missing = sorted(keys - actual)
        extra = sorted(actual - keys)
        errors.append(f"{label} 字段不匹配；缺少={missing}，多余={extra}")
        return False
    return True


def require_string(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} 必须是非空字符串")


def require_string_list(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        errors.append(f"{label} 必须是非空字符串组成的数组（数组本身可为空）")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{label} 不能包含重复项")
    return value


def safe_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def validate_schema(contract: Any) -> list[str]:
    errors: list[str] = []
    if not require_exact_keys(contract, TOP_LEVEL_KEYS, "设计合同", errors):
        return errors
    if contract["schemaVersion"] != SCHEMA_VERSION:
        errors.append(
            f"schemaVersion 必须为 {SCHEMA_VERSION}，实际为 {contract['schemaVersion']}"
        )
    require_string(contract["product"], "product", errors)

    artifacts = contract["artifacts"]
    actions = contract["actions"]
    order = require_string_list(contract["implementationOrder"], "implementationOrder", errors)
    if not isinstance(artifacts, list):
        errors.append("artifacts 必须是数组")
        artifacts = []
    if not isinstance(actions, list):
        errors.append("actions 必须是数组")
        actions = []

    artifact_by_id: dict[str, dict[str, Any]] = {}
    provider_by_symbol: dict[str, str] = {}
    action_by_id: dict[str, dict[str, Any]] = {}
    creator_by_path: dict[str, str] = {}

    for index, artifact in enumerate(artifacts):
        label = f"artifacts[{index}]"
        if not require_exact_keys(artifact, ARTIFACT_KEYS, label, errors):
            continue
        artifact_id = artifact["id"]
        kind = artifact["kind"]
        if not isinstance(artifact_id, str) or not re.fullmatch(r"[MV]\d{3}", artifact_id):
            errors.append(f"{label}.id 必须匹配 M001 或 V001")
            continue
        if artifact_id in artifact_by_id:
            errors.append(f"MDD ID 重复：{artifact_id}")
        artifact_by_id[artifact_id] = artifact
        expected_kind = "module" if artifact_id.startswith("M") else "view"
        if kind != expected_kind:
            errors.append(f"{artifact_id}.kind 必须为 {expected_kind}")
        require_string(artifact["title"], f"{artifact_id}.title", errors)
        if kind == "module" and isinstance(artifact["title"], str) and NON_BUSINESS_TITLE.search(artifact["title"]):
            errors.append(f"{artifact_id} 标题像工具/验证/发布职责，不是业务能力：{artifact['title']}")
        artifact_path = normalized_relative_path(artifact["path"], f"{artifact_id}.path", errors)
        if artifact_path:
            parent = "MDD/Modules/" if kind == "module" else "MDD/Views/"
            expected_stem = f"{artifact_id}_{artifact['title']}"
            if not artifact_path.startswith(parent) or PurePosixPath(artifact_path).stem != expected_stem or not artifact_path.endswith(".md"):
                errors.append(f"{artifact_id}.path 与种类、编号或标题不一致：{artifact_path}")
        for field in ("dependsOn", "actionsOwned", "actionsUsed"):
            require_string_list(artifact[field], f"{artifact_id}.{field}", errors)
        if isinstance(artifact["actionsOwned"], list) and isinstance(artifact["actionsUsed"], list):
            overlap = set(safe_string_list(artifact["actionsOwned"])) & set(safe_string_list(artifact["actionsUsed"]))
            if overlap:
                errors.append(f"{artifact_id} 不能同时拥有和消费同一动作：{sorted(overlap)}")

        provides = artifact["provides"]
        if not isinstance(provides, list):
            errors.append(f"{artifact_id}.provides 必须是数组")
            provides = []
        elif not provides:
            errors.append(f"{artifact_id}.provides 不能为空")
        for provide_index, provide in enumerate(provides):
            provide_label = f"{artifact_id}.provides[{provide_index}]"
            if not require_exact_keys(provide, PROVIDE_KEYS, provide_label, errors):
                continue
            for key in PROVIDE_KEYS:
                require_string(provide[key], f"{provide_label}.{key}", errors)
            symbol = provide["id"]
            if isinstance(symbol, str):
                if symbol in provider_by_symbol:
                    errors.append(
                        f"产品符号提供者重复：{symbol} 同时属于 {provider_by_symbol[symbol]} 和 {artifact_id}"
                    )
                provider_by_symbol[symbol] = artifact_id

        consumes = artifact["consumes"]
        if not isinstance(consumes, list):
            errors.append(f"{artifact_id}.consumes 必须是数组")
            consumes = []
        seen_consumes: set[str] = set()
        for consume_index, consume in enumerate(consumes):
            consume_label = f"{artifact_id}.consumes[{consume_index}]"
            if not require_exact_keys(consume, CONSUME_KEYS, consume_label, errors):
                continue
            for key in CONSUME_KEYS:
                require_string(consume[key], f"{consume_label}.{key}", errors)
            if isinstance(consume["dependencyType"], str) and consume["dependencyType"] not in DEPENDENCY_TYPES:
                errors.append(
                    f"{consume_label}.dependencyType 必须是 {sorted(DEPENDENCY_TYPES)} 之一"
                )
            symbol = consume["symbol"]
            if isinstance(symbol, str) and symbol in seen_consumes:
                errors.append(f"{artifact_id} 重复消费产品符号：{symbol}")
            if isinstance(symbol, str):
                seen_consumes.add(symbol)

        files = artifact["files"]
        if require_exact_keys(files, FILE_KEYS, f"{artifact_id}.files", errors):
            all_files: list[str] = []
            for group in ("create", "modify", "generated"):
                values = require_string_list(files[group], f"{artifact_id}.files.{group}", errors)
                for file_index, value in enumerate(values):
                    normalized_relative_path(value, f"{artifact_id}.files.{group}[{file_index}]", errors)
                    lowered = f"/{value.lower().strip('/')}"
                    if is_target_test_path(value):
                        errors.append(f"{artifact_id} 白名单包含目标测试文件：{value}")
                    if "/editor/" in lowered and PurePosixPath(value).suffix.lower() in {".cs", ".asmdef"}:
                        errors.append(f"{artifact_id} 白名单包含 Editor 工具代码：{value}")
                    if group == "create":
                        normalized_key = value.casefold()
                        previous = creator_by_path.get(normalized_key)
                        if previous is not None and previous != artifact_id:
                            errors.append(
                                f"产品文件被多个 MDD 声明创建：{value} 同时属于 {previous} 和 {artifact_id}"
                            )
                        creator_by_path[normalized_key] = artifact_id
                all_files.extend(values)
            if not all_files:
                errors.append(f"{artifact_id} 的文件白名单不能为空")
            if len(all_files) != len(set(all_files)):
                errors.append(f"{artifact_id} 的同一文件不能同时出现在多个白名单分组")

    if not any(item.get("kind") == "module" for item in artifact_by_id.values()):
        errors.append("完整设计至少需要一份 Module MDD")
    if not any(item.get("kind") == "view" for item in artifact_by_id.values()):
        errors.append("完整设计至少需要一份 View MDD")

    for index, action in enumerate(actions):
        label = f"actions[{index}]"
        if not require_exact_keys(action, ACTION_KEYS, label, errors):
            continue
        for key in ACTION_KEYS:
            require_string(action[key], f"{label}.{key}", errors)
        action_id = action["id"]
        if not isinstance(action_id, str) or not re.fullmatch(r"A\d{3}", action_id):
            errors.append(f"{label}.id 必须匹配 A001")
            continue
        if action_id in action_by_id:
            errors.append(f"动作 ID 重复：{action_id}")
        action_by_id[action_id] = action
        if isinstance(action["kind"], str) and action["kind"] not in ACTION_KINDS:
            errors.append(f"{action_id}.kind 必须是 {sorted(ACTION_KINDS)} 之一")
        if isinstance(action["owner"], str) and action["owner"] not in artifact_by_id:
            errors.append(f"{action_id}.owner 不存在：{action['owner']}")

    if set(order) != set(artifact_by_id) or len(order) != len(artifact_by_id):
        errors.append("implementationOrder 必须且只能包含全部 MDD 一次")
    if [item.get("id") for item in artifacts if isinstance(item, dict)] != order:
        errors.append("artifacts 必须按 implementationOrder 排列，避免两套顺序")
    order_index = {artifact_id: index for index, artifact_id in enumerate(order)}

    for kind, prefix in (("module", "M"), ("view", "V")):
        ids = [item for item in order if item.startswith(prefix)]
        expected = [f"{prefix}{number:03d}" for number in range(1, len(ids) + 1)]
        if ids != expected:
            errors.append(f"{kind} 编号必须按全局拓扑序从 001 连续递增：{ids}")

    for artifact_id, artifact in artifact_by_id.items():
        depends = safe_string_list(artifact["dependsOn"])
        for provider in depends:
            if provider == artifact_id:
                errors.append(f"{artifact_id} 不能依赖自身")
            elif provider not in artifact_by_id:
                errors.append(f"{artifact_id} 依赖不存在的 MDD：{provider}")
            elif order_index.get(provider, 10**9) >= order_index.get(artifact_id, -1):
                errors.append(f"{artifact_id} 前向依赖 {provider}，实施顺序无闭包")

        owned = set(safe_string_list(artifact["actionsOwned"]))
        expected_owned = {action_id for action_id, action in action_by_id.items() if action.get("owner") == artifact_id}
        if owned != expected_owned:
            errors.append(f"{artifact_id}.actionsOwned 与全局动作所有权不一致")
        used = set(safe_string_list(artifact["actionsUsed"]))
        for action_id in owned | used:
            if action_id not in action_by_id:
                errors.append(f"{artifact_id} 引用不存在的动作：{action_id}")
        for action_id in used:
            owner = action_by_id.get(action_id, {}).get("owner")
            if isinstance(owner, str) and owner != artifact_id and owner not in depends:
                errors.append(f"{artifact_id} 使用 {action_id}，但未依赖其所有者 {owner}")

        dependency_evidence: set[str] = set()
        consumes = artifact["consumes"] if isinstance(artifact["consumes"], list) else []
        for consume in consumes:
            if not isinstance(consume, dict) or not CONSUME_KEYS.issubset(consume):
                continue
            symbol = consume["symbol"]
            provider = consume["provider"]
            if not isinstance(symbol, str) or not isinstance(provider, str):
                continue
            actual_provider = provider_by_symbol.get(symbol)
            if actual_provider is None:
                errors.append(f"{artifact_id} 消费未声明提供者的产品符号：{symbol}")
            elif actual_provider != provider:
                errors.append(
                    f"{artifact_id} 对 {symbol} 声明提供者 {provider}，实际为 {actual_provider}"
                )
            if provider != artifact_id:
                dependency_evidence.add(provider)
                if provider not in depends:
                    errors.append(f"{artifact_id} 消费 {symbol}，但 dependsOn 缺少 {provider}")
            else:
                errors.append(f"{artifact_id}.consumes 只记录跨 MDD 消费，不能列自有符号：{symbol}")
        for action_id in used:
            owner = action_by_id.get(action_id, {}).get("owner")
            if isinstance(owner, str) and owner != artifact_id:
                dependency_evidence.add(owner)
        unsupported = set(depends) - dependency_evidence
        if unsupported:
            errors.append(f"{artifact_id}.dependsOn 缺少产品符号或动作依据：{sorted(unsupported)}")

    return errors


def strip_contract_blocks(text: str) -> str:
    return re.sub(r"```july-(?:design|mdd)-contract[ \t]*\r?\n.*?\r?\n```", "", text, flags=re.DOTALL)


def content_outside_exclusions(text: str) -> str:
    kept: list[str] = []
    excluded = False
    for line in text.splitlines():
        if line.startswith("#"):
            excluded = bool(re.search(r"明确不实施|排除|不在范围", line))
        if not excluded and not re.search(r"不实施|排除|不包含|不设计", line):
            kept.append(line)
    return "\n".join(kept)


def markdown_sections(text: str) -> list[tuple[int, str, str]]:
    masked = re.sub(
        r"```.*?```",
        lambda match: "".join("\n" if char == "\n" else " " for char in match.group()),
        text,
        flags=re.DOTALL,
    )
    matches = list(re.finditer(r"^(#{1,6})[ \t]+(.+?)[ \t]*$", masked, re.MULTILINE))
    sections: list[tuple[int, str, str]] = []
    for index, match in enumerate(matches):
        level = len(match.group(1))
        end = len(text)
        for following in matches[index + 1:]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        sections.append((level, match.group(2).strip(), text[match.end():end]))
    return sections


def normalized_heading(title: str) -> str:
    return re.sub(r"^\d+(?:[.、]\d+)*[.、]?[ \t]*", "", title).strip()


def meaningful_length(text: str) -> int:
    without_fence_markers = re.sub(r"^```[^\n]*$", "", text, flags=re.MULTILINE)
    return len(re.findall(r"[\w\u3400-\u9fff]", without_fence_markers, re.UNICODE))


def validate_section_content(
    path: Path,
    sections: list[tuple[int, str, str]],
    required_titles: Iterable[str],
    exact: bool,
    errors: list[str],
) -> None:
    selected: list[tuple[str, str]] = []
    for required in required_titles:
        if required.startswith("# "):
            continue
        if "结构化" in required and "合同" in required:
            continue
        title_without_marks = required.lstrip("# ")
        candidates = [
            (title, body)
            for level, title, body in sections
            if (f"{'#' * level} {title}" == required if exact else title_without_marks in normalized_heading(title))
        ]
        if not candidates:
            continue
        title, body = candidates[0]
        selected.append((title, body))
        stripped = re.sub(r"[`*_>#|\-]", "", body).strip()
        if meaningful_length(body) < 12:
            errors.append(f"{path} 章节内容过少：{title}")
        if re.fullmatch(r"无[。.]?", stripped):
            errors.append(f"{path} 章节不能只写“无”，必须说明为什么不适用：{title}")

    normalized_bodies: dict[str, list[str]] = {}
    for title, body in selected:
        normalized = re.sub(r"[^\w\u3400-\u9fff]", "", body, flags=re.UNICODE).casefold()
        if len(normalized) >= 12:
            normalized_bodies.setdefault(normalized, []).append(title)
    repeated = [titles for titles in normalized_bodies.values() if len(titles) >= 3]
    if repeated:
        errors.append(f"{path} 至少三个章节重复同一段正文：{repeated[0]}")


def validate_text(
    path: Path,
    text: str,
    headings: Iterable[str],
    errors: list[str],
    *,
    gdd: bool = False,
) -> None:
    if len(text.strip()) < 200:
        errors.append(f"文档为空或明显未完成：{path}")
    sections = markdown_sections(text)
    if gdd:
        actual = [normalized_heading(title) for _, title, _ in sections]
        for heading in headings:
            if not any(heading in title for title in actual):
                errors.append(f"{path} 缺少必需 Markdown 标题：{heading}")
        validate_section_content(path, sections, headings, False, errors)
    else:
        actual_lines = {f"{'#' * level} {title}" for level, title, _ in sections}
        for heading in headings:
            if heading not in actual_lines:
                errors.append(f"{path} 缺少必需标题：{heading}")
        validate_section_content(path, sections, headings, True, errors)
    body = strip_contract_blocks(text)
    for pattern in UNRESOLVED_PATTERNS:
        match = pattern.search(body)
        if match:
            errors.append(f"{path} 含未解决占位：{match.group(0)}")
    active = content_outside_exclusions(body)
    for pattern in PERSISTENCE_PATTERNS:
        match = pattern.search(active)
        if match:
            errors.append(f"{path} 在排除章节之外包含持久化设计：{match.group(0)}")


def require_body_terms(
    path: Path,
    body: str,
    terms: Iterable[tuple[str, str]],
    errors: list[str],
) -> None:
    seen: set[str] = set()
    for label, term in terms:
        if not term or term in seen:
            continue
        seen.add(term)
        if term not in body:
            errors.append(f"{path} 正文未引用{label}：{term}")


def validate_artifacts(
    source: Path,
    mode: str,
    surface: str,
    workspace: Path | None = None,
) -> dict[str, Any]:
    source_was_link = path_is_link(source)
    source = source.resolve()
    errors: list[str] = []
    if not source.is_dir():
        raise ContractFailure([f"设计根目录不存在：{source}"])
    if source_was_link or tree_contains_links(source):
        errors.append(f"设计目录不能包含符号链接：{source}")

    metadata_path = source / STAGE_META_FILE
    if surface == "staging":
        if workspace is None:
            errors.append("验证 staging 时必须提供 --workspace，以核对暂存区归属")
        else:
            try:
                load_stage_metadata(source, workspace)
            except ContractFailure as exc:
                errors.extend(exc.errors)
    elif metadata_path.exists():
        errors.append(f"正式设计不能保留暂存区元数据：{metadata_path}")

    index_path = source / "MDD" / "索引.md"
    gdd_path = source / "GDD.md"
    if not index_path.is_file():
        errors.append(f"缺少 MDD 索引：{index_path}")
    if not gdd_path.is_file():
        errors.append(f"缺少 GDD：{gdd_path}")
    if errors:
        raise ContractFailure(errors)

    index_text = read_text(index_path)
    contract = extract_block(index_text, INDEX_BLOCK, index_path)
    contract_path = source / CONTRACT_FILE
    if surface == "staging" and not contract_path.is_file():
        errors.append(f"暂存设计缺少机器权威合同：{contract_path}")
    elif surface == "published" and contract_path.exists():
        errors.append(f"正式设计不能保留临时合同文件：{contract_path}")
    elif contract_path.exists():
        staged_contract = load_json(contract_path)
        if staged_contract != contract:
            errors.append(f"{CONTRACT_FILE} 与索引中的结构化设计合同不一致")
    schema_errors = validate_schema(contract)
    errors.extend(schema_errors)
    if schema_errors:
        raise ContractFailure(errors)
    serialized_contract = json.dumps(contract, ensure_ascii=False)
    for pattern in PERSISTENCE_PATTERNS:
        match = pattern.search(serialized_contract)
        if match:
            errors.append(f"结构化设计合同包含持久化实施内容：{match.group(0)}")
    validate_text(index_path, index_text, INDEX_HEADINGS, errors)
    validate_text(gdd_path, read_text(gdd_path), GDD_HEADINGS, errors, gdd=True)

    artifacts = contract.get("artifacts", []) if isinstance(contract, dict) else []
    expected_paths = {
        artifact.get("path")
        for artifact in artifacts
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str)
    }
    actual_paths: set[str] = set()
    for folder in (source / "MDD" / "Modules", source / "MDD" / "Views"):
        if folder.exists():
            actual_paths.update(path.relative_to(source).as_posix() for path in folder.rglob("*") if path.is_file())
    unexpected = actual_paths - expected_paths
    missing = expected_paths - actual_paths
    if unexpected:
        errors.append(f"存在索引未声明的 MDD：{sorted(unexpected)}")
    if mode == "full" and missing:
        errors.append(f"索引声明但尚未生成的 MDD：{sorted(missing)}")

    action_by_id = {
        action.get("id"): action
        for action in contract.get("actions", [])
        if isinstance(action, dict)
    }
    index_body = strip_contract_blocks(index_text)
    index_terms: list[tuple[str, str]] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        for key, label in (("id", " MDD ID"), ("title", " MDD 标题"), ("path", " MDD 路径")):
            value = artifact.get(key)
            if isinstance(value, str):
                index_terms.append((label, value))
        for provide in artifact.get("provides", []):
            if isinstance(provide, dict) and isinstance(provide.get("id"), str):
                index_terms.append(("产品符号", provide["id"]))
    for action in contract.get("actions", []):
        if not isinstance(action, dict):
            continue
        if isinstance(action.get("id"), str):
            index_terms.append(("动作 ID", action["id"]))
        if isinstance(action.get("signature"), str):
            index_terms.append(("动作签名", action["signature"]))
    require_body_terms(index_path, index_body, index_terms, errors)

    for artifact in artifacts:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str):
            continue
        relative = artifact["path"]
        path = source / Path(*PurePosixPath(relative).parts)
        if not path.is_file():
            continue
        text = read_text(path)
        headings = MODULE_HEADINGS if artifact.get("kind") == "module" else VIEW_HEADINGS
        validate_text(path, text, headings, errors)
        expected_heading = f"# {artifact.get('id')}_{artifact.get('title')}"
        if not text.lstrip().startswith(expected_heading):
            errors.append(f"{path} 一级标题必须为：{expected_heading}")
        embedded = extract_block(text, MDD_BLOCK, path)
        if embedded != artifact:
            errors.append(f"{path} 的结构化 MDD 合同与索引不一致")
        body = strip_contract_blocks(text)
        action_ids = set(artifact.get("actionsOwned", [])) | set(artifact.get("actionsUsed", []))
        for action_id in action_ids:
            action = action_by_id.get(action_id)
            if action_id not in body:
                errors.append(f"{path} 正文未引用动作 ID：{action_id}")
            signature = action.get("signature") if isinstance(action, dict) else None
            if isinstance(signature, str) and signature not in body:
                errors.append(f"{path} 正文未逐字引用 {action_id} 的规范签名：{signature}")
        body_terms: list[tuple[str, str]] = []
        for dependency in artifact.get("dependsOn", []):
            if isinstance(dependency, str):
                body_terms.append(("依赖 MDD", dependency))
        for provide in artifact.get("provides", []):
            if isinstance(provide, dict) and isinstance(provide.get("id"), str):
                body_terms.append(("提供符号", provide["id"]))
        for consume in artifact.get("consumes", []):
            if isinstance(consume, dict) and isinstance(consume.get("symbol"), str):
                body_terms.append(("消费符号", consume["symbol"]))
        files = artifact.get("files", {})
        if isinstance(files, dict):
            for group in FILE_KEYS:
                for file_path in files.get(group, []):
                    if isinstance(file_path, str):
                        body_terms.append(("白名单路径", file_path))
        require_body_terms(path, body, body_terms, errors)

    if errors:
        raise ContractFailure(errors)
    return contract


def validate_workspace(workspace: Path) -> Path:
    workspace = workspace.resolve()
    required_directories = (
        workspace / "Assets",
        workspace / "Packages",
        workspace / "ProjectSettings",
        workspace / "Design" / "Docs",
    )
    required_files = (
        workspace / "Packages" / "manifest.json",
        workspace / "ProjectSettings" / "ProjectVersion.txt",
        workspace / "Design" / "Docs" / "策划案.md",
    )
    missing = [str(path) for path in required_directories if not path.is_dir()]
    missing.extend(str(path) for path in required_files if not path.is_file())
    if missing:
        raise ContractFailure([f"当前工作区缺少必需项目输入：{path}" for path in missing])
    return workspace


def create_stage(workspace: Path) -> Path:
    workspace = validate_workspace(workspace)
    stage = Path(tempfile.mkdtemp(prefix=f"july-design-{workspace.name}-"))
    try:
        (stage / "MDD" / "Modules").mkdir(parents=True)
        (stage / "MDD" / "Views").mkdir(parents=True)
        planning = workspace / "Design" / "Docs" / "策划案.md"
        metadata = {
            "schemaVersion": SCHEMA_VERSION,
            "workspace": str(workspace),
            "planningSha256": sha256_file(planning),
            "projectVersion": read_text(workspace / "ProjectSettings" / "ProjectVersion.txt").strip(),
            "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        }
        (stage / STAGE_META_FILE).write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return stage


def discard_stage(staging: Path) -> None:
    staging = staging.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if staging.parent != temp_root or not staging.name.startswith("july-design-"):
        raise ContractFailure([f"拒绝清理非本工具暂存目录：{staging}"])
    if not staging.is_dir():
        raise ContractFailure([f"暂存目录不存在：{staging}"])
    load_stage_metadata(staging)
    shutil.rmtree(staging)


def remove_exact(path: Path, allowed_parent: Path) -> None:
    resolved_parent = allowed_parent.resolve()
    resolved = path.resolve()
    if resolved.parent != resolved_parent:
        raise ContractFailure([f"拒绝删除非预期路径：{resolved}"])
    if resolved.is_dir():
        shutil.rmtree(resolved)
    elif resolved.exists():
        resolved.unlink()


def publish(staging: Path, workspace: Path) -> None:
    if path_is_link(staging):
        raise ContractFailure([f"暂存目录不能是符号链接或目录联接：{staging}"])
    staging = staging.resolve()
    workspace = validate_workspace(workspace)
    try:
        staging.relative_to(workspace)
    except ValueError:
        pass
    else:
        raise ContractFailure(["暂存目录必须位于目标项目之外"])

    validate_artifacts(staging, "full", "staging", workspace)
    design_root = workspace / "Design"
    docs = design_root / "Docs"
    if tree_contains_links(docs):
        raise ContractFailure([f"正式 Design/Docs 包含符号链接或目录联接，拒绝复制发布：{docs}"])
    stale = sorted(design_root.glob(".july-design-txn-*"))
    if stale:
        raise ContractFailure([f"发现未决设计事务，停止发布并人工核对：{path}" for path in stale])
    txn = design_root / f".july-design-txn-{uuid.uuid4().hex}"
    new_docs = txn / "new-docs"
    old_docs = txn / "old-docs"
    txn.mkdir()
    moved_old = False
    installed_new = False
    cleanup_txn = False
    try:
        shutil.copytree(docs, new_docs)
        remove_exact(new_docs / "GDD.md", new_docs)
        remove_exact(new_docs / "MDD", new_docs)
        remove_exact(new_docs / CONTRACT_FILE, new_docs)
        remove_exact(new_docs / STAGE_META_FILE, new_docs)
        shutil.copy2(staging / "GDD.md", new_docs / "GDD.md")
        shutil.copytree(staging / "MDD", new_docs / "MDD")
        validate_artifacts(new_docs, "full", "published")

        os.replace(docs, old_docs)
        moved_old = True
        os.replace(new_docs, docs)
        installed_new = True
        validate_artifacts(docs, "full", "published")
        cleanup_txn = True
    except Exception as exc:
        rollback_errors: list[str] = []
        if installed_new and docs.exists():
            try:
                remove_exact(docs, design_root)
            except Exception as rollback_exc:  # rollback must report every failure
                rollback_errors.append(f"移除失败的新设计时出错：{rollback_exc}")
        if moved_old and old_docs.exists() and not docs.exists():
            try:
                os.replace(old_docs, docs)
            except Exception as rollback_exc:
                rollback_errors.append(f"恢复旧设计时出错：{rollback_exc}")
        if not rollback_errors and (not moved_old or (docs.exists() and not old_docs.exists())):
            cleanup_txn = True
        details = [f"发布失败，已尝试回滚：{exc}"] + rollback_errors
        raise ContractFailure(details) from exc
    finally:
        if cleanup_txn and txn.exists():
            shutil.rmtree(txn)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-stage", help="在系统临时目录创建隔离设计暂存区")
    create.add_argument("--workspace", required=True, type=Path)

    validate = subparsers.add_parser("validate", help="验证暂存或正式设计产物")
    validate.add_argument("--source", required=True, type=Path)
    validate.add_argument("--mode", choices=("partial", "full"), default="full")
    validate.add_argument("--surface", choices=("staging", "published"), required=True)
    validate.add_argument("--workspace", type=Path)

    publish_parser = subparsers.add_parser("publish", help="验证后事务发布完整设计")
    publish_parser.add_argument("--staging", required=True, type=Path)
    publish_parser.add_argument("--workspace", required=True, type=Path)

    discard = subparsers.add_parser("discard-stage", help="清理由本工具创建的本轮暂存区")
    discard.add_argument("--staging", required=True, type=Path)
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    try:
        if args.command == "create-stage":
            print(create_stage(args.workspace))
        elif args.command == "validate":
            if args.surface == "staging" and args.workspace is None:
                raise ContractFailure(["验证 staging 时必须提供 --workspace"])
            validate_artifacts(args.source, args.mode, args.surface, args.workspace)
            print(f"PASS: {args.mode} {args.surface} design validation: {args.source.resolve()}")
        elif args.command == "publish":
            publish(args.staging, args.workspace)
            print(f"PASS: published complete design to {(args.workspace / 'Design' / 'Docs').resolve()}")
        elif args.command == "discard-stage":
            discard_stage(args.staging)
            print(f"PASS: discarded design staging directory: {args.staging.resolve()}")
        return 0
    except ContractFailure as exc:
        for error in exc.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: 文件系统操作失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
