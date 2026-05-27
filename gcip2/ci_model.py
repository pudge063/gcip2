from enum import Enum
from typing import Any, Optional, Self
from pydantic import BaseModel, ConfigDict
import jsonschema
import json


class BasePipelineModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def dump(self: Self, **kwargs: Any) -> dict[str, Any]:
        return self.model_dump(
            mode="json",
            exclude_none=True,
            exclude_defaults=True,
            **kwargs,
        )


class TriggerStrategy(str, Enum):
    DEPEND = "depend"
    MIRROR = "mirror"


class TriggerInclude(BasePipelineModel):
    local: Optional[str] = None
    "Relative path from local repository root (`/`) to the local YAML file to define the pipeline configuration."

    template: Optional[str] = None
    "Name of the template YAML file to use in the pipeline configuration."

    artifact: Optional[str] = None
    "Relative path to the generated YAML file which is extracted from the artifacts and used as the configuration for triggering the child pipeline."


class TriggerForward(BasePipelineModel):
    yaml_variables: Optional[bool] = None
    "Variables defined in the trigger job are passed to downstream pipelines."

    pipeline_variables: Optional[bool] = None
    "Variables added for manual pipeline runs and scheduled pipelines are passed to downstream pipelines."


class Trigger(BasePipelineModel):
    "Trigger allows you to define downstream pipeline trigger."

    "When a job created from trigger definition is started by GitLab, a downstream pipeline gets created."
    "https://docs.gitlab.com/ci/yaml/#trigger"

    project: Optional[str] = None
    "Path to the project, e.g. `group/project`, or `group/sub-group/project`."

    branch: Optional[str] = None
    "The branch name that a downstream pipeline will use"

    strategy: Optional[TriggerStrategy] = None
    "You can mirror or depend on the pipeline status from the triggered pipeline to the source bridge job by using strategy: `depend` or `mirror`"

    inputs: None

    forward: Optional[TriggerForward] = None
    "Specify what to forward to the downstream pipeline."


class Stage(str, Enum):
    PRE = ".pre"
    POST = ".post"
    JOBS = "jobs"
    BUILD = "build"
    TEST = "test"
    DEPLOY = "deploy"


class Image(BasePipelineModel):
    name: Optional[str] = None

    entrypoint: list[str] = []


class Job(BasePipelineModel):
    name: str

    image: Image = Image()

    script: list[str] = []

    stage: Optional[Stage | str] = None


class Pipeline(BasePipelineModel):
    jobs: list[Job] = []

    stages: Optional[list[Stage | str]] = None
    "Groups jobs into stages. All jobs in one stage must complete before next stage is executed."
    "https://docs.gitlab.com/ci/yaml/#stages"

    @staticmethod
    def load_pipeline_default_schema() -> dict[str, Any]:
        with open("gcip2/ci.json", "r") as f:
            return json.loads(f.read())

    def validate_pipeline(self: Self) -> None:
        try:
            jsonschema.validate(
                instance=self.dump(),
                schema=self.load_pipeline_default_schema(),
            )
        except jsonschema.ValidationError as exc:
            raise exc
