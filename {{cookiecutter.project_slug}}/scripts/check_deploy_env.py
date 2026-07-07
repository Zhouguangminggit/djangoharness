import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_TITLE = "__PRODUCT_NAME__"
BASE_DIR = Path(__file__).resolve().parent.parent

REQUIRED_PRODUCTION_ENV = {
    "DJANGO_SECRET_KEY": "Django 密钥",
    "DJANGO_ALLOWED_HOSTS": "线上域名",
    "DJANGO_CSRF_TRUSTED_ORIGINS": "HTTPS CSRF 来源",
    "DB_ENGINE": "数据库类型，生产应为 mysql",
    "DB_NAME": "RDS 数据库名",
    "DB_USER": "RDS 用户名",
    "DB_PASSWORD": "RDS 密码",
    "DB_HOST": "RDS 地址",
    "DB_PORT": "RDS 端口",
    "CELERY_BROKER_URL": "Redis broker 地址",
    "CELERY_RESULT_BACKEND": "Redis result backend 地址",
    "AUTH_VERIFICATION_REDIS_URL": "验证码 Redis 地址",
    "DJANGO_SUPERUSER_USERNAME": "初始化超级管理员用户名",
    "DJANGO_SUPERUSER_EMAIL": "初始化超级管理员邮箱",
    "DJANGO_SUPERUSER_PASSWORD": "初始化超级管理员密码",
}

OPTIONAL_SERVICE_ENV = {
    "USE_THIRD_PARTY_SERVICES": "是否启用短信、邮件等第三方服务",
    "ALIYUN_ACCESS_KEY_ID": "阿里云 AccessKey ID",
    "ALIYUN_ACCESS_KEY_SECRET": "阿里云 AccessKey Secret",
    "ALIYUN_SMS_SIGN_NAME": "阿里云短信签名",
    "ALIYUN_SMS_TEMPLATE_CODE": "阿里云短信模板",
    "ALIYUN_EMAIL_ACCOUNT_NAME": "阿里云邮件发信地址",
    "AI_ENABLE_REAL_CALLS": "是否启用真实 AI 调用",
    "AI_VOLCANO_API_KEY": "火山方舟 API Key",
}

GITHUB_ACTIONS_SECRETS = {
    "ACR_REGISTRY": "阿里云 ACR registry",
    "ACR_NAMESPACE": "阿里云 ACR namespace",
    "ACR_REPO": "阿里云 ACR repo",
    "ACR_USERNAME": "阿里云 ACR 用户名",
    "ACR_PASSWORD": "阿里云 ACR 密码",
    "DEPLOY_HOST": "部署服务器地址",
    "DEPLOY_PORT": "部署 SSH 端口",
    "DEPLOY_USER": "部署 SSH 用户",
    "DEPLOY_PATH": "服务器部署目录",
    "DEPLOY_SSH_PRIVATE_KEY": "部署 SSH 私钥",
    "APP_ENV_VARS": "完整应用 .env 内容",
}


def log(message: str) -> None:
    print(f"[{PROJECT_TITLE}] {message}")


def get_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def is_missing(name: str) -> bool:
    value = os.environ.get(name)
    return value is None or value.strip() == ""


def main() -> int:
    load_dotenv(BASE_DIR / ".env")
    strict = os.environ.get("DEPLOY_CHECK_ENV", "").lower() == "production"
    log("开始部署配置检查")

    missing = [name for name in REQUIRED_PRODUCTION_ENV if is_missing(name)]
    if missing:
        level = "错误" if strict else "提示"
        for name in missing:
            log(f"{level}: 缺少 {name}（{REQUIRED_PRODUCTION_ENV[name]}）")
        if strict:
            log("生产部署检查失败，请补齐 .env 或 GitHub APP_ENV_VARS")
            return 1

    if os.environ.get("DB_ENGINE", "").lower() == "mysql":
        log("数据库配置为 MySQL，确认使用外部 RDS 或可访问的 MySQL 服务")
    elif strict:
        log("错误: 生产部署 DB_ENGINE 必须设置为 mysql")
        return 1
    else:
        log("提示: 当前未启用 MySQL，适用于本地或受控测试环境")

    redis_values = {
        "CELERY_BROKER_URL": os.environ.get("CELERY_BROKER_URL", ""),
        "CELERY_RESULT_BACKEND": os.environ.get("CELERY_RESULT_BACKEND", ""),
        "AUTH_VERIFICATION_REDIS_URL": os.environ.get("AUTH_VERIFICATION_REDIS_URL", ""),
    }
    for name, value in redis_values.items():
        if value and "localhost" in value and strict:
            log(f"错误: 生产部署 {name} 不应指向 localhost")
            return 1

    if get_bool("USE_THIRD_PARTY_SERVICES", False):
        aliyun_missing = [
            name
            for name in (
                "ALIYUN_ACCESS_KEY_ID",
                "ALIYUN_ACCESS_KEY_SECRET",
                "ALIYUN_SMS_SIGN_NAME",
                "ALIYUN_SMS_TEMPLATE_CODE",
            )
            if is_missing(name)
        ]
        if aliyun_missing:
            for name in aliyun_missing:
                log(f"错误: USE_THIRD_PARTY_SERVICES=True 时缺少 {name}")
            return 1
        log("第三方服务已启用，阿里云短信配置已提供")
    else:
        log("第三方服务未启用，短信、OSS、邮件等能力以手工配置为准")

    log("GitHub Actions secrets 需在 environment 中配置：")
    for name, description in GITHUB_ACTIONS_SECRETS.items():
        log(f"- {name}: {description}")

    log("可选服务变量按需配置：")
    for name, description in OPTIONAL_SERVICE_ENV.items():
        log(f"- {name}: {description}")

    log("部署配置检查完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
