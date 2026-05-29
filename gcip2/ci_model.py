import json
from enum import Enum
from typing import Any, Optional, Self

import jsonschema
import pydantic


class BasePipelineModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    def dump(self: Self, **kwargs: Any) -> dict[str, Any]:
        return self.model_dump(
            mode="json",
            exclude_none=True,
            exclude_defaults=True,
            by_alias=True,
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


class ArtifactsReportsCoverage(BasePipelineModel):
    coverage_format: Optional[str] = None
    path: Optional[str] = None


class ArtifactsReports(BasePipelineModel):
    accessibility: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsaccessibility"

    annotations: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsannotations"

    api_fuzzing: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsapi_fuzzing"

    browser_performance: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsbrowser_performance"

    coverage_report: Optional[ArtifactsReportsCoverage] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportscoverage_report"

    codequality: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportscodequality"

    container_scanning: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportscontainer_scanning"

    coverage_fuzzing: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportscoverage_fuzzing"

    cyclonedx: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportscyclonedx"

    dast: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsdast"

    dependency_scanning: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsdependency_scanning"

    dotenv: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsdotenv"

    junit: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsjunit"

    load_performance: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsload_performance"

    metrics: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsmetrics"

    requirements: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsrequirements"

    sarif: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportssarif"

    sast: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportssast"

    secret_detection: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportssecret_detection"

    terraform: Optional[list[str]] = None
    "https://docs.gitlab.com/ci/yaml/artifacts_reports/#artifactsreportsterraform"


class Artifacts(BasePipelineModel):
    paths: Optional[list[str]] = None
    "A list of paths to files/folders that should be included in the artifact."
    "https://docs.gitlab.com/ci/yaml/#artifactspaths"

    reports: Optional[ArtifactsReports] = None

    exclude: Optional[list[str]] = None
    "A list of paths to files/folders that should be excluded in the artifact."
    "https://docs.gitlab.com/ci/yaml/#artifactsexclude"

    expose_as: Optional[str] = None
    "Can be used to expose job artifacts in the merge request UI. GitLab will add a link <expose_as> to the relevant merge request that points to the artifact."
    "https://docs.gitlab.com/ci/yaml/#artifactsexpose_as"


class JobVariables(BasePipelineModel):
    value: Optional[str | bool | int | float] = None
    "Default value of the variable. If used with `options`, `value` must be included in the array."
    "https://docs.gitlab.com/ci/yaml/#variablesvalue"

    expand: Optional[bool] = None
    "If the variable is expandable or not."
    "https://docs.gitlab.com/ci/yaml/#variablesexpand"


class GlobalVariables(JobVariables):
    description: Optional[str] = None
    "Explains what the variable is used for, what the acceptable values are."
    "Variables with `description` are prefilled when running a pipeline manually."
    "https://docs.gitlab.com/ci/yaml/#variablesdescription"

    options: Optional[list[str | bool | int | float]] = []
    "A list of predefined values that users can select from in the **Run pipeline** page when running a pipeline manually."
    "https://docs.gitlab.com/ci/yaml/#variablesoptions"


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

    variables: Optional[dict[str, JobVariables | str]] = None


class RulesChanges(BasePipelineModel):
    paths: list[str] = []
    "List of file paths."

    compare_to: Optional[str] = None
    "Ref for comparing changes."


class RulesExists(BasePipelineModel):
    paths: list[str] = []
    "List of file paths."

    project: Optional[str] = None
    "Path of the project to search in."

    ref: Optional[str] = None
    "Ref of the project to search in."


class JobWhen(str, Enum):
    ON_SUCCESS = "on_success"
    ON_FAILURE = "on_failure"
    ALWAYS = "always"
    NEVER = "never"
    MANUAL = "manual"
    DELAYED = "delayed"


class WorkflowAutoCancelOnJobFailure(str, Enum):
    NONE = "none"
    ALL = "all"


class WorkflowAutoCancelOnNewCommit(str, Enum):
    NONE = "none"
    CONSERVATIVE = "conservative"
    INTERRUPTIBLE = "interruptible"


class WorkflowAutoCancel(BasePipelineModel):
    on_job_failure: Optional[WorkflowAutoCancelOnJobFailure] = None
    "Define which jobs to stop after a job fails."

    on_new_commit: Optional[WorkflowAutoCancelOnNewCommit] = None
    "Configure the behavior of the auto-cancel redundant pipelines feature."
    "https://docs.gitlab.com/ci/yaml/#workflowauto_cancelon_new_commit"


class Rules(BasePipelineModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    if_: Optional[str] = pydantic.Field(serialization_alias="if", validation_alias="if", default=None)
    "Expression to evaluate whether additional attributes should be provided to the job."
    "https://docs.gitlab.com/ci/yaml/#rulesif"

    changes: Optional[RulesChanges | list[str]] = None
    "Additional attributes will be provided to job if any of the provided paths matches a modified file."
    "https://docs.gitlab.com/ci/yaml/#ruleschanges"

    exists: Optional[RulesExists | list[str]] = None
    "Additional attributes will be provided to job if any of the provided paths matches an existing file in the repository."
    "https://docs.gitlab.com/ci/yaml/#rulesexists"

    variables: Optional[dict[str, str]] = None
    "Defines variables for a rule result."
    "https://docs.gitlab.com/ci/yaml/#rulesvariables"

    when: Optional[JobWhen] = None

    auto_cancel: Optional[WorkflowAutoCancel] = None


class Workflow(BasePipelineModel):
    name: Optional[str] = None
    "Defines the pipeline name."
    "https://docs.gitlab.com/ci/yaml/#workflowname"

    auto_cancel: Optional[WorkflowAutoCancel] = None
    "Define the rules for when pipeline should be automatically cancelled."

    rules: Optional[list[Rules]] = None


class Pipeline(BasePipelineModel):
    jobs: list[Job] = []

    workflow: Optional[Workflow] = None

    stages: Optional[list[Stage | str]] = None
    "Groups jobs into stages. All jobs in one stage must complete before next stage is executed."
    "https://docs.gitlab.com/ci/yaml/#stages"

    include: list[IncludeComponent] = []

    variables: Optional[dict[str, GlobalVariables]] = {}

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
