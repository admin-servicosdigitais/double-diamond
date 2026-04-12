import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.domain.models.workflow import StageState, WorkflowState


class WorkflowRepository:
    def __init__(self, base_path: str | Path = "data/workflows") -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_workflow(self, workflow: WorkflowState) -> WorkflowState:
        workflow_dir = self._workflow_dir(workflow.id)
        (workflow_dir / "stages").mkdir(parents=True, exist_ok=True)
        self._write_json(workflow_dir / "state.json", workflow.model_dump(mode="json"))
        return workflow

    def get_workflow(self, workflow_id: str) -> WorkflowState:
        state_file = self._workflow_dir(workflow_id) / "state.json"
        if not state_file.exists():
            raise FileNotFoundError(f"Workflow '{workflow_id}' not found")

        data = json.loads(state_file.read_text(encoding="utf-8"))
        return WorkflowState.model_validate(data)

    def save_stage_input(self, workflow_id: str, stage: str, payload: dict[str, Any]) -> Path:
        stage_dir = self._stage_dir(workflow_id, stage)
        stage_dir.mkdir(parents=True, exist_ok=True)
        input_path = stage_dir / "input.json"
        self._write_json(input_path, payload)
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
        compact_path.write_text(compact_output_text, encoding="utf-8")

        full_output_paths: list[str] = []
        for filename, content in (full_outputs or {}).items():
            file_path = output_full_dir / filename
            file_path.write_text(content, encoding="utf-8")
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
        self._write_json(metadata_path, metadata_payload)

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
        workflow = self.get_workflow(workflow_id)
        now = datetime.utcnow()

        target = next((item for item in workflow.stages if item.id == stage), None)
        if target is None:
            target = StageState(id=stage, name=stage, status=status, metadata=metadata or {})
            workflow.stages.append(target)
        else:
            target.status = status
            target.updated_at = now
            if metadata:
                target.metadata.update(metadata)

        workflow.updated_at = now
        self._write_json(
            self._workflow_dir(workflow_id) / "state.json",
            workflow.model_dump(mode="json"),
        )
        return workflow

    def _workflow_dir(self, workflow_id: str) -> Path:
        return self.base_path / workflow_id

    def _stage_dir(self, workflow_id: str, stage: str) -> Path:
        return self._workflow_dir(workflow_id) / "stages" / stage

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
