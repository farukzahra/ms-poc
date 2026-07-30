from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.chat import router as chat_router
from app.routes.health import router as health_router
from app.storage.blob import sync_documents_from_blob
from app.telemetry.insights import configure_application_insights

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_application_insights()

    app = FastAPI(
        title="Enterprise AI Sales Intelligence API",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.cors_origin, "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(chat_router)

    @app.on_event("startup")
    async def startup() -> None:
        try:
            sync_documents_from_blob()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Blob sync skipped: %s", exc)

    return app


app = create_app()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
