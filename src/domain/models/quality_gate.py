from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class QualityGateStatus(str, Enum):
    NOT_STARTED = "not_started"
    QUESTIONS_GENERATED = "questions_generated"
    ANSWERED = "answered"
    SKIPPED = "skipped"


class QualityGateRecommendation(str, Enum):
    APPROVE = "approve"
    REVIEW_BEFORE_APPROVE = "review_before_approve"
    BLOCK_APPROVAL = "block_approval"


class QualityGateState(BaseModel):
    status: QualityGateStatus = Field(default=QualityGateStatus.NOT_STARTED)
    required_questions: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    answers: list[dict[str, str]] = Field(default_factory=list)
    recommendation: QualityGateRecommendation | None = None
    skip_reason: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
