import shlex
import subprocess
import typing
from abc import ABC, abstractmethod
from collections.abc import Iterable

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig
from gcip2.vault import SecretsHandler

ActionResult = typing.Any


class ActionBuilderImpl(ABC):
    _config = ProjectConfig.from_file()

    _secret_handler = SecretsHandler

    @abstractmethod
    def impl(self, **kwargs: typing.Any) -> ActionResult: ...

    @abstractmethod
    def execute(self, **kwargs: typing.Any): ...


class InteractivePythonAction(ActionBuilderImpl):
    @typing.override
    def impl(self, **kwargs: typing.Any) -> None:
        raise NotImplementedError

    @typing.override
    def execute(self, **kwargs: typing.Any) -> None:
        LOGGER.debug(f"running InteractivePythonAction action: {self.__class__.__name__}")
        self.impl(**kwargs)


class InteractiveShlex(ActionBuilderImpl):
    @typing.override
    def impl(self, **kwargs: typing.Any) -> Iterable[list[str]]:
        raise NotImplementedError

    @typing.override
    def execute(self, **kwargs: typing.Any) -> None:
        LOGGER.debug(f"running InteractiveShlex action: {self.__class__.__name__}")
        for cmd in self.impl(**kwargs):
            LOGGER.debug("running: {}", shlex.join(cmd))
            subprocess.run(cmd, check=True)
