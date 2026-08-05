import os
import pathlib
import subprocess
import tomllib
import typing

import git
import requests

from gcip2 import Predefined
from gcip2.logging import logger as LOGGER
from gcip2.tasks_core.models.actions import InteractivePythonAction, InteractiveShlex


class GitSetupInsteadofAction(InteractivePythonAction):
    def impl(self, *, flavor: str, **_):
        LOGGER.info(f"flavor: {flavor}")


class CheckUvVersion(InteractivePythonAction):
    def impl(self, *, extra__version: str, **_):
        LOGGER.warning(f"extra_version: {extra__version}")
        subprocess.run("uv --version", shell=True)


class CheckInsecureParam(InteractiveShlex):
    def impl(self, *, insecure: bool, **_) -> list[list[str]]:
        return [["echo", "insecure", str(insecure)]]


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


class CheckVersion(InteractivePythonAction):
    def ensure_tag_is_not_exists(self, tag: str) -> bool:
        token = Predefined.CI_JOB_TOKEN.must()
        gitlab_url = Predefined.CI_API_V4_URL.must()
        project_id = Predefined.CI_PROJECT_ID.must()

        return requests.get(
            url=f"{gitlab_url}/projects/{project_id}/repository/tags/{tag}",
            headers={"PRIVATE-TOKEN": token},
        ).ok

    def check_version_diff(self):
        default_branch = Predefined.CI_DEFAULT_BRANCH.getenv("master")
        repo = git.Repo(".")
        repo.remotes.origin.fetch(default_branch)

        diff = repo.git.diff("--color=always", f"origin/{default_branch}", "HEAD", "--", "gcip2/VERSION")
        LOGGER.warning(diff)
        if not diff:
            raise ValueError("diff in version not found.")

    def get_tag_from_version_file(self, version_file: pathlib.Path) -> str:
        if not version_file.exists():
            raise FileNotFoundError(f"version file: {version_file} not found.")
        return version_file.read_text()

    def get_tag_from_pyproject_file(self, pyproject_file: pathlib.Path) -> str:
        if not pyproject_file.exists():
            raise FileNotFoundError(f"version file: {pyproject_file} not found.")
        pyproject_data = tomllib.loads(pyproject_file.read_text())

        return pyproject_data["project"]["version"]

    def impl(self, **_: typing.Any) -> None:
        if not os.getenv("PARENT_PIPELINE_SOURCE") == "merge_request_event":
            LOGGER.warning("not merge request")
            return

        version_file = pathlib.Path("gcip2/VERSION")
        pyproject_file = pathlib.Path("pyproject.toml")

        self.check_version_diff()

        version = self.get_tag_from_version_file(version_file=version_file)
        pyproject_version = self.get_tag_from_pyproject_file(pyproject_file=pyproject_file)
        project_config_version = self._config.extra["version"]

        LOGGER.info(f"version in VERSION file: {version}")
        LOGGER.info(f"version in PYPROJECT file: {version}")
        LOGGER.info(f"version in PROJECTCONFIG: {project_config_version}")

        if not version == pyproject_version == project_config_version:
            raise ValueError(
                "versions diff:\n"
                f"{version_file.name}: {version}\n"
                f"{pyproject_file.name}: {pyproject_version}\n"
                f"environment.toml: {project_config_version}"
            )

        if self.ensure_tag_is_not_exists(tag=version):
            raise RuntimeError(f"tag for version {version} already exists")

        LOGGER.info(f"tag for version {version} not found")


class CreateVersionTag(InteractivePythonAction):
    def create_version_tag(self, version: str, gitlab_token_section: str):
        token = self._secret_handler(gitlab_token_section).fetch()["token"]

        gitlab_url = Predefined.CI_API_V4_URL.must()
        project_id = Predefined.CI_PROJECT_ID.must()
        default_branch = Predefined.CI_DEFAULT_BRANCH.must()
        r = requests.post(
            url=f"{gitlab_url}/projects/{project_id}/repository/tags",
            data={
                "tag_name": "v" + version,
                "ref": default_branch,
            },
            headers={"PRIVATE-TOKEN": token},
        )

        if not r.ok:
            raise RuntimeError(f"failed tag creating: {r.json()}")
        LOGGER.info("tag creating successful")

    def get_tag_from_version_file(self, version_file: pathlib.Path) -> str:
        if not version_file.exists():
            raise FileNotFoundError(f"version file: {version_file} not found.")
        return version_file.read_text()

    def impl(self, *, gitlab_token_section: str, **_: typing.Any) -> None:
        version_file = pathlib.Path("gcip2/VERSION")

        version = self.get_tag_from_version_file(version_file=version_file)

        LOGGER.info(f"creating tag for release: {version}")
        if Predefined.CI_DEFAULT_BRANCH.must() == Predefined.CI_COMMIT_BRANCH.getenv():
            self.create_version_tag(
                version=version,
                gitlab_token_section=gitlab_token_section,
            )
        else:
            LOGGER.warning("DRY-RUN: not release branch")


class PublishPackage(InteractiveShlex):
    def impl(self, **_: typing.Any) -> list[list[str]]:
        token = self._secret_handler("pypi-token").fetch()["token"]

        os.environ["UV_PUBLISH_TOKEN"] = token

        publish_cmds = ["uv", "publish"]
        if not (
            Predefined.CI_COMMIT_BRANCH.getenv()
            and Predefined.CI_COMMIT_BRANCH.getenv() == Predefined.CI_DEFAULT_BRANCH.getenv()
        ):
            publish_cmds.append("--dry-run")

        return [["uv", "build"], publish_cmds]
