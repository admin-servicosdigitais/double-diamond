from __future__ import annotations

import fcntl
import json
import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from src.domain.models.workflow import StageState, StageStatus, WorkflowState, can_transition


class WorkflowRepository:
    def __init__(self, base_path: str | Path = "data/workflows") -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_workflow(self, workflow: WorkflowState) -> WorkflowState:
        workflow_dir = self._workflow_dir(workflow.id)
        (workflow_dir / "stages").mkdir(parents=True, exist_ok=True)
        self._write_json_atomic(workflow_dir / "state.json", workflow.model_dump(mode="json"))
        return workflow

    def get_workflow(self, workflow_id: str) -> WorkflowState:
        state_file = self._workflow_dir(workflow_id) / "state.json"
        if not state_file.exists():
            raise FileNotFoundError(f"Workflow '{workflow_id}' not found")

        data = json.loads(state_file.read_text(encoding="utf-8"))
        return WorkflowState.model_validate(data)

    def list_workflows(self) -> list[WorkflowState]:
        workflows: list[WorkflowState] = []
        for workflow_dir in sorted(self.base_path.iterdir()):
            if not workflow_dir.is_dir():
                continue

            state_file = workflow_dir / "state.json"
            if not state_file.exists():
                continue

            data = json.loads(state_file.read_text(encoding="utf-8"))
            workflows.append(WorkflowState.model_validate(data))

        return workflows

    def save_stage_input(self, workflow_id: str, stage: str, payload: dict[str, Any]) -> Path:
        stage_dir = self._stage_dir(workflow_id, stage)
        stage_dir.mkdir(parents=True, exist_ok=True)
        input_path = stage_dir / "input.json"
        self._write_json_atomic(input_path, payload)
        return input_path

    def save_stage_output(
        self,
        workflow_id: str,
        stage: str,
        compact_output_text: str,
        full_outputs: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        stage_dir = self._stage_dir(workflow_id, stage)
        output_full_dir = stage_dir / "output_full"
        output_full_dir.mkdir(parents=True, exist_ok=True)

        compact_path = stage_dir / "output_compact.md"
        self._write_text_atomic(compact_path, compact_output_text)

        full_output_paths: list[str] = []
        for filename, content in (full_outputs or {}).items():
            file_path = output_full_dir / filename
            self._write_text_atomic(file_path, content)
            full_output_paths.append(str(file_path))

        metadata_path = stage_dir / "metadata.json"
        metadata_payload = {
            "workflow_id": workflow_id,
            "stage": stage,
            "compact_output_path": str(compact_path),
            "full_output_paths": full_output_paths,
            "updated_at": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }
        self._write_json_atomic(metadata_path, metadata_payload)

        return {
            "compact_output_path": str(compact_path),
            "metadata_path": str(metadata_path),
            "output_full_path": str(output_full_dir),
            "full_output_paths": full_output_paths,
        }

    def update_stage_status(
        self,
        workflow_id: str,
        stage: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowState:
        with self._workflow_lock(workflow_id):
            workflow = self.get_workflow(workflow_id)
            now = datetime.utcnow()
            target_status = StageStatus(status)

            target = next((item for item in workflow.stages if item.id == stage), None)
            if target is None:
                if not can_transition(None, target_status):
                    raise ValueError(f"Invalid initial status transition for stage '{stage}': {target_status.value}")
                target = StageState(id=stage, name=stage, status=target_status, metadata=metadata or {})
                workflow.stages.append(target)
            else:
                current_status = StageStatus(target.status)
                if not can_transition(current_status, target_status):
                    raise ValueError(
                        f"Invalid status transition for stage '{stage}': {current_status.value} -> {target_status.value}"
                    )
                target.status = target_status
                target.updated_at = now
                if metadata:
                    target.metadata.update(metadata)

            workflow.updated_at = now
            self._write_json_atomic(
                self._workflow_dir(workflow_id) / "state.json",
                workflow.model_dump(mode="json"),
            )
            return workflow

    def get_stage_outputs(self, workflow_id: str, stage: str) -> dict[str, Any]:
        stage_dir = self._stage_dir(workflow_id, stage)
        if not stage_dir.exists():
            raise FileNotFoundError(f"Stage '{stage}' not found in workflow '{workflow_id}'")

        compact_path = stage_dir / "output_compact.md"
        metadata_path = stage_dir / "metadata.json"
        output_full_dir = stage_dir / "output_full"

        metadata: dict[str, Any] = {}
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        full_outputs = []
        if output_full_dir.exists():
            full_outputs = [str(path) for path in sorted(output_full_dir.iterdir()) if path.is_file()]

        compact_output_text = compact_path.read_text(encoding="utf-8") if compact_path.exists() else ""

        return {
            "workflow_id": workflow_id,
            "stage": stage,
            "compact_output_text": compact_output_text,
            "full_output_paths": full_outputs,
            "metadata": metadata,
        }

    def get_stage_artifact(self, workflow_id: str, stage: str, artifact: str) -> dict[str, Any]:
        stage_dir = self._stage_dir(workflow_id, stage)
        if not stage_dir.exists():
            raise FileNotFoundError(f"Stage '{stage}' not found in workflow '{workflow_id}'")

        artifact_path = stage_dir / "output_full" / artifact
        if not artifact_path.exists() or not artifact_path.is_file():
            raise FileNotFoundError(f"Artifact '{artifact}' not found in stage '{stage}' for workflow '{workflow_id}'")

        metadata = self._read_stage_metadata(stage_dir)
        return {
            "workflow_id": workflow_id,
            "stage": stage,
            "artifact": artifact,
            "content": artifact_path.read_text(encoding="utf-8"),
            "metadata": metadata,
        }

    def update_stage_artifact(self, workflow_id: str, stage: str, artifact: str, content: str) -> dict[str, Any]:
        stage_dir = self._stage_dir(workflow_id, stage)
        if not stage_dir.exists():
            raise FileNotFoundError(f"Stage '{stage}' not found in workflow '{workflow_id}'")

        artifact_path = stage_dir / "output_full" / artifact
        if not artifact_path.exists() or not artifact_path.is_file():
            raise FileNotFoundError(f"Artifact '{artifact}' not found in stage '{stage}' for workflow '{workflow_id}'")

        self._write_text_atomic(artifact_path, content)

        summary_file = self._find_summary_artifact(stage_dir / "output_full")
        if summary_file is not None:
            compact_content = summary_file.read_text(encoding="utf-8")
            self._write_text_atomic(stage_dir / "output_compact.md", compact_content)

        metadata = self._read_stage_metadata(stage_dir)
        metadata["updated_at"] = datetime.utcnow().isoformat()
        self._write_json_atomic(stage_dir / "metadata.json", metadata)

        return self.get_stage_artifact(workflow_id, stage, artifact)

    def read_stage_compact_output(self, workflow_id: str, stage: str) -> str | None:
        compact_path = self._stage_dir(workflow_id, stage) / "output_compact.md"
        if not compact_path.exists():
            return None
        return compact_path.read_text(encoding="utf-8").strip()

    def read_stage_full_outputs(self, workflow_id: str, stage: str) -> dict[str, str] | None:
        output_full_dir = self._stage_dir(workflow_id, stage) / "output_full"
        if not output_full_dir.exists():
            return None

        outputs: dict[str, str] = {}
        for file_path in sorted(output_full_dir.iterdir()):
            if file_path.is_file():
                outputs[file_path.name] = file_path.read_text(encoding="utf-8")

        return outputs or None

    def _workflow_dir(self, workflow_id: str) -> Path:
        return self.base_path / workflow_id

    def _stage_dir(self, workflow_id: str, stage: str) -> Path:
        return self._workflow_dir(workflow_id) / "stages" / stage

    @staticmethod
    def _find_summary_artifact(output_full_dir: Path) -> Path | None:
        if not output_full_dir.exists():
            return None

        for path in sorted(output_full_dir.iterdir()):
            if path.is_file() and "resumo" in path.name.lower():
                return path
        return None

    @staticmethod
    def _read_stage_metadata(stage_dir: Path) -> dict[str, Any]:
        metadata_path = stage_dir / "metadata.json"
        if not metadata_path.exists():
            return {}
        return json.loads(metadata_path.read_text(encoding="utf-8"))

    @contextmanager
    def _workflow_lock(self, workflow_id: str) -> Iterator[None]:
        lock_file = self._workflow_dir(workflow_id) / ".state.lock"
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        with lock_file.open("w", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    @staticmethod
    def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
        content = json.dumps(payload, ensure_ascii=False, indent=2)
        WorkflowRepository._write_text_atomic(path, content)

    @staticmethod
    def _write_text_atomic(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f"{path.suffix}.tmp-{os.getpid()}")
        temp_path.write_text(content, encoding="utf-8")
        os.replace(temp_path, path)
