from pathlib import Path

import yaml

from src.domain.models.agent_definition import AgentDefinition


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

        return AgentDefinition(
            id=file_path.parent.name,
            stage=str(metadata.get("stage", "")),
            name=str(metadata.get("name", "")),
            description=str(metadata.get("description", "")),
            role=str(metadata.get("role", "")),
            model=str(metadata.get("model", "")),
            summary_format=str(metadata.get("summary_format", "")),
            instructions_md=instructions_md,
        )

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
