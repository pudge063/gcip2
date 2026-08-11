import enum
import os
import typing

T = typing.TypeVar("T")


class VarEnum(str, enum.Enum):
    @typing.override
    def __repr__(self) -> str:
        return self.name

    @typing.override
    def __str__(self) -> str:
        return self.__repr__()

    def __call__(self) -> typing.Optional[str]:
        return self.getenv()

    def getenv(self, default: typing.Optional[T] = None) -> typing.Optional[T | str]:
        return os.getenv(key=self.name, default=default)

    def must(self) -> str:
        value = self.getenv()
        if not value:
            raise ValueError(f"could not get variable from env: {self.name}")
        return value


class Predefined(VarEnum, enum.Enum):
    CHAT_CHANNEL = enum.auto()
    "The Source chat channel that triggered the ChatOps command."
    "Availability: Pipeline"

    CHAT_INPUT = enum.auto()
    "The additional arguments passed with the ChatOps command."
    "Availability: Pipeline"

    CHAT_USER_ID = enum.auto()
    "The chat service’s user ID of the user who triggered the ChatOps command."
    "Availability: Pipeline"

    CI = enum.auto()
    "Available for all jobs executed in CI/CD. true when available."
    "Availability: Pre-pipeline"

    CI_API_V4_URL = enum.auto()
    "The GitLab API v4 root URL."
    "Availability: Pre-pipeline"

    CI_API_GRAPHQL_URL = enum.auto()
    "The GitLab API GraphQL root URL."
    "Availability: Pre-pipeline"

    CI_BUILD_NETWORK_NAME = enum.auto()
    "The name of the network that the job created. Available only with the Docker executor when FF_NETWORK_PER_BUILD "
    "is enabled."
    "Availability: Job-only"

    CI_BUILDS_DIR = enum.auto()
    "The top-level directory where builds are executed."
    "Availability: Job-only"

    CI_COMMIT_AUTHOR = enum.auto()
    "The author of the commit in Name <email> format."
    "Availability: Pre-pipeline"

    CI_COMMIT_BEFORE_SHA = enum.auto()
    "The previous latest commit present on a branch or tag. It is always 0000000000000000000000000000000000000000 for "
    "merge request pipelines, scheduled pipelines, the first commit in pipelines for branches or tags, "
    "or when manually running a pipeline."
    "Availability: Pre-pipeline"

    CI_COMMIT_BRANCH = enum.auto()
    "The commit branch name. Available in branch pipelines, including pipelines for the default branch. "
    "Not available in merge request pipelines or tag pipelines."
    "Availability: Pre-pipeline"

    CI_COMMIT_DEFAULT_BRANCH_BASE_SHA = enum.auto()
    "The merge base between CI_COMMIT_SHA and the default branch. Available only in non-default branch pipelines. "
    "Introduced in GitLab 19.1."
    "Availability: Pre-pipeline"

    CI_COMMIT_DESCRIPTION = enum.auto()
    "The description of the commit. If the title is shorter than 100 characters, the description is the "
    "message without the first line."
    "Availability: Pre-pipeline"

    CI_COMMIT_MESSAGE = enum.auto()
    "The full commit message."
    "Availability: Pre-pipeline"

    CI_COMMIT_MESSAGE_IS_TRUNCATED = enum.auto()
    "true if CI_COMMIT_MESSAGE is truncated to the size specified in the GITLAB_CI_MAX_COMMIT_MESSAGE_SIZE_IN_BYTES "
    "system environment variable (default 100 KB) because the commit message is too long. Otherwise false. "
    "Introduced in GitLab 18.6."
    "Availability: Pre-pipeline"

    CI_COMMIT_REF_NAME = enum.auto()
    "The branch or tag name for which project is built."
    "Availability: Pre-pipeline"

    CI_COMMIT_REF_PROTECTED = enum.auto()
    "true if the job is running for a protected reference, false otherwise."
    "Availability: Pre-pipeline"

    CI_COMMIT_REF_SLUG = enum.auto()
    "CI_COMMIT_REF_NAME in lowercase, shortened to 63 bytes, and with everything except 0-9 and a-z replaced "
    "with -. No leading / trailing -. Use in URLs, host names and domain names."
    "Availability: Pre-pipeline"

    CI_COMMIT_SHA = enum.auto()
    "The commit revision the project is built for."
    "Availability: Pre-pipeline"

    CI_COMMIT_SHORT_SHA = enum.auto()
    "The first eight characters of CI_COMMIT_SHA."
    "Availability: Pre-pipeline"

    CI_COMMIT_TAG = enum.auto()
    "The commit tag name. Available only in pipelines for tags."
    "Availability: Pre-pipeline"

    CI_COMMIT_TAG_MESSAGE = enum.auto()
    "The commit tag message. Available only in pipelines for tags."
    "Availability: Pre-pipeline"

    CI_COMMIT_TIMESTAMP = enum.auto()
    "The timestamp of the commit in the ISO 8601 format. For example, 2022-01-31T16:47:55Z. UTC by default."
    "Availability: Pre-pipeline"

    CI_COMMIT_TITLE = enum.auto()
    "The title of the commit. The full first line of the message."
    "Availability: Pre-pipeline"

    CI_COMMIT_USER_LOGIN = enum.auto()
    "The GitLab username of the commit author if the author’s profile and email are public and match the commit email, "
    "otherwise an empty string. Introduced in GitLab 18.10."
    "Availability: Pre-pipeline"

    CI_CONCURRENT_ID = enum.auto()
    "The unique ID of build execution in a single executor."
    "Availability: Job-only"

    CI_CONCURRENT_PROJECT_ID = enum.auto()
    "The unique ID of build execution in a single executor and project."
    "Availability: Job-only"

    CI_CONFIG_PATH = enum.auto()
    "The path to the CI/CD configuration file. Defaults to .gitlab-ci.yml."
    "Availability: Pre-pipeline"

    CI_CONFIG_REF_URI = enum.auto()
    "The fully qualified ref path to the top-level pipeline definition, for example "
    "gitlab.example.com/my-group/my-project//.gitlab-ci.yml@refs/heads/main. "
    "Not available when the pipeline source ref cannot be determined. Introduced in GitLab 19.0."
    "Availability: Pipeline"

    CI_DEBUG_TRACE = enum.auto()
    "true if debug logging (tracing) is enabled."
    "Availability: Pipeline"

    CI_DEBUG_SERVICES = enum.auto()
    "true if service container logging is enabled."
    "Availability: Pipeline"

    CI_DEFAULT_BRANCH = enum.auto()
    "The name of the project’s default branch."
    "Availability: Pre-pipeline"

    CI_DEFAULT_BRANCH_SLUG = enum.auto()
    "CI_DEFAULT_BRANCH in lowercase, shortened to 63 bytes, and with everything except 0-9 and a-z replaced "
    "with -. No leading / trailing -."
    "Availability: Pre-pipeline"

    CI_DEPENDENCY_PROXY_DIRECT_GROUP_IMAGE_PREFIX = enum.auto()
    "The direct group image prefix for pulling images through the Dependency Proxy."
    "Availability: Pre-pipeline"

    CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX = enum.auto()
    "The top-level group image prefix for pulling images through the Dependency Proxy."
    "Availability: Pre-pipeline"

    CI_DEPENDENCY_PROXY_PASSWORD = enum.auto()
    "The password to pull images through the Dependency Proxy."
    "Availability: Pipeline"

    CI_DEPENDENCY_PROXY_SERVER = enum.auto()
    "The server for logging in to the Dependency Proxy. This variable is equivalent to $CI_SERVER_HOST:$CI_SERVER_PORT."
    "Availability: Pre-pipeline"

    CI_DEPENDENCY_PROXY_USER = enum.auto()
    "The username to pull images through the Dependency Proxy."
    "Availability: Pipeline"

    CI_DEPLOY_FREEZE = enum.auto()
    "Only available if the pipeline runs during a deploy freeze window. true when available."
    "Availability: Pre-pipeline"

    CI_DEPLOY_PASSWORD = enum.auto()
    "The authentication password of the GitLab Deploy Token, if the project has one."
    "Availability: Job-only"

    CI_DEPLOY_USER = enum.auto()
    "The authentication username of the GitLab Deploy Token, if the project has one."
    "Availability: Job-only"

    CI_DISPOSABLE_ENVIRONMENT = enum.auto()
    "Only available if the job is executed in a disposable environment (something that is created only for this "
    "job and disposed of/destroyed after the execution - all executors except shell and ssh). true when available."
    "Availability: Pipeline"

    CI_ENVIRONMENT_ID = enum.auto()
    "The ID of the environment for this job. Available if environment:name is set."
    "Availability: Pipeline"

    CI_ENVIRONMENT_NAME = enum.auto()
    "The name of the environment for this job. Available if environment:name is set."
    "Availability: Pipeline"

    CI_ENVIRONMENT_SLUG = enum.auto()
    "The simplified version of the environment name, suitable for inclusion in DNS, URLs, Kubernetes labels, "
    "and so on. Available if environment:name is set. The slug is truncated to 24 characters. "
    "A random suffix is automatically added to uppercase environment names."
    "Availability: Pipeline"

    CI_ENVIRONMENT_URL = enum.auto()
    "The URL of the environment for this job. Available if environment:url is set."
    "Availability: Pipeline"

    CI_ENVIRONMENT_ACTION = enum.auto()
    "The action annotation specified for this job’s environment. Available if environment:action is set. Can be start, "
    "prepare, or stop."
    "Availability: Pipeline"

    CI_ENVIRONMENT_TIER = enum.auto()
    "The deployment tier of the environment for this job."
    "Availability: Pipeline"

    CI_GITLAB_FIPS_MODE = enum.auto()
    "Only available if FIPS mode is enabled in the GitLab instance. true when available."
    "Availability: Pre-pipeline"

    CI_HAS_OPEN_REQUIREMENTS = enum.auto()
    "Only available if the pipeline’s project has an open requirement. true when available."
    "Availability: Pipeline"

    CI_JOB_GROUP_NAME = enum.auto()
    "The shared name of a group of jobs, when using either parallel or manually grouped jobs. For example, if the job "
    "name is rspec:test: [ruby, ubuntu], the CI_JOB_GROUP_NAME is rspec:test. It is the same as CI_JOB_NAME otherwise. "
    "Introduced in GitLab 17.10."
    "Availability: Pipeline"

    CI_JOB_ID = enum.auto()
    "The internal ID of the job, unique across all jobs in the GitLab instance."
    "Availability: Job-only"

    CI_JOB_IMAGE = enum.auto()
    "The name of the Docker image running the job. Only available when the job explicitly specifies a Docker image."
    "Availability: Job-only"

    CI_JOB_MANUAL = enum.auto()
    "Only available if the job was started manually. true when available."
    "Availability: Pipeline"

    CI_JOB_NAME = enum.auto()
    "The name of the job."
    "Availability: Pipeline"

    CI_JOB_NAME_SLUG = enum.auto()
    "CI_JOB_NAME in lowercase, shortened to 63 bytes, and with everything except 0-9 and a-z replaced "
    "with -. No leading / trailing -. Use in paths."
    "Availability: Pipeline"

    CI_JOB_STAGE = enum.auto()
    "The name of the job’s stage."
    "Availability: Pipeline"

    CI_JOB_STATUS = enum.auto()
    "The status of the job as each runner stage is executed. Use with after_script. "
    "Can be success, failed, or canceled."
    "Availability: Job-only"

    CI_JOB_TAGS = enum.auto()
    'A JSON array of the job’s runner tags. For example ["tag_1", "tag_2"]. Introduced in GitLab 19.3.'
    "Availability: Job-only"

    CI_JOB_TIMEOUT = enum.auto()
    "The job timeout, in seconds."
    "Availability: Job-only"

    CI_JOB_TOKEN = enum.auto()
    "A token to authenticate with certain API endpoints. The token is valid as long as the job is running."
    "Availability: Job-only"

    CI_JOB_URL = enum.auto()
    "The job details URL."
    "Availability: Job-only"

    CI_JOB_STARTED_AT = enum.auto()
    "The date and time when a job started, in ISO 8601 format. For example, 2022-01-31T16:47:55Z. UTC by default."
    "Availability: Job-only"

    CI_JOB_STARTED_AT_SLUG = enum.auto()
    "CI_JOB_STARTED_AT in lowercase, shortened to 63 characters, and with everything except 0-9 and a-z replaced "
    "with -. No leading / trailing -. Suitable for use in Docker image tags and other identifiers."
    "Availability: Job-only"

    CI_KUBERNETES_ACTIVE = enum.auto()
    "Only available if the pipeline has a Kubernetes cluster available for deployments. true when available."
    "Availability: Pre-pipeline"

    CI_NODE_INDEX = enum.auto()
    "The index of the job in the job set. Only available if the job uses parallel."
    "Availability: Pipeline"

    CI_NODE_TOTAL = enum.auto()
    "The total number of instances of this job running in parallel. Set to 1 if the job does not use parallel."
    "Availability: Pipeline"

    CI_OPEN_MERGE_REQUESTS = enum.auto()
    "A comma-separated list of up to four merge requests that use the current branch and project as the merge request "
    "source. Only available in branch and merge request pipelines if the branch has an associated merge request. "
    "For example, gitlab-org/gitlab!333,gitlab-org/gitlab-foss!11."
    "Availability: Pre-pipeline"

    CI_PAGES_DOMAIN = enum.auto()
    "The instance’s domain that hosts GitLab Pages, not including the namespace subdomain. To use the full hostname, "
    "use CI_PAGES_HOSTNAME instead."
    "Availability: Pre-pipeline"

    CI_PAGES_HOSTNAME = enum.auto()
    "The full hostname of the Pages deployment."
    "Availability: Job-only"

    CI_PAGES_URL = enum.auto()
    "The URL for a GitLab Pages site. Always a subdomain of CI_PAGES_DOMAIN. In GitLab 17.9 and later, the value "
    "includes the path_prefix when one is specified."
    "Availability: Job-only"

    CI_PIPELINE_ID = enum.auto()
    "The instance-level ID of the current pipeline. This ID is unique across all projects on the GitLab instance."
    "Availability: Job-only"

    CI_PIPELINE_IID = enum.auto()
    "The project-level IID (internal ID) of the current pipeline. This ID is unique only in the current project."
    "Availability: Pipeline"

    CI_PIPELINE_SOURCE = enum.auto()
    "How the pipeline was triggered. The value can be one of the pipeline sources."
    "Availability: Pre-pipeline"

    CI_PIPELINE_TRIGGERED = enum.auto()
    "true for pipelines triggered with a trigger token. For pipelines triggered with the trigger keyword, "
    "use CI_PIPELINE_SOURCE instead."
    "Availability: Pipeline"

    CI_PIPELINE_URL = enum.auto()
    "The URL for the pipeline details."
    "Availability: Job-only"

    CI_PIPELINE_CREATED_AT = enum.auto()
    "The date and time when the pipeline was created, in ISO 8601 format. For example, 2022-01-31T16:47:55Z. "
    "UTC by default."
    "Availability: Job-only"

    CI_PIPELINE_NAME = enum.auto()
    "The pipeline name defined in workflow:name."
    "Availability: Pre-pipeline"

    CI_PIPELINE_SCHEDULE_DESCRIPTION = enum.auto()
    "The description of the pipeline schedule. Only available in scheduled pipelines. Introduced in GitLab 17.8."
    "Availability: Pre-pipeline"

    CI_PROJECT_DIR = enum.auto()
    "The full path the repository is cloned to, and where the job runs from. If the GitLab Runner builds_dir parameter "
    "is set, this variable is set relative to the value of builds_dir. "
    "For more information, see the Advanced GitLab Runner configuration."
    "Availability: Job-only"

    CI_PROJECT_ID = enum.auto()
    "The ID of the current project. This ID is unique across all projects on the GitLab instance."
    "Availability: Pre-pipeline"

    CI_PROJECT_NAME = enum.auto()
    "The name of the directory for the project. For example if the project URL is "
    "gitlab.example.com/group-name/project-1, CI_PROJECT_NAME is project-1."
    "Availability: Pre-pipeline"

    CI_PROJECT_NAMESPACE = enum.auto()
    "The project namespace (username or group name) of the job."
    "Availability: Pre-pipeline"

    CI_PROJECT_NAMESPACE_ID = enum.auto()
    "The project namespace ID of the job."
    "Availability: Pre-pipeline"

    CI_PROJECT_NAMESPACE_SLUG = enum.auto()
    "$CI_PROJECT_NAMESPACE in lowercase, shortened to 63 characters, and with everything except 0-9 and a-z replaced "
    " with -. No leading / trailing -."
    "Availability: Pre-pipeline"

    CI_PROJECT_PATH_SLUG = enum.auto()
    "$CI_PROJECT_PATH in lowercase, shortened to 63 characters, and with everything except 0-9 and a-z replaced with -."
    " No leading / trailing -. Use in URLs and domain names."
    "Availability: Pre-pipeline"

    CI_PROJECT_PATH = enum.auto()
    "The project namespace with the project name included."
    "Availability: Pre-pipeline"

    CI_PROJECT_REPOSITORY_LANGUAGES = enum.auto()
    "A comma-separated, lowercase list of the languages used in the repository. For example ruby,javascript,html,css. "
    "The maximum number of languages is limited to 5. An issue proposes to increase the limit."
    "Availability: Pre-pipeline"

    CI_PROJECT_ROOT_NAMESPACE = enum.auto()
    "The root project namespace (username or group name) of the job. For example, if CI_PROJECT_NAMESPACE is "
    "root-group/child-group/grandchild-group, CI_PROJECT_ROOT_NAMESPACE is root-group."
    "Availability: Pre-pipeline"

    CI_PROJECT_ROOT_NAMESPACE_SLUG = enum.auto()
    "$CI_PROJECT_ROOT_NAMESPACE in lowercase, shortened to 63 characters, and with everything except 0-9 and a-z "
    "replaced with -. No leading / trailing -. Introduced in GitLab 19.0."
    "Availability: Pre-pipeline"

    CI_PROJECT_TITLE = enum.auto()
    "The human-readable project name as displayed in the GitLab web interface."
    "Availability: Pre-pipeline"

    CI_PROJECT_DESCRIPTION = enum.auto()
    "The project description as displayed in the GitLab web interface."
    "Availability: Pre-pipeline"

    CI_PROJECT_TOPICS = enum.auto()
    "A comma-separated, lowercase list of topics (limited to the first 20) assigned to the project. "
    "Introduced in GitLab 18.3"
    "Availability: Pre-pipeline"

    CI_PROJECT_URL = enum.auto()
    "The HTTP(S) address of the project."
    "Availability: Pre-pipeline"

    CI_PROJECT_VISIBILITY = enum.auto()
    "The project visibility. Can be internal, private, or public."
    "Availability: Pre-pipeline"

    CI_PROJECT_CLASSIFICATION_LABEL = enum.auto()
    "The project external authorization classification label."
    "Availability: Pre-pipeline"

    CI_REGISTRY = enum.auto()
    "Address of the container registry server, formatted as <host>[:<port>]. For example: registry.gitlab.example.com. "
    "Only available if the container registry is enabled for the GitLab instance."
    "Availability: Pre-pipeline"

    CI_REGISTRY_IMAGE = enum.auto()
    "Base address for the container registry to push, pull, or tag project’s images, formatted as "
    "<host>[:<port>]/<project_full_path>. For example: registry.gitlab.example.com/my_group/my_project. "
    "Image names must follow the container registry naming convention. Only available if the container "
    "registry is enabled for the project."
    "Availability: Pre-pipeline"

    CI_REGISTRY_PASSWORD = enum.auto()
    "The password to push containers to the GitLab project’s container registry. Only available if the container "
    "registry is enabled for the project. This password value is the same as the CI_JOB_TOKEN and is valid only as "
    "long as the job is running. Use the CI_DEPLOY_PASSWORD for long-lived access to the registry"
    "Availability: Job-only"

    CI_REGISTRY_USER = enum.auto()
    "The username to push containers to the GitLab project’s container registry. Only available if the container "
    "registry is enabled for the project."
    "Availability: Job-only"

    CI_RELEASE_DESCRIPTION = enum.auto()
    "The description of the release. Available only on pipelines for tags. Description length is limited to first 1024 "
    "characters."
    "Availability: Pipeline"

    CI_REPOSITORY_URL = enum.auto()
    "The full path to Git clone (HTTP) the repository with a CI/CD job token, in the format https://gitlab-ci-token:$CI_JOB_TOKEN@gitlab.example.com/my-group/my-project.git."
    "Availability: Job-only"

    CI_RUNNER_DESCRIPTION = enum.auto()
    "The description of the runner."
    "Availability: Job-only"

    CI_RUNNER_EXECUTABLE_ARCH = enum.auto()
    "The OS/architecture of the GitLab Runner executable. Might not be the same as the environment of the executor."
    "Availability: Job-only"

    CI_RUNNER_ID = enum.auto()
    "The unique ID of the runner being used."
    "Availability: Job-only"

    CI_RUNNER_REVISION = enum.auto()
    "The revision of the runner running the job."
    "Availability: Job-only"

    CI_RUNNER_SHORT_TOKEN = enum.auto()
    "The runner’s unique ID, used to authenticate new job requests. The token contains a prefix, and the first 17 "
    "characters are used."
    "Availability: Job-only"

    CI_RUNNER_TAGS = enum.auto()
    'A JSON array of the runner tags configured on the runner that picked up the job. For example ["tag_1", "tag_2"].'
    "Availability: Job-only"

    CI_RUNNER_VERSION = enum.auto()
    "The version of the GitLab Runner running the job."
    "Availability: Job-only"

    CI_SERVER_FQDN = enum.auto()
    "The fully qualified domain name (FQDN) of the instance. For example gitlab.example.com:8080."
    "Availability: Pre-pipeline"

    CI_SERVER_HOST = enum.auto()
    "The host of the GitLab instance URL, without protocol or port. For example gitlab.example.com."
    "Availability: Pre-pipeline"

    CI_SERVER_NAME = enum.auto()
    "The name of CI/CD server that coordinates jobs."
    "Availability: Pre-pipeline"

    CI_SERVER_PORT = enum.auto()
    "The port of the GitLab instance URL, without host or protocol. For example 8080."
    "Availability: Pre-pipeline"

    CI_SERVER_PROTOCOL = enum.auto()
    "The protocol of the GitLab instance URL, without host or port. For example https."
    "Availability: Pre-pipeline"

    CI_SERVER_SHELL_SSH_HOST = enum.auto()
    "The SSH host of the GitLab instance, used for access to Git repositories through SSH. For example gitlab.com."
    "Availability: Pre-pipeline"

    CI_SERVER_SHELL_SSH_PORT = enum.auto()
    "The SSH port of the GitLab instance. For example 22."
    "Availability: Pre-pipeline"

    CI_SERVER_REVISION = enum.auto()
    "GitLab revision that schedules jobs."
    "Availability: Pre-pipeline"

    CI_SERVER_TLS_CA_FILE = enum.auto()
    "File containing the TLS CA certificate to verify the GitLab server when tls-ca-file set in runner settings."
    "Availability: Pipeline"

    CI_SERVER_TLS_CERT_FILE = enum.auto()
    "File containing the TLS certificate to verify the GitLab server when tls-cert-file set in runner settings."
    "Availability: Pipeline"

    CI_SERVER_TLS_KEY_FILE = enum.auto()
    "File containing the TLS key to verify the GitLab server when tls-key-file set in runner settings."
    "Availability: Pipeline"

    CI_SERVER_URL = enum.auto()
    "The base URL of the GitLab instance, including protocol and port. For example https://gitlab.example.com:8080."
    "Availability: Pre-pipeline"

    CI_SERVER_VERSION_MAJOR = enum.auto()
    "The major version of the GitLab instance. For example, if the GitLab version is 17.2.1, "
    "the CI_SERVER_VERSION_MAJOR is 17."
    "Availability: Pre-pipeline"

    CI_SERVER_VERSION_MINOR = enum.auto()
    "The minor version of the GitLab instance. For example, if the GitLab version is 17.2.1, "
    "the CI_SERVER_VERSION_MINOR is 2."
    "Availability: Pre-pipeline"

    CI_SERVER_VERSION_PATCH = enum.auto()
    "The patch version of the GitLab instance. For example, if the GitLab version is 17.2.1, "
    "the CI_SERVER_VERSION_PATCH is 1."
    "Availability: Pre-pipeline"

    CI_SERVER_VERSION = enum.auto()
    "The full version of the GitLab instance."
    "Availability: Pre-pipeline"

    CI_SERVER = enum.auto()
    "Available for all jobs executed in CI/CD. yes when available."
    "Availability: Job-only"

    CI_SHARED_ENVIRONMENT = enum.auto()
    "Only available if the job is executed in a shared environment (something that is persisted across CI/CD "
    "invocations, like the shell or ssh executor). true when available."
    "Availability: Pipeline"

    CI_TEMPLATE_REGISTRY_HOST = enum.auto()
    "The host of the registry used by CI/CD templates. Defaults to registry.gitlab.com."
    "Availability: Pre-pipeline"

    CI_TRIGGER_SHORT_TOKEN = enum.auto()
    "First 4 characters of the trigger token of the current job. Only available if the pipeline was triggered with a "
    "trigger token. For example, for a trigger token of glptt-1234567890abcdefghij, "
    "CI_TRIGGER_SHORT_TOKEN would be 1234. Introduced in GitLab 17.0."
    "Availability: Job-only"

    CI_UPSTREAM_JOB_ID = enum.auto()
    "ID of the upstream trigger job that triggered the current pipeline in a multi-project or parent-child pipeline. "
    "Introduced in GitLab 18.9."
    "Availability: Pre-pipeline"

    CI_UPSTREAM_PIPELINE_ID = enum.auto()
    "ID of the upstream pipeline that triggered the current pipeline in a multi-project or parent-child pipeline. "
    "Introduced in GitLab 18.9."
    "Availability: Pre-pipeline"

    CI_UPSTREAM_PROJECT_ID = enum.auto()
    "ID of the upstream project that triggered the current pipeline in a multi-project or parent-child pipeline. "
    "Introduced in GitLab 18.9."
    "Availability: Pre-pipeline"

    CI_TRACEPARENT = enum.auto()
    "A W3C Trace Context traceparent header value for the job, in the format 00-<trace_id>-<span_id>-01. The trace_id "
    "is the root pipeline ID as a zero-padded 32-character hex string, shared by all jobs in the same pipeline  "
    "hierarchy, including parent and child pipelines. The span_id is a deterministic hash derived from the root "
    "pipeline ID and job ID, unique per job. You can use this variable to correlate CI/CD jobs with external "
    "distributed tracing systems."
    "Availability: Job-only"

    CI_TRACESTATE = enum.auto()
    "A W3C Trace Context tracestate header value containing GitLab-specific trace metadata. "
    "Format: gitlab=pipeline:<pipeline_id>;job:<job_id>."
    "Availability: Job-only"

    GITLAB_CI = enum.auto()
    "Available for all jobs executed in CI/CD. true when available."
    "Availability: Pre-pipeline"

    GITLAB_FEATURES = enum.auto()
    "The comma-separated list of licensed features available for the GitLab instance and license."
    "Availability: Pre-pipeline"

    GITLAB_USER_EMAIL = enum.auto()
    "The email of the user who started the pipeline, unless the job is a manual job. In manual jobs, "
    "the value is the email of the user who started the job."
    "Availability: Pipeline"

    GITLAB_USER_ID = enum.auto()
    "The numeric ID of the user who started the pipeline, unless the job is a manual job. In manual jobs, "
    "the value is the ID of the user who started the job."
    "Availability: Pipeline"

    GITLAB_USER_LOGIN = enum.auto()
    "The unique username of the user who started the pipeline, unless the job is a manual job. In manual jobs, "
    "the value is the username of the user who started the job."
    "Availability: Pipeline"

    GITLAB_USER_NAME = enum.auto()
    "The display name (user-defined Full name in the profile settings) of the user who started the pipeline, "
    "unless the job is a manual job. In manual jobs, the value is the name of the user who started the job."
    "Availability: Pipeline"

    KUBECONFIG = enum.auto()
    "The path to the kubeconfig file with contexts for every shared agent connection. "
    "Only available when a GitLab agent for Kubernetes is authorized to access the project."
    "Availability: Pipeline"

    TRIGGER_PAYLOAD = enum.auto()
    "The webhook payload. Only available when a pipeline is triggered with a webhook."
    "Availability: Pipeline"

    CI_JOB_JWT = enum.auto()


class PredefinedMergeRequest(VarEnum, enum.Enum):
    CI_MERGE_REQUEST_APPROVED = enum.auto()
    "Approval status of the merge request. true when merge request approvals is available and "
    "the merge request has been approved."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_ASSIGNEES = enum.auto()
    "Comma-separated list of usernames of assignees for the merge request. "
    "Only available if the merge request has at least one assignee."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_DIFF_BASE_SHA = enum.auto()
    "The base SHA of the merge request diff."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_DIFF_ID = enum.auto()
    "The version of the merge request diff."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_EVENT_TYPE = enum.auto()
    "The event type of the merge request. Can be detached, merged_result or merge_train."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_DESCRIPTION = enum.auto()
    "The description of the merge request. If the description is more than 2700 characters long, "
    "only the first 2700 characters are stored in the variable."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_DESCRIPTION_IS_TRUNCATED = enum.auto()
    "true if CI_MERGE_REQUEST_DESCRIPTION is truncated down to 2700 characters "
    "because the description of the merge request is too long, otherwise false."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_ID = enum.auto()
    "The instance-level ID of the merge request. The ID is unique across all projects on the GitLab instance."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_IID = enum.auto()
    "The project-level IID (internal ID) of the merge request. This ID is unique for the current project, "
    "and is the number used in the merge request URL, page title, and other visible locations."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_LABELS = enum.auto()
    "Comma-separated label names of the merge request. Only available if the merge request has at least one label."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_MILESTONE = enum.auto()
    "The milestone title of the merge request. Only available if the merge request has a milestone set."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_PROJECT_ID = enum.auto()
    "The ID of the project of the merge request."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_PROJECT_PATH = enum.auto()
    "The path of the project of the merge request. For example namespace/awesome-project."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_PROJECT_URL = enum.auto()
    "The URL of the project of the merge request. For example, http://192.168.10.15:3000/namespace/awesome-project."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_REF_PATH = enum.auto()
    "The ref path of the merge request. For example, refs/merge-requests/1/head."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_SOURCE_BRANCH_NAME = enum.auto()
    "The source branch name of the merge request."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_SOURCE_BRANCH_PROTECTED = enum.auto()
    "true when the source branch of the merge request is protected."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_SOURCE_BRANCH_SHA = enum.auto()
    "The HEAD SHA of the source branch of the merge request. The variable is empty in merge request pipelines. "
    "The SHA is present only in merged results pipelines."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_SOURCE_PROJECT_ID = enum.auto()
    "The ID of the source project of the merge request."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_SOURCE_PROJECT_PATH = enum.auto()
    "The path of the source project of the merge request."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_SOURCE_PROJECT_URL = enum.auto()
    "The URL of the source project of the merge request."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_SQUASH_ON_MERGE = enum.auto()
    "true when the squash on merge option is set."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_TARGET_BRANCH_NAME = enum.auto()
    "The target branch name of the merge request."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_TARGET_BRANCH_PROTECTED = enum.auto()
    "true when the target branch of the merge request is protected."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_TARGET_BRANCH_SHA = enum.auto()
    "The HEAD SHA of the target branch of the merge request. The variable is empty in merge request pipelines. "
    "The SHA is present only in merged results pipelines."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_TITLE = enum.auto()
    "The title of the merge request."
    "Availability: Pre-pipeline"

    CI_MERGE_REQUEST_DRAFT = enum.auto()
    "true if the merge request is a draft. Introduced in GitLab 17.10."
    "Availability: Pre-pipeline"


class PredefinedExternalPullRequest(VarEnum, enum.Enum):
    CI_EXTERNAL_PULL_REQUEST_IID = enum.auto()
    "Pull request ID from GitHub."
    "Availability: Pipeline"

    CI_EXTERNAL_PULL_REQUEST_SOURCE_REPOSITORY = enum.auto()
    "The source repository name of the pull request."
    "Availability: Pipeline"

    CI_EXTERNAL_PULL_REQUEST_TARGET_REPOSITORY = enum.auto()
    "The target repository name of the pull request."
    "Availability: Pipeline"

    CI_EXTERNAL_PULL_REQUEST_SOURCE_BRANCH_NAME = enum.auto()
    "The source branch name of the pull request."
    "Availability: Pipeline"

    CI_EXTERNAL_PULL_REQUEST_SOURCE_BRANCH_SHA = enum.auto()
    "The HEAD SHA of the source branch of the pull request."
    "Availability: Pipeline"

    CI_EXTERNAL_PULL_REQUEST_TARGET_BRANCH_NAME = enum.auto()
    "The target branch name of the pull request."
    "Availability: Pipeline"

    CI_EXTERNAL_PULL_REQUEST_TARGET_BRANCH_SHA = enum.auto()
    "The HEAD SHA of the target branch of the pull request."
    "Availability: Pipeline"
