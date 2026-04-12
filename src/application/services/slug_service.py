from __future__ import annotations

import re
from typing import Any


class SlugService:
    def resolve_slug(
        self,
        stage_id: str,
        user_input: str | dict[str, Any] | None,
        previous_compact: str | None,
    ) -> str:
        stage_number = self._extract_stage_number(stage_id)

        if stage_number == 1:
            derived = self._derive_from_input(user_input)
            if derived:
                return derived

        inherited = self._extract_slug_from_frontmatter(previous_compact)
        if inherited:
            return inherited

        fallback = self._derive_from_input(user_input)
        if fallback:
            return fallback

        return "workflow"

    @staticmethod
    def _extract_stage_number(stage_id: str) -> int | None:
        try:
            return int(stage_id.split("-", 1)[0])
        except (ValueError, IndexError):
            return None

    def _derive_from_input(self, user_input: str | dict[str, Any] | None) -> str | None:
        if isinstance(user_input, dict):
            for key in ("slug", "tema", "temas", "title", "titulo", "topic", "topics"):
                value = user_input.get(key)
                normalized = self._normalize_candidate(value)
                if normalized:
                    return normalized

        return self._normalize_candidate(user_input)

    def _normalize_candidate(self, value: object) -> str | None:
        if value is None:
            return None

        if isinstance(value, list):
            raw = " ".join(str(item) for item in value)
        else:
            raw = str(value)

        text = raw.strip().lower()
        if not text:
            return None

        text = re.sub(r"[^a-z0-9\s-]", " ", text)
        text = re.sub(r"\s+", "-", text)
        text = re.sub(r"-+", "-", text)
        text = text.strip("-")

        return text[:80] or None

    @staticmethod
    def _extract_slug_from_frontmatter(content: str | None) -> str | None:
        if not content:
            return None

        if not content.strip().startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        frontmatter = parts[1]
        for line in frontmatter.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("slug:"):
                value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                return value or None

        return None
