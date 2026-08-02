import subprocess

from gcip2.logging import logger as LOGGER
from gcip2.tasks_core.actions import InteractivePythonAction, InteractiveShlex


class GitSetupInsteadofAction(InteractivePythonAction):
    def test_method(self):
        LOGGER.warning("called test method")

    def impl(self):
        self.test_method()
        LOGGER.info("set up")


class CheckPoetryVersion(InteractivePythonAction):
    def impl(self):
        subprocess.run("poetry --version", shell=True)


class CheckShellCmd(InteractiveShlex):
    def impl(self) -> list[str]:
        return ["echo", self._config.extra["version"]]


class CheckSecret(InteractivePythonAction):
    def impl(self):
        secret = self._secret_handler("vault-with-approle").fetch()
        username, password = secret["test_username"], secret["test_password"]
        LOGGER.info(f"secret username: {username}")
        LOGGER.info(f"secret password: {password}")
