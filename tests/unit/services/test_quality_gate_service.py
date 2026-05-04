from pathlib import Path

import pytest

from src.application.services.quality_gate_service import QualityGateService
from src.infrastructure.persistence.sqlite_workflow_repository import SQLiteWorkflowRepository
from src.infrastructure.persistence.workflow_repository import WorkflowRepository


@pytest.fixture(params=["filesystem", "sqlite"])
def repo(tmp_path: Path, request: pytest.FixtureRequest):
    if request.param == "sqlite":
        return SQLiteWorkflowRepository(db_path=tmp_path / "workflows.db")
    return WorkflowRepository(base_path=tmp_path / "workflows")


def test_generate_quality_gate_with_full_outputs(repo) -> None:
    workflow_id = "wf-qg-service"
    service = QualityGateService(repository=repo)

    workflow = service.agent_loader.load_all()
    assert workflow

    from src.application.services.workflow_service import WorkflowService

    wf_service = WorkflowService(repository=repo)
    wf_service.create_workflow(workflow_id, words=[])
    repo.save_stage_output(
        workflow_id=workflow_id,
        stage="1-explorer",
        compact_output_text="Resumo com evidências e plano.",
        full_outputs={"evidencia.md": "conteudo"},
    )

    draft = service.generate_for_stage(workflow_id, "1-explorer")

    assert draft.recommendation == "approve"
    assert draft.required_questions
    assert "2-intake" in draft.required_questions[-1]


def test_generate_quality_gate_without_full_outputs(repo) -> None:
    workflow_id = "wf-qg-no-full"
    from src.application.services.workflow_service import WorkflowService

    wf_service = WorkflowService(repository=repo)
    wf_service.create_workflow(workflow_id, words=[])
    repo.save_stage_output(
        workflow_id=workflow_id,
        stage="1-explorer",
        compact_output_text="Resumo sem anexos.",
        full_outputs={},
    )

    service = QualityGateService(repository=repo)
    draft = service.generate_for_stage(workflow_id, "1-explorer")

    assert draft.recommendation == "review_before_approve"
    assert any("Artefatos completos ausentes" in gap for gap in draft.gaps)
    assert draft.required_questions
