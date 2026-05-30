import dataclasses
import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional, Self

import jsonschema
import pydantic

__all__ = (
    "Trigger",
    "Pipeline",
    "Job",
    "Stage",
    "Image",
    "Needs",
    "Artifacts",
    "ArtifactsReports",
    "IncludeComponent",
    "BaseInput",
    "Workflow",
    "WorkflowAutoCancel",
    "Rule",
    "WorkflowAutoCancelOnJobFailure",
    "RuleChanges",
    "WorkflowAutoCancelOnNewCommit",
    "JobVariables",
    "GlobalVariables",
    "Default",
    "pipeline",
    "PipelineBuilderImpl",
)


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


class RuleChanges(BasePipelineModel):
    paths: list[str] = []
    "List of file paths."

    compare_to: Optional[str] = None
    "Ref for comparing changes."


class RuleExists(BasePipelineModel):
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


class Rule(BasePipelineModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    if_: Optional[str] = pydantic.Field(serialization_alias="if", validation_alias="if", default=None)
    "Expression to evaluate whether additional attributes should be provided to the job."
    "https://docs.gitlab.com/ci/yaml/#rulesif"

    changes: Optional[RuleChanges | list[str]] = None
    "Additional attributes will be provided to job if any of the provided paths matches a modified file."
    "https://docs.gitlab.com/ci/yaml/#ruleschanges"

    exists: Optional[RuleExists | list[str]] = None
    "Additional attributes will be provided to job if any of the provided paths matches an existing file in the repository."
    "https://docs.gitlab.com/ci/yaml/#rulesexists"

    variables: Optional[dict[str, str]] = None
    "Defines variables for a rule result."
    "https://docs.gitlab.com/ci/yaml/#rulesvariables"

    when: Optional[JobWhen] = None

    auto_cancel: Optional[WorkflowAutoCancel] = None


class IdTokens(BasePipelineModel):
    aud: Optional[str | list[str]] = []


class Identity(str, Enum):
    GOOGLE_CLOUD = "google_cloud"


class JobTemplate(BasePipelineModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    image: Image = Image()

    services: Optional[Any] = None

    before_script: Optional[list[str] | str] = None

    after_script: Optional[list[str] | str] = None

    hooks: Optional[Any] = None

    rules: Optional[list[Rule]] = None

    variables: Optional[dict[str, JobVariables | str]] = None

    cache: Optional[Any] = None

    id_tokens: Optional[IdTokens] = None

    identity: Optional[Identity] = None

    inputs: Optional[BaseInput] = None

    secrets: Optional[Any] = None

    script: list[str] | str = []

    run: Optional[Any] = None
    "Specifies a list of steps to execute in the job. The `run` keyword is an alternative to `script` and allows for more advanced job configuration."
    "Each step is an object that defines a single task or command."
    "Use either `run` or `script` in a job, but not both, otherwise the pipeline will error out."

    stage: Optional[Stage | str] = None

    only: Optional[Any] = None
    "Job will run *only* when these filtering options match."

    extends: Optional[str | list[str]] = None
    "The name of one or more jobs to inherit configuration from."

    needs: Optional[list[Needs | str]] = None
    "The list of jobs in previous stages whose sole completion is needed to start the current job."

    except_: Optional[Any] = pydantic.Field(serialization_alias="except", validation_alias="except", default=None)

    tags: list[str] = []

    allow_failure: Optional[list[bool | int | list[int]]] = None

    timeout: Optional[str] = None
    "Allows you to configure a timeout for a specific job (e.g. `1 minute`, `1h 30m 12s`)."
    "https://docs.gitlab.com/ci/yaml/#timeout"

    when: Optional[JobWhen] = None
    "Describes the conditions for when to run the job. Defaults to 'on_success'."
    "https://docs.gitlab.com/ci/yaml/#when"

    start_in: Optional[str] = None
    "Used in conjunction with 'when: delayed' to set how long to delay before starting a job. e.g. '5', 5 seconds, 30 minutes, 1 week, etc."
    "https://docs.gitlab.com/ci/jobs/job_control/#run-a-job-after-a-delay"

    manual_confirmation: Optional[str] = None
    "Describes the Custom confirmation message for a manual job."
    "https://docs.gitlab.com/ci/yaml/#when"

    dependencies: Optional[list[str]] = None
    "Specify a list of job names from earlier stages from which artifacts should be loaded."
    "By default, all previous artifacts are passed."
    "Use an empty array to skip downloading artifacts."

    artifacts: Artifacts = Artifacts()

    environment: Optional[Any] = None

    release: Optional[Any] = None

    coverage: Optional[str] = None
    "Must be a regular expression, optionally but recommended to be quoted, and must be surrounded with '/'."
    "Example: '/Code coverage: \\d+\\.\\d+/'"

    retry: Optional[Any] = None

    parallel: Optional[Parallel | int] = None

    interruptible: Optional[bool] = None
    "Interruptible is used to indicate that a job should be canceled if made redundant by a newer pipeline run."
    "https://docs.gitlab.com/ci/yaml/#interruptible)."

    resource_group: Optional[str] = None
    "Limit job concurrency. Can be used to ensure that the Runner will not run certain jobs simultaneously."

    trigger: Optional[Trigger] = None

    inherit: Optional[Any] = None

    publish: Optional[str] = None
    "Deprecated. Use `pages.publish` instead. A path to a directory that contains the files to be published with Pages."

    pages: Optional[Any] = None


class Job(JobTemplate):
    name: Optional[str] = None


class Workflow(BasePipelineModel):
    name: Optional[str] = None
    "Defines the pipeline name."
    "https://docs.gitlab.com/ci/yaml/#workflowname"

    auto_cancel: Optional[WorkflowAutoCancel] = None
    "Define the rules for when pipeline should be automatically cancelled."

    rules: Optional[list[Rule]] = None


class Default(BasePipelineModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    after_script: Optional[list[str] | str] = None

    artifacts: Optional[Artifacts] = None

    before_script: Optional[list[str] | str] = None

    hooks: Optional[Any] = None

    cache: Optional[Any] = None

    image: Optional[Image] = None

    interuptable: Optional[bool] = None
    "Interruptible is used to indicate that a job should be canceled if made redundant by a newer pipeline run."
    "https://docs.gitlab.com/ci/yaml/#interruptible"

    id_tokens: Optional[IdTokens] = None
    "Defines JWTs to be injected as environment variables."

    identity: Optional[Identity] = None
    "Sets a workload identity (experimental), allowing automatic authentication with the external system."
    "https://docs.gitlab.com/ci/yaml/#identity"

    retry: Optional[Any] = None
    "Retry a job if it fails. Can be a simple integer or object definition."
    "https://docs.gitlab.com/ci/yaml/#retry)."

    services: Optional[Any] = None

    tags: Optional[list[str]] = None

    timeout: Optional[str] = None
    "Allows you to configure a timeout for a specific job (e.g. `1 minute`, `1h 30m 12s`)."
    "https://docs.gitlab.com/ci/yaml/#timeout"

    # reference_: Optional[str] = pydantic.Field(
    #     serialization_alias="!reference", validation_alias="!reference", default=None
    # )
    # invalid schema


class Pipeline(BasePipelineModel):
    jobs: list[Job] = []

    workflow: Optional[Workflow] = Workflow()

    stages: Optional[list[Stage | str]] = None
    "Groups jobs into stages. All jobs in one stage must complete before next stage is executed."
    "https://docs.gitlab.com/ci/yaml/#stages"

    include: list[IncludeComponent] = []

    default: Optional[Default] = None

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


class JobBuilderImpl(Job):
    model: Job = pydantic.Field(
        repr=False,
        default_factory=Job,
        init=False,
    )

    def impl(self: Self) -> Self: ...

    def apply(self: Self) -> Self: ...

    def build(self: Self) -> Job:
        return self.model.model_copy(deep=True)

    def with_name(self: Self, name: str) -> Self:
        self.model.name = name
        return self

    def with_image(self, image: str, entrypoint: list[str] = []) -> Self:
        self.model.image = Image(name=image, entrypoint=entrypoint)
        return self

    def with_tags(self, tags: list[str]) -> Self:
        self.model.tags = tags
        return self

    def with_stage(self, stage: str) -> Self:
        self.model.stage = stage
        return self

    def with_artifacts(
        self,
        paths: Optional[list[str]] = None,
        reports: Optional[ArtifactsReports] = None,
        exclude: Optional[list[str]] = None,
        expose_as: Optional[str] = None,
    ) -> Self:
        self.model.artifacts = Artifacts(
            paths=paths,
            reports=reports,
            exclude=exclude,
            expose_as=expose_as,
        )
        return self

    def with_needs(self, needs: list[Needs | str]) -> Self:
        self.model.needs = needs
        return self


class PipelineBuilderImpl(Pipeline):
    model: Pipeline = pydantic.Field(
        repr=False,
        default_factory=Pipeline,
        init=False,
    )

    def impl(self: Self) -> Self: ...

    def apply(self: Self) -> Self: ...

    def build(self: Self) -> Pipeline:
        return self.model.model_copy(deep=True)

    @staticmethod
    def job(job_class: type[JobBuilderImpl]) -> JobBuilderImpl:
        return job_class()

    def with_workflow(self, workflow: Workflow = Workflow()):
        self.model.workflow = workflow
        return self

    def with_default(self, default: Default = Default()):
        self.model.default = default
        return self


def pipeline(func: Any):

    func.__gcip2_pipeline__ = True

    return func
