from datetime import datetime

import pytest

from src.application.services.file_naming_service import FileNamingService


class TestFileNamingService:
    def test_build_filename_basic(self):
        service = FileNamingService()
        when = datetime(2024, 1, 15, 10, 30)
        result = service.build_filename("test-slug", "1-explorer", "prompt", when)
        assert result == "test-slug--20240115--explorer--prompt.md"

    def test_build_filename_with_spaces_and_underscores(self):
        service = FileNamingService()
        result = service.build_filename("my-slug", "2-intake", "full output")
        # Should replace spaces with hyphens
        assert "full-output" in result

    def test_build_filename_current_time(self):
        service = FileNamingService()
        result = service.build_filename("slug", "agent", "artifact")
        # Should contain current date
        assert "--" in result
        assert result.endswith(".md")

    @pytest.mark.parametrize(
        "agent_id,expected",
        [
            ("1-explorer", "explorer"),
            ("2-intake", "intake"),
            ("multiple-dashes-here", "dashes-here"),
        ],
    )
    def test_extract_agent_name(self, agent_id, expected):
        result = FileNamingService._extract_agent_name(agent_id)
        assert result == expected