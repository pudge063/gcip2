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


class BaseInputType(Enum):
    ARRAY = "array"
    BOOLEAN = "boolean"
    NUMBER = "number"
    STRING = "string"


class BaseInput(BasePipelineModel):
    type: Optional[BaseInputType] = BaseInputType.STRING
    "Input type. Defaults to 'string' when not specified."

    description: Optional[str] = None
    "Human-readable explanation of the parameter."

    options: Optional[list[BaseInputType]] = None
    "List of allowed values for this input."

    regex: Optional[str] = None
    "Regular expression that string values must match."

    default: Optional[Any] = None
    "Default value for this input."


class TriggerStrategy(str, Enum):
    DEPEND = "depend"
    MIRROR = "mirror"


class TriggerIncludeArtifact(BasePipelineModel):
    job: Optional[str] = None

    artifact: Optional[str] = None
    "Relative path to the generated YAML file which is extracted from the artifacts and used as the configuration for triggering the child pipeline."


class TriggerIncludeLocal(BasePipelineModel):
    local: Optional[str] = None
    "Relative path from local repository root (`/`) to the local YAML file to define the pipeline configuration."


class TriggerIncludeTemplate(BasePipelineModel):
    template: Optional[str] = None
    "Name of the template YAML file to use in the pipeline configuration."


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

    ref: Optional[str] = None
    "Branch/Tag/Commit hash for the target project."

    file: Optional[str] = None
    "Relative path from repository root (`/`) to the pipeline configuration YAML file."

    branch: Optional[str] = None
    "The branch name that a downstream pipeline will use"

    strategy: Optional[TriggerStrategy] = None
    "You can mirror or depend on the pipeline status from the triggered pipeline to the source bridge job by using strategy: `depend` or `mirror`"

    include: Optional[list[TriggerIncludeArtifact | TriggerIncludeLocal | TriggerIncludeTemplate]] = None

    forward: Optional[TriggerForward] = None
    "Specify what to forward to the downstream pipeline."

    component: Optional[str] = None
    "Local path to component directory or full path to external component directory."

    remote: Optional[str] = None
    "URL to a `yaml`/`yml` template file using HTTP/HTTPS."

    inputs: Optional[Any] = None
    "Used to pass input values to included templates, components, downstream pipelines, or child pipelines."
    "https://docs.gitlab.com/ci/inputs"


class IncludeItem(BasePipelineModel):
    inputs: Optional[dict[str, BaseInput]] = None


class IncludeComponent(IncludeItem):
    component: Optional[str] = None
    "Local path to component directory or full path to external component directory."

    rules: Optional[Any] = None


class Stage(str, Enum):
    PRE = ".pre"
    POST = ".post"
    JOBS = "jobs"
    BUILD = "build"
    TEST = "test"
    DEPLOY = "deploy"


class Parallel(BasePipelineModel):
    matrix: dict[str, list[str]] = {}


class Needs(BasePipelineModel):
    pipeline: Optional[str] = None

    job: Optional[str] = None

    project: Optional[str] = None

    optional: Optional[bool] = None

    artifacts: Optional[bool] = None

    parallel: Optional[Parallel | int] = None


class Image(BasePipelineModel):
    name: Optional[str] = None

    entrypoint: list[str] = []


class Artifacts(BasePipelineModel):
    paths: Optional[list[str]] = None
    "A list of paths to files/folders that should be included in the artifact."
    "https://docs.gitlab.com/ci/yaml/#artifactspaths"

    exclude: Optional[list[str]] = None
    "A list of paths to files/folders that should be excluded in the artifact."
    "https://docs.gitlab.com/ci/yaml/#artifactsexclude"

    expose_as: Optional[str] = None
    "Can be used to expose job artifacts in the merge request UI. GitLab will add a link <expose_as> to the relevant merge request that points to the artifact."
    "https://docs.gitlab.com/ci/yaml/#artifactsexpose_as"


class Job(BasePipelineModel):
    name: str

    artifacts: Artifacts = Artifacts()

    image: Image = Image()

    script: list[str] | str = []

    stage: Optional[Stage | str] = None

    tags: list[str] = []

    trigger: Optional[Trigger] = None

    parallel: Optional[Parallel | int] = None

    needs: Optional[list[Needs]] = None
    "The list of jobs in previous stages whose sole completion is needed to start the current job."


class Pipeline(BasePipelineModel):
    jobs: list[Job] = []

    stages: Optional[list[Stage | str]] = None
    "Groups jobs into stages. All jobs in one stage must complete before next stage is executed."
    "https://docs.gitlab.com/ci/yaml/#stages"

    include: list[IncludeComponent] = []

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
