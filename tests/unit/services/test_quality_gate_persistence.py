from pathlib import Path

import pytest

from src.application.services.workflow_service import WorkflowService
from src.domain.models.quality_gate import QualityGateRecommendation, QualityGateState, QualityGateStatus
from src.infrastructure.persistence.sqlite_workflow_repository import SQLiteWorkflowRepository
from src.infrastructure.persistence.workflow_repository import WorkflowRepository


@pytest.fixture(params=["filesystem", "sqlite"])
def service(tmp_path: Path, request: pytest.FixtureRequest) -> WorkflowService:
    if request.param == "sqlite":
        repository = SQLiteWorkflowRepository(db_path=tmp_path / "workflows.db")
    else:
        repository = WorkflowRepository(base_path=tmp_path / "workflows")

    return WorkflowService(repository=repository)


def test_quality_gate_defaults_and_persists(service: WorkflowService) -> None:
    workflow_id = "wf-quality-gate"
    service.create_workflow(workflow_id, words=[])

    default_gate = service.get_stage_quality_gate(workflow_id, "1-explorer")
    assert default_gate.status == QualityGateStatus.NOT_STARTED
    assert default_gate.questions == []
    assert default_gate.answers == []

    updated = QualityGateState(
        status=QualityGateStatus.ANSWERED,
        questions=["Q1"],
        answers=[{"question_id": "q1", "answer": "A1"}],
        recommendation=QualityGateRecommendation.APPROVE,
        created_at=default_gate.created_at,
    )
    saved = service.save_stage_quality_gate(workflow_id, "1-explorer", updated)

    loaded = service.get_stage_quality_gate(workflow_id, "1-explorer")
    assert saved.status == QualityGateStatus.ANSWERED
    assert loaded.questions == ["Q1"]
    assert loaded.answers == [{"question_id": "q1", "answer": "A1"}]
    assert loaded.recommendation == QualityGateRecommendation.APPROVE
