from __future__ import annotations

from datetime import datetime


class FileNamingService:
    def build_filename(self, slug: str, agent_id: str, artifact: str, when: datetime | None = None) -> str:
        date_str = (when or datetime.utcnow()).strftime("%Y%m%d")
        agent_name = self._extract_agent_name(agent_id)
        safe_artifact = artifact.strip().lower().replace("_", "-").replace(" ", "-")
        return f"{slug}--{date_str}--{agent_name}--{safe_artifact}.md"

    @staticmethod
    def _extract_agent_name(agent_id: str) -> str:
        if "-" not in agent_id:
            return agent_id.strip().lower()
        return agent_id.split("-", 1)[1].strip().lower()
