from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from apps.ai_integration.models import AIGenerationTask, AIModelConfig
from apps.ai_integration.services import (
    _extract_result_url,
    _resolve_image_url,
    create_content_task,
    download_result,
    refresh_task_status,
    run_generation_workflow,
)
from apps.ai_integration.tasks import execute_ai_generation_task

User = get_user_model()
PASSWORD = "Harness-test-password-2026"


@pytest.fixture
def ai_config(db):
    return AIModelConfig.objects.create(
        name="火山视频",
        provider=AIModelConfig.Provider.VOLCANO_ARK,
        model_id="doubao-seedance-1-5-pro-251215",
        api_key="test-key",
        is_default=True,
    )


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        username="ai_admin", email="ai_admin@example.com", password=PASSWORD
    )
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=("is_staff", "is_superuser"))
    return user


@pytest.mark.django_db
def test_model_config_default_constraint(ai_config):
    assert ai_config.is_default is True
    assert str(ai_config) == "火山视频 (volcano_ark) [默认]"

    with pytest.raises(ValidationError):
        duplicate = AIModelConfig(
            name="另一个默认",
            provider=AIModelConfig.Provider.VOLCANO_ARK,
            model_id="other",
            api_key="key",
            is_default=True,
        )
        duplicate.full_clean()


@pytest.mark.django_db
def test_generation_task_status_defaults(ai_config, admin_user):
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="无人机穿越峡谷",
        created_by=admin_user,
    )
    assert task.status == AIGenerationTask.Status.PENDING
    assert task.task_type == AIGenerationTask.TaskType.VIDEO
    assert "视频" in str(task)


@pytest.mark.django_db
def test_resolve_image_url_uses_ai_media_base_url(ai_config, settings):
    settings.AI_MEDIA_BASE_URL = "https://cdn.example.com"
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
    )
    assert _resolve_image_url(task) is None


@pytest.mark.django_db
def test_resolve_image_url_warns_and_returns_none_for_relative_media(
    ai_config, settings
):
    settings.AI_MEDIA_BASE_URL = ""
    settings.MEDIA_URL = "/media/"
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
    )
    assert _resolve_image_url(task) is None


@pytest.mark.django_db
def test_resolve_image_url_uses_data_url_for_local_real_call(
    ai_config, settings, tmp_path
):
    settings.DEBUG = True
    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"
    settings.AI_MEDIA_BASE_URL = ""
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
        image=SimpleUploadedFile(
            "reference.png",
            b"\x89PNG\r\n\x1a\nlocal-image",
            content_type="image/png",
        ),
    )

    image_url = _resolve_image_url(task)

    assert image_url is not None
    assert image_url.startswith("data:image/png;base64,")


@pytest.mark.django_db
def test_resolve_image_url_requires_public_url_outside_debug(
    ai_config, settings, tmp_path
):
    settings.DEBUG = False
    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"
    settings.AI_MEDIA_BASE_URL = ""
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
        image=SimpleUploadedFile("reference.png", b"image", content_type="image/png"),
    )

    assert _resolve_image_url(task) is None


@pytest.mark.django_db
@patch("apps.ai_integration.services.build_ark_client")
def test_create_content_task_returns_external_id_when_enabled(
    mock_build, ai_config, settings
):
    settings.AI_ENABLE_REAL_CALLS = True
    mock_client = MagicMock()
    mock_client.content_generation.tasks.create.return_value = MagicMock(id="ext-001")
    mock_build.return_value = mock_client

    task = AIGenerationTask.objects.create(config=ai_config, prompt="test")
    external_id = create_content_task(task.pk)

    assert external_id == "ext-001"
    mock_build.assert_called_once_with(ai_config)
    mock_client.content_generation.tasks.create.assert_called_once()


@pytest.mark.django_db
@patch("apps.ai_integration.services.build_ark_client")
def test_create_content_task_skips_when_disabled(mock_build, ai_config, settings):
    settings.AI_ENABLE_REAL_CALLS = False
    task = AIGenerationTask.objects.create(config=ai_config, prompt="test")
    assert create_content_task(task.pk) == f"mock-task-{task.pk}"
    mock_build.assert_not_called()


@pytest.mark.django_db
@patch("apps.ai_integration.services.build_ark_client")
def test_refresh_task_status_updates_succeeded(mock_build, ai_config, settings):
    settings.AI_ENABLE_REAL_CALLS = True
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.status = "succeeded"
    mock_result.result_url = ""
    mock_result.content.video_url = "https://example.com/video.mp4"
    mock_client.content_generation.tasks.get.return_value = mock_result
    mock_build.return_value = mock_client

    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
        external_task_id="ext-001",
    )
    status = refresh_task_status(task.pk)

    assert status == AIGenerationTask.Status.SUCCEEDED
    task.refresh_from_db()
    assert task.result_url == "https://example.com/video.mp4"
    assert task.completed_at is not None


def test_extract_result_url_supports_ark_content_and_file_fallback():
    assert (
        _extract_result_url(
            {"content": {"video_url": "https://example.com/generated.mp4"}}
        )
        == "https://example.com/generated.mp4"
    )
    assert (
        _extract_result_url(
            MagicMock(
                result_url="",
                content=MagicMock(
                    video_url="", file_url="https://example.com/file.zip"
                ),
            )
        )
        == "https://example.com/file.zip"
    )


@pytest.mark.django_db
def test_download_result_saves_mock_file_to_media(ai_config, settings, tmp_path):
    settings.AI_ENABLE_REAL_CALLS = False
    settings.MEDIA_ROOT = tmp_path
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
        status=AIGenerationTask.Status.SUCCEEDED,
    )

    saved_name = download_result(task.pk)

    task.refresh_from_db()
    assert saved_name == task.result_file.name
    assert saved_name
    assert (tmp_path / saved_name).read_bytes() == b"mock ai generation result"


@pytest.mark.django_db
@patch("apps.ai_integration.services.build_ark_client")
def test_refresh_task_status_updates_failed(mock_build, ai_config, settings):
    settings.AI_ENABLE_REAL_CALLS = True
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.status = "failed"
    mock_result.error = "balance insufficient"
    mock_client.content_generation.tasks.get.return_value = mock_result
    mock_build.return_value = mock_client

    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
        external_task_id="ext-002",
    )
    status = refresh_task_status(task.pk)

    assert status == AIGenerationTask.Status.FAILED
    task.refresh_from_db()
    assert "balance insufficient" in task.error_message


@pytest.mark.django_db
@patch("apps.ai_integration.services.create_content_task")
@patch("apps.ai_integration.services.refresh_task_status")
@patch("apps.ai_integration.services.download_result")
@patch("apps.ai_integration.services.time.sleep", return_value=None)
def test_run_generation_workflow_succeeds(
    _mock_sleep, mock_download, mock_refresh, mock_create, ai_config
):
    mock_create.return_value = "ext-003"
    mock_refresh.side_effect = ["processing", "succeeded"]
    mock_download.return_value = "ai_results/1/abc.mp4"

    task = AIGenerationTask.objects.create(config=ai_config, prompt="test")
    run_generation_workflow(task.pk)

    task.refresh_from_db()
    assert task.status == AIGenerationTask.Status.SUCCEEDED
    assert task.started_at is not None
    assert mock_create.called
    assert mock_download.called


@pytest.mark.django_db
@patch("apps.ai_integration.services.create_content_task")
@patch("apps.ai_integration.services.refresh_task_status")
@patch("apps.ai_integration.services.time.sleep", return_value=None)
def test_run_generation_workflow_handles_create_failure(
    _mock_sleep, mock_refresh, mock_create, ai_config
):
    mock_create.side_effect = RuntimeError("network error")

    task = AIGenerationTask.objects.create(config=ai_config, prompt="test")
    run_generation_workflow(task.pk)

    task.refresh_from_db()
    assert task.status == AIGenerationTask.Status.FAILED
    assert "network error" in task.error_message
    assert not mock_refresh.called


@pytest.mark.django_db
@patch("apps.ai_integration.admin.execute_ai_generation_task.delay")
def test_admin_creates_task_without_auto_dispatch(
    mock_delay, client: Client, admin_user, ai_config
):
    client.force_login(admin_user)
    response = client.post(
        reverse("admin:ai_integration_aigenerationtask_add"),
        {
            "config": ai_config.pk,
            "task_type": "video",
            "prompt": "无人机穿越峡谷",
            "extra_params": '{"duration": 5}',
            "_save": "保存",
        },
    )

    assert response.status_code == 302
    task = AIGenerationTask.objects.get()
    assert task.created_by == admin_user
    assert task.prompt == "无人机穿越峡谷"
    assert task.status == AIGenerationTask.Status.PENDING
    mock_delay.assert_not_called()


@pytest.mark.django_db
@patch("apps.ai_integration.admin.execute_ai_generation_task.delay")
def test_admin_generate_button_dispatches_task(
    mock_delay, client: Client, admin_user, ai_config
):
    client.force_login(admin_user)
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="无人机穿越峡谷",
        created_by=admin_user,
    )

    response = client.post(
        reverse("admin:ai_integration_aigenerationtask_generate", args=(task.pk,))
    )

    assert response.status_code == 302
    task.refresh_from_db()
    assert task.status == AIGenerationTask.Status.PENDING
    mock_delay.assert_called_once_with(task.pk)


@pytest.mark.django_db
@patch("apps.ai_integration.admin.execute_ai_generation_task.delay")
def test_admin_generate_button_rejects_duplicate_processing(
    mock_delay, client: Client, admin_user, ai_config
):
    client.force_login(admin_user)
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
        created_by=admin_user,
        status=AIGenerationTask.Status.PROCESSING,
    )

    response = client.post(
        reverse("admin:ai_integration_aigenerationtask_generate", args=(task.pk,))
    )

    assert response.status_code == 302
    mock_delay.assert_not_called()


@pytest.mark.django_db
@patch("apps.ai_integration.admin.execute_ai_generation_task.delay")
def test_admin_form_rejects_unsupported_task_type(
    mock_delay, client: Client, admin_user, ai_config
):
    client.force_login(admin_user)
    response = client.post(
        reverse("admin:ai_integration_aigenerationtask_add"),
        {
            "config": ai_config.pk,
            "task_type": "voice",
            "prompt": "朗读一段文字",
            "_save": "保存",
        },
    )

    assert response.status_code == 200
    assert "当前仅支持视频生成任务" in response.content.decode()
    assert not AIGenerationTask.objects.exists()
    mock_delay.assert_not_called()


@pytest.mark.django_db
def test_execute_ai_generation_task_runs_service(ai_config):
    with patch("apps.ai_integration.tasks.run_generation_workflow") as mock_workflow:
        task = AIGenerationTask.objects.create(config=ai_config, prompt="test")
        execute_ai_generation_task.run(task.pk)
        mock_workflow.assert_called_once_with(task.pk)


@pytest.mark.django_db
def test_admin_download_button_requires_result_file(
    client: Client, admin_user, ai_config
):
    client.force_login(admin_user)
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
        created_by=admin_user,
    )

    response = client.get(
        reverse("admin:ai_integration_aigenerationtask_download", args=(task.pk,))
    )

    assert response.status_code == 302
    assert AIGenerationTask.objects.filter(pk=task.pk).exists()


@pytest.mark.django_db
def test_admin_list_includes_operations_column(client: Client, admin_user, ai_config):
    client.force_login(admin_user)
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="无人机穿越峡谷",
        created_by=admin_user,
    )
    response = client.get(reverse("admin:ai_integration_aigenerationtask_changelist"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "生成" in content
    assert task.prompt[:20] in content


@pytest.mark.django_db
def test_admin_list_shows_download_for_remote_result_url(
    client: Client, admin_user, ai_config
):
    client.force_login(admin_user)
    AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
        created_by=admin_user,
        status=AIGenerationTask.Status.SUCCEEDED,
        result_url="https://example.com/generated.mp4",
    )

    response = client.get(reverse("admin:ai_integration_aigenerationtask_changelist"))

    assert response.status_code == 200
    assert "下载" in response.content.decode()


@pytest.mark.django_db
@patch("apps.ai_integration.admin.download_result")
def test_admin_download_fetches_remote_result_when_file_is_missing(
    mock_download, client: Client, admin_user, ai_config
):
    client.force_login(admin_user)
    task = AIGenerationTask.objects.create(
        config=ai_config,
        prompt="test",
        created_by=admin_user,
        status=AIGenerationTask.Status.SUCCEEDED,
        result_url="https://example.com/generated.mp4",
    )

    def save_result(task_id):
        current = AIGenerationTask.objects.get(pk=task_id)
        current.result_file.save("generated.mp4", ContentFile(b"video"))
        return current.result_file.name

    mock_download.side_effect = save_result
    response = client.get(
        reverse("admin:ai_integration_aigenerationtask_download", args=(task.pk,))
    )

    assert response.status_code == 200
    assert response["Content-Disposition"].startswith("attachment;")
    mock_download.assert_called_once_with(task.pk)
