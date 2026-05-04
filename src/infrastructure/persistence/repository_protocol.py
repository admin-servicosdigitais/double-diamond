from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from src.domain.models.workflow import WorkflowState


class WorkflowRepositoryProtocol(Protocol):
    def create_workflow(self, workflow: WorkflowState) -> WorkflowState: ...

    def get_workflow(self, workflow_id: str) -> WorkflowState: ...

    def save_stage_input(self, workflow_id: str, stage: str, payload: dict[str, Any]) -> Path: ...

    def save_stage_output(
        self,
        workflow_id: str,
        stage: str,
        compact_output_text: str,
        full_outputs: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, str]: ...

    def list_workflows(self) -> list[WorkflowState]: ...

    def update_stage_status(
        self,
        workflow_id: str,
        stage: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowState: ...

    def get_stage_outputs(self, workflow_id: str, stage: str) -> dict[str, Any]: ...

    def get_stage_artifact(self, workflow_id: str, stage: str, artifact: str) -> dict[str, Any]: ...

    def update_stage_artifact(self, workflow_id: str, stage: str, artifact: str, content: str) -> dict[str, Any]: ...

    def read_stage_compact_output(self, workflow_id: str, stage: str) -> str | None: ...

    def read_stage_full_outputs(self, workflow_id: str, stage: str) -> dict[str, str] | None: ...

    def get_stage_quality_gate(self, workflow_id: str, stage: str) -> dict[str, Any] | None: ...

    def save_stage_quality_gate(self, workflow_id: str, stage: str, quality_gate: dict[str, Any]) -> dict[str, Any]: ...
