import json
from enum import Enum
from typing import Any, ClassVar, Optional, Self

import jsonschema
import pydantic

from gcip2.project_config import ProjectConfig
from gcip2.project_config.compose import ComposeImage
from gcip2.vault import SecretsHandler

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
)


class BaseModel(pydantic.BaseModel):
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


class Stage(str, Enum):
    PRE = ".pre"
    POST = ".post"
    JOBS = "jobs"
    BUILD = "build"
    TEST = "test"
    DEPLOY = "deploy"


class ArtifactsWhen(str, Enum):
    ON_SUCCESS = "on_success"
    ON_FAILURE = "on_failure"
    ALWAYS = "always"


class WorkflowWhen(str, Enum):
    ALWAYS = "always"
    NEVER = "never"


class JobWhen(str, Enum):
    ALWAYS = "always"
    NEVER = "never"
    ON_SUCCESS = "on_success"
    ON_FAILURE = "on_failure"
    MANUAL = "manual"
    DELAYED = "delayed"


class BaseInput(BaseModel):
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


class TriggerIncludeArtifact(BaseModel):
    job: Optional[str] = None

    artifact: Optional[str] = None
    "Relative path to the generated YAML file which is extracted from the artifacts and used as the configuration for triggering the child pipeline."


class TriggerIncludeLocal(BaseModel):
    local: Optional[str] = None
    "Relative path from local repository root (`/`) to the local YAML file to define the pipeline configuration."


class TriggerIncludeTemplate(BaseModel):
    template: Optional[str] = None
    "Name of the template YAML file to use in the pipeline configuration."


class TriggerForward(BaseModel):
    yaml_variables: Optional[bool] = None
    "Variables defined in the trigger job are passed to downstream pipelines."

    pipeline_variables: Optional[bool] = None
    "Variables added for manual pipeline runs and scheduled pipelines are passed to downstream pipelines."


class Trigger(BaseModel):
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


class Parallel(BaseModel):
    matrix: list[dict[str, list[str]]] = pydantic.Field(default_factory=lambda: [])


class Needs(BaseModel):
    pipeline: Optional[str] = None

    job: Optional[str] = None

    project: Optional[str] = None

    optional: Optional[bool] = None

    artifacts: Optional[bool] = None

    parallel: Optional[Parallel | int] = None


class Image(BaseModel):
    name: Optional[str] = None

    entrypoint: list[str] = pydantic.Field(default_factory=list)


class ArtifactsReportsCoverage(BaseModel):
    coverage_format: Optional[str] = None
    path: Optional[str] = None


class ArtifactsReports(BaseModel):
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

    junit: Optional[str | list[str]] = None
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


class ArtifactsAccess(str, Enum):
    ALL = "all"
    DEVELOPER = "developer"
    MAINTAINER = "maintainer"
    NONE = "none"


class Artifacts(BaseModel):
    paths: Optional[list[str]] = None
    "A list of paths to files/folders that should be included in the artifact."
    "https://docs.gitlab.com/ci/yaml/#artifactspaths"

    exclude: Optional[list[str]] = None
    "A list of paths to files/folders that should be excluded in the artifact."
    "https://docs.gitlab.com/ci/yaml/#artifactsexclude"

    expose_as: Optional[str] = None
    "Can be used to expose job artifacts in the merge request UI. GitLab will add a link <expose_as> to the relevant merge request that points to the artifact."
    "https://docs.gitlab.com/ci/yaml/#artifactsexpose_as"

    expire_in: Optional[str] = None
    "Use expire_in to specify how long job artifacts are stored before they expire and are deleted."
    "https://archives.docs.gitlab.com/17.11/ci/yaml/#artifactsexpire_in"

    name: Optional[str] = None
    "Use the artifacts:name keyword to define the name of the created artifacts archive. You can specify a unique name for every archive."
    "https://archives.docs.gitlab.com/17.11/ci/yaml/#artifactsname"

    public: Optional[bool] = None
    "Use artifacts:public to determine whether the job artifacts should be publicly available."
    "https://archives.docs.gitlab.com/17.11/ci/yaml/#artifactspublic"

    access: Optional[ArtifactsAccess] = None
    "Use artifacts:access to determine who can access the job artifacts from the GitLab UI or API."
    "This option does not prevent you from forwarding artifacts to downstream pipelines."
    "https://archives.docs.gitlab.com/17.11/ci/yaml/#artifactsaccess"

    reports: Optional[ArtifactsReports] = None

    untracked: Optional[bool] = None
    "Use artifacts:untracked to add all Git untracked files as artifacts (along with the paths defined in artifacts:paths)."
    "artifacts:untracked ignores configuration in the repository's .gitignore, so matching artifacts in .gitignore are included."
    "https://archives.docs.gitlab.com/17.11/ci/yaml/#artifactsuntracked"

    when: Optional[ArtifactsWhen] = None
    "Use artifacts:when to upload artifacts on job failure or despite the failure."
    "https://archives.docs.gitlab.com/17.11/ci/yaml/#artifactswhen"


class JobVariables(BaseModel):
    "Defines default variables for all jobs. Job level property overrides global variables."

    "https://docs.gitlab.com/ci/yaml/#variables)."

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

    options: Optional[list[str | bool | int | float]] = pydantic.Field(default_factory=lambda: [])
    "A list of predefined values that users can select from in the **Run pipeline** page when running a pipeline manually."
    "https://docs.gitlab.com/ci/yaml/#variablesoptions"


class RuleVariables(JobVariables):
    ...
    "Defines variables for a rule result."
    "https://docs.gitlab.com/ci/yaml/#rulesvariables"


class RuleChanges(BaseModel):
    paths: list[str] = pydantic.Field(default_factory=list)
    "List of file paths."

    compare_to: Optional[str] = None
    "Ref for comparing changes."


class RuleExists(BaseModel):
    paths: list[str] = pydantic.Field(default_factory=list)
    "List of file paths."

    project: Optional[str] = None
    "Path of the project to search in."

    ref: Optional[str] = None
    "Ref of the project to search in."


class WorkflowAutoCancelOnJobFailure(str, Enum):
    NONE = "none"
    ALL = "all"


class WorkflowAutoCancelOnNewCommit(str, Enum):
    NONE = "none"
    CONSERVATIVE = "conservative"
    INTERRUPTIBLE = "interruptible"


class WorkflowAutoCancel(BaseModel):
    on_job_failure: Optional[WorkflowAutoCancelOnJobFailure] = None
    "Define which jobs to stop after a job fails."

    on_new_commit: Optional[WorkflowAutoCancelOnNewCommit] = None
    "Configure the behavior of the auto-cancel redundant pipelines feature."
    "https://docs.gitlab.com/ci/yaml/#workflowauto_cancelon_new_commit"


class Rule(BaseModel):
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


class IncludeRule(BaseModel): ...


class IncludeItem(BaseModel):
    inputs: Optional[dict[str, BaseInput]] = None

    rules: Optional[list[IncludeRule]] = None
    "You can use rules to conditionally include other configuration files."
    "https://docs.gitlab.com/ci/yaml/includes/#use-rules-with-include"


class IncludeLocalItem(BaseModel):
    local: str
    "Relative path from local repository root (`/`) to the `yaml`/`yml` file template. The file must be on the same branch, and does not work across git submodules."


class IncludeComponent(IncludeItem):
    component: Optional[str] = None
    "Local path to component directory or full path to external component directory."


class IdTokens(BaseModel):
    aud: Optional[str | list[str]] = pydantic.Field(default_factory=list)


class Identity(str, Enum):
    GOOGLE_CLOUD = "google_cloud"


class JobRule(Rule):
    when: Optional[JobWhen] = None


class Docker(BaseModel):
    platform: Optional[str] = None
    "Image architecture to pull."

    user: Optional[str] = None
    "Username or UID to use for the container."


class Kubernetes(BaseModel):
    user: str | int


class PullPolicy(str, Enum):
    ALWAYS = "always"
    NEVER = "never"
    IFNOTPRESENT = "if-not-present"


class Services(BaseModel):
    "Similar to `image` property, but will link the specified services to the `image` container."

    name: str
    "Full name of the image that should be used. It should contain the Registry part if needed."

    entrypoint: Optional[list[str]] = None
    "Command or script that should be executed as the container's entrypoint."
    "It will be translated to Docker's --entrypoint option while creating the container."
    "The syntax is similar to Dockerfile's ENTRYPOINT directive, where each shell token is a separate string in the array."
    "https://docs.gitlab.com/ci/services/#available-settings-for-services"

    docker: Optional[Docker] = None
    "Options to pass to Runners Docker Executor."
    "https://docs.gitlab.com/ci/yaml/#servicesdocker"

    kubernetes: Optional[Kubernetes] = None
    "Options to pass to Runners Kubernetes Executor."
    "https://docs.gitlab.com/ci/yaml/#imagekubernetes"

    pull_policy: Optional[PullPolicy | list[PullPolicy]] = None
    "Specifies how to pull the image in Runner. It can be one of `always`, `never` or `if-not-present`. The default value is `always`."
    "https://docs.gitlab.com/ci/yaml/#servicespull_policy"

    command: Optional[list[str] | str | list[list[str]]] = None
    "Command or script that should be used as the container's command. It will be translated to arguments passed to Docker after the image's name."
    "The syntax is similar to Dockerfile's CMD directive, where each shell token is a separate string in the array."
    "https://docs.gitlab.com/ci/services/#available-settings-for-services"

    alias: Optional[str] = None
    "Additional alias that can be used to access the service from the job's container. Read Accessing the services for more information."
    "https://docs.gitlab.com/ci/services/#available-settings-for-services"

    variables: Optional[JobVariables] = None
    "Additional environment variables that are passed exclusively to the service. Service variables cannot reference themselves."
    "https://docs.gitlab.com/ci/services/#available-settings-for-services)"


class JobTemplate(BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    image: Optional[Image] = None
    "Full name of the image that should be used. It should contain the Registry part if needed."

    services: Optional[list[str | Services]] = None
    "https://docs.gitlab.com/ci/yaml/#services"

    before_script: Optional[list[str] | str] = None

    after_script: Optional[list[str] | str] = None

    hooks: Optional[Any] = None

    rules: Optional[list[JobRule]] = None

    variables: Optional[dict[str, JobVariables | str]] = None

    cache: Optional[Any] = None

    id_tokens: Optional[IdTokens] = None

    identity: Optional[Identity] = None

    inputs: Optional[BaseInput] = None

    secrets: Optional[Any] = None

    script: list[str] | str = pydantic.Field(default_factory=list)

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

    tags: list[str] = pydantic.Field(default_factory=list)

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

    artifacts: Artifacts = pydantic.Field(default_factory=Artifacts)

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


class WorkflowRule(Rule):
    when: Optional[WorkflowWhen] = None

    auto_cancel: Optional[WorkflowAutoCancel] = None


class Workflow(BaseModel):
    name: Optional[str] = None
    "Defines the pipeline name."
    "https://docs.gitlab.com/ci/yaml/#workflowname"

    auto_cancel: Optional[WorkflowAutoCancel] = None
    "Define the rules for when pipeline should be automatically cancelled."

    rules: Optional[list[WorkflowRule]] = None


class Default(BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    after_script: Optional[list[str] | str] = None

    artifacts: Optional[Artifacts] = None

    before_script: Optional[list[str] | str] = None

    hooks: Optional[Any] = None

    cache: Optional[Any] = None

    image: Optional[Image] = None

    interruptible: Optional[bool] = None
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


class Pipeline(BaseModel):
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    )

    jobs: list["Job | JobBuilderImpl"] = pydantic.Field(default_factory=lambda: [])

    workflow: Optional[Workflow] = Workflow()

    stages: Optional[list[Stage | str]] = None
    "Groups jobs into stages. All jobs in one stage must complete before next stage is executed."
    "https://docs.gitlab.com/ci/yaml/#stages"

    include: list[IncludeComponent] = pydantic.Field(default_factory=lambda: [])

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


class JobBuilder:
    def build(self) -> Job:
        raise NotImplementedError


class JobBuilderImpl(JobBuilder):
    _base: ClassVar[type["JobBuilderImpl"] | None] = None
    _task: ClassVar[str | Enum | None] = None

    _config = ProjectConfig()
    _secret_handler = SecretsHandler

    def __init__(self) -> None:
        self.model: Job = Job()

    def _apply_base(self) -> None:
        if self._base is None:
            return

        base = self._base()
        base._apply_base()
        base.apply()

        base_model = base.model.model_dump(exclude_none=True)
        current_model = self.model.model_dump(exclude_none=True)

        merged = {
            **base_model,
            **current_model,
        }

        self.model = Job.model_validate(merged)

    def _apply_task(self):
        if self._task and isinstance(self.model.script, list):
            if isinstance(self._task, str):
                self.model.script.extend([f"gciptask run {self._task}"])
            else:
                self.model.script.extend([f"gciptask run {self._task.value}"])

    def apply(self: Self) -> Self:
        return self

    def build(self: Self) -> Job:
        self._apply_base()
        self._apply_task()
        return self.model.model_copy(deep=True)

    def with_name(self: Self, name: str) -> Self:
        self.model.name = name
        return self

    def add_to_name(self: Self, suffix: str) -> Self:
        if not self.model.name:
            raise ValueError("Could not add suffix to job name because job name is not set.")
        self.model.name += suffix
        return self

    def with_script(self: Self, script: str | list[str]) -> Self:
        self.model.script = script
        return self

    def with_before_script(self: Self, script: str | list[str]) -> Self:
        self.model.before_script = script
        return self

    def with_after_script(self: Self, script: str | list[str]) -> Self:
        self.model.after_script = script
        return self

    def add_to_script(self: Self, script: str | list[str]) -> Self:
        if isinstance(self.model.script, list):
            if isinstance(script, str):
                self.model.script.extend([script])
            else:
                self.model.script.extend(script)
        return self

    def with_image(self, image: str, entrypoint: list[str] = []) -> Self:
        self.model.image = Image(name=image, entrypoint=entrypoint)
        return self

    def with_compose_image(self, image_name: str, entrypoint: list[str] = []) -> Self:
        image_data = self._config.compose.images.get(image_name)
        if not image_data:
            raise ValueError(f"image_data not found in {self._config.compose.path.name}")

        self.model.image = Image(name=image_data.image, entrypoint=entrypoint)
        return self

    def with_tags(self, tags: list[str]) -> Self:
        self.model.tags = tags
        return self

    def with_stage(self, stage: str) -> Self:
        self.model.stage = stage
        return self

    def with_when(self: Self, when: JobWhen) -> Self:
        self.model.when = when
        return self

    def with_artifacts(
        self,
        paths: Optional[list[str]] = None,
        exclude: Optional[list[str]] = None,
        expire_in: Optional[str] = None,
        expose_as: Optional[str] = None,
        name: Optional[str] = None,
        public: Optional[bool] = None,
        access: Optional[ArtifactsAccess] = None,
        reports: Optional[ArtifactsReports] = None,
        untracked: Optional[bool] = None,
        when: Optional[ArtifactsWhen] = None,
    ) -> Self:
        if public and access:
            raise ValueError("Could not be set both parameters: public and access.")

        self.model.artifacts = Artifacts(
            paths=paths,
            exclude=exclude,
            expose_as=expose_as,
            expire_in=expire_in,
            name=name,
            public=public,
            access=access,
            reports=reports,
            untracked=untracked,
            when=when,
        )
        return self

    def with_needs(self, needs: list[Needs | str]) -> Self:
        self.model.needs = needs
        return self

    def with_dependencies(self, dependencies: list[str]) -> Self:
        self.model.dependencies = dependencies
        return self
