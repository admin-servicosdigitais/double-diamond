from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from src.domain.models.workflow import StageState, StageStatus, WorkflowState, can_transition


class SQLiteWorkflowRepository:
    """SQLite-backed repository for workflow state and stage artifacts."""

    def __init__(self, db_path: str | Path = "data/workflows/workflows.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS stage_inputs (
                    workflow_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (workflow_id, stage)
                );

                CREATE TABLE IF NOT EXISTS stage_outputs (
                    workflow_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    compact_output_text TEXT NOT NULL,
                    full_outputs_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (workflow_id, stage)
                );
                """
            )

    def create_workflow(self, workflow: WorkflowState) -> WorkflowState:
        payload = workflow.model_dump(mode="json")
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO workflows (id, state_json, updated_at) VALUES (?, ?, ?)",
                (workflow.id, json.dumps(payload, ensure_ascii=False), now),
            )
        return workflow

    def get_workflow(self, workflow_id: str) -> WorkflowState:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT state_json FROM workflows WHERE id = ?",
                (workflow_id,),
            ).fetchone()

        if row is None:
            raise FileNotFoundError(f"Workflow '{workflow_id}' not found")

        return WorkflowState.model_validate(json.loads(row["state_json"]))

    def list_workflows(self) -> list[WorkflowState]:
        with self._connect() as conn:
            rows = conn.execute("SELECT state_json FROM workflows ORDER BY id").fetchall()

        return [WorkflowState.model_validate(json.loads(row["state_json"])) for row in rows]

    def save_stage_input(self, workflow_id: str, stage: str, payload: dict[str, Any]) -> Path:
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO stage_inputs (workflow_id, stage, payload_json, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(workflow_id, stage)
                DO UPDATE SET payload_json = excluded.payload_json, updated_at = excluded.updated_at
                """,
                (workflow_id, stage, json.dumps(payload, ensure_ascii=False), now),
            )

        return Path(f"sqlite://{workflow_id}/stages/{stage}/input.json")

    def save_stage_output(
        self,
        workflow_id: str,
        stage: str,
        compact_output_text: str,
        full_outputs: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        full_outputs = full_outputs or {}
        full_output_paths = [f"sqlite://{workflow_id}/stages/{stage}/output_full/{name}" for name in sorted(full_outputs)]
        metadata_payload = {
            "workflow_id": workflow_id,
            "stage": stage,
            "compact_output_path": f"sqlite://{workflow_id}/stages/{stage}/output_compact.md",
            "full_output_paths": full_output_paths,
            "updated_at": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }

        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO stage_outputs (workflow_id, stage, compact_output_text, full_outputs_json, metadata_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(workflow_id, stage)
                DO UPDATE SET
                    compact_output_text = excluded.compact_output_text,
                    full_outputs_json = excluded.full_outputs_json,
                    metadata_json = excluded.metadata_json,
                    updated_at = excluded.updated_at
                """,
                (
                    workflow_id,
                    stage,
                    compact_output_text,
                    json.dumps(full_outputs, ensure_ascii=False),
                    json.dumps(metadata_payload, ensure_ascii=False),
                    now,
                ),
            )

        return {
            "compact_output_path": metadata_payload["compact_output_path"],
            "metadata_path": f"sqlite://{workflow_id}/stages/{stage}/metadata.json",
            "output_full_path": f"sqlite://{workflow_id}/stages/{stage}/output_full",
            "full_output_paths": full_output_paths,
        }

    def update_stage_status(
        self,
        workflow_id: str,
        stage: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowState:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT state_json FROM workflows WHERE id = ?",
                (workflow_id,),
            ).fetchone()

            if row is None:
                raise FileNotFoundError(f"Workflow '{workflow_id}' not found")

            workflow = WorkflowState.model_validate(json.loads(row["state_json"]))
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

            conn.execute(
                "UPDATE workflows SET state_json = ?, updated_at = ? WHERE id = ?",
                (
                    json.dumps(workflow.model_dump(mode="json"), ensure_ascii=False),
                    now.isoformat(),
                    workflow_id,
                ),
            )
            conn.execute("COMMIT")

        return workflow

    def get_stage_outputs(self, workflow_id: str, stage: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT compact_output_text, full_outputs_json, metadata_json FROM stage_outputs WHERE workflow_id = ? AND stage = ?",
                (workflow_id, stage),
            ).fetchone()

        if row is None:
            raise FileNotFoundError(f"Stage '{stage}' not found in workflow '{workflow_id}'")

        return {
            "workflow_id": workflow_id,
            "stage": stage,
            "compact_output_text": row["compact_output_text"],
            "full_output_paths": json.loads(row["metadata_json"]).get("full_output_paths", []),
            "metadata": json.loads(row["metadata_json"]),
        }

    def get_stage_artifact(self, workflow_id: str, stage: str, artifact: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT full_outputs_json, metadata_json FROM stage_outputs WHERE workflow_id = ? AND stage = ?",
                (workflow_id, stage),
            ).fetchone()

        if row is None:
            raise FileNotFoundError(f"Stage '{stage}' not found in workflow '{workflow_id}'")

        full_outputs = json.loads(row["full_outputs_json"])
        if artifact not in full_outputs:
            raise FileNotFoundError(f"Artifact '{artifact}' not found in stage '{stage}' for workflow '{workflow_id}'")

        return {
            "workflow_id": workflow_id,
            "stage": stage,
            "artifact": artifact,
            "content": str(full_outputs[artifact]),
            "metadata": json.loads(row["metadata_json"]),
        }

    def update_stage_artifact(self, workflow_id: str, stage: str, artifact: str, content: str) -> dict[str, Any]:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT compact_output_text, full_outputs_json, metadata_json FROM stage_outputs WHERE workflow_id = ? AND stage = ?",
                (workflow_id, stage),
            ).fetchone()

            if row is None:
                conn.execute("ROLLBACK")
                raise FileNotFoundError(f"Stage '{stage}' not found in workflow '{workflow_id}'")

            full_outputs = json.loads(row["full_outputs_json"])
            if artifact not in full_outputs:
                conn.execute("ROLLBACK")
                raise FileNotFoundError(f"Artifact '{artifact}' not found in stage '{stage}' for workflow '{workflow_id}'")

            full_outputs[artifact] = content
            canonical_key = self._find_canonical_key(full_outputs)
            compact_output = str(full_outputs[canonical_key]) if canonical_key else str(row["compact_output_text"])

            metadata = json.loads(row["metadata_json"])
            metadata["updated_at"] = datetime.utcnow().isoformat()

            now = datetime.utcnow().isoformat()
            conn.execute(
                """
                UPDATE stage_outputs
                SET compact_output_text = ?, full_outputs_json = ?, metadata_json = ?, updated_at = ?
                WHERE workflow_id = ? AND stage = ?
                """,
                (
                    compact_output,
                    json.dumps(full_outputs, ensure_ascii=False),
                    json.dumps(metadata, ensure_ascii=False),
                    now,
                    workflow_id,
                    stage,
                ),
            )
            conn.execute("COMMIT")

        return self.get_stage_artifact(workflow_id, stage, artifact)

    def read_stage_compact_output(self, workflow_id: str, stage: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT compact_output_text FROM stage_outputs WHERE workflow_id = ? AND stage = ?",
                (workflow_id, stage),
            ).fetchone()

        if row is None:
            return None

        return str(row["compact_output_text"]).strip()

    def read_stage_full_outputs(self, workflow_id: str, stage: str) -> dict[str, str] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT full_outputs_json FROM stage_outputs WHERE workflow_id = ? AND stage = ?",
                (workflow_id, stage),
            ).fetchone()

        if row is None:
            return None

        outputs = json.loads(row["full_outputs_json"])
        if not isinstance(outputs, dict):
            return None

        return {str(k): str(v) for k, v in outputs.items()} or None

    @staticmethod
    def _find_canonical_key(full_outputs: dict[str, Any]) -> str | None:
        sorted_keys = sorted(str(key) for key in full_outputs.keys())

        for key in sorted_keys:
            if "resumo" in key.lower():
                return key

        for key in sorted_keys:
            if "trade-offs" not in key.lower():
                return key

        if sorted_keys:
            return sorted_keys[0]

        return None
