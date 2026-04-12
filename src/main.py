from fastapi import FastAPI

from src.api.routes import agents_router, health_router, workflows_router


def create_app() -> FastAPI:
    app = FastAPI(title="Agent Workflow Orchestrator", version="0.1.0")
    app.include_router(health_router)
    app.include_router(agents_router)
    app.include_router(workflows_router)
    return app


app = create_app()
