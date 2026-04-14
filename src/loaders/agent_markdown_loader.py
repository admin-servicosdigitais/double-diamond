from pathlib import Path
import re

import yaml

from src.domain.models.agent_definition import AgentDefinition, ProviderEnum


class AgentMarkdownLoader:
    def __init__(self, agents_path: str | Path = "agents") -> None:
        self.agents_path = Path(agents_path)

    def load_all(self) -> list[AgentDefinition]:
        if not self.agents_path.exists():
            return []

        definitions: list[AgentDefinition] = []
        for agent_file in sorted(self.agents_path.glob("*/agent.md")):
            definitions.append(self._parse_agent_file(agent_file))

        return definitions

    def load_by_id(self, agent_id: str) -> AgentDefinition | None:
        agent_file = self.agents_path / agent_id / "agent.md"
        if not agent_file.exists():
            return None

        return self._parse_agent_file(agent_file)

    def _parse_agent_file(self, file_path: Path) -> AgentDefinition:
        raw_content = file_path.read_text(encoding="utf-8")
        metadata, instructions_md = self._split_frontmatter(raw_content)

        raw_provider = metadata.get("provider")
        provider = None
        if raw_provider is not None:
            if isinstance(raw_provider, str):
                raw_provider = raw_provider.strip()
            try:
                provider = ProviderEnum(raw_provider)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid provider '{raw_provider}' in {file_path}. "
                    f"Supported providers: {[item.value for item in ProviderEnum]}"
                ) from exc

        return AgentDefinition(
            id=file_path.parent.name,
            stage=str(metadata.get("stage", "")),
            name=str(metadata.get("name", "")),
            description=str(metadata.get("description", "")),
            role=str(metadata.get("role", "")),
            model=str(metadata.get("model", "")),
            provider=provider,
            summary_format=str(metadata.get("summary_format", "")),
            instructions_md=instructions_md,
            tools=self._parse_tools(metadata.get("tools")),
            execution_mode=str(metadata.get("execution_mode", "single_pass")),
            max_steps=self._parse_max_steps(metadata.get("max_steps")),
            output_artifacts=self._parse_output_artifacts(instructions_md),
        )

    @staticmethod
    def _parse_tools(raw_tools: object) -> list[str]:
        if raw_tools is None:
            return []

        if isinstance(raw_tools, str):
            return [tool.strip() for tool in raw_tools.split(",") if tool.strip()]

        if isinstance(raw_tools, list):
            parsed: list[str] = []
            for tool in raw_tools:
                if isinstance(tool, str) and tool.strip():
                    parsed.append(tool.strip())
            return parsed

        return []

    @staticmethod
    def _parse_max_steps(raw_steps: object) -> int:
        if raw_steps is None:
            return 1

        try:
            parsed = int(raw_steps)
        except (TypeError, ValueError):
            return 1

        return max(parsed, 1)

    @staticmethod
    def _split_frontmatter(content: str) -> tuple[dict, str]:
        if not content.startswith("---"):
            return {}, content.strip()

        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content.strip()

        yaml_raw = parts[1].strip()
        body = parts[2].strip()
        metadata = yaml.safe_load(yaml_raw) or {}

        if not isinstance(metadata, dict):
            raise ValueError("Invalid frontmatter format in agent markdown")

        return metadata, body

    @staticmethod
    def _parse_output_artifacts(instructions_md: str) -> list[str]:
        heading_pattern = r"^##\s+Artefatos de saida\b"
        artifact_pattern = r"^\s*\d+\.\s+\*\*(.+?)\*\*"

        lines = instructions_md.splitlines()
        start_idx: int | None = None
        for index, line in enumerate(lines):
            if re.match(heading_pattern, line.strip(), flags=re.IGNORECASE):
                start_idx = index + 1
                break

        if start_idx is None:
            return []

        parsed: list[str] = []
        for line in lines[start_idx:]:
            stripped = line.strip()
            if stripped.startswith("## "):
                break

            match = re.match(artifact_pattern, stripped)
            if not match:
                continue

            artifact_name = match.group(1).strip()
            if artifact_name:
                parsed.append(artifact_name)

        return parsed
