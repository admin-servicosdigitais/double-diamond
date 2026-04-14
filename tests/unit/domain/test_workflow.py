import pytest

from src.domain.models.workflow import StageStatus, can_transition


class TestStageStatus:
    def test_enum_values(self):
        assert StageStatus.PENDING == "pending"
        assert StageStatus.DRAFT == "draft"
        assert StageStatus.RUNNING == "running"
        assert StageStatus.AWAITING_HUMAN_APPROVAL == "awaiting_human_approval"
        assert StageStatus.APPROVED == "approved"
        assert StageStatus.COMPLETED == "completed"
        assert StageStatus.FAILED == "failed"


class TestCanTransition:
    @pytest.mark.parametrize(
        "current,target,expected",
        [
            # From None (initial state)
            (None, StageStatus.DRAFT, True),
            (None, StageStatus.RUNNING, True),
            (None, StageStatus.PENDING, False),
            (None, StageStatus.COMPLETED, False),
            # From PENDING
            (StageStatus.PENDING, StageStatus.DRAFT, True),
            (StageStatus.PENDING, StageStatus.RUNNING, True),
            (StageStatus.PENDING, StageStatus.COMPLETED, False),
            # From DRAFT
            (StageStatus.DRAFT, StageStatus.RUNNING, True),
            (StageStatus.DRAFT, StageStatus.DRAFT, True),  # Same state
            (StageStatus.DRAFT, StageStatus.PENDING, False),
            # From RUNNING
            (StageStatus.RUNNING, StageStatus.AWAITING_HUMAN_APPROVAL, True),
            (StageStatus.RUNNING, StageStatus.FAILED, True),
            (StageStatus.RUNNING, StageStatus.PENDING, False),
            # From AWAITING_HUMAN_APPROVAL
            (StageStatus.AWAITING_HUMAN_APPROVAL, StageStatus.APPROVED, True),
            (StageStatus.AWAITING_HUMAN_APPROVAL, StageStatus.FAILED, True),
            (StageStatus.AWAITING_HUMAN_APPROVAL, StageStatus.RUNNING, False),
            # From APPROVED
            (StageStatus.APPROVED, StageStatus.COMPLETED, True),
            (StageStatus.APPROVED, StageStatus.RUNNING, True),
            (StageStatus.APPROVED, StageStatus.PENDING, False),
            # From COMPLETED (terminal)
            (StageStatus.COMPLETED, StageStatus.COMPLETED, True),
            (StageStatus.COMPLETED, StageStatus.RUNNING, False),
            # From FAILED
            (StageStatus.FAILED, StageStatus.RUNNING, True),
            (StageStatus.FAILED, StageStatus.COMPLETED, False),
        ],
    )
    def test_transitions(self, current, target, expected):
        assert can_transition(current, target) == expected