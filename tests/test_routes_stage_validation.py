from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.routes import workflows as workflow_routes
from src.application.services.workflow_service import WorkflowService
from src.infrastructure.persistence.workflow_repository import WorkflowRepository
from src.main import create_app


@pytest.fixture(autouse=True)
def _mock_agno_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGNO_MOCK", "1")


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    repository = WorkflowRepository(base_path=tmp_path / "workflows")
    service = WorkflowService(repository=repository)
    app = create_app()
    workflow_routes.workflow_service = service
    return TestClient(app)


@pytest.mark.parametrize(
    "stage_value",
    ["2", "abc", "2-", "2_intake", "Stage2", "2-INTAKE", " 2-intake", "intake-2"],
)
def test_stage_path_param_rejects_non_composite_format(client: TestClient, stage_value: str) -> None:
    response = client.post(f"/workflows/wf-test/stages/{stage_value}/run", json={})
    assert response.status_code == 422, (
        f"Esperado 422 para stage={stage_value!r}, recebido {response.status_code}: {response.text}"
    )


@pytest.mark.parametrize(
    "stage_value",
    ["1-explorer", "2-intake", "8-prototype-visual", "9-definicao"],
)
def test_stage_path_param_accepts_composite_format(client: TestClient, stage_value: str) -> None:
    # Workflow não existe ainda — esperamos 4xx do service (404), NÃO 422 do validator.
    response = client.post(f"/workflows/wf-test/stages/{stage_value}/run", json={})
    assert response.status_code != 422, (
        f"Stage composto {stage_value!r} foi rejeitado pelo validator: {response.text}"
    )
