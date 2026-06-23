"""
Entry point — create the FastAPI app, wire the router, and run with uvicorn.
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import config
from src.routes import router

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    log.info("Invoice → GRN agent starting (version=%s, log_level=%s)",
             config.API_VERSION, config.LOG_LEVEL)
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────────
    log.info("Invoice → GRN agent shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Invoice → GRN Data Creation Agent",
        version=config.API_VERSION,
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT)
