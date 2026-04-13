from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.routes import workflows as workflow_routes
from src.application.services.workflow_service import WorkflowService
from src.infrastructure.persistence.sqlite_workflow_repository import SQLiteWorkflowRepository
from src.infrastructure.persistence.workflow_repository import WorkflowRepository
from src.main import create_app


@pytest.fixture(autouse=True)
def _mock_agno_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGNO_MOCK", "1")


@pytest.fixture(params=["filesystem", "sqlite"])
def client_and_service(tmp_path: Path, request: pytest.FixtureRequest) -> tuple[TestClient, WorkflowService]:
    if request.param == "sqlite":
        repository = SQLiteWorkflowRepository(db_path=tmp_path / "workflows.db")
    else:
        repository = WorkflowRepository(base_path=tmp_path / "workflows")

    service = WorkflowService(repository=repository)
    app = create_app()
    workflow_routes.workflow_service = service
    return TestClient(app), service


def _prepare_stage_with_outputs(service: WorkflowService) -> tuple[str, str, str]:
    workflow_id = "wf-artifacts"
    service.create_workflow(workflow_id, words=["saude"])
    outputs = service.get_stage_outputs(workflow_id, "1-explorer")
    artifact = next(path.split("/")[-1] for path in outputs["full_output_paths"] if "resumo" in path.lower())
    return workflow_id, "1-explorer", artifact


def test_get_stage_artifact_returns_content_and_metadata(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id, stage, artifact = _prepare_stage_with_outputs(service)

    response = client.get(f"/workflows/{workflow_id}/stages/{stage}/outputs/{artifact}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["artifact"] == artifact
    assert payload["content"]
    assert payload["metadata"]["stage"] == stage


def test_patch_stage_artifact_regenerates_compact(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id, stage, artifact = _prepare_stage_with_outputs(service)
    patched_content = "# Novo resumo validado"

    before = service.get_stage_outputs(workflow_id, stage)["metadata"]["updated_at"]
    response = client.patch(
        f"/workflows/{workflow_id}/stages/{stage}/outputs/{artifact}",
        json={"content": patched_content},
    )
    after_outputs = service.get_stage_outputs(workflow_id, stage)

    assert response.status_code == 200
    assert response.json()["content"] == patched_content
    assert after_outputs["compact_output_text"] == patched_content
    assert after_outputs["metadata"]["updated_at"] != before


def test_patch_stage_artifact_requires_awaiting_approval(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id, stage, artifact = _prepare_stage_with_outputs(service)
    service.approve_stage(workflow_id, stage)

    response = client.patch(
        f"/workflows/{workflow_id}/stages/{stage}/outputs/{artifact}",
        json={"content": "tentativa inválida"},
    )

    assert response.status_code == 409
    assert "awaiting_human_approval" in response.json()["detail"]


def test_artifact_not_found_returns_404(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id, stage, _ = _prepare_stage_with_outputs(service)

    response = client.get(f"/workflows/{workflow_id}/stages/{stage}/outputs/inexistente.md")

    assert response.status_code == 404
