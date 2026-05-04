from src.domain.models.quality_gate import QualityGateRecommendation, QualityGateState, QualityGateStatus


def test_quality_gate_serialization_roundtrip() -> None:
    gate = QualityGateState(
        status=QualityGateStatus.ANSWERED,
        questions=["Pergunta 1"],
        answers=[{"question_id": "q1", "answer": "Resposta 1"}],
        recommendation=QualityGateRecommendation.REVIEW_BEFORE_APPROVE,
    )

    payload = gate.model_dump(mode="json")
    restored = QualityGateState.model_validate(payload)

    assert restored.status == QualityGateStatus.ANSWERED
    assert restored.questions == ["Pergunta 1"]
    assert restored.answers == [{"question_id": "q1", "answer": "Resposta 1"}]
    assert restored.recommendation == QualityGateRecommendation.REVIEW_BEFORE_APPROVE
