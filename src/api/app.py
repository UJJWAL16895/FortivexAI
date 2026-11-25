from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.api.text_session import text_session
from src.api.voice import router as voice_router
from src.core.settings import Settings
from src.llm.reply import ReplyPath, RequestBudget


class Health(BaseModel):
    status: Literal["ok"]
    mode: Literal["mock", "live"]


def create_app() -> FastAPI:
    settings = Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with httpx.AsyncClient(timeout=12, trust_env=False) as client:
            app.state.http = client
            app.state.replies = ReplyPath(settings, client)
            app.state.voice_budget = RequestBudget(
                settings.gemini_rpm, settings.gemini_daily, settings.gemini_tpm
            )
            yield

    app = FastAPI(title="ShelfPilot Sales Agent", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.replies = ReplyPath(settings)

    @app.get("/health", response_model=Health, operation_id="getHealth")
    async def health() -> Health:
        """Process liveness and configured mode. Does not contact providers."""
        return Health(status="ok", mode=settings.agent_mode)

    app.add_api_websocket_route("/ws/text", text_session)
    app.include_router(voice_router)
    dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if (dist / "index.html").is_file():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

        @app.get("/", include_in_schema=False)
        async def console() -> FileResponse:
            return FileResponse(dist / "index.html")

    return app
