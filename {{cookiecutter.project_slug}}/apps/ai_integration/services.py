from __future__ import annotations

import base64
import mimetypes
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse
from urllib.request import urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from loguru import logger

from .models import AIGenerationTask, AIModelConfig

if TYPE_CHECKING:
    from volcenginesdkarkruntime import Ark


def build_ark_client(config: AIModelConfig) -> Ark:
    """Build a Volcano Ark client from a model configuration."""
    from volcenginesdkarkruntime import Ark

    return Ark(
        base_url=config.base_url or settings.AI_VOLCANO_BASE_URL,
        api_key=config.api_key or settings.AI_VOLCANO_API_KEY,
        timeout=config.timeout,
    )


def _resolve_image_url(task: AIGenerationTask) -> str | None:
    """Resolve a remote URL or local Data URL for the reference image.

    Priority:
    1. ``AI_MEDIA_BASE_URL`` if set.
    2. ``MEDIA_URL`` if it is an absolute URL.
    3. A Base64 Data URL when Django runs in debug mode.

    Returns ``None`` when no supported image input can be built.
    """
    if not task.image:
        return None

    media_base = getattr(settings, "AI_MEDIA_BASE_URL", "")
    if not media_base:
        media_base = settings.MEDIA_URL

    if media_base.startswith("http"):
        base = media_base.rstrip("/")
        name = task.image.name.lstrip("/")
        return f"{base}/{name}"

    if settings.DEBUG:
        return _build_local_image_data_url(task)

    return None


def _build_local_image_data_url(task: AIGenerationTask) -> str:
    """Encode a locally stored reference image for a real remote API call."""
    max_bytes = getattr(settings, "AI_LOCAL_IMAGE_MAX_BYTES", 10 * 1024 * 1024)
    task.image.open("rb")
    try:
        image_bytes = task.image.read(max_bytes + 1)
    finally:
        task.image.close()

    if len(image_bytes) > max_bytes:
        raise ValueError(
            f"本地参考图片超过 {max_bytes // (1024 * 1024)} MB，无法使用 Base64 传输。"
        )

    content_type = (
        mimetypes.guess_type(task.image.name)[0] or "application/octet-stream"
    )
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


def _build_content_payload(task: AIGenerationTask) -> list[dict[str, Any]]:
    """Construct the content payload for a video generation task."""
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": task.prompt,
        }
    ]
    if not task.image:
        return content

    if not settings.AI_ENABLE_REAL_CALLS:
        # In mock mode the remote API never sees the payload, so we keep the
        # image attached locally for testing and skip the public URL check.
        return content

    image_url = _resolve_image_url(task)
    if image_url:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": image_url},
            }
        )
    else:
        raise ValueError(
            "上传了参考图片但无法构建公开 URL。"
            "本地开发请启用 DEBUG 以使用 Base64 图片；"
            "生产环境请配置 AI_MEDIA_BASE_URL，或确保 MEDIA_URL 为绝对 URL。"
        )
    return content


def create_content_task(task_id: int) -> str:
    """Create a remote generation task and return the external task id."""
    task = AIGenerationTask.objects.select_related("config").get(pk=task_id)
    config = task.config
    if not config.is_active:
        raise ValueError(f"模型配置 {config.name} 未启用。")

    if not settings.AI_ENABLE_REAL_CALLS:
        logger.info("AI 真实调用已关闭，使用 mock 任务 task_id={}", task_id)
        return f"mock-task-{task_id}"

    client = build_ark_client(config)
    result = client.content_generation.tasks.create(
        model=config.model_id,
        content=_build_content_payload(task),
    )
    external_id = str(result.id)
    logger.info("AI 任务已创建 task_id={} external_id={}", task_id, external_id)
    return external_id


def refresh_task_status(task_id: int) -> str:
    """Poll the remote task status once and update the local record."""
    task = AIGenerationTask.objects.select_related("config").get(pk=task_id)
    config = task.config

    if not settings.AI_ENABLE_REAL_CALLS:
        # Simulate a quick success path for local development.
        return _simulate_mock_status(task)

    if not task.external_task_id:
        raise ValueError("外部任务 ID 为空，无法刷新状态。")

    client = build_ark_client(config)
    result = client.content_generation.tasks.get(task_id=task.external_task_id)
    status = str(result.status).lower()

    if status == "succeeded":
        task.status = AIGenerationTask.Status.SUCCEEDED
        task.result_url = _extract_result_url(result) or task.result_url
        task.completed_at = timezone.now()
    elif status == "failed":
        task.status = AIGenerationTask.Status.FAILED
        task.error_message = str(getattr(result, "error", "") or "")
        task.completed_at = timezone.now()
    elif status in {"cancelled", "canceled"}:
        task.status = AIGenerationTask.Status.CANCELLED
        task.completed_at = timezone.now()
    else:
        task.status = AIGenerationTask.Status.PROCESSING

    update_fields = ["status"]
    if task.result_url:
        update_fields.append("result_url")
    if task.error_message:
        update_fields.append("error_message")
    if task.completed_at:
        update_fields.append("completed_at")
    task.save(update_fields=update_fields)

    logger.info("AI 任务状态已刷新 task_id={} status={}", task_id, task.status)
    return task.status


def _extract_result_url(result: Any) -> str:
    """Extract the generated file URL from Ark SDK and compatible responses."""
    direct_url = getattr(result, "result_url", "")
    if direct_url:
        return str(direct_url)

    content = getattr(result, "content", None)
    if content is None and isinstance(result, dict):
        content = result.get("content")

    for field_name in ("video_url", "file_url"):
        if isinstance(content, dict):
            value = content.get(field_name)
        else:
            value = getattr(content, field_name, "") if content is not None else ""
        if value:
            return str(value)
    return ""


def _simulate_mock_status(task: AIGenerationTask) -> str:
    """Simulate a successful remote status for local development."""
    if task.status == AIGenerationTask.Status.PROCESSING:
        task.status = AIGenerationTask.Status.SUCCEEDED
        task.result_url = f"mock://localhost/media/ai_results/{task.pk}/mock_result.mp4"
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "result_url", "completed_at"])
        logger.info("AI mock 任务已标记成功 task_id={}", task.pk)
    return task.status


def download_result(task_id: int) -> str | None:
    """Download or create the result file for a task and save it to storage."""
    task = AIGenerationTask.objects.get(pk=task_id)
    extension = ".mp4"
    if task.result_url:
        extension = Path(urlparse(task.result_url).path).suffix or extension

    target_name = f"ai_results/{task.pk}/{uuid.uuid4().hex}{extension}"

    if not settings.AI_ENABLE_REAL_CALLS:
        # Create a placeholder file in media storage for local testing.
        placeholder = ContentFile(b"mock ai generation result")
        saved_name = default_storage.save(target_name, placeholder)
        task.result_file = saved_name
        task.save(update_fields=["result_file"])
        logger.info("AI mock 结果文件已创建 task_id={} path={}", task_id, saved_name)
        return saved_name

    if not task.result_url:
        return None

    with urlopen(task.result_url, timeout=60) as response:
        saved_name = default_storage.save(target_name, response)
    task.result_file = saved_name
    task.save(update_fields=["result_file"])
    logger.info("AI 结果已下载 task_id={} path={}", task_id, saved_name)
    return saved_name


def run_generation_workflow(task_id: int) -> None:
    """Execute the full create → poll → download workflow for a task."""
    task = AIGenerationTask.objects.get(pk=task_id)
    task.status = AIGenerationTask.Status.PROCESSING
    task.started_at = timezone.now()
    task.save(update_fields=["status", "started_at"])

    try:
        task.external_task_id = create_content_task(task_id)
        task.save(update_fields=["external_task_id"])
    except Exception as exc:
        logger.exception("AI 任务创建失败 task_id={}", task_id)
        task.status = AIGenerationTask.Status.FAILED
        task.error_message = str(exc)
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "error_message", "completed_at"])
        return

    interval = getattr(settings, "AI_TASK_POLL_INTERVAL_SECONDS", 3)
    max_seconds = getattr(settings, "AI_TASK_MAX_POLL_SECONDS", 600)
    elapsed = 0

    while elapsed < max_seconds:
        time.sleep(interval)
        elapsed += interval
        try:
            status = refresh_task_status(task_id)
        except Exception as exc:
            logger.exception("AI 任务状态刷新失败 task_id={}", task_id)
            task.status = AIGenerationTask.Status.FAILED
            task.error_message = str(exc)
            task.completed_at = timezone.now()
            task.save(update_fields=["status", "error_message", "completed_at"])
            return

        if status == AIGenerationTask.Status.SUCCEEDED:
            task.status = AIGenerationTask.Status.SUCCEEDED
            task.completed_at = timezone.now()
            task.save(update_fields=["status", "completed_at"])
            try:
                download_result(task_id)
            except Exception:
                logger.exception("AI 结果下载失败 task_id={}", task_id)
            return
        if status == AIGenerationTask.Status.FAILED:
            task.status = AIGenerationTask.Status.FAILED
            task.completed_at = timezone.now()
            task.save(update_fields=["status", "completed_at"])
            return
        if status == AIGenerationTask.Status.CANCELLED:
            task.status = AIGenerationTask.Status.CANCELLED
            task.completed_at = timezone.now()
            task.save(update_fields=["status", "completed_at"])
            return

    task.status = AIGenerationTask.Status.FAILED
    task.error_message = "轮询超时。"
    task.completed_at = timezone.now()
    task.save(update_fields=["status", "error_message", "completed_at"])
    logger.warning("AI 任务轮询超时 task_id={}", task_id)
