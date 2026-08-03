import subprocess
import typing

from gcip2.logging import logger as LOGGER
from gcip2.tasks_core.models.actions import InteractivePythonAction, InteractiveShlex


class GitSetupInsteadofAction(InteractivePythonAction):
    def test_method(self):
        LOGGER.warning("called test method")

    def impl(self, *, test_param: str, **_):
        self.test_method()
        LOGGER.info(f"test_param: {test_param}")


class CheckPoetryVersion(InteractivePythonAction):
    def impl(self, *, test_param: str, extra__version: str, **_):
        LOGGER.warning(f"extra_version: {extra__version}")
        LOGGER.info(f"test_param: {test_param}")
        subprocess.run("poetry --version", shell=True)


class CheckShellCmd(InteractiveShlex):
    def impl(self, *, allow_failure: bool, **_) -> list[str]:
        LOGGER.warning(f"allow_failure: {allow_failure}")
        return ["echo", self._config.extra["version"]]


class TestVaultSecretAction(InteractivePythonAction):
    def impl(
        self,
        *,
        vault_section: str,
        **_: typing.Any,
    ):
        secret = self._secret_handler(vault_section).fetch()
        username, password = secret["test_username"], secret["test_password"]
        LOGGER.info(f"secret username: {username}")
        LOGGER.info(f"secret password: {password}")
