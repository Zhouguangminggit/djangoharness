import re
import sys

PROJECT_SLUG = "{{ cookiecutter.project_slug }}"
SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


if not SLUG_PATTERN.fullmatch(PROJECT_SLUG):
    print(
        "错误：project_slug 必须以小写英文字母开头，"
        "并且只能包含小写英文字母、数字和单个连字符。",
        file=sys.stderr,
    )
    sys.exit(1)
