from os import getenv as os_getenv

import requests

from gcip2 import Predefined
from gcip2.logging import logger as LOGGER


class GitlabApi:
    def __init__(
        self,
        gitlab_url: str | None = None,
        gitlab_token: str | None = None,
    ) -> None:
        self.session = requests.Session()

        token = gitlab_token or os_getenv("GITLAB_TOKEN", "")
        if not token:
            raise ValueError("Gitlab token does not set")
        self.session.headers.update({"PRIVATE-TOKEN": token})

        self.gitlab_url = gitlab_url if gitlab_url else ""

        self.base_api_url = gitlab_url or Predefined.CI_API_V4_URL.getenv("")

    def _send_gitlab_request(
        self,
        url_suffix: str,
        method: str = "GET",
        json: dict[str, str] | None = None,
        allow_failure: bool = False,
    ) -> requests.Response:
        url = f"{self.base_api_url}/{url_suffix}"

        LOGGER.debug(f"Sending {method} request: {url}")

        r = self.session.request(
            url=url,
            method=method,
            json=json,
        )

        if not r.ok:
            fail_message = f"Request failed: {r.status_code} - {r.text}"
            if allow_failure:
                LOGGER.warning(fail_message)
            else:
                raise requests.HTTPError(fail_message)

        return r

    def create_release_tag(self, version: str):
        project_id = Predefined.CI_PROJECT_ID.must()
        default_branch = Predefined.CI_DEFAULT_BRANCH.must()
        r = self._send_gitlab_request(
            url_suffix=f"projects/{project_id}/repository/tags",
            method="POST",
            json={
                "tag_name": "v" + version,
                "ref": default_branch,
            },
        )

        LOGGER.debug(f"status code: {r.status_code}")

        LOGGER.info(f"tag for version: {version} creating successful")

    def trigger_pipeline(self, project_url: str, ref: str) -> int:
        response = self._send_gitlab_request(
            url_suffix="/".join(["projects", project_url, "pipeline"]),
            method="POST",
            json={"ref": ref},
        ).json()

        pipeline_status = response.get("status", "failed")
        pipeline_url = response.get("web_url")

        LOGGER.info(f"pipeline in status {pipeline_status}: {pipeline_url}")

        return response.get("id")

    def fetch_pipeline_status(self, project_url: str, pipeline_id: str) -> str:
        response = self._send_gitlab_request(
            url_suffix="/".join(
                [
                    "projects",
                    project_url,
                    "pipelines",
                    pipeline_id,
                ]
            ),
            method="GET",
        ).json()

        pipeline_status = response.get("status", "failed")
        pipeline_url = response.get("web_url")

        LOGGER.info(f"pipeline in status {pipeline_status}: {pipeline_url}")

        return pipeline_status
