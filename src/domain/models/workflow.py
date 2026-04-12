from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class StageState(BaseModel):
    id: str
    name: str
    status: str = Field(default="pending")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowState(BaseModel):
    id: str
    name: str
    stages: list[StageState] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
