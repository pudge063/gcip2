import pathlib

import requests

from gcip2 import Predefined
from gcip2.logging import logger as LOGGER
from gcip2.vault import SecretsHandler


def create_version_tag(version: str):
    client = SecretsHandler("gitlab-token")
    token = client.fetch()["token"]

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


def get_tag_from_version_file(version_file: pathlib.Path) -> str:
    if not version_file.exists():
        raise FileNotFoundError(f"version file: {version_file} not found.")
    return version_file.read_text()


def main():
    version_file = pathlib.Path("gcip2/VERSION")

    version = get_tag_from_version_file(version_file=version_file)

    LOGGER.info(f"creating tag for release: {version}")
    if Predefined.CI_DEFAULT_BRANCH.must() == Predefined.CI_COMMIT_BRANCH.getenv():
        create_version_tag(version=version)
    else:
        LOGGER.warning("DRY-RUN: not release branch")


if __name__ == "__main__":
    main()
