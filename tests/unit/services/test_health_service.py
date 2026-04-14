import pytest

from src.application.services.health_service import HealthService
from src.domain.models.agent_definition import AgentDefinition


def _make_agent(agent_id: str) -> AgentDefinition:
    return AgentDefinition(
        id=agent_id,
        stage=agent_id,
        name=agent_id,
        description="test",
        role="test",
        model="gpt-4",
        summary_format="markdown",
        instructions_md="test",
    )


class _StubLoader:
    def __init__(self, agents: list[AgentDefinition]) -> None:
        self._agents = agents

    def load_all(self) -> list[AgentDefinition]:
        return self._agents


class TestHealthService:
    def test_get_health_returns_ok_status(self):
        service = HealthService(_StubLoader([]))
        result = service.get_health()
        assert result.status == "ok"

    def test_empty_agents_list(self):
        service = HealthService(_StubLoader([]))
        result = service.get_health()
        assert result.agents == []

    def test_get_health_lists_all_agents(self):
        agents = [_make_agent("1-explorer"), _make_agent("2-intake"), _make_agent("3-sourcing")]
        service = HealthService(_StubLoader(agents))
        result = service.get_health()
        assert len(result.agents) == 3

    def test_agent_id_parsed_correctly(self):
        service = HealthService(_StubLoader([_make_agent("1-explorer")]))
        result = service.get_health()
        assert result.agents[0].id == 1

    def test_agent_name_parsed_correctly(self):
        service = HealthService(_StubLoader([_make_agent("1-explorer")]))
        result = service.get_health()
        assert result.agents[0].name == "explorer"

    def test_agent_status_is_ready(self):
        service = HealthService(_StubLoader([_make_agent("1-explorer")]))
        result = service.get_health()
        assert result.agents[0].status == "ready"

    def test_compound_name_preserved(self):
        service = HealthService(_StubLoader([_make_agent("8-prototype-visual")]))
        result = service.get_health()
        assert result.agents[0].id == 8
        assert result.agents[0].name == "prototype-visual"
