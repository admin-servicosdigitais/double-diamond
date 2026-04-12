from pydantic import BaseModel, Field


class AgentDefinition(BaseModel):
    id: str
    stage: str
    name: str
    description: str
    role: str
    model: str
    summary_format: str
    instructions_md: str
    tools: list[str] = Field(default_factory=list)
    execution_mode: str = "single_pass"
    max_steps: int = 1
