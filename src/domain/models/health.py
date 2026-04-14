from pydantic import BaseModel


class AgentHealthStatus(BaseModel):
    id: int
    name: str
    status: str


class HealthResponse(BaseModel):
    status: str
    agents: list[AgentHealthStatus]
