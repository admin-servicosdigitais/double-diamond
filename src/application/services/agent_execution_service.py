from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from src.application.services.file_naming_service import FileNamingService
from src.application.services.prompt_assembler import PromptAssembler
from src.application.services.slug_service import SlugService
from src.domain.models.agent_definition import AgentDefinition
from src.domain.models.execution import StageExecutionResult
from src.infrastructure.agents.agno_agent_runner import AgnoAgentRunner
from src.infrastructure.persistence.repository_protocol import WorkflowRepositoryProtocol


class AgentExecutionService:
    def __init__(
        self,
        repository: WorkflowRepositoryProtocol,
        prompt_assembler: PromptAssembler | None = None,
        agent_runner: AgnoAgentRunner | None = None,
        slug_service: SlugService | None = None,
        file_naming_service: FileNamingService | None = None,
    ) -> None:
        self.repository = repository
        self.prompt_assembler = prompt_assembler or PromptAssembler()
        self.agent_runner = agent_runner or AgnoAgentRunner()
        self.slug_service = slug_service or SlugService()
        self.file_naming_service = file_naming_service or FileNamingService()

    def execute(
        self,
        workflow_id: str,
        agent_definition: AgentDefinition,
        user_input: str | dict[str, Any] | None,
        previous_compact: str | None = None,
        previous_full_outputs: dict[str, str] | None = None,
        include_full_previous_stage: bool = False,
    ) -> StageExecutionResult:
        stage = agent_definition.id
        runtime_context = self._prepare_runtime_context(agent_definition, user_input)

        prompt = self.prompt_assembler.build(
            agent=agent_definition,
            previous_compact=previous_compact,
            context=runtime_context,
            previous_full_outputs=previous_full_outputs,
            include_full_previous_stage=include_full_previous_stage,
        )

        run_id = str(uuid4())
        output_text = self.agent_runner.run(agent_definition, prompt)

        slug = self.slug_service.resolve_slug(stage, user_input, previous_compact)
        named_full_outputs = self._build_named_outputs(
            slug=slug,
            agent_id=stage,
            prompt=prompt,
            output_text=output_text,
        )

        saved_output = self.repository.save_stage_output(
            workflow_id=workflow_id,
            stage=stage,
            compact_output_text=output_text,
            full_outputs=named_full_outputs,
            metadata={"run_id": run_id, "slug": slug},
        )

        return StageExecutionResult(
            workflow_id=workflow_id,
            run_id=run_id,
            stage=stage,
            agent_id=agent_definition.id,
            status="awaiting_human_approval",
            compact_output_text=output_text,
            full_output_paths=saved_output.get("full_output_paths", []),
            next_stage_available=False,
        )

    def _build_named_outputs(self, slug: str, agent_id: str, prompt: str, output_text: str) -> dict[str, str]:
        now = datetime.utcnow()
        prompt_filename = self.file_naming_service.build_filename(slug, agent_id, "prompt", now)
        response_filename = self.file_naming_service.build_filename(slug, agent_id, "response-full", now)
        compact_filename = self.file_naming_service.build_filename(slug, agent_id, "resumo", now)

        return {
            prompt_filename: prompt,
            response_filename: output_text,
            compact_filename: output_text,
        }

    def _prepare_runtime_context(
        self,
        agent_definition: AgentDefinition,
        user_input: str | dict[str, Any] | None,
    ) -> str | dict[str, Any] | None:
        if agent_definition.id != "1-explorer":
            return user_input

        themes = self._extract_themes(user_input)
        parallel_hint = self._build_parallel_hint(themes)

        base_context: dict[str, Any] = {
            "input": user_input,
            "runtime_tools": "WebSearch habilitado automaticamente; escalonamento para subagente permitido.",
            "parallel_execution_hint": parallel_hint,
            "subagent_escalation_hint": (
                "Quando faltar evidência ou houver análise competitiva densa, delegar para subagente com escopo claro."
            ),
        }

        if themes:
            base_context["themes"] = ", ".join(themes)

        return base_context

    @staticmethod
    def _extract_themes(user_input: str | dict[str, Any] | None) -> list[str]:
        if isinstance(user_input, str):
            return [item.strip() for item in user_input.split(",") if item.strip()]

        if isinstance(user_input, dict):
            for key in ("words", "temas", "themes", "topicos", "topics"):
                value = user_input.get(key)
                if isinstance(value, list):
                    return [str(item).strip() for item in value if str(item).strip()]
                if isinstance(value, str):
                    return [item.strip() for item in value.split(",") if item.strip()]

        return []

    @staticmethod
    def _build_parallel_hint(themes: list[str]) -> str:
        if len(themes) <= 1:
            return "Sem paralelismo adicional: processar tema único."

        theme_threads = [f"thread-{index + 1}: {theme}" for index, theme in enumerate(themes)]
        return (
            "Paralelismo simples (simulado): trate cada tema como uma thread lógica independente, "
            "consolidando achados ao final. "
            f"Threads sugeridas: {' | '.join(theme_threads)}"
        )
