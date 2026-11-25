from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from src.core.settings import Settings


class Health(BaseModel):
    status: Literal["ok"]
    mode: Literal["mock", "live"]


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(title="ShelfPilot Sales Agent", version="0.1.0")

    @app.get("/health", response_model=Health, operation_id="getHealth")
    async def health() -> Health:
        """Process liveness and configured mode. Does not contact providers."""
        return Health(status="ok", mode=settings.agent_mode)

    return app
