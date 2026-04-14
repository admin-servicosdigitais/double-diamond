from enum import Enum

from pydantic import BaseModel, Field


class ProviderEnum(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class AgentDefinition(BaseModel):
    id: str
    stage: str
    name: str
    description: str
    role: str
    model: str
    provider: ProviderEnum | None = None
    summary_format: str
    instructions_md: str
    tools: list[str] = Field(default_factory=list)
    execution_mode: str = "single_pass"
    max_steps: int = 1
    output_artifacts: list[str] = Field(default_factory=list)
