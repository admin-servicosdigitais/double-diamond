from pathlib import Path

import pytest

from src.application.services.quality_gate_service import QualityGateService
from src.infrastructure.persistence.workflow_repository import WorkflowRepository


class DummyRunner:
    def __init__(self, response: str = "", error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.calls = 0

    def run(self, agent_definition, prompt: str) -> str:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.response


@pytest.fixture
def repo(tmp_path: Path):
    return WorkflowRepository(base_path=tmp_path / "workflows")


def _seed_stage(repo: WorkflowRepository, workflow_id: str) -> None:
    from src.application.services.workflow_service import WorkflowService

    wf_service = WorkflowService(repository=repo)
    wf_service.create_workflow(workflow_id, words=[])
    repo.save_stage_output(
        workflow_id=workflow_id,
        stage="1-explorer",
        compact_output_text="Resumo com evidências e plano.",
        full_outputs={"evidencia.md": "conteudo"},
    )


def test_quality_gate_mock_mode_uses_deterministic(repo, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGNO_MOCK", "1")
    runner = DummyRunner(response='{"diagnosis":"x","recommendation":"approve"}')
    _seed_stage(repo, "wf-qg-mock")

    service = QualityGateService(repository=repo, agent_runner=runner)
    draft = service.generate_for_stage("wf-qg-mock", "1-explorer")

    assert draft.recommendation == "approve"
    assert runner.calls == 0


def test_quality_gate_llm_mode_attempts_runner(repo, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGNO_MOCK", "0")
    monkeypatch.setenv("AGNO_DEFAULT_PROVIDER", "openai")
    valid_json = (
        '{"diagnosis":"ok","gaps":[],"required_questions":["q1"],'
        '"optional_questions":[],"recommendation":"review_before_approve"}'
    )
    runner = DummyRunner(response=valid_json)
    _seed_stage(repo, "wf-qg-llm")

    service = QualityGateService(repository=repo, agent_runner=runner)
    draft = service.generate_for_stage("wf-qg-llm", "1-explorer")

    assert runner.calls == 1
    assert draft.diagnosis == "ok"
    assert draft.recommendation == "review_before_approve"


def test_quality_gate_llm_valid_json_contract(repo, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGNO_MOCK", "0")
    monkeypatch.setenv("AGNO_DEFAULT_PROVIDER", "openai")
    runner = DummyRunner(
        response='{"diagnosis":"d","gaps":["g"],"required_questions":[],"optional_questions":["o"],"recommendation":"approve"}'
    )
    _seed_stage(repo, "wf-qg-valid-json")

    service = QualityGateService(repository=repo, agent_runner=runner)
    draft = service.generate_for_stage("wf-qg-valid-json", "1-explorer")

    assert isinstance(draft.required_questions, list)
    assert isinstance(draft.optional_questions, list)
    assert draft.recommendation == "approve"


def test_quality_gate_llm_failure_falls_back_to_deterministic(repo, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGNO_MOCK", "0")
    monkeypatch.setenv("AGNO_DEFAULT_PROVIDER", "openai")
    runner = DummyRunner(error=RuntimeError("timeout"))
    _seed_stage(repo, "wf-qg-fallback")

    service = QualityGateService(repository=repo, agent_runner=runner)
    draft = service.generate_for_stage("wf-qg-fallback", "1-explorer")

    assert runner.calls == 1
    assert draft.recommendation == "approve"
    assert "regras determinísticas" in draft.diagnosis


def test_quality_gate_response_compatible_with_clarify_shape(repo, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGNO_MOCK", "0")
    monkeypatch.setenv("AGNO_DEFAULT_PROVIDER", "openai")
    runner = DummyRunner(
        response='{"diagnosis":"d","gaps":[],"required_questions":["rq"],"optional_questions":["oq"],"recommendation":"block_approval"}'
    )
    _seed_stage(repo, "wf-qg-shape")

    service = QualityGateService(repository=repo, agent_runner=runner)
    draft = service.generate_for_stage("wf-qg-shape", "1-explorer")

    payload = draft.model_dump()
    assert set(payload.keys()) == {"diagnosis", "gaps", "required_questions", "optional_questions", "recommendation"}
