import asyncio
import hashlib
import json
import uuid
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, Dict

from app.core.config import settings

class JobPriority(str, Enum):
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"

class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"

PRIORITY_SCORES = {
    JobPriority.HIGH: 100,
    JobPriority.NORMAL: 50,
    JobPriority.LOW: 10,
}

# In-memory mock storage for zero-dependency local runs
_memory_jobs: Dict[str, dict] = {}
_memory_queue: list = []  # sorted by priority
_memory_dlq: list = []

_redis_client = None
_redis_available = True

async def get_redis():
    global _redis_client, _redis_available
    if not _redis_available:
        return None
    if _redis_client is None:
        try:
            import redis.asyncio as aioredis
            client = aioredis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1.5)
            await client.ping()
            _redis_client = client
        except Exception:
            _redis_available = False
            return None
    return _redis_client

async def enqueue_job(
    job_type: str,
    payload: dict,
    priority: JobPriority = JobPriority.NORMAL,
    delay_seconds: int = 0,
    max_retries: int = 3,
    idempotency_key: Optional[str] = None,
) -> dict:
    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    scheduled_at = (datetime.utcnow() + timedelta(seconds=delay_seconds)).isoformat()

    job_data = {
        "id": job_id,
        "job_type": job_type,
        "payload": payload,
        "priority": priority.value,
        "status": JobStatus.QUEUED.value,
        "created_at": now,
        "scheduled_at": scheduled_at,
        "retry_count": 0,
        "max_retries": max_retries,
        "idempotency_key": idempotency_key,
        "result": None,
        "error": None,
    }

    r = await get_redis()
    if r:
        try:
            await r.set(f"job:{job_id}", json.dumps(job_data))
            score = PRIORITY_SCORES.get(priority, 50) + (1.0 / (time.time() + delay_seconds))
            await r.zadd("queue:jobs", {job_id: score})
            return job_data
        except Exception:
            pass

    # In-memory fallback
    _memory_jobs[job_id] = job_data
    _memory_queue.append(job_data)
    _memory_queue.sort(key=lambda x: PRIORITY_SCORES.get(JobPriority(x["priority"]), 50), reverse=True)
    return job_data

async def get_job_status(job_id: str) -> Optional[dict]:
    r = await get_redis()
    if r:
        try:
            val = await r.get(f"job:{job_id}")
            if val:
                return json.loads(val)
        except Exception:
            pass
    return _memory_jobs.get(job_id)

async def dequeue_job() -> Optional[dict]:
    r = await get_redis()
    if r:
        try:
            items = await r.zpopmax("queue:jobs", count=1)
            if items:
                job_id, _ = items[0]
                val = await r.get(f"job:{job_id}")
                if val:
                    job = json.loads(val)
                    job["status"] = JobStatus.PROCESSING.value
                    await r.set(f"job:{job_id}", json.dumps(job))
                    return job
        except Exception:
            pass

    if _memory_queue:
        job = _memory_queue.pop(0)
        job["status"] = JobStatus.PROCESSING.value
        return job
    return None

async def complete_job(job_id: str, result: Any = None):
    r = await get_redis()
    if r:
        try:
            val = await r.get(f"job:{job_id}")
            if val:
                job = json.loads(val)
                job["status"] = JobStatus.COMPLETED.value
                job["result"] = result
                job["completed_at"] = datetime.utcnow().isoformat()
                await r.set(f"job:{job_id}", json.dumps(job))
                await r.incr("stats:completed")
                return
        except Exception:
            pass

    if job_id in _memory_jobs:
        _memory_jobs[job_id]["status"] = JobStatus.COMPLETED.value
        _memory_jobs[job_id]["result"] = result
        _memory_jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()

async def fail_job(job_id: str, error: str):
    r = await get_redis()
    if r:
        try:
            val = await r.get(f"job:{job_id}")
            if val:
                job = json.loads(val)
                job["retry_count"] += 1
                job["error"] = error
                if job["retry_count"] >= job["max_retries"]:
                    job["status"] = JobStatus.DEAD_LETTER.value
                    await r.zadd("queue:dlq", {job_id: time.time()})
                else:
                    job["status"] = JobStatus.QUEUED.value
                    await r.zadd("queue:jobs", {job_id: 10})
                await r.set(f"job:{job_id}", json.dumps(job))
                return
        except Exception:
            pass

    if job_id in _memory_jobs:
        job = _memory_jobs[job_id]
        job["retry_count"] += 1
        job["error"] = error
        if job["retry_count"] >= job["max_retries"]:
            job["status"] = JobStatus.DEAD_LETTER.value
            _memory_dlq.append(job)
        else:
            job["status"] = JobStatus.QUEUED.value
            _memory_queue.append(job)

async def get_queue_stats() -> dict:
    r = await get_redis()
    if r:
        try:
            q_len = await r.zcard("queue:jobs")
            dlq_len = await r.zcard("queue:dlq")
            completed = int(await r.get("stats:completed") or 0)
            return {
                "queued_jobs": q_len,
                "dead_letter_jobs": dlq_len,
                "completed_jobs": completed,
                "active_workers": settings.NUM_WORKERS,
                "backend": "redis",
            }
        except Exception:
            pass

    completed_count = sum(1 for j in _memory_jobs.values() if j.get("status") == JobStatus.COMPLETED.value)
    return {
        "queued_jobs": len(_memory_queue),
        "dead_letter_jobs": len(_memory_dlq),
        "completed_jobs": completed_count,
        "active_workers": settings.NUM_WORKERS,
        "backend": "in-memory",
    }
