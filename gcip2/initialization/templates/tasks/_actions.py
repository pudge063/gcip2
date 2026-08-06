import typing

from gcip2.logging import logger as LOGGER
from gcip2.tasks_core.models.actions import InteractivePythonAction, InteractiveShlex


class ShowPackageVersion(InteractivePythonAction):
    def impl(self, *, extra__version: str, **_):
        LOGGER.info(f"package version: {extra__version}")


class CheckPythonVersion(InteractiveShlex):
    def impl(self, **_: typing.Any) -> list[list[str]]:
        return [["python", "--version"]]
