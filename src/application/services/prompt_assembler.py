from typing import Any

from src.domain.models.agent_definition import AgentDefinition


class PromptAssembler:
    def build(
        self,
        agent: AgentDefinition,
        previous_compact: str | None = None,
        context: str | dict[str, Any] | None = None,
        previous_full_outputs: dict[str, str] | None = None,
        include_full_previous_stage: bool = False,
    ) -> str:
        sections: list[str] = []

        sections.append("# Agent Instructions")
        sections.append(agent.instructions_md.strip())

        if previous_compact and previous_compact.strip():
            sections.append("# Previous Stage (N-1) Compact Output")
            sections.append(previous_compact.strip())

        if include_full_previous_stage and previous_full_outputs:
            sections.append("# Previous Stage (N-1) Full Outputs")
            sections.append(self._format_full_outputs(previous_full_outputs))

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

    @staticmethod
    def _format_full_outputs(previous_full_outputs: dict[str, str]) -> str:
        blocks: list[str] = []
        for filename in sorted(previous_full_outputs.keys()):
            content = previous_full_outputs[filename].strip()
            blocks.append(f"## {filename}\n{content}")
        return "\n\n".join(blocks).strip()
