from pydantic import BaseModel


class AgentDefinition(BaseModel):
    id: str
    stage: str
    name: str
    description: str
    role: str
    model: str
    summary_format: str
    instructions_md: str
