import pathlib

import requests

from gcip2 import Predefined


def create_version_tag(version: str):
    token = Predefined.CI_JOB_TOKEN.must()
    gitlab_url = Predefined.CI_API_V4_URL.must()
    project_id = Predefined.CI_PROJECT_ID.must()
    default_branch = Predefined.CI_DEFAULT_BRANCH.must()
    return requests.post(
        url=f"{gitlab_url}/projects/{project_id}/repository/tags",
        data={
            "tag_name": version,
            "ref": default_branch,
        },
        headers={"PRIVATE-TOKEN": token},
    )


def get_tag_from_version_file(version_file: pathlib.Path) -> str:
    if not version_file.exists():
        raise FileNotFoundError(f"version file: {version_file} not found.")
    return version_file.read_text()


def main():
    version_file = pathlib.Path("gcip2/VERSION")

    version = get_tag_from_version_file(version_file=version_file)

    print(f"creating tag for release: {version}", flush=True)
    if Predefined.CI_DEFAULT_BRANCH.must() == Predefined.CI_COMMIT_BRANCH.getenv():
        create_version_tag(version=version)
    else:
        print("DRY-RUN: not release branch")


if __name__ == "__main__":
    main()
