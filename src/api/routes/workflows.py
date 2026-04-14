import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from src.application.services.workflow_service import WorkflowService
from src.domain.models.execution import StageExecutionResult
from src.domain.models.workflow import StageState, WorkflowState
from src.infrastructure.persistence.repository_factory import build_workflow_repository

router = APIRouter(prefix="/workflows", tags=["workflows"])
workflow_service = WorkflowService(repository=build_workflow_repository())


class CreateWorkflowRequest(BaseModel):
    workflow_id: str
    name: str | None = None
    words: list[str]


class RunStageRequest(BaseModel):
    input: str | dict[str, Any] | None = None


class RunNextStageRequest(BaseModel):
    input: str | dict[str, Any] | None = None


class UpdateArtifactRequest(BaseModel):
    content: str


@router.get("", response_model=list[WorkflowState])
def list_workflows() -> list[WorkflowState]:
    return workflow_service.list_workflows()


@router.post("", response_model=WorkflowState)
def create_workflow(payload: CreateWorkflowRequest) -> WorkflowState:
    logger.info(f"POST /workflows - Payload recebido: {payload}")
    try:
        logger.info(f"Iniciando create_workflow com id={payload.workflow_id}, words={payload.words}")
        result = workflow_service.create_workflow(payload.workflow_id, payload.name, payload.words)
        logger.info(f"create_workflow sucedeu para {payload.workflow_id}")
        return result
    except FileNotFoundError as exc:
        logger.error(f"FileNotFoundError em create_workflow: {exc}")
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        logger.error(f"ValueError em create_workflow: {exc}")
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        import traceback
        error_detail = f"{type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
        logger.error(f"Erro não tratado em create_workflow: {error_detail}")
        raise HTTPException(status_code=400, detail=error_detail) from exc


@router.get("/{workflow_id}", response_model=WorkflowState)
def get_workflow(workflow_id: str) -> WorkflowState:
    try:
        return workflow_service.get_workflow(workflow_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{workflow_id}/stages/{stage}/run", response_model=StageExecutionResult)
def run_stage(workflow_id: str, stage: str, payload: RunStageRequest) -> StageExecutionResult:
    try:
        return workflow_service.run_stage(workflow_id, stage, payload.input)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        import traceback
        error_detail = f"{type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=400, detail=error_detail) from exc


@router.post("/{workflow_id}/stages/{stage}/approve", response_model=WorkflowState)
def approve_stage(workflow_id: str, stage: str) -> WorkflowState:
    try:
        return workflow_service.approve_stage(workflow_id, stage)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{workflow_id}/stages/{stage}/next", response_model=StageExecutionResult)
def run_next_stage(workflow_id: str, stage: str, payload: RunNextStageRequest) -> StageExecutionResult:
    try:
        return workflow_service.run_next_stage(workflow_id, stage, payload.input)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{workflow_id}/stages/{stage}", response_model=StageState)
def get_stage(workflow_id: str, stage: str) -> StageState:
    try:
        return workflow_service.get_stage_state(workflow_id, stage)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{workflow_id}/stages/{stage}/outputs")
def get_stage_outputs(workflow_id: str, stage: str) -> dict[str, Any]:
    try:
        return workflow_service.get_stage_outputs(workflow_id, stage)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{workflow_id}/stages/{stage}/outputs/{artifact}")
def get_stage_artifact(workflow_id: str, stage: str, artifact: str) -> dict[str, Any]:
    try:
        return workflow_service.get_stage_artifact(workflow_id, stage, artifact)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{workflow_id}/stages/{stage}/outputs/{artifact}")
def patch_stage_artifact(
    workflow_id: str,
    stage: str,
    artifact: str,
    payload: UpdateArtifactRequest,
) -> dict[str, Any]:
    try:
        return workflow_service.update_stage_artifact(workflow_id, stage, artifact, payload.content)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{workflow_id}/agents/{agent_code}/latest-output")
def get_latest_output_by_agent_code(workflow_id: str, agent_code: str) -> dict[str, Any]:
    try:
        return workflow_service.get_latest_output_by_agent_code(workflow_id, agent_code)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
