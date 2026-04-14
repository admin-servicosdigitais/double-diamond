#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.application.services.workflow_service import WorkflowService
from src.infrastructure.persistence.workflow_repository import WorkflowRepository

ALL_STAGES = [
    "1-explorer",
    "2-intake",
    "3-sourcing",
    "4-pesquisa",
    "5-framing",
    "6-ideacao",
    "7-validacao",
    "8-prototype-visual",
    "9-definicao",
]


def _stage_input(stage: str) -> dict:
    return {
        "stage": stage,
        "context": f"input-{stage}",
        "temas": ["corrida", "saude"],
    }


def run_full_workflow_assertions(base_path: Path) -> None:
    os.environ["AGNO_MOCK"] = "1"

    repository = WorkflowRepository(base_path=base_path)
    service = WorkflowService(repository=repository)
    workflow_id = "wf-integration-full"

    service.create_workflow(workflow_id)

    current_stage = ALL_STAGES[0]
    result = service.run_stage(workflow_id, current_stage, _stage_input(current_stage))
    assert result.status == "awaiting_human_approval"

    for index, stage in enumerate(ALL_STAGES):
        outputs = service.get_stage_outputs(workflow_id, stage)
        assert outputs["compact_output_text"].strip()
        assert outputs["full_output_paths"]
        assert outputs["metadata"].get("run_id")

        stage_dir = base_path / workflow_id / "stages" / stage
        assert (stage_dir / "input.json").exists()
        assert (stage_dir / "output_compact.md").exists()
        assert (stage_dir / "metadata.json").exists()

        service.approve_stage(workflow_id, stage)

        if index < len(ALL_STAGES) - 1:
            next_result = service.run_next_stage(workflow_id, stage, _stage_input(ALL_STAGES[index + 1]))
            assert next_result.status == "awaiting_human_approval"
            assert next_result.stage == ALL_STAGES[index + 1]

    final_stage_state = service.get_stage_state(workflow_id, "9-definicao")
    assert final_stage_state.status == "completed"


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa teste de integração completo do workflow")
    parser.add_argument(
        "--base-path",
        type=Path,
        default=None,
        help="Diretório para persistência. Se omitido, usa diretório temporário.",
    )
    args = parser.parse_args()

    if args.base_path is not None:
        args.base_path.mkdir(parents=True, exist_ok=True)
        run_full_workflow_assertions(args.base_path)
        print("OK: integração completa validada.")
        return

    with TemporaryDirectory(prefix="workflow-integration-") as temp_dir:
        run_full_workflow_assertions(Path(temp_dir) / "workflows")
        print("OK: integração completa validada.")


if __name__ == "__main__":
    main()
