import os

from src.domain.models.agent_definition import AgentDefinition, ProviderEnum
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
        provider = self._resolve_provider(agent_definition.provider)
        model_id = agent_definition.model or os.getenv("AGNO_DEFAULT_MODEL", "gpt-4")

        self._validate_api_key(provider)
        model = self._resolve_model(provider, model_id)

        agent_kwargs = {
            "model": model,
            "name": agent_definition.name,
            "description": agent_definition.description,
            "instructions": agent_definition.instructions_md,
        }

        tools = self.tool_registry.build(agent_definition)
        if tools:
            agent_kwargs["tools"] = tools

        return agent_kwargs

    def _resolve_provider(self, provider: ProviderEnum | None) -> ProviderEnum:
        if provider is not None:
            return provider

        default_provider = os.getenv("AGNO_DEFAULT_PROVIDER", "openai").strip().lower()
        try:
            return ProviderEnum(default_provider)
        except ValueError as exc:
            raise ValueError(
                f"AGNO_DEFAULT_PROVIDER '{default_provider}' is inválido. "
                f"Use um dos valores: {[item.value for item in ProviderEnum]}"
            ) from exc

    def _validate_api_key(self, provider: ProviderEnum) -> None:
        env_keys = {
            ProviderEnum.OPENAI: "OPENAI_API_KEY",
            ProviderEnum.ANTHROPIC: "ANTHROPIC_API_KEY",
            ProviderEnum.GOOGLE: "GOOGLE_API_KEY",
        }
        key_name = env_keys.get(provider)
        if key_name and not os.getenv(key_name):
            raise RuntimeError(
                f"Chave de API ausente para o provedor '{provider.value}'. "
                f"Defina a variável de ambiente {key_name}."
            )

    def _resolve_model(self, provider: ProviderEnum, model_id: str) -> object:
        if provider == ProviderEnum.OPENAI:
            from agno.models.openai import OpenAIChat

            return OpenAIChat(id=model_id)
        if provider == ProviderEnum.ANTHROPIC:
            from agno.models.anthropic import Claude

            return Claude(id=model_id)
        if provider == ProviderEnum.GOOGLE:
            from agno.models.google import Gemini

            return Gemini(id=model_id)

        raise ValueError(
            f"Provedor '{provider.value}' não suportado. "
            f"Suporte atual: {[item.value for item in ProviderEnum]}"
        )

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
