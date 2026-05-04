from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.infrastructure.persistence.repository_protocol import WorkflowRepositoryProtocol
from src.loaders.agent_markdown_loader import AgentMarkdownLoader


class QualityGateDraft(BaseModel):
    diagnosis: str
    gaps: list[str] = Field(default_factory=list)
    required_questions: list[str] = Field(default_factory=list)
    optional_questions: list[str] = Field(default_factory=list)
    recommendation: str


class QualityGateService:
    """Deterministic quality-gate generator.

    This service is intentionally rule-based so it can be swapped later for an
    Agno/LLM-backed implementation without changing callers.
    """

    def __init__(
        self,
        repository: WorkflowRepositoryProtocol,
        agent_loader: AgentMarkdownLoader | None = None,
    ) -> None:
        self.repository = repository
        self.agent_loader = agent_loader or AgentMarkdownLoader()

    def generate_for_stage(self, workflow_id: str, stage: str) -> QualityGateDraft:
        stage_outputs = self.repository.get_stage_outputs(workflow_id, stage)
        compact_output = str(stage_outputs.get("compact_output_text", "")).strip()
        full_outputs = self.repository.read_stage_full_outputs(workflow_id, stage) or {}

        current_agent = self.agent_loader.load_by_id(stage)
        next_stage = self._get_next_stage(stage)

        gaps: list[str] = []
        required_questions: list[str] = []
        optional_questions: list[str] = []

        if not compact_output:
            gaps.append("Compact output ausente para o stage atual")
            required_questions.append("Qual é o resumo executivo mínimo que justifica este stage?")

        if not full_outputs:
            gaps.append("Artefatos completos ausentes")
            required_questions.append("Há evidências adicionais que deveriam ser anexadas antes da aprovação?")
        elif len(full_outputs) == 1:
            optional_questions.append("Existe alguma evidência complementar que reduza risco de interpretação única?")

        if current_agent is not None:
            if current_agent.description.strip():
                optional_questions.append(
                    f"O output cobre claramente o objetivo do agente '{current_agent.name}' ({current_agent.description})?"
                )
            else:
                optional_questions.append(f"O output cobre claramente o objetivo do agente '{current_agent.name}'?")

        if next_stage is not None:
            required_questions.append(
                f"Este output está pronto para servir de input confiável para o próximo stage '{next_stage}'?"
            )

        if not compact_output:
            recommendation = "block_approval"
            diagnosis = "Material insuficiente para aprovação: output compact inexistente."
        elif gaps:
            recommendation = "review_before_approve"
            diagnosis = "Existem lacunas de qualidade que pedem revisão humana antes da aprovação."
        else:
            recommendation = "approve"
            diagnosis = "Output consistente para aprovação com base nas regras determinísticas atuais."

        return QualityGateDraft(
            diagnosis=diagnosis,
            gaps=gaps,
            required_questions=required_questions,
            optional_questions=optional_questions,
            recommendation=recommendation,
        )

    def _get_next_stage(self, stage: str) -> str | None:
        ordered_agents = sorted(self.agent_loader.load_all(), key=lambda agent: int(agent.stage))
        ordered_ids = [agent.id for agent in ordered_agents]

        if stage not in ordered_ids:
            return None

        index = ordered_ids.index(stage)
        if index + 1 >= len(ordered_ids):
            return None

        return ordered_ids[index + 1]
