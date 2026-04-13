import pytest

from src.application.services.workflow_service import WorkflowService
from src.infrastructure.persistence.workflow_repository import WorkflowRepository


@pytest.fixture(autouse=True)
def _mock_agno_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGNO_MOCK", "1")


def test_run_stage_blocks_when_previous_stage_not_approved(tmp_path) -> None:
    service = WorkflowService(repository=WorkflowRepository(base_path=tmp_path / "workflows"))
    service.create_workflow("wf-blocked", words=[])

    with pytest.raises(ValueError, match="estágio anterior.*approved"):
        service.run_stage("wf-blocked", "2-intake", {"tema": "teste"})


def test_workflow_advances_only_after_approval(tmp_path) -> None:
    service = WorkflowService(repository=WorkflowRepository(base_path=tmp_path / "workflows"))
    workflow_id = "wf-approval"
    service.create_workflow(workflow_id, words=[])

    first_run = service.run_stage(workflow_id, "1-explorer", {"temas": ["fintech", "saude"]})
    assert first_run.status == "awaiting_human_approval"

    with pytest.raises(ValueError, match="estágio atual estiver aprovado"):
        service.run_next_stage(workflow_id, "1-explorer", {"input": "sem aprovação"})

    service.approve_stage(workflow_id, "1-explorer")
    second_run = service.run_next_stage(workflow_id, "1-explorer", {"input": "aprovado"})

    assert second_run.stage == "2-intake"
    assert second_run.status == "awaiting_human_approval"

    updated = service.get_stage_state(workflow_id, "1-explorer")
    assert updated.status == "completed"
