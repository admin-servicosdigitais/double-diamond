from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class StageStatus(str, Enum):
    PENDING = "pending"
    DRAFT = "draft"
    RUNNING = "running"
    AWAITING_HUMAN_APPROVAL = "awaiting_human_approval"
    APPROVED = "approved"
    COMPLETED = "completed"
    FAILED = "failed"


_ALLOWED_TRANSITIONS: dict[StageStatus, set[StageStatus]] = {
    StageStatus.PENDING: {StageStatus.DRAFT, StageStatus.RUNNING},
    StageStatus.DRAFT: {StageStatus.RUNNING},
    StageStatus.RUNNING: {StageStatus.AWAITING_HUMAN_APPROVAL, StageStatus.FAILED},
    StageStatus.AWAITING_HUMAN_APPROVAL: {StageStatus.APPROVED, StageStatus.FAILED},
    StageStatus.APPROVED: {StageStatus.COMPLETED, StageStatus.RUNNING},
    StageStatus.COMPLETED: set(),
    StageStatus.FAILED: {StageStatus.RUNNING},
}


def can_transition(current: StageStatus | None, target: StageStatus) -> bool:
    if current is None:
        return target in {StageStatus.DRAFT, StageStatus.RUNNING}

    if current == target:
        return True

    return target in _ALLOWED_TRANSITIONS.get(current, set())


class StageState(BaseModel):
    id: str
    name: str
    status: StageStatus = Field(default=StageStatus.PENDING)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowState(BaseModel):
    id: str
    name: str
    stages: list[StageState] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
