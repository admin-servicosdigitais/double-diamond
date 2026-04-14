from fastapi import APIRouter

from src.application.services.health_service import HealthService
from src.domain.models.health import HealthResponse
from src.loaders.agent_markdown_loader import AgentMarkdownLoader

router = APIRouter()

_service = HealthService(AgentMarkdownLoader())


@router.get("/health", response_model=HealthResponse, tags=["health"])
def healthcheck() -> HealthResponse:
    return _service.get_health()
