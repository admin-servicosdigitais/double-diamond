from src.domain.models.health import AgentHealthStatus, HealthResponse


class HealthService:
    def __init__(self, loader: object) -> None:
        self._loader = loader

    def get_health(self) -> HealthResponse:
        agents = self._loader.load_all()
        return HealthResponse(
            status="ok",
            agents=[self._to_agent_status(a) for a in agents],
        )

    @staticmethod
    def _to_agent_status(agent: object) -> AgentHealthStatus:
        parts = agent.id.split("-", 1)
        agent_id = int(parts[0])
        agent_name = parts[1] if len(parts) > 1 else agent.id
        return AgentHealthStatus(id=agent_id, name=agent_name, status="ready")
