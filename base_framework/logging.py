"""Loguru configuration and standard-library logging bridge."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from types import FrameType
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from loguru import Record

CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)
FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
    "{process.name}:{process.id} | {thread.name}:{thread.id} | "
    "{name}:{function}:{line} | {message}"
)


def _format_console(record: Record) -> str:
    extra = " | <magenta>{extra}</magenta>" if record["extra"] else ""
    return f"{CONSOLE_FORMAT}{extra}\n{{exception}}"


def _format_file(record: Record) -> str:
    extra = " | {extra}" if record["extra"] else ""
    return f"{FILE_FORMAT}{extra}\n{{exception}}"


def _is_async_record(record: Record) -> bool:
    source = str(record["extra"].get("source", record["name"]))
    return (
        source.startswith(("celery", "celery_app"))
        or ".tasks" in source
        or source.endswith(".task")
    )


def _is_application_record(record: Record) -> bool:
    return not _is_async_record(record)


class InterceptHandler(logging.Handler):
    """Forward records emitted through ``logging`` to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame: FrameType | None = logging.currentframe()
        depth = 0
        while frame is not None and frame.f_code.co_filename in {
            logging.__file__,
            __file__,
        }:
            frame = frame.f_back
            depth += 1

        logger.bind(source=record.name).opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_logging(
    *,
    level: str,
    colorize: bool,
    file_enabled: bool,
    app_file_path: Path,
    async_file_path: Path,
    error_file_path: Path,
    rotation: str,
    retention: str,
    compression: str,
    backtrace: bool,
    diagnose: bool,
) -> None:
    """Configure the application-wide Loguru sinks."""

    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format=_format_console,
        colorize=colorize,
        backtrace=backtrace,
        diagnose=diagnose,
    )

    if file_enabled:
        for file_path in {app_file_path, async_file_path, error_file_path}:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            app_file_path,
            level=level,
            format=_format_file,
            filter=_is_application_record,
            colorize=False,
            rotation=rotation,
            retention=retention,
            compression=compression,
            encoding="utf-8",
            backtrace=backtrace,
            diagnose=diagnose,
        )
        logger.add(
            async_file_path,
            level=level,
            format=_format_file,
            filter=_is_async_record,
            colorize=False,
            rotation=rotation,
            retention=retention,
            compression=compression,
            encoding="utf-8",
            backtrace=backtrace,
            diagnose=diagnose,
        )
        logger.add(
            error_file_path,
            level="ERROR",
            format=_format_file,
            colorize=False,
            rotation=rotation,
            retention=retention,
            compression=compression,
            encoding="utf-8",
            backtrace=backtrace,
            diagnose=diagnose,
        )
