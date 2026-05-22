"""Celery application configuration."""

from celery import Celery
from tech_ziwei.config import settings

celery_app = Celery(
    "tech_ziwei",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["tech_ziwei.workers.report_worker"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,           # only ack after task completes (safer retry)
    task_reject_on_worker_lost=True,
    result_expires=86400,          # keep results for 24 h
)
