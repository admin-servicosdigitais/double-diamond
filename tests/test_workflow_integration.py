from pathlib import Path

from scripts.test_full_workflow_integration import run_full_workflow_assertions
from src.application.services.workflow_service import WorkflowService
from src.infrastructure.persistence.workflow_repository import WorkflowRepository


def test_full_workflow_integration(tmp_path: Path) -> None:
    run_full_workflow_assertions(tmp_path / "workflows")


def test_create_workflow_initializes_stage_timeline(tmp_path: Path) -> None:
    repository = WorkflowRepository(base_path=tmp_path)
    service = WorkflowService(repository=repository)
    workflow = service.create_workflow("wf-test", name="Test Workflow")

    assert workflow.id == "wf-test"
    assert workflow.name == "Test Workflow"
    assert len(workflow.stages) == 9
    assert workflow.stages[0].id == "1-explorer"
    assert workflow.stages[0].status == "draft"
    assert all(stage.status == "pending" for stage in workflow.stages[1:])

    workflows = service.list_workflows()
    assert any(item.id == "wf-test" for item in workflows)
