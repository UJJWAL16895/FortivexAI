import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.analytics.store import Dashboard, ReportStore
from src.analytics.worker import Insights
from src.api.text_session import text_session
from src.api.voice import router as voice_router
from src.core.logging import protect_server_logs
from src.core.public import PublicGuard
from src.core.settings import Settings
from src.crm.store import CRM
from src.llm.reply import ReplyPath, RequestBudget
from src.rag.index import Knowledge
from src.voice.local import warm


class Health(BaseModel):
    status: Literal["ok"]
    mode: Literal["mock", "live"]


def create_app() -> FastAPI:
    protect_server_logs()
    settings = Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if settings.public_demo:
            if not app.state.knowledge.records:
                raise RuntimeError("Public startup failed: reviewed knowledge is empty")
            logging.getLogger("uvicorn.error").info(
                "Public startup self-check passed. Mode=%s; reviewed knowledge and SQLite ready.",
                settings.agent_mode,
            )
        if settings.knowledge_embeddings:
            try:
                knowledge = Knowledge.load()
                await asyncio.to_thread(knowledge.enable_embeddings)
                app.state.knowledge = knowledge
            except Exception:
                logging.getLogger("uvicorn.error").warning(
                    "Local embeddings unavailable. Using reviewed keyword retrieval."
                )
        if settings.agent_mode == "live" and settings.voice_stt == "local":
            await warm()
        async with httpx.AsyncClient(timeout=12, trust_env=False) as client:
            app.state.http = client
            app.state.replies = ReplyPath(settings, client)
            app.state.voice_budget = RequestBudget(
                settings.gemini_rpm, settings.gemini_daily, settings.gemini_tpm
            )
            insights: Insights = app.state.insights
            worker = asyncio.create_task(insights.work())
            try:
                yield
            finally:
                await insights.jobs.join()
                worker.cancel()
                with suppress(asyncio.CancelledError):
                    await worker

    app = FastAPI(title="ShelfPilot Sales Agent", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.replies = ReplyPath(settings)
    app.state.knowledge = Knowledge.load()
    app.state.crm = CRM(Path(settings.crm_path))
    app.state.insights = Insights(ReportStore(Path(settings.crm_path)))
    if settings.public_demo:
        access_code = settings.public_access_code
        app.add_middleware(
            PublicGuard,
            access_code=access_code.get_secret_value() if access_code else "",
            rpm=settings.public_requests_per_minute,
            daily=settings.public_daily_request_cap,
        )

    @app.get("/api/public-status")
    async def public_status() -> dict[str, bool | Literal["mock", "live"]]:
        return {
            "public": settings.public_demo,
            "mode": settings.agent_mode,
            "locked": bool(settings.public_demo and settings.public_access_code),
        }

    @app.get("/api/insights")
    async def insights_view() -> Dashboard:
        insights: Insights = app.state.insights
        return await asyncio.to_thread(insights.store.dashboard, insights.dropped)

    @app.get("/api/crm")
    async def crm_view() -> dict[str, list[dict[str, object]]]:
        crm: CRM = app.state.crm
        return await asyncio.to_thread(crm.snapshot)

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
        @app.get("/console", include_in_schema=False)
        async def console() -> FileResponse:
            return FileResponse(dist / "index.html")

    return app
