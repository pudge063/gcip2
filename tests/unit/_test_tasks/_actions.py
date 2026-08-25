import subprocess
import typing

from gcip2 import Predefined
from gcip2.logging import logger as LOGGER
from gcip2.tasks_core import InteractivePythonAction, InteractiveShlex


class GitSetupInsteadofAction(InteractivePythonAction):
    def test_method(self):
        LOGGER.warning("called test method")

    def impl(self, **_: typing.Any):
        self.test_method()
        LOGGER.info("set up")


class CheckUvVersion(InteractivePythonAction):
    def impl(self, **_: typing.Any):
        subprocess.run("uv --version", shell=True)


class CheckShellCmd(InteractiveShlex):
    def impl(self, **_: typing.Any) -> list[list[str]]:
        return [["echo", self._config.extra["version"]]]


class CheckSecret(InteractivePythonAction):
    def impl(self, **_: typing.Any):
        if not Predefined.CI_PIPELINE_SOURCE.getenv():
            LOGGER.info("not ci.")
            return
        secret = self._secret_handler.fetch("vault-with-approle")
        username, password = secret["test_username"], secret["test_password"]
        LOGGER.info(f"secret username: {username}")
        LOGGER.info(f"secret password: {password}")
