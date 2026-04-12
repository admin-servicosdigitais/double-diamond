import os

from src.domain.models.agent_definition import AgentDefinition


class AgnoAgentRunner:
    def run(self, agent_definition: AgentDefinition, prompt: str) -> str:
        if os.getenv("AGNO_MOCK", "0") == "1":
            return (
                f"[MOCK:{agent_definition.id}] Execução simulada para {agent_definition.name}\n\n"
                f"Resumo do prompt:\n{prompt[:2000]}"
            )

        try:
            from agno.agent import Agent
        except ImportError as exc:
            raise RuntimeError(
                "Agno não está instalado. Instale dependências de runtime para executar agentes."
            ) from exc

        agno_agent = Agent(
            model=agent_definition.model,
            name=agent_definition.name,
            description=agent_definition.description,
            instructions=agent_definition.instructions_md,
        )

        response = agno_agent.run(prompt)
        content = getattr(response, "content", None)
        if content is None:
            return str(response)
        return str(content)
