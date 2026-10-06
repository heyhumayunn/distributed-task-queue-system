from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Any, List
from enum import Enum

from app.core.queue import (
    enqueue_job, get_job_status, get_queue_stats,
    JobPriority, JobStatus, _memory_jobs
)

router = APIRouter()

class EnqueueRequest(BaseModel):
    job_type: str = Field(..., description="Registered job handler (e.g. send_email, http_webhook, generate_report, resize_image)")
    payload: dict = Field(default_factory=dict, description="Arbitrary task payload parameters")
    priority: JobPriority = Field(default=JobPriority.NORMAL, description="Queue priority level")
    delay_seconds: int = Field(default=0, ge=0, description="Optional delay before execution")
    max_retries: int = Field(default=3, ge=0, le=10, description="Max retry attempts on failure")
    idempotency_key: Optional[str] = Field(default=None, description="Unique key for deduplication")

@router.post("/jobs", status_code=201, summary="Enqueue new async job")
async def create_job(req: EnqueueRequest):
    job = await enqueue_job(
        job_type=req.job_type,
        payload=req.payload,
        priority=req.priority,
        delay_seconds=req.delay_seconds,
        max_retries=req.max_retries,
        idempotency_key=req.idempotency_key,
    )
    return job

@router.get("/jobs/{job_id}", summary="Get job status and result")
async def fetch_job(job_id: str):
    job = await get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return job

@router.get("/stats", summary="Get queue health and throughput stats")
async def fetch_stats():
    return await get_queue_stats()

@router.get("/jobs", summary="List recent jobs")
async def list_jobs(limit: int = 50):
    jobs = list(_memory_jobs.values())[-limit:]
    return {"jobs": list(reversed(jobs))}
