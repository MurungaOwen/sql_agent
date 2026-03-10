from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from sql_agent.config import Settings
from sql_agent.factory import build_orchestrator
from sql_agent.orchestrator import SQLAgentOrchestrator

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(title="SQL Agent API", version="0.1.0")
app.mount("/assets", StaticFiles(directory=WEB_DIR / "assets"), name="assets")


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class AskResponse(BaseModel):
    question: str
    sql: str
    rows: str
    summary: str


@lru_cache(maxsize=1)
def get_orchestrator() -> SQLAgentOrchestrator:
    settings = Settings.from_env()
    return build_orchestrator(settings)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        result = get_orchestrator().run(request.question)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    except Exception as err:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {err}") from err

    return AskResponse(
        question=result.user_question,
        sql=result.sql,
        rows=result.rows,
        summary=result.summary,
    )
