import subprocess
import typing
from abc import ABC, abstractmethod

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig
from gcip2.vault import SecretsHandler

ActionResult = typing.Any


class ActionBuilderImpl(ABC):
    _config = ProjectConfig.from_file()

    _secret_handler = SecretsHandler

    @abstractmethod
    def impl(self) -> ActionResult: ...

    @abstractmethod
    def execute(self): ...


class InteractivePythonAction(ActionBuilderImpl):
    @typing.override
    def impl(self) -> None:
        pass

    @typing.override
    def execute(self) -> None:
        LOGGER.debug(f"running InteractivePythonAction action: {self.__class__.__name__}")
        self.impl()


class InteractiveShlex(ActionBuilderImpl):
    @typing.override
    def impl(self) -> list[str]:
        raise NotImplementedError

    @typing.override
    def execute(self) -> None:
        LOGGER.debug(f"running InteractiveShlex action: {self.__class__.__name__}")
        subprocess.run(
            self.impl(),
            check=True,
            shell=False,
        )
