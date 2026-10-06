from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.api.jobs import router as jobs_router
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Distributed Task Queue API",
    description="Scalable async task queue engine with Redis priority queues, exponential retries, and real-time dashboard.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_dashboard():
        return FileResponse(os.path.join(static_dir, "index.html"))

app.include_router(jobs_router, prefix="/api", tags=["Jobs & Queue"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "distributed-task-queue", "version": "1.0.0"}
