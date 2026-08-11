import os
import pathlib
import subprocess
import tomllib
import typing
from time import sleep

import git
import requests

from _tasks._consts import PipelineStatus
from _tasks._helpers import GitlabApi
from gcip2 import Predefined
from gcip2.logging import logger as LOGGER
from gcip2.tasks_core import InteractivePythonAction, InteractiveShlex


class SetupSsh(InteractivePythonAction):
    def impl(self, *, flavor: str, **_):
        if not Predefined.CI_API_V4_URL.getenv(""):
            LOGGER.warning("not CI")
            return

        secret = self._secret_handler("gl-pivlab-maintainer").fetch()
        ssh_private_key = secret["ssh_private_key"]

        ssh_dir = pathlib.Path("/root/.ssh")
        ssh_dir.mkdir(exist_ok=True)
        ssh_dir.chmod(0o600)

        private_key_file = ssh_dir / "id_ci"
        private_key_file.write_text(ssh_private_key)
        private_key_file.chmod(0o600)

        ssh_config_file = ssh_dir / "config"
        ssh_config_data = [
            "Host gl.pivlab.space",
            "    IdentityFile /root/.ssh/id_ci",
            "    IdentitiesOnly yes",
            "    StrictHostKeyChecking no",
            "    UserKnownHostsFile /dev/null",
        ]
        ssh_config_file.write_text("\n".join(ssh_config_data))
        ssh_config_file.chmod(0o644)

        LOGGER.info(f"flavor: {flavor}")


class SetupGitInsteadOf(InteractiveShlex):
    def impl(self, **_: typing.Any) -> list[list[str]]:
        return [
            ["git", "config", "--global", "user.email", "ci@pivlab.space"],
            ["git", "config", "--global", "user.name", "CI"],
            ["git", "config", "--global", "init.defaultBranch", "master"],
        ]


class CheckUvVersion(InteractivePythonAction):
    def impl(self, *, ci: bool, extra__version: str, **_):
        LOGGER.warning(f"ci: {ci}")
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


class UpdateTestProject(InteractiveShlex):
    def impl(self, **_: typing.Any) -> list[list[str]]:
        cmds: list[list[str]] = []

        tmp_dir = "tmp_out"
        test_repo = self._config.extra.get("test_repo", "")

        if not test_repo:
            raise ValueError("test_repo url not set")

        sed_string = (
            f"s|gcip2>=0.0.1|gcip2 @ git+https://gl.pivlab.space/rnd/gcip2.git@{Predefined.CI_COMMIT_SHA.getenv('')}|"
        )

        branch, remote = "master", "origin"

        cmds.extend(
            [
                ["mkdir", "-p", tmp_dir],
                ["cd", tmp_dir],
                ["gcip2", "init"],
                ["git", "init"],
                ["git", "remote", "add", remote, f"ssh://git@gl.pivlab.space/{test_repo}.git"],
                ["gcip2", "build-gitlab-ci"],
                ["sed", "-i", sed_string, "pyproject.toml"],
                ["ls", "-la"],
            ]
        )

        if Predefined.CI_API_V4_URL.getenv(""):
            cmds.extend(
                [
                    ["git", "add", "--a"],
                    ["git", "commit", "-m", "ci"],
                    ["git", "push", "-f", remote, branch],
                ]
            )

        return cmds


class RunInitializationPipeline(InteractivePythonAction):
    def impl(self, **_: typing.Any):
        token = self._secret_handler("gl-pivlab-maintainer").fetch()["token"]
        project_url = self._config.extra.get("test_repo", "").replace("/", "%2F")

        gl = GitlabApi(gitlab_token=token)
        pipeline_id = gl.trigger_pipeline(project_url=project_url, ref="master")

        sleep(2)

        while True:
            pipeline_status = gl.fetch_pipeline_status(project_url=project_url, pipeline_id=str(pipeline_id))

            if pipeline_status == PipelineStatus.success.value:
                LOGGER.success("pipeline completed successfull")
                break
            elif pipeline_status == PipelineStatus.failed.value:
                LOGGER.error("pipeline failed")
                raise RuntimeError("triggered pipeline failed")

            sleep(10)


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

    def impl(self, *, ci: bool, **_: typing.Any) -> None:
        if not ci:
            LOGGER.warning(f"skipping {type(self)}, not in CI")
            return

        if not Predefined.CI_MERGE_REQUEST_ID.getenv(""):
            LOGGER.warning(f"skipping {type(self)}, not in merge request")
            return

        version_file = pathlib.Path("gcip2/VERSION")
        pyproject_file = pathlib.Path("pyproject.toml")

        self.check_version_diff()

        version = self.get_tag_from_version_file(version_file=version_file).strip()
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
    def get_tag_from_version_file(self, version_file: pathlib.Path) -> str:
        if not version_file.exists():
            raise FileNotFoundError(f"version file: {version_file} not found.")
        return version_file.read_text().strip()

    def impl(self, *, ci: bool, gitlab_token_section: str, **_: typing.Any) -> None:
        if not ci:
            LOGGER.warning(f"skipping {type(self)}, not in CI")
            return

        version_file = pathlib.Path("gcip2/VERSION")

        version = self.get_tag_from_version_file(version_file=version_file)

        LOGGER.info(f"creating tag for release: {version}")

        if Predefined.CI_DEFAULT_BRANCH.must() == Predefined.CI_COMMIT_BRANCH.getenv():
            token = self._secret_handler(gitlab_token_section).fetch()["token"]
            gl = GitlabApi(gitlab_token=token)
            gl.create_release_tag(version=version)
        else:
            LOGGER.warning("DRY-RUN: not release branch")


class PublishPackage(InteractiveShlex):
    def impl(self, *, ci: bool, pypi_token_section: str, **_: typing.Any) -> list[list[str]]:
        if not ci:
            LOGGER.warning(f"skipping {type(self)}, not in CI")
            return [["echo", "DRY-RUN"]]

        token = self._secret_handler(pypi_token_section).fetch()["token"]

        os.environ["UV_PUBLISH_TOKEN"] = token

        publish_cmds = ["uv", "publish"]
        if not (
            Predefined.CI_COMMIT_BRANCH.getenv()
            and Predefined.CI_COMMIT_BRANCH.getenv() == Predefined.CI_DEFAULT_BRANCH.getenv()
        ):
            publish_cmds.append("--dry-run")

        return [["uv", "build"], publish_cmds]
