from __future__ import annotations

from datetime import datetime
from typing import Any

from src.application.services.agent_execution_service import AgentExecutionService
from src.application.services.prompt_assembler import PromptAssembler
from src.domain.models.execution import StageExecutionResult
from src.domain.models.workflow import StageState, StageStatus, WorkflowState
from src.infrastructure.agents.agno_agent_runner import AgnoAgentRunner
from src.infrastructure.persistence.repository_protocol import WorkflowRepositoryProtocol
from src.loaders.agent_markdown_loader import AgentMarkdownLoader


class WorkflowService:
    def __init__(
        self,
        repository: WorkflowRepositoryProtocol,
        agent_loader: AgentMarkdownLoader | None = None,
        prompt_assembler: PromptAssembler | None = None,
        agent_runner: AgnoAgentRunner | None = None,
    ) -> None:
        self.repository = repository
        self.agent_loader = agent_loader or AgentMarkdownLoader()
        self.prompt_assembler = prompt_assembler or PromptAssembler()
        self.agent_runner = agent_runner or AgnoAgentRunner()
        self.agent_execution_service = AgentExecutionService(
            repository=self.repository,
            prompt_assembler=self.prompt_assembler,
            agent_runner=self.agent_runner,
        )

    def create_workflow(self, workflow_id: str, name: str | None = None) -> WorkflowState:
        ordered_agents = sorted(self.agent_loader.load_all(), key=lambda agent: int(agent.stage))
        stages = [
            StageState(
                id=agent.id,
                name=agent.name,
                status=StageStatus.DRAFT if index == 0 else StageStatus.PENDING,
            )
            for index, agent in enumerate(ordered_agents)
        ]
        workflow = WorkflowState(id=workflow_id, name=name or workflow_id, stages=stages)
        return self.repository.create_workflow(workflow)

    def list_workflows(self) -> list[WorkflowState]:
        return self.repository.list_workflows()

    def get_workflow(self, workflow_id: str) -> WorkflowState:
        return self.repository.get_workflow(workflow_id)

    def run_stage(self, workflow_id: str, stage: str, user_input: str | dict[str, Any] | None) -> StageExecutionResult:
        workflow = self.repository.get_workflow(workflow_id)
        previous_stage = self._get_previous_stage(stage)

        if previous_stage:
            previous_state = self._find_stage_state(workflow, previous_stage)
            if previous_state is None or previous_state.status != "approved":
                raise ValueError(
                    f"Stage '{stage}' só pode executar quando o estágio anterior '{previous_stage}' estiver approved."
                )

        self.repository.update_stage_status(workflow_id, stage, "running")
        self.repository.save_stage_input(workflow_id, stage, {"input": user_input})

        try:
            agent_definition = self.agent_loader.load_by_id(stage)
            if agent_definition is None:
                raise FileNotFoundError(f"Agent '{stage}' not found")

            input_source_stage = self.get_input_for_stage(stage)
            previous_compact = self._read_previous_compact(workflow_id, input_source_stage)
            include_full_previous_stage = stage == "8-prototype-visual" and input_source_stage == "7-validacao"
            previous_full_outputs = self._read_previous_full_outputs(workflow_id, input_source_stage) if include_full_previous_stage else None

            execution_result = self.agent_execution_service.execute(
                workflow_id=workflow_id,
                agent_definition=agent_definition,
                user_input=user_input,
                previous_compact=previous_compact,
                previous_full_outputs=previous_full_outputs,
                include_full_previous_stage=include_full_previous_stage,
            )
        except Exception as exc:  # noqa: BLE001
            self.repository.update_stage_status(
                workflow_id,
                stage,
                "failed",
                metadata={"error": str(exc), "updated_at": datetime.utcnow().isoformat()},
            )
            raise

        self.repository.update_stage_status(
            workflow_id,
            stage,
            "awaiting_human_approval",
            metadata={"run_id": execution_result.run_id, "updated_at": datetime.utcnow().isoformat()},
        )

        if previous_stage:
            self.repository.update_stage_status(workflow_id, previous_stage, "completed")

        execution_result.next_stage_available = self.get_next_stage(stage) is not None
        return execution_result

    def approve_stage(self, workflow_id: str, stage: str) -> WorkflowState:
        workflow = self.repository.get_workflow(workflow_id)
        current = self._find_stage_state(workflow, stage)
        if current is None or current.status != "awaiting_human_approval":
            raise ValueError(f"Stage '{stage}' precisa estar em awaiting_human_approval para aprovação.")

        updated = self.repository.update_stage_status(
            workflow_id,
            stage,
            "approved",
            metadata={"approved_at": datetime.utcnow().isoformat()},
        )

        next_stage = self.get_next_stage(stage)
        if next_stage is None:
            return self.repository.update_stage_status(workflow_id, stage, "completed")

        if self._find_stage_state(updated, next_stage) is None:
            self.repository.update_stage_status(workflow_id, next_stage, "draft")

        return self.repository.get_workflow(workflow_id)

    def run_next_stage(
        self,
        workflow_id: str,
        stage: str,
        user_input: str | dict[str, Any] | None = None,
    ) -> StageExecutionResult:
        workflow = self.repository.get_workflow(workflow_id)
        current = self._find_stage_state(workflow, stage)
        if current is None or current.status != "approved":
            raise ValueError("next só funciona se o estágio atual estiver aprovado.")

        next_stage = self.get_next_stage(stage)
        if next_stage is None:
            raise ValueError("Não existe próximo estágio para este stage.")

        return self.run_stage(workflow_id, next_stage, user_input)

    def get_next_stage(self, stage: str) -> str | None:
        ordered_agents = sorted(
            self.agent_loader.load_all(),
            key=lambda agent: int(agent.stage),
        )
        ordered_ids = [agent.id for agent in ordered_agents]

        if stage not in ordered_ids:
            return None

        index = ordered_ids.index(stage)
        if index + 1 >= len(ordered_ids):
            return None

        return ordered_ids[index + 1]


    def get_input_for_stage(self, stage: str) -> str | None:
        if stage == "9-definicao":
            return "7-validacao"

        return self._get_previous_stage(stage)

    def get_stage_state(self, workflow_id: str, stage: str) -> StageState:
        workflow = self.repository.get_workflow(workflow_id)
        stage_state = self._find_stage_state(workflow, stage)
        if stage_state is None:
            raise FileNotFoundError(f"Stage '{stage}' not found in workflow '{workflow_id}'")
        return stage_state

    def get_stage_outputs(self, workflow_id: str, stage: str) -> dict[str, Any]:
        return self.repository.get_stage_outputs(workflow_id, stage)


    def get_latest_output_by_agent_code(self, workflow_id: str, agent_code: str) -> dict[str, Any]:
        stage = self._resolve_stage_from_agent_code(agent_code)
        if stage is None:
            raise FileNotFoundError(f"Agent code '{agent_code}' not found")

        stage_state = self.get_stage_state(workflow_id, stage)
        outputs = self.get_stage_outputs(workflow_id, stage)

        return {
            "stage": stage,
            "status": stage_state.status,
            "compact_output": outputs.get("compact_output_text", ""),
            "full_outputs": outputs.get("full_output_paths", []),
        }

    @staticmethod
    def _find_stage_state(workflow: WorkflowState, stage: str) -> StageState | None:
        return next((item for item in workflow.stages if item.id == stage), None)

    def _get_previous_stage(self, stage: str) -> str | None:
        ordered_agents = sorted(
            self.agent_loader.load_all(),
            key=lambda agent: int(agent.stage),
        )
        ordered_ids = [agent.id for agent in ordered_agents]

        if stage not in ordered_ids:
            return None

        index = ordered_ids.index(stage)
        if index == 0:
            return None

        return ordered_ids[index - 1]



    def _read_previous_full_outputs(self, workflow_id: str, previous_stage: str | None) -> dict[str, str] | None:
        if previous_stage is None:
            return None

        return self.repository.read_stage_full_outputs(workflow_id, previous_stage)

    def _resolve_stage_from_agent_code(self, agent_code: str) -> str | None:
        normalized = agent_code.strip().lower()
        agents = self.agent_loader.load_all()

        for agent in agents:
            if agent.id.lower() == normalized:
                return agent.id

        for agent in agents:
            suffix = agent.id.split("-", 1)[-1].lower()
            if suffix == normalized:
                return agent.id

        for agent in agents:
            if agent.name.lower() == normalized:
                return agent.id

        return None

    def _read_previous_compact(self, workflow_id: str, previous_stage: str | None) -> str | None:
        if previous_stage is None:
            return None

        return self.repository.read_stage_compact_output(workflow_id, previous_stage)
