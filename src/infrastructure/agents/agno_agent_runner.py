import os

from src.domain.models.agent_definition import AgentDefinition
from src.infrastructure.agents.tool_registry import ToolRegistry


class AgnoAgentRunner:
    def __init__(self, tool_registry: ToolRegistry | None = None) -> None:
        self.tool_registry = tool_registry or ToolRegistry()

    def run(self, agent_definition: AgentDefinition, prompt: str) -> str:
        resolved_tool_names = self.tool_registry.resolve_tool_names(agent_definition)
        execution_mode = (agent_definition.execution_mode or "single_pass").strip().lower()
        max_steps = max(agent_definition.max_steps, 1)

        if os.getenv("AGNO_MOCK", "0") == "1":
            tools_info = ", ".join(resolved_tool_names) or "none"
            return (
                f"[MOCK:{agent_definition.id}] Execução simulada para {agent_definition.name}\n"
                f"Mode: {execution_mode} | Max steps: {max_steps}\n"
                f"Tools: {tools_info}\n\n"
                f"Resumo do prompt:\n{prompt[:2000]}"
            )

        try:
            from agno.agent import Agent
        except ImportError as exc:
            raise RuntimeError(
                "Agno não está instalado. Instale dependências de runtime para executar agentes."
            ) from exc

        agno_agent = Agent(**self._build_agent_kwargs(agent_definition))

        if execution_mode == "deep_research":
            return self._run_deep_research(agno_agent, prompt, max_steps)

        response = agno_agent.run(prompt)
        return self._extract_response_text(response)

    def _build_agent_kwargs(self, agent_definition: AgentDefinition) -> dict:
        agent_kwargs = {
            "model": agent_definition.model,
            "name": agent_definition.name,
            "description": agent_definition.description,
            "instructions": agent_definition.instructions_md,
        }

        tools = self.tool_registry.build(agent_definition)
        if tools:
            agent_kwargs["tools"] = tools

        return agent_kwargs

    def _run_deep_research(self, agno_agent: object, prompt: str, max_steps: int) -> str:
        intermediate_outputs: list[str] = []

        for step in range(1, max_steps + 1):
            step_prompt = self._build_step_prompt(prompt, intermediate_outputs, step, max_steps)
            step_response = agno_agent.run(step_prompt)
            intermediate_text = self._extract_response_text(step_response)
            intermediate_outputs.append(intermediate_text)

        consolidation_prompt = self._build_consolidation_prompt(prompt, intermediate_outputs)
        final_response = agno_agent.run(consolidation_prompt)
        final_text = self._extract_response_text(final_response).strip()

        if final_text:
            return final_text

        return self._fallback_consolidation(intermediate_outputs)

    @staticmethod
    def _extract_response_text(response: object) -> str:
        content = getattr(response, "content", None)
        if content is None:
            return str(response)
        return str(content)

    @staticmethod
    def _build_step_prompt(
        base_prompt: str,
        intermediate_outputs: list[str],
        step: int,
        max_steps: int,
    ) -> str:
        if not intermediate_outputs:
            prior_context = "Nenhuma resposta intermediária ainda."
        else:
            prior_context = "\n\n".join(
                f"[Step {idx + 1}]\n{output}" for idx, output in enumerate(intermediate_outputs)
            )

        return (
            f"{base_prompt}\n\n"
            f"## Deep Research Loop\n"
            f"- Step atual: {step}/{max_steps}\n"
            f"- Faça pesquisa incremental, evitando repetir conteúdo anterior.\n"
            f"- Se tools estiverem disponíveis, use quando necessário.\n\n"
            f"## Contexto intermediário\n{prior_context}"
        )

    @staticmethod
    def _build_consolidation_prompt(base_prompt: str, intermediate_outputs: list[str]) -> str:
        combined = "\n\n".join(
            f"[Step {index + 1}]\n{item}" for index, item in enumerate(intermediate_outputs)
        )
        return (
            f"{base_prompt}\n\n"
            "## Consolidação Final\n"
            "Consolide as respostas intermediárias em uma única resposta final, sem duplicações. "
            "Priorize clareza, síntese e rastreabilidade de evidências.\n\n"
            f"## Respostas intermediárias\n{combined}"
        )

    @staticmethod
    def _fallback_consolidation(intermediate_outputs: list[str]) -> str:
        if not intermediate_outputs:
            return ""

        unique_segments: list[str] = []
        seen: set[str] = set()
        for output in intermediate_outputs:
            normalized = output.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_segments.append(normalized)

        return "\n\n".join(unique_segments)
