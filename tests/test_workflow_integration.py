from pathlib import Path

from scripts.test_full_workflow_integration import run_full_workflow_assertions
from src.application.services.workflow_service import WorkflowService
from src.infrastructure.persistence.workflow_repository import WorkflowRepository


def test_full_workflow_integration(tmp_path: Path) -> None:
    run_full_workflow_assertions(tmp_path / "workflows")


def test_create_workflow_initializes_stage_timeline(tmp_path: Path) -> None:
    repository = WorkflowRepository(base_path=tmp_path)
    service = WorkflowService(repository=repository)
    workflow = service.create_workflow("wf-test", name="Test Workflow", words=["fintech", "saude"])

    assert workflow.id == "wf-test"
    assert workflow.name == "Test Workflow"
    assert len(workflow.stages) == 9
    assert workflow.stages[0].id == "1-explorer"
    assert workflow.stages[0].status == "awaiting_human_approval"
    assert all(stage.status == "pending" for stage in workflow.stages[1:])

    workflows = service.list_workflows()
    assert any(item.id == "wf-test" for item in workflows)


def test_create_workflow_with_words_auto_runs_explorer(tmp_path: Path) -> None:
    repository = WorkflowRepository(base_path=tmp_path)
    service = WorkflowService(repository=repository)
    words = ["futebol", "copa-do-mundo"]
    
    workflow = service.create_workflow("wf-words-test", name="Workflow with Words", words=words)
    
    # Verify 1-explorer was auto-executed
    explorer_stage = workflow.stages[0]
    assert explorer_stage.id == "1-explorer"
    assert explorer_stage.status == "awaiting_human_approval"
    
    # Verify outputs were generated
    outputs = service.get_stage_outputs("wf-words-test", "1-explorer")
    assert "compact_output_text" in outputs
    assert "full_output_paths" in outputs
    assert len(outputs["full_output_paths"]) > 0
