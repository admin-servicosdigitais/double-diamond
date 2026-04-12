from typing import Any

from pydantic import BaseModel, Field


class StageExecutionRequest(BaseModel):
    workflow_id: str
    stage: str
    user_input: str | None = None
    additional_context: dict[str, Any] | None = None


class StageExecutionResult(BaseModel):
    workflow_id: str
    run_id: str
    stage: str
    agent_id: str
    status: str
    compact_output_text: str
    full_output_paths: list[str] = Field(default_factory=list)
    next_stage_available: bool = False
