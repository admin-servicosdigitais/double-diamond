from __future__ import annotations

import os
from pathlib import Path

from src.infrastructure.persistence.repository_protocol import WorkflowRepositoryProtocol
from src.infrastructure.persistence.sqlite_workflow_repository import SQLiteWorkflowRepository
from src.infrastructure.persistence.workflow_repository import WorkflowRepository


def build_workflow_repository() -> WorkflowRepositoryProtocol:
    backend = os.getenv("WORKFLOW_BACKEND", "filesystem").strip().lower()

    if backend == "sqlite":
        db_path = Path(os.getenv("WORKFLOW_SQLITE_PATH", "data/workflows/workflows.db"))
        return SQLiteWorkflowRepository(db_path=db_path)

    base_path = Path(os.getenv("WORKFLOW_BASE_PATH", "data/workflows"))
    return WorkflowRepository(base_path=base_path)
