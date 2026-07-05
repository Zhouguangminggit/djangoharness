from __future__ import annotations

from celery import shared_task
from loguru import logger

from .services import run_generation_workflow


@shared_task(
    bind=True,
    autoretry_for=(OSError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 2},
    soft_time_limit=600,
    time_limit=720,
)
def execute_ai_generation_task(self, task_id: int) -> None:
    """Asynchronously create and poll an AI generation task."""
    logger.info(
        "AI 生成任务开始执行 task_id={} celery_task_id={}", task_id, self.request.id
    )
    run_generation_workflow(task_id)
    logger.info("AI 生成任务执行结束 task_id={}", task_id)
