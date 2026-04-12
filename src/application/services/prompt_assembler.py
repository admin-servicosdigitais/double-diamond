from typing import Any

from src.domain.models.agent_definition import AgentDefinition


class PromptAssembler:
    def build(
        self,
        agent: AgentDefinition,
        previous_compact: str | None = None,
        context: str | dict[str, Any] | None = None,
    ) -> str:
        sections: list[str] = []

        sections.append("# Agent Instructions")
        sections.append(agent.instructions_md.strip())

        if previous_compact and previous_compact.strip():
            sections.append("# Previous Stage (N-1) Compact Output")
            sections.append(previous_compact.strip())

        if context is not None:
            cleaned_context = self._normalize_context(context)
            if cleaned_context:
                sections.append("# Additional User Context")
                sections.append(cleaned_context)

        return "\n\n".join(part for part in sections if part).strip()

    @staticmethod
    def _normalize_context(context: str | dict[str, Any]) -> str:
        if isinstance(context, str):
            return context.strip()

        lines: list[str] = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines).strip()
