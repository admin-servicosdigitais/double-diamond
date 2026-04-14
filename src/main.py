from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import agents_router, health_router, workflows_router

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="Agent Workflow Orchestrator", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(agents_router)
    app.include_router(workflows_router)
    return app


app = create_app()
