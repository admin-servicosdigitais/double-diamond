from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.domain.models.agent_definition import AgentDefinition


class ToolRegistry:
    """Resolve and instantiate runtime tools for Agno agents."""

    WEBSEARCH = "websearch"
    SUBAGENT = "subagent"

    def resolve_tool_names(self, agent_definition: AgentDefinition) -> list[str]:
        names = [self._normalize(name) for name in agent_definition.tools]

        if agent_definition.id == "1-explorer" and self.WEBSEARCH not in names:
            names.append(self.WEBSEARCH)

        if agent_definition.id == "1-explorer" and self.SUBAGENT not in names:
            names.append(self.SUBAGENT)

        deduped: list[str] = []
        for name in names:
            if name and name not in deduped:
                deduped.append(name)

        return deduped

    def build(self, agent_definition: AgentDefinition) -> list[Any]:
        tools: list[Any] = []

        for name in self.resolve_tool_names(agent_definition):
            if name == self.WEBSEARCH:
                websearch_tool = self._build_websearch_tool()
                if websearch_tool is not None:
                    tools.append(websearch_tool)
            elif name == self.SUBAGENT:
                tools.append(self._build_subagent_tool())

        return tools

    @staticmethod
    def _normalize(name: str) -> str:
        normalized = name.strip().lower().replace("_", "").replace("-", "").replace(" ", "")
        aliases = {
            "websearchtool": "websearch",
            "web": "websearch",
            "search": "websearch",
            "agentsubagent": "subagent",
            "agent": "subagent",
        }
        return aliases.get(normalized, normalized)

    @staticmethod
    def _build_websearch_tool() -> Any | None:
        try:
            from agno.tools.duckduckgo import DuckDuckGoTools

            return DuckDuckGoTools()
        except Exception:  # noqa: BLE001
            pass

        try:
            from agno.tools.tavily import TavilyTools

            return TavilyTools()
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _build_subagent_tool() -> Callable[..., str]:
        def run_subagent(
            task: str,
            subagent_type: str = "general-purpose",
            model: str = "sonnet",
        ) -> str:
            """Escalate complex research tasks to a dedicated subagent."""
            try:
                from agno.agent import Agent

                subagent = Agent(
                    model=model,
                    name=f"{subagent_type}-subagent",
                    description="Subagente de pesquisa para tarefas complexas.",
                    instructions=(
                        "Faça pesquisa aprofundada com foco em evidências e síntese prática. "
                        "Retorne resposta objetiva e citando fontes quando possível."
                    ),
                )
                response = subagent.run(task)
                content = getattr(response, "content", None)
                return str(content if content is not None else response)
            except Exception as exc:  # noqa: BLE001
                return f"Subagent escalation failed: {exc}"

        return run_subagent
