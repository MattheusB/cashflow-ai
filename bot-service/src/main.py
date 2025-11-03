"""FastAPI main application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router
from .utils.config import get_settings
from .utils.logger import setup_logger

logger = setup_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    logger.info("Starting Bot Service...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Model: {settings.llm_model}")
    yield
    logger.info("Shutting down Bot Service...")


app = FastAPI(
    title="Expense Tracker Bot Service",
    description="LLM-powered expense extraction and categorization service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api", tags=["expenses"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Expense Tracker Bot Service",
        "status": "running",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.bot_service_host,
        port=settings.bot_service_port,
        reload=settings.environment == "development",
    )
