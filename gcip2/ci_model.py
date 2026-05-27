from enum import Enum
from typing import Any, Optional, Self
from pydantic import BaseModel, ConfigDict


class BasePipelineModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def dump(self: Self) -> dict[str, Any]:
        return self.model_dump(
            mode="json",
            exclude_none=True,
            exclude_defaults=True,
        )


class TriggerStrategy(str, Enum):
    DEPEND = "depend"
    MIRROR = "mirror"


class TriggerInclude(BasePipelineModel):
    local: Optional[str] = None


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
