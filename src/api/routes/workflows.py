from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.application.services.workflow_service import WorkflowService
from src.domain.models.execution import StageExecutionResult
from src.domain.models.workflow import StageState, WorkflowState
from src.infrastructure.persistence.repository_factory import build_workflow_repository

router = APIRouter(prefix="/workflows", tags=["workflows"])
workflow_service = WorkflowService(repository=build_workflow_repository())


class CreateWorkflowRequest(BaseModel):
    workflow_id: str
    name: str | None = None


class RunStageRequest(BaseModel):
    input: str | dict[str, Any] | None = None


class RunNextStageRequest(BaseModel):
    input: str | dict[str, Any] | None = None


@router.get("", response_model=list[WorkflowState])
def list_workflows() -> list[WorkflowState]:
    return workflow_service.list_workflows()


@router.post("", response_model=WorkflowState)
def create_workflow(payload: CreateWorkflowRequest) -> WorkflowState:
    try:
        return workflow_service.create_workflow(payload.workflow_id, payload.name)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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


@router.get("/{workflow_id}/agents/{agent_code}/latest-output")
def get_latest_output_by_agent_code(workflow_id: str, agent_code: str) -> dict[str, Any]:
    try:
        return workflow_service.get_latest_output_by_agent_code(workflow_id, agent_code)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

