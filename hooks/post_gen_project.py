import keyword
import re
import sys
from pathlib import Path

PRODUCT_NAME = {{ cookiecutter.product_name | tojson }}
PROJECT_SLUG = {{ cookiecutter.project_slug | tojson }}
PRODUCT_SUBTITLE = {{ cookiecutter.product_subtitle | tojson }}
AUTHOR_NAME = {{ cookiecutter.author_name | tojson }}

PROJECT_PACKAGE = PROJECT_SLUG.replace("-", "_")
DOCKER_IMAGE_ENV = f"{PROJECT_PACKAGE.upper()}_IMAGE"
INVALID_EMAIL_DOMAIN = f"{PROJECT_SLUG}.invalid"

if (
    not PROJECT_PACKAGE.isidentifier()
    or keyword.iskeyword(PROJECT_PACKAGE)
    or not re.fullmatch(r"[a-z][a-z0-9_]*", PROJECT_PACKAGE)
):
    print(
        f"错误：由 project_slug 派生的 Python 包名无效：{PROJECT_PACKAGE}",
        file=sys.stderr,
    )
    sys.exit(1)

replacements = {
    "__PRODUCT_NAME__": PRODUCT_NAME,
    "__PROJECT_SLUG__": PROJECT_SLUG,
    "__PROJECT_PACKAGE__": PROJECT_PACKAGE,
    "__PRODUCT_SUBTITLE__": PRODUCT_SUBTITLE,
    "__AUTHOR_NAME__": AUTHOR_NAME,
    "__DOCKER_IMAGE_ENV__": DOCKER_IMAGE_ENV,
    "__DATABASE_NAME__": PROJECT_PACKAGE,
    "__INVALID_EMAIL_DOMAIN__": INVALID_EMAIL_DOMAIN,
}

for path in Path.cwd().rglob("*"):
    if not path.is_file():
        continue
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    rendered = content
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)

    if rendered != content:
        path.write_text(rendered, encoding="utf-8")
