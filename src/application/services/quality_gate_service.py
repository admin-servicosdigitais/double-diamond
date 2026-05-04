from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from src.domain.models.agent_definition import AgentDefinition, ProviderEnum
from src.domain.models.quality_gate import QualityGateRecommendation
from src.infrastructure.agents.agno_agent_runner import AgnoAgentRunner
from src.infrastructure.persistence.repository_protocol import WorkflowRepositoryProtocol
from src.loaders.agent_markdown_loader import AgentMarkdownLoader

logger = logging.getLogger(__name__)


class QualityGateDraft(BaseModel):
    diagnosis: str
    gaps: list[str] = Field(default_factory=list)
    required_questions: list[str] = Field(default_factory=list)
    optional_questions: list[str] = Field(default_factory=list)
    recommendation: QualityGateRecommendation


class QualityGateLLMResponse(BaseModel):
    diagnosis: str
    gaps: list[str] = Field(default_factory=list)
    required_questions: list[str] = Field(default_factory=list, max_length=5)
    optional_questions: list[str] = Field(default_factory=list, max_length=3)
    recommendation: Literal["approve", "review_before_approve", "block_approval"]


class QualityGateService:
    def __init__(
        self,
        repository: WorkflowRepositoryProtocol,
        agent_loader: AgentMarkdownLoader | None = None,
        agent_runner: AgnoAgentRunner | None = None,
    ) -> None:
        self.repository = repository
        self.agent_loader = agent_loader or AgentMarkdownLoader()
        self.agent_runner = agent_runner or AgnoAgentRunner()

    def generate_for_stage(self, workflow_id: str, stage: str) -> QualityGateDraft:
        if os.getenv("AGNO_MOCK", "0") == "1":
            return self._generate_deterministic(workflow_id, stage)

        try:
            return self._generate_with_llm(workflow_id, stage)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "quality_gate.llm_fallback",
                extra={"workflow_id": workflow_id, "stage": stage, "error": str(exc), "error_type": type(exc).__name__},
            )
            return self._generate_deterministic(workflow_id, stage)

    def _generate_with_llm(self, workflow_id: str, stage: str) -> QualityGateDraft:
        stage_outputs = self.repository.get_stage_outputs(workflow_id, stage)
        compact_output = str(stage_outputs.get("compact_output_text", "")).strip()
        full_outputs = self.repository.read_stage_full_outputs(workflow_id, stage) or {}
        current_agent = self.agent_loader.load_by_id(stage)
        next_stage = self._get_next_stage(stage)

        prompt = self._build_quality_gate_prompt(
            workflow_id=workflow_id,
            stage=stage,
            current_agent_name=current_agent.name if current_agent else stage,
            compact_output=compact_output,
            full_outputs=full_outputs,
            next_stage=next_stage,
        )
        response_text = self.agent_runner.run(self._build_quality_gate_agent_definition(), prompt).strip()
        if not response_text:
            raise ValueError("Empty LLM response for quality gate")

        parsed_payload = self._parse_llm_response(response_text)
        return QualityGateDraft(**parsed_payload.model_dump())

    def _generate_deterministic(self, workflow_id: str, stage: str) -> QualityGateDraft:
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

    @staticmethod
    def _build_quality_gate_agent_definition() -> AgentDefinition:
        return AgentDefinition(
            id="quality-gate",
            stage="quality-gate",
            name="Quality Gate",
            description="Interrogador entre stages do Double Diamond antes da aprovação humana.",
            role="quality_gate",
            model=os.getenv("AGNO_QUALITY_GATE_MODEL", os.getenv("AGNO_DEFAULT_MODEL", "gpt-4")),
            provider=ProviderEnum(os.getenv("AGNO_DEFAULT_PROVIDER", "openai").strip().lower()),
            summary_format="json",
            instructions_md=QualityGateService._load_quality_gate_skill(),
            tools=[],
            execution_mode="single_pass",
            max_steps=1,
            output_artifacts=[],
        )

    @staticmethod
    def _load_quality_gate_skill() -> str:
        skill_path = Path("skills/quality-gate/SKILL.md")
        if not skill_path.exists():
            raise FileNotFoundError(f"Quality Gate skill não encontrada em {skill_path}")
        return skill_path.read_text(encoding="utf-8").strip()

    @staticmethod
    def _build_quality_gate_prompt(
        workflow_id: str,
        stage: str,
        current_agent_name: str,
        compact_output: str,
        full_outputs: dict[str, str],
        next_stage: str | None,
    ) -> str:
        serialized_full_outputs = json.dumps(full_outputs, ensure_ascii=False)
        return (
            "Analise o stage atual e responda estritamente com JSON válido conforme a skill.\n\n"
            f"workflow_id: {workflow_id}\n"
            f"current_stage: {stage}\n"
            f"current_agent: {current_agent_name}\n"
            f"next_stage: {next_stage or ''}\n"
            f"current_stage_output_compact:\n{compact_output}\n\n"
            f"current_stage_artifacts_full_json: {serialized_full_outputs}"
        )

    @staticmethod
    def _parse_llm_response(raw_response: str) -> QualityGateLLMResponse:
        payload_text = raw_response.strip()
        if payload_text.startswith("```"):
            payload_text = payload_text.strip("`")
            if payload_text.lower().startswith("json"):
                payload_text = payload_text[4:].strip()

        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON from Quality Gate LLM") from exc

        try:
            return QualityGateLLMResponse.model_validate(payload)
        except ValidationError as exc:
            raise ValueError("Quality Gate LLM response failed schema validation") from exc

    def _get_next_stage(self, stage: str) -> str | None:
        ordered_agents = sorted(self.agent_loader.load_all(), key=lambda agent: int(agent.stage))
        ordered_ids = [agent.id for agent in ordered_agents]

        if stage not in ordered_ids:
            return None

        index = ordered_ids.index(stage)
        if index + 1 >= len(ordered_ids):
            return None

        return ordered_ids[index + 1]
