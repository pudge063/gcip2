import sys

from loguru import logger


def setup_logger(debug: bool = False) -> None:
    logger.remove()

    level = "DEBUG" if debug else "INFO"

    logger.add(
        sys.stdout,
        level=level,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:"
            "<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        backtrace=True,
        diagnose=debug,
    )


setup_logger(debug=True)

__all__ = ["logger"]
