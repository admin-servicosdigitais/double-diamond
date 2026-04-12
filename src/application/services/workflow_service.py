from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import uuid4

from src.application.services.prompt_assembler import PromptAssembler
from src.domain.models.execution import StageExecutionResult
from src.domain.models.workflow import StageState, WorkflowState
from src.infrastructure.agents.agno_agent_runner import AgnoAgentRunner
from src.infrastructure.persistence.workflow_repository import WorkflowRepository
from src.loaders.agent_markdown_loader import AgentMarkdownLoader


class WorkflowService:
    def __init__(
        self,
        repository: WorkflowRepository,
        agent_loader: AgentMarkdownLoader | None = None,
        prompt_assembler: PromptAssembler | None = None,
        agent_runner: AgnoAgentRunner | None = None,
    ) -> None:
        self.repository = repository
        self.agent_loader = agent_loader or AgentMarkdownLoader()
        self.prompt_assembler = prompt_assembler or PromptAssembler()
        self.agent_runner = agent_runner or AgnoAgentRunner()

    def create_workflow(self, workflow_id: str, name: str | None = None) -> WorkflowState:
        workflow = WorkflowState(id=workflow_id, name=name or workflow_id)
        return self.repository.create_workflow(workflow)

    def get_workflow(self, workflow_id: str) -> WorkflowState:
        return self.repository.get_workflow(workflow_id)

    def run_stage(self, workflow_id: str, stage: str, user_input: str | dict[str, Any] | None) -> StageExecutionResult:
        if stage != "2-intake":
            raise ValueError("No fluxo atual, apenas o agente 2-intake está habilitado.")

        workflow = self.repository.get_workflow(workflow_id)
        previous_stage = self._get_previous_stage(stage)

        if previous_stage:
            previous_state = self._find_stage_state(workflow, previous_stage)
            if previous_state and previous_state.status == "approved":
                self.repository.update_stage_status(workflow_id, previous_stage, "completed")

        self.repository.update_stage_status(workflow_id, stage, "running")
        self.repository.save_stage_input(workflow_id, stage, {"input": user_input})

        agent_definition = self.agent_loader.load_by_id(stage)
        if agent_definition is None:
            raise FileNotFoundError(f"Agent '{stage}' not found")

        previous_compact = self._read_previous_compact(workflow_id, previous_stage)
        prompt = self.prompt_assembler.build(
            agent=agent_definition,
            previous_compact=previous_compact,
            context=user_input,
        )

        run_id = str(uuid4())
        output_text = self.agent_runner.run(agent_definition, prompt)
        saved_output = self.repository.save_stage_output(
            workflow_id=workflow_id,
            stage=stage,
            compact_output_text=output_text,
            full_outputs={"prompt.md": prompt, "response_full.md": output_text},
            metadata={"run_id": run_id},
        )
        self.repository.update_stage_status(
            workflow_id,
            stage,
            "awaiting_human_approval",
            metadata={"run_id": run_id, "updated_at": datetime.utcnow().isoformat()},
        )

        return StageExecutionResult(
            workflow_id=workflow_id,
            run_id=run_id,
            stage=stage,
            agent_id=stage,
            status="awaiting_human_approval",
            compact_output_text=output_text,
            full_output_paths=saved_output.get("full_output_paths", []),
            next_stage_available=self.get_next_stage(stage) is not None,
        )

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
        if current is None or current.status not in {"approved", "completed"}:
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

    def get_stage_state(self, workflow_id: str, stage: str) -> StageState:
        workflow = self.repository.get_workflow(workflow_id)
        stage_state = self._find_stage_state(workflow, stage)
        if stage_state is None:
            raise FileNotFoundError(f"Stage '{stage}' not found in workflow '{workflow_id}'")
        return stage_state

    def get_stage_outputs(self, workflow_id: str, stage: str) -> dict[str, Any]:
        stage_dir = self.repository.base_path / workflow_id / "stages" / stage
        if not stage_dir.exists():
            raise FileNotFoundError(f"Stage '{stage}' not found in workflow '{workflow_id}'")

        compact_path = stage_dir / "output_compact.md"
        metadata_path = stage_dir / "metadata.json"
        output_full_dir = stage_dir / "output_full"

        metadata: dict[str, Any] = {}
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        full_outputs = []
        if output_full_dir.exists():
            full_outputs = [str(path) for path in sorted(output_full_dir.iterdir()) if path.is_file()]

        compact_output_text = compact_path.read_text(encoding="utf-8") if compact_path.exists() else ""

        return {
            "workflow_id": workflow_id,
            "stage": stage,
            "compact_output_text": compact_output_text,
            "full_output_paths": full_outputs,
            "metadata": metadata,
        }


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

        compact_path = (
            self.repository.base_path
            / workflow_id
            / "stages"
            / previous_stage
            / "output_compact.md"
        )
        if not compact_path.exists():
            return None

        return compact_path.read_text(encoding="utf-8").strip()
