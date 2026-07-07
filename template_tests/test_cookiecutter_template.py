import re
from pathlib import Path

import pytest
from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter

TEMPLATE_ROOT = Path(__file__).resolve().parents[1]


def generate_project(tmp_path: Path, **overrides: str) -> Path:
    context = {
        "product_name": "校园二手交易平台",
        "project_slug": "campus-second-platform",
        "product_subtitle": "校园好物，就来校园二手交易平台",
        "author_name": "示例作者名",
    }
    context.update(overrides)
    result = cookiecutter(
        str(TEMPLATE_ROOT),
        no_input=True,
        extra_context=context,
        output_dir=str(tmp_path),
    )
    return Path(result)


def test_generates_productized_project(tmp_path: Path) -> None:
    project = generate_project(tmp_path)

    assert project.name == "campus-second-platform"
    assert (project / "campus_second_platform" / "settings" / "base.py").is_file()
    assert not (project / "{{cookiecutter.project_slug}}").exists()
    assert not (project / "hooks").exists()
    assert not (project / "template_tests").exists()
    assert not (project / "cookiecutter.json").exists()

    expected = {
        "README.md": ["校园二手交易平台", "校园好物，就来校园二手交易平台"],
        "LICENSE": ["示例作者名"],
        "pyproject.toml": ['name = "campus-second-platform"'],
        "deploy/docker-compose.yml": [
            "name: campus-second-platform",
            "CAMPUS_SECOND_PLATFORM_IMAGE",
        ],
        ".github/workflows/deploy.yml": [
            "校园二手交易平台",
            "CAMPUS_SECOND_PLATFORM_IMAGE",
            "make deploy-check",
        ],
        ".github/workflows/quality.yml": ["校园二手交易平台", "make docs-build"],
        ".env.example": [
            "DJANGO_SUPERUSER_USERNAME",
            "DJANGO_SUPERUSER_EMAIL",
            "DJANGO_SUPERUSER_PASSWORD",
        ],
        "scripts/check_deploy_env.py": ["校园二手交易平台", "DEPLOY_CHECK_ENV"],
        "apps/accounts/management/commands/ensure_superuser.py": [
            "DJANGO_SUPERUSER_USERNAME",
            "DJANGO_SUPERUSER_PASSWORD",
        ],
        "campus_second_platform/settings/admin.py": ["校园二手交易平台"],
        "apps/core/templates/core/home.html": [
            "校园二手交易平台",
            "校园好物，就来校园二手交易平台",
        ],
    }
    for relative_path, values in expected.items():
        content = (project / relative_path).read_text(encoding="utf-8")
        for value in values:
            assert value in content

    compose = (project / "deploy/docker-compose.yml").read_text(encoding="utf-8")
    assert "  mysql:" not in compose
    assert "  redis:" not in compose
    assert "mysql_data:" not in compose
    assert "redis_data:" not in compose
    assert "redis://redis" not in compose
    assert not (project / "deploy/README.md").exists()

    text_extensions = {
        ".css",
        ".html",
        ".js",
        ".json",
        ".md",
        ".py",
        ".sql",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
    product_files = [
        path
        for path in project.rglob("*")
        if path.is_file()
        and path.suffix in text_extensions
        and "agent-docs" not in path.parts
        and "skill" not in path.parts
        and not (
            "docs" in path.parts
            and "iterations" in path.parts
            and path.name != "28-cookiecutter-template.md"
        )
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in product_files)
    assert not re.search(
        r"__(?:PRODUCT_NAME|PROJECT_SLUG|PROJECT_PACKAGE|PRODUCT_SUBTITLE|"
        r"AUTHOR_NAME|DOCKER_IMAGE_ENV|DATABASE_NAME|INVALID_EMAIL_DOMAIN)__",
        combined,
    )
    assert "djangoharness:local" not in combined.lower()
    assert "DJANGOHARNESS_IMAGE" not in combined

    assert "DjangoHarness" in (project / "agent-docs/AGENTS.md").read_text(
        encoding="utf-8"
    )
    assert "DjangoHarness" in (project / "skill/SKILL.md").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "project_slug",
    [
        "Campus-Second",
        "2campus",
        "campus_second",
        "campus--second",
        "class",
        "校园平台",
    ],
)
def test_rejects_invalid_project_slug(tmp_path: Path, project_slug: str) -> None:
    with pytest.raises(FailedHookException):
        generate_project(tmp_path, project_slug=project_slug)
