import dataclasses
import shlex
import subprocess
import typing
from abc import ABC, abstractmethod
from collections.abc import Iterable

import injector

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig
from gcip2.vault import SecretsHandler

ActionResult = typing.Any


@injector.inject
@dataclasses.dataclass
class ActionBuilderImpl(ABC):
    _di: injector.Injector
    _config: ProjectConfig
    _secret_handler: SecretsHandler

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

        commands = [shlex.join(cmd) for cmd in self.impl(**kwargs)]

        script = " && ".join(commands)

        LOGGER.info("running: {}", script)
        subprocess.run(script, shell=True, check=True)
