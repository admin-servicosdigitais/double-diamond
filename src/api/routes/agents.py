from fastapi import APIRouter, HTTPException

from src.domain.models.agent_definition import AgentDefinition
from src.loaders.agent_markdown_loader import AgentMarkdownLoader

router = APIRouter(prefix="/agents", tags=["agents"])
loader = AgentMarkdownLoader()


@router.get("", response_model=list[AgentDefinition])
def list_agents() -> list[AgentDefinition]:
    return loader.load_all()


@router.get("/{agent_id}", response_model=AgentDefinition)
def get_agent(agent_id: str) -> AgentDefinition:
    agent = loader.load_by_id(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent
