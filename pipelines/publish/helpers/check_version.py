import pathlib

import git
import requests
import tomllib

from gcip2 import Predefined


def ensure_tag_is_not_exists(tag: str) -> bool:
    token = Predefined.CI_JOB_TOKEN.must()
    gitlab_url = Predefined.CI_API_V4_URL.must()
    project_id = Predefined.CI_PROJECT_ID.must()

    return requests.get(
        url=f"{gitlab_url}/projects/{project_id}/repository/tags/{tag}",
        headers={"PRIVATE-TOKEN": token},
    ).ok


def check_version_diff():
    default_branch = Predefined.CI_DEFAULT_BRANCH.getenv("master")
    repo = git.Repo(".")
    repo.remotes.origin.fetch(default_branch)

    diff = repo.git.diff("--color=always", f"origin/{default_branch}", "HEAD", "--", "gcip2/VERSION")
    print(diff)
    if not diff:
        raise ValueError("diff in version not found.")


def get_tag_from_version_file(version_file: pathlib.Path) -> str:
    if not version_file.exists():
        raise FileNotFoundError(f"version file: {version_file} not found.")
    return version_file.read_text()


def get_tag_from_pyproject_file(pyproject_file: pathlib.Path) -> str:
    if not pyproject_file.exists():
        raise FileNotFoundError(f"version file: {pyproject_file} not found.")
    pyproject_data = tomllib.loads(pyproject_file.read_text())

    return pyproject_data["tool"]["poetry"]["version"]


def main():
    if not Predefined.CI_PIPELINE_SOURCE.getenv() == "merge_request_event":
        print("not merge request")
        return

    version_file = pathlib.Path("gcip2/VERSION")
    pyproject_file = pathlib.Path("pyproject.toml")

    check_version_diff()

    version = get_tag_from_version_file(version_file=version_file)

    pyproject_version = get_tag_from_pyproject_file(pyproject_file=pyproject_file)

    print(f"version in VERSION file: {version}")
    print(f"version in PYPROJECT file: {version}")

    if not version == pyproject_version:
        raise ValueError(
            f"Versions diff between {version_file.name}: {version} and {pyproject_file.name}: {pyproject_version}"
        )

    if ensure_tag_is_not_exists(tag=version):
        raise RuntimeError(f"tag for version {version} already exists")

    print(f"tag for version {version} not found")


if __name__ == "__main__":
    main()
