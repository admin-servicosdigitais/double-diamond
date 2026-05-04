import pytest

from src.application.services.workflow_service import WorkflowService
from src.domain.models.quality_gate import QualityGateState, QualityGateStatus
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


def test_approval_without_quality_gate_keeps_compatibility(tmp_path) -> None:
    service = WorkflowService(repository=WorkflowRepository(base_path=tmp_path / "workflows"))
    workflow_id = "wf-approval-no-gate"
    service.create_workflow(workflow_id, words=["saude"])

    updated = service.approve_stage(workflow_id, "1-explorer")
    current = next(item for item in updated.stages if item.id == "1-explorer")
    assert current.status == "approved"


def test_approval_with_pending_quality_gate_is_blocked(tmp_path) -> None:
    service = WorkflowService(repository=WorkflowRepository(base_path=tmp_path / "workflows"))
    workflow_id = "wf-approval-pending-gate"
    service.create_workflow(workflow_id, words=["saude"])

    pending_gate = QualityGateState(
        status=QualityGateStatus.QUESTIONS_GENERATED,
        required_questions=["Q1 obrigatória"],
        questions=["Q1 obrigatória"],
    )
    service.save_stage_quality_gate(workflow_id, "1-explorer", pending_gate)

    with pytest.raises(ValueError, match="Quality Gate pendente"):
        service.approve_stage(workflow_id, "1-explorer")


def test_approval_with_answered_quality_gate_works(tmp_path) -> None:
    service = WorkflowService(repository=WorkflowRepository(base_path=tmp_path / "workflows"))
    workflow_id = "wf-approval-answered-gate"
    service.create_workflow(workflow_id, words=["saude"])

    answered_gate = QualityGateState(
        status=QualityGateStatus.ANSWERED,
        required_questions=["Q1 obrigatória"],
        questions=["Q1 obrigatória"],
        answers=[{"question_id": "q1", "answer": "respondida"}],
    )
    service.save_stage_quality_gate(workflow_id, "1-explorer", answered_gate)

    updated = service.approve_stage(workflow_id, "1-explorer")
    current = next(item for item in updated.stages if item.id == "1-explorer")
    assert current.status == "approved"
