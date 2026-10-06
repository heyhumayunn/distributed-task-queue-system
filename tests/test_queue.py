import asyncio
import pytest
from app.core.queue import (
    enqueue_job, dequeue_job, complete_job, fail_job,
    get_job_status, get_queue_stats, JobPriority, JobStatus
)

def run_async(coro):
    return asyncio.run(coro)

def test_enqueue_and_get_job():
    job = run_async(enqueue_job(
        job_type="send_email",
        payload={"to": "test@example.com"},
        priority=JobPriority.HIGH
    ))
    assert job is not None
    assert job["job_type"] == "send_email"
    assert job["priority"] == "HIGH"
    assert job["status"] == "QUEUED"

    fetched = run_async(get_job_status(job["id"]))
    assert fetched is not None
    assert fetched["id"] == job["id"]

def test_dequeue_and_complete_job():
    job = run_async(enqueue_job(
        job_type="generate_report",
        payload={"report_id": 123},
        priority=JobPriority.NORMAL
    ))
    
    dequeued = run_async(dequeue_job())
    assert dequeued is not None
    assert dequeued["status"] == "PROCESSING"

    run_async(complete_job(dequeued["id"], result={"status": "done"}))
    completed = run_async(get_job_status(dequeued["id"]))
    assert completed["status"] == "COMPLETED"
    assert completed["result"] == {"status": "done"}

def test_fail_and_dead_letter():
    job = run_async(enqueue_job(
        job_type="resize_image",
        payload={"img": "invalid.png"},
        priority=JobPriority.LOW,
        max_retries=1
    ))
    
    run_async(fail_job(job["id"], error="Corrupt image"))
    failed = run_async(get_job_status(job["id"]))
    assert failed["status"] == "DEAD_LETTER"
    assert failed["error"] == "Corrupt image"

def test_queue_stats():
    stats = run_async(get_queue_stats())
    assert "queued_jobs" in stats
    assert "active_workers" in stats
    assert "completed_jobs" in stats
