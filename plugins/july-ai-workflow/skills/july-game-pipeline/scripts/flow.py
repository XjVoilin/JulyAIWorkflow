#!/usr/bin/env python3
"""Manage a July game workflow under DesignDoc/<product>."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 2
STAGES = ("gdd", "gdd_review", "mdd", "implementation", "validation")
STATUSES = {"pending", "in_progress", "done"}
STATE_FILE_NAME = ".july-ai-workflow.json"
STATUS_FILE_NAME = "工作流状态.md"
PLAN_FILE_NAME = "策划案.md"
REQUIRED_MARKERS = (
    Path("Assets"),
    Path("Packages/manifest.json"),
    Path("ProjectSettings/ProjectVersion.txt"),
    Path("Tools/Luban/DataTables"),
)


class FlowError(RuntimeError):
    """An invalid external input or workflow transition."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def validate_project_root(root: Path) -> None:
    missing = [str(marker) for marker in REQUIRED_MARKERS if not (root / marker).exists()]
    if missing:
        raise FlowError(f"Not a standalone July project; missing: {', '.join(missing)}")

    manifest_path = root / "Packages/manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise FlowError(f"Invalid JSON in {manifest_path}: {exc}") from exc

    dependencies = manifest.get("dependencies")
    if not isinstance(dependencies, dict):
        raise FlowError(f"Manifest has no dependencies object: {manifest_path}")

    required_dependencies = ("com.july.arch", "com.code-philosophy.luban")
    missing_dependencies = [name for name in required_dependencies if name not in dependencies]
    if missing_dependencies:
        raise FlowError(
            "Not a supported July/Luban composition; missing dependencies: "
            + ", ".join(missing_dependencies)
        )


def resolve_project_root(value: str | Path) -> Path:
    project_root = Path(value).resolve()
    if not project_root.is_dir():
        raise FlowError(f"Unity project directory does not exist: {project_root}")
    validate_project_root(project_root)
    return project_root


def resolve_design_dir(project_root: Path, product: str) -> Path:
    product = product.strip()
    if not product or product in {".", ".."} or Path(product).name != product:
        raise FlowError("Product must be one directory name under DesignDoc")
    design_dir = (project_root / "DesignDoc" / product).resolve()
    if not design_dir.is_dir():
        raise FlowError(f"Product directory does not exist: {design_dir}")
    if not (design_dir / PLAN_FILE_NAME).is_file():
        raise FlowError(f"Product directory is missing {PLAN_FILE_NAME}: {design_dir}")
    return design_dir


def state_path(design_dir: Path) -> Path:
    return design_dir / STATE_FILE_NAME


def status_path(design_dir: Path) -> Path:
    return design_dir / STATUS_FILE_NAME


def render_status(state: dict[str, Any]) -> str:
    status_names = {"pending": "待开始", "in_progress": "进行中", "done": "已完成"}
    stage_rows = []
    for stage_name in STAGES:
        record = state["stages"][stage_name]
        evidence = "<br>".join(f"`{item}`" for item in record["evidence"]) or "-"
        stage_rows.append(
            f"| `{stage_name}` | {status_names[record['status']]} | {evidence} | "
            f"{record['updated_at'] or '-'} |"
        )

    history_rows = []
    for event in state["history"]:
        detail = event.get("reason") or "<br>".join(event.get("evidence", [])) or "-"
        history_rows.append(
            f"| {event['at']} | `{event['action']}` | `{event.get('stage', '-')}` | {detail} |"
        )

    pending = next_stage(state) or "全部完成"
    return "\n".join(
        [
            "# 工作流状态",
            "",
            "> 此文件由 July AI Workflow 自动生成，请勿手工编辑。",
            "",
            f"- 更新时间：{state['updated_at']}",
            f"- 项目：`{state['project']['product']}`",
            f"- 设计目录：`{state['project']['design_dir']}`",
            f"- 流程起点：`{PLAN_FILE_NAME}`",
            f"- 下一阶段：`{pending}`",
            "",
            "## 阶段",
            "",
            "| 阶段 | 状态 | 证据 | 更新时间 |",
            "|---|---|---|---|",
            *stage_rows,
            "",
            "## 历史",
            "",
            "| 时间 | 动作 | 阶段 | 说明 |",
            "|---|---|---|---|",
            *history_rows,
            "",
        ]
    )


def write_state(design_dir: Path, state: dict[str, Any]) -> None:
    path = state_path(design_dir)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)

    readable_path = status_path(design_dir)
    readable_temporary = readable_path.with_suffix(readable_path.suffix + ".tmp")
    readable_temporary.write_text(render_status(state), encoding="utf-8")
    os.replace(readable_temporary, readable_path)


def load_state(
    project_root: str | Path, product: str
) -> tuple[Path, Path, dict[str, Any]]:
    project_root = resolve_project_root(project_root)
    resolved_design_dir = resolve_design_dir(project_root, product)
    path = state_path(resolved_design_dir)
    if not path.is_file():
        raise FlowError(f"Workflow is not initialized: {path}")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FlowError(f"Invalid workflow JSON in {path}: {exc}") from exc
    validate_state(project_root, resolved_design_dir, state)
    return project_root, resolved_design_dir, state


def normalize_evidence(root: Path, values: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        candidate = Path(value)
        if candidate.is_absolute():
            raise FlowError(f"Evidence must be project-relative: {value}")
        resolved = (root / candidate).resolve()
        try:
            relative = resolved.relative_to(root)
        except ValueError as exc:
            raise FlowError(f"Evidence escapes the project root: {value}") from exc
        if not resolved.is_file():
            raise FlowError(f"Evidence is not a file: {relative.as_posix()}")
        relative_text = relative.as_posix()
        if relative_text not in normalized:
            normalized.append(relative_text)
    if not normalized:
        raise FlowError("At least one evidence path is required")
    return normalized


def validate_pass_report(root: Path, relative_path: str) -> None:
    content = (root / relative_path).read_text(encoding="utf-8")
    pass_pattern = re.compile(r"^\s*-\s*Gate\s*[：:]\s*PASS\s*$", re.MULTILINE)
    if not pass_pattern.search(content):
        raise FlowError(f"Gate report does not declare PASS: {relative_path}")


def artifact_path(state: dict[str, Any], relative_path: str) -> str:
    return (Path(state["project"]["design_dir"]) / relative_path).as_posix()


def validate_stage_evidence(
    root: Path, state: dict[str, Any], stage: str, evidence: list[str]
) -> None:
    expected = {
        "gdd": artifact_path(state, "GDD.md"),
        "gdd_review": artifact_path(state, "QA_GDD.md"),
        "validation": artifact_path(state, "QA/验收报告.md"),
    }
    if stage in expected and expected[stage] not in evidence:
        raise FlowError(f"Stage {stage} requires evidence: {expected[stage]}")

    if stage == "gdd_review":
        validate_pass_report(root, expected[stage])
    elif stage == "mdd":
        required = {
            artifact_path(state, "MDD/索引.md"),
            artifact_path(state, "MDD/进度.md"),
            artifact_path(state, "MDD/资源清单.md"),
        }
        missing = sorted(required.difference(evidence))
        if missing:
            raise FlowError(f"Stage mdd is missing evidence: {', '.join(missing)}")
        module_prefix = re.escape(artifact_path(state, "MDD"))
        module_pattern = re.compile(rf"^{module_prefix}/M\d+_[^/]+\.md$")
        if not any(module_pattern.fullmatch(item) for item in evidence):
            raise FlowError("Stage mdd requires at least one MDD module document")
    elif stage == "implementation":
        progress = artifact_path(state, "MDD/进度.md")
        if progress not in evidence:
            raise FlowError(f"Stage implementation requires evidence: {progress}")
        if len(evidence) < 2:
            raise FlowError("Stage implementation requires progress plus engineering evidence")
    elif stage == "validation":
        validate_pass_report(root, expected[stage])


def validate_state(root: Path, design_dir: Path, state: dict[str, Any]) -> None:
    if state.get("schema_version") != SCHEMA_VERSION:
        raise FlowError(f"Unsupported workflow schema: {state.get('schema_version')}")

    project = state.get("project")
    if not isinstance(project, dict):
        raise FlowError("Workflow project metadata is missing")
    if project.get("product") != design_dir.name:
        raise FlowError(
            f"Workflow product mismatch: {project.get('product')} != {design_dir.name}"
        )
    expected_design_dir = design_dir.relative_to(root).as_posix()
    if project.get("design_dir") != expected_design_dir:
        raise FlowError(
            f"Workflow design directory mismatch: {project.get('design_dir')} != {expected_design_dir}"
        )

    stages = state.get("stages")
    if not isinstance(stages, dict) or tuple(stages.keys()) != STAGES:
        raise FlowError("Workflow stages do not match the supported ordered stage set")

    active_stages: list[str] = []
    previous_done = True
    for stage_name in STAGES:
        record = stages[stage_name]
        if not isinstance(record, dict):
            raise FlowError(f"Stage record is invalid: {stage_name}")
        status = record.get("status")
        evidence = record.get("evidence")
        if status not in STATUSES:
            raise FlowError(f"Stage status is invalid: {stage_name}={status}")
        if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
            raise FlowError(f"Stage evidence is invalid: {stage_name}")
        if status in {"in_progress", "done"} and not previous_done:
            raise FlowError(f"Stage {stage_name} started before its prerequisite completed")
        if status == "in_progress":
            active_stages.append(stage_name)
        if status == "done":
            if not evidence:
                raise FlowError(f"Completed stage has no evidence: {stage_name}")
            normalized = normalize_evidence(root, evidence)
            validate_stage_evidence(root, state, stage_name, normalized)
        elif evidence:
            raise FlowError(f"Incomplete stage retains evidence: {stage_name}")
        previous_done = status == "done"

    if len(active_stages) > 1:
        raise FlowError(f"More than one stage is in progress: {', '.join(active_stages)}")
    if not isinstance(state.get("history"), list):
        raise FlowError("Workflow history is invalid")


def initialize(project_root: str | Path, product: str) -> dict[str, Any]:
    root = resolve_project_root(project_root)
    resolved_design_dir = resolve_design_dir(root, product)
    if state_path(resolved_design_dir).exists():
        raise FlowError(f"Workflow is already initialized: {state_path(resolved_design_dir)}")

    timestamp = utc_now()
    state = {
        "schema_version": SCHEMA_VERSION,
        "project": {
            "product": product.strip(),
            "design_dir": resolved_design_dir.relative_to(root).as_posix(),
        },
        "created_at": timestamp,
        "updated_at": timestamp,
        "stages": {
            stage: {"status": "pending", "evidence": [], "updated_at": None}
            for stage in STAGES
        },
        "history": [{"at": timestamp, "action": "init"}],
    }
    write_state(resolved_design_dir, state)
    return state


def stage_index(stage: str) -> int:
    try:
        return STAGES.index(stage)
    except ValueError as exc:
        raise FlowError(f"Unknown stage: {stage}") from exc


def start_stage(project_root: str | Path, product: str, stage: str) -> dict[str, Any]:
    _, resolved_design_dir, state = load_state(project_root, product)
    index = stage_index(stage)
    record = state["stages"][stage]
    if record["status"] != "pending":
        raise FlowError(f"Stage is not pending: {stage}={record['status']}")
    if index > 0 and state["stages"][STAGES[index - 1]]["status"] != "done":
        raise FlowError(f"Prerequisite stage is incomplete: {STAGES[index - 1]}")
    if any(item["status"] == "in_progress" for item in state["stages"].values()):
        raise FlowError("Another stage is already in progress")

    timestamp = utc_now()
    record["status"] = "in_progress"
    record["updated_at"] = timestamp
    state["updated_at"] = timestamp
    state["history"].append({"at": timestamp, "action": "start", "stage": stage})
    write_state(resolved_design_dir, state)
    return state


def complete_stage(
    project_root: str | Path, product: str, stage: str, evidence: Iterable[str]
) -> dict[str, Any]:
    root, resolved_design_dir, state = load_state(project_root, product)
    stage_index(stage)
    record = state["stages"][stage]
    if record["status"] != "in_progress":
        raise FlowError(f"Stage is not in progress: {stage}={record['status']}")
    normalized = normalize_evidence(root, evidence)
    validate_stage_evidence(root, state, stage, normalized)

    timestamp = utc_now()
    record["status"] = "done"
    record["evidence"] = normalized
    record["updated_at"] = timestamp
    state["updated_at"] = timestamp
    state["history"].append(
        {"at": timestamp, "action": "complete", "stage": stage, "evidence": normalized}
    )
    write_state(resolved_design_dir, state)
    return state


def reopen_stage(
    project_root: str | Path, product: str, stage: str, reason: str
) -> dict[str, Any]:
    _, resolved_design_dir, state = load_state(project_root, product)
    index = stage_index(stage)
    if not reason.strip():
        raise FlowError("Reopen reason cannot be empty")
    if index > 0 and state["stages"][STAGES[index - 1]]["status"] != "done":
        raise FlowError(f"Cannot reopen {stage}; prerequisite is incomplete: {STAGES[index - 1]}")

    timestamp = utc_now()
    for offset, stage_name in enumerate(STAGES[index:]):
        record = state["stages"][stage_name]
        record["status"] = "in_progress" if offset == 0 else "pending"
        record["evidence"] = []
        record["updated_at"] = timestamp
    state["updated_at"] = timestamp
    state["history"].append(
        {"at": timestamp, "action": "reopen", "stage": stage, "reason": reason.strip()}
    )
    write_state(resolved_design_dir, state)
    return state


def next_stage(state: dict[str, Any]) -> str | None:
    for stage_name in STAGES:
        if state["stages"][stage_name]["status"] != "done":
            return stage_name
    return None


def print_status(state: dict[str, Any]) -> None:
    project = state["project"]
    print(f"Product: {project['product']}")
    print(f"Design directory: {project['design_dir']}")
    for stage_name in STAGES:
        print(f"{stage_name:14} {state['stages'][stage_name]['status']}")
    print(f"Next: {next_stage(state) or 'complete'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("init", "status", "validate"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--project-root", default=".")
        command_parser.add_argument("--product", required=True)

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--project-root", default=".")
    start_parser.add_argument("--product", required=True)
    start_parser.add_argument("--stage", required=True, choices=STAGES)

    complete_parser = subparsers.add_parser("complete")
    complete_parser.add_argument("--project-root", default=".")
    complete_parser.add_argument("--product", required=True)
    complete_parser.add_argument("--stage", required=True, choices=STAGES)
    complete_parser.add_argument("--evidence", action="append", required=True)

    reopen_parser = subparsers.add_parser("reopen")
    reopen_parser.add_argument("--project-root", default=".")
    reopen_parser.add_argument("--product", required=True)
    reopen_parser.add_argument("--stage", required=True, choices=STAGES)
    reopen_parser.add_argument("--reason", required=True)
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = Path(args.project_root)

    if args.command == "init":
        state = initialize(project_root, args.product)
    elif args.command == "status":
        _, _, state = load_state(project_root, args.product)
    elif args.command == "validate":
        _, _, state = load_state(project_root, args.product)
        print_status(state)
        print("Validation: passed")
        return 0
    elif args.command == "start":
        state = start_stage(project_root, args.product, args.stage)
    elif args.command == "complete":
        state = complete_stage(project_root, args.product, args.stage, args.evidence)
    else:
        state = reopen_stage(project_root, args.product, args.stage, args.reason)
    print_status(state)
    return 0


def main() -> None:
    try:
        raise SystemExit(run())
    except FlowError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
