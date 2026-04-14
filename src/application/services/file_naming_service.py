from __future__ import annotations

from datetime import datetime
import re
import unicodedata


class FileNamingService:
    def build_filename(self, slug: str, agent_id: str, artifact: str, when: datetime | None = None) -> str:
        date_str = (when or datetime.utcnow()).strftime("%Y%m%d")
        agent_name = self._extract_agent_name(agent_id)
        safe_artifact = self._slugify_fragment(artifact)
        return f"{slug}--{date_str}--{agent_name}--{safe_artifact}.md"

    @staticmethod
    def _extract_agent_name(agent_id: str) -> str:
        if "-" not in agent_id:
            return agent_id.strip().lower()
        return agent_id.split("-", 1)[1].strip().lower()

    @staticmethod
    def _slugify_fragment(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        lowered = ascii_text.strip().lower().replace("_", "-")
        compact = re.sub(r"[^a-z0-9\- ]", "", lowered)
        hyphenated = re.sub(r"[\s\-]+", "-", compact).strip("-")
        return hyphenated or "artifact"
