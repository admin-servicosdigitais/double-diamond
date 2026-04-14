import pytest

from src.application.services.slug_service import SlugService


class TestSlugService:
    def test_resolve_slug_stage_1_with_input(self):
        service = SlugService()
        result = service.resolve_slug("1-explorer", {"temas": ["fintech", "saude"]}, None)
        assert result == "fintech-saude"

    def test_resolve_slug_stage_1_with_string_input(self):
        service = SlugService()
        result = service.resolve_slug("1-explorer", "fintech innovation", None)
        assert result == "fintech-innovation"

    def test_resolve_slug_non_stage_1_inherits_from_previous(self):
        service = SlugService()
        previous_compact = """---
slug: inherited-slug
---
Content here"""
        result = service.resolve_slug("2-intake", None, previous_compact)
        assert result == "inherited-slug"

    def test_resolve_slug_fallback_to_input(self):
        service = SlugService()
        result = service.resolve_slug("2-intake", {"topic": "fallback topic"}, None)
        assert result == "fallback-topic"

    def test_resolve_slug_default_workflow(self):
        service = SlugService()
        result = service.resolve_slug("2-intake", None, None)
        assert result == "workflow"

    @pytest.mark.parametrize(
        "stage_id,expected",
        [
            ("1-explorer", 1),
            ("2-intake", 2),
            ("10-final", 10),
            ("invalid", None),
            ("no-number", None),
        ],
    )
    def test_extract_stage_number(self, stage_id, expected):
        result = SlugService._extract_stage_number(stage_id)
        assert result == expected

    @pytest.mark.parametrize(
        "user_input,expected",
        [
            ({"temas": ["fintech", "saude"]}, "fintech-saude"),
            ({"slug": "custom-slug"}, "custom-slug"),
            ({"titulo": "Título com Acentos"}, "t-tulo-com-acentos"),
            ("simple string", "simple-string"),
            (None, None),
            ({}, None),
            ({"other": "value"}, None),
        ],
    )
    def test_derive_from_input(self, user_input, expected):
        service = SlugService()
        result = service._derive_from_input(user_input)
        assert result == expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("Hello World!", "hello-world"),
            ("Fintech & Saúde", "fintech-sa-de"),
            ("Multiple   Spaces", "multiple-spaces"),
            ("--leading-trailing--", "leading-trailing"),
            ("", None),
            (None, None),
            (123, "123"),
            (["item1", "item2"], "item1-item2"),
        ],
    )
    def test_normalize_candidate(self, value, expected):
        service = SlugService()
        result = service._normalize_candidate(value)
        assert result == expected

    @pytest.mark.parametrize(
        "content,expected",
        [
            ("---\nslug: test-slug\n---\nContent", "test-slug"),
            ("---\nslug: 'quoted'\n---", "quoted"),
            ("---\nother: value\n---", None),
            ("No frontmatter", None),
            (None, None),
            ("---\nslug:\n---", None),
        ],
    )
    def test_extract_slug_from_frontmatter(self, content, expected):
        result = SlugService._extract_slug_from_frontmatter(content)
        assert result == expected