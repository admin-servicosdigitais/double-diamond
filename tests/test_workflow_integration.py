from pathlib import Path

from scripts.test_full_workflow_integration import run_full_workflow_assertions


def test_full_workflow_integration(tmp_path: Path) -> None:
    run_full_workflow_assertions(tmp_path / "workflows")
