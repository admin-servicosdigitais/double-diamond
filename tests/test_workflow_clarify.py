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


def test_clarify_stage_success(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id = "wf-clarify-ok"
    service.create_workflow(workflow_id, words=["saude", "fintech"])

    response = client.post(f"/workflows/{workflow_id}/stages/1-explorer/clarify")

    assert response.status_code == 200
    payload = response.json()
    assert payload["diagnosis"]
    assert isinstance(payload["gaps"], list)
    assert isinstance(payload["required_questions"], list)
    assert isinstance(payload["optional_questions"], list)
    assert payload["recommendation"] in {"approve", "review_before_approve", "block_approval"}

    gate = service.get_stage_quality_gate(workflow_id, "1-explorer")
    assert gate.status == "questions_generated"
    assert len(gate.questions) >= len(payload["required_questions"])
    assert gate.recommendation == payload["recommendation"]


def test_clarify_stage_requires_awaiting_human_approval(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id = "wf-clarify-409"
    service.create_workflow(workflow_id, words=[])

    response = client.post(f"/workflows/{workflow_id}/stages/1-explorer/clarify")

    assert response.status_code == 409
    assert "awaiting_human_approval" in response.json()["detail"]


def test_clarify_answer_success(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id = "wf-clarify-answer-ok"
    service.create_workflow(workflow_id, words=["saude"])
    client.post(f"/workflows/{workflow_id}/stages/1-explorer/clarify")

    response = client.post(
        f"/workflows/{workflow_id}/stages/1-explorer/clarify/answer",
        json={"answers": [{"question_id": "q1", "answer": "Resposta consolidada"}]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "answered"
    assert payload["answers"] == [{"question_id": "q1", "answer": "Resposta consolidada"}]


def test_clarify_answer_requires_generated_quality_gate(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id = "wf-clarify-answer-no-gate"
    service.create_workflow(workflow_id, words=["saude"])

    response = client.post(
        f"/workflows/{workflow_id}/stages/1-explorer/clarify/answer",
        json={"answers": [{"question_id": "q1", "answer": "Resposta"}]},
    )

    assert response.status_code == 409
    assert "quality gate gerado" in response.json()["detail"]


def test_clarify_answer_requires_awaiting_human_approval(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id = "wf-clarify-answer-409"
    service.create_workflow(workflow_id, words=[])

    response = client.post(
        f"/workflows/{workflow_id}/stages/1-explorer/clarify/answer",
        json={"answers": [{"question_id": "q1", "answer": "Resposta"}]},
    )

    assert response.status_code == 409
    assert "awaiting_human_approval" in response.json()["detail"]


def test_clarify_skip_success(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id = "wf-clarify-skip-ok"
    service.create_workflow(workflow_id, words=["saude"])

    response = client.post(
        f"/workflows/{workflow_id}/stages/1-explorer/clarify/skip",
        json={"reason": "deadline curto no MVP"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "skipped"
    assert payload["skip_reason"] == "deadline curto no MVP"


def test_clarify_skip_invalid_stage_returns_404(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id = "wf-clarify-skip-invalid"
    service.create_workflow(workflow_id, words=["saude"])

    response = client.post(
        f"/workflows/{workflow_id}/stages/99-inexistente/clarify/skip",
        json={"reason": "nao existe"},
    )

    assert response.status_code == 404


def test_clarify_skip_requires_awaiting_human_approval(client_and_service: tuple[TestClient, WorkflowService]) -> None:
    client, service = client_and_service
    workflow_id = "wf-clarify-skip-409"
    service.create_workflow(workflow_id, words=[])

    response = client.post(
        f"/workflows/{workflow_id}/stages/1-explorer/clarify/skip",
        json={"reason": "sem execução"},
    )

    assert response.status_code == 409
    assert "awaiting_human_approval" in response.json()["detail"]
