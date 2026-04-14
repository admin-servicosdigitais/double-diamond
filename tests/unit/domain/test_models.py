from datetime import datetime

import pytest

from src.domain.models.agent_definition import AgentDefinition, ProviderEnum
from src.domain.models.execution import StageExecutionRequest, StageExecutionResult
from src.domain.models.workflow import StageState, WorkflowState


class TestAgentDefinition:
    def test_valid_agent_definition(self):
        agent = AgentDefinition(
            id="1-explorer",
            stage="1-explorer",
            name="Explorer",
            description="Explores opportunities",
            role="explorer",
            model="gpt-4",
            provider=ProviderEnum.OPENAI,
            summary_format="markdown",
            instructions_md="# Instructions\nExplore topics",
            tools=["search"],
            execution_mode="single_pass",
            max_steps=1,
        )
        assert agent.id == "1-explorer"
        assert agent.provider == ProviderEnum.OPENAI

    def test_agent_definition_defaults(self):
        agent = AgentDefinition(
            id="1-explorer",
            stage="1-explorer",
            name="Explorer",
            description="Explores opportunities",
            role="explorer",
            model="gpt-4",
            summary_format="markdown",
            instructions_md="# Instructions\nExplore topics",
        )
        assert agent.provider is None
        assert agent.tools == []
        assert agent.execution_mode == "single_pass"
        assert agent.max_steps == 1


class TestStageExecutionRequest:
    def test_valid_request(self):
        request = StageExecutionRequest(
            workflow_id="wf-123",
            stage="1-explorer",
            user_input="explore fintech",
            additional_context={"priority": "high"},
        )
        assert request.workflow_id == "wf-123"
        assert request.additional_context == {"priority": "high"}


class TestStageExecutionResult:
    def test_valid_result(self):
        result = StageExecutionResult(
            workflow_id="wf-123",
            run_id="run-456",
            stage="1-explorer",
            agent_id="1-explorer",
            status="completed",
            compact_output_text="Found opportunities",
            full_output_paths=["output.md"],
            next_stage_available=True,
        )
        assert result.workflow_id == "wf-123"
        assert result.full_output_paths == ["output.md"]


class TestStageState:
    def test_stage_state_creation(self):
        stage = StageState(id="1-explorer", name="Explorer")
        assert stage.id == "1-explorer"
        assert stage.status.name == "PENDING"
        assert isinstance(stage.created_at, datetime)
        assert isinstance(stage.updated_at, datetime)

    def test_stage_state_with_metadata(self):
        metadata = {"run_id": "run-123"}
        stage = StageState(id="1-explorer", name="Explorer", metadata=metadata)
        assert stage.metadata == metadata


class TestWorkflowState:
    def test_workflow_state_creation(self):
        workflow = WorkflowState(id="wf-123", name="Test Workflow")
        assert workflow.id == "wf-123"
        assert workflow.stages == []
        assert isinstance(workflow.created_at, datetime)