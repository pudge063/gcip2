## Changelog

### [11.08.26 - 0.1.5]
- updated default tasks
- fixed module structure
- changed cli script in module `tasks_core` from `gciptask` to `dothat`
- added all predefined pipeline variables
- added `dothat` argument `help` for describe task params
- added detailed information about task in `dothat help`
- added `doc` field to `Task` model

### [08.08.26 - 0.1.4]
- fixed package `tasks_core` - added `__init__.py`

### [08.08.26 - 0.1.3]
- fixed builder for package

### [08.08.26 - 0.1.2]
- added PyPi proxy for python packages

### [08.08.26 - 0.1.1]
- changed base image replaced to local artifactory
- enabled pipeline timestamps provided by `FF_TIMESTAMPS`
- fixed tag creation

### [04.08.26 - 0.1.0]
- added `Task`, `TaskBuilder` and `TaskBuilderImpl` entities for job task executing
- added `InteractivePythonAction` and `InteractiveShlex` actions
- added `Params` for `Tasks` -> `Actions.impl()`
- added `ProjectConfig` to actions that provide tools like SecretsHandler or Extra values
- added `BaseTask` job template
- added tasks testing pipeline
- added `tasks_core` package with CLI for running tasks
- added `loguru` for logging instead of `builtins.print`
- added `extra.tasks` to `ProjectConfig` with `module` field - path to `_tasks` dir in project
- added `extra.extra_model` convert to `extra__` actions arguments
- added `JobBuilder`, `PipelineBuiler` and `GitlabCiBuilder` without `pydantic.Basemodel`
- changed `model` initialization in `JobBuilderImpl`, `PipelineBuilderImpl`, `GitlabCiBuilderImpl`
- added `docker-compose.yml` with base images and `with_compose_image` method for `JobBuilderImpl`
- added diff on pipeline generation
- fixed pipeline and gitlab-ci paths params
- added `ruff` instead of `black`, `isort`, `mypy`
- migrated from `poetry` to `uv`

### [02.08.26 - 0.0.12]
- added readme to package

### [02.08.26 - 0.0.11]
- added `create_tag` status checks
- added check version in `environment.toml` - `extra.version` field
- for `Extra` in `ProjectConfig` added methods `get` and `__getitem__`
- for `Extra` added `model_config` with allowed `extra` fields


### [02.08.26 - 0.0.10]
- added `initialization` test pipeline
- init empty `ProjectConfig` model if not found `environment.toml` instead of failure

### [02.08.26 - 0.0.9]
- added SecretsHandler and Vault modules for secrets
- added ProjectConfig with `extra` and `secrets` sections and models
- added `secrets.vault` section with approle and jwks auth methods
- removed API requests to Vault from jobs `create-version-tag` and `publish`

### [02.08.26 - 0.0.8]
- added unit-tests with pipeline module coverage ~70%
- added unit-tests with job module coverage ~ 65%
- added integration tests with golden pipeline templates
- added junit reports and pytest coverage reports
- redesigned pipeline for main package - split jobs by stages
- added `VERSION` file which one checks on tag publish
- added pipeline_core.Artifacts fields: expire_in, name, public, access, reports, untracked, when
- fixed JobBuilderImpl default apply - now it returns `self` instead of `None`
- added to JobBuilderImpl helpers: add_to_name, with_script, with_before_script, with_after_script, add_to_script
- added fields and validation to JobBuilderImpl `with_artifacts` helper
- fixed pre-commit colors in CI by flag `--color=always`
- fixed section in BaseLinux before_script and after scripts - sections had same names before fix
- added to PipelineBuilderImpl helper `add_jobs`
- added version check and create tag on default branch pipeline

### [30.07.26 - 0.0.7]
- fixed publish job
- fixed .gitignore in initialization

### [30.07.26 - 0.0.6]
- added py.typed

### [30.07.26 - 0.0.5]
- added base project structure initialization with `gcip2 init`
- added base predefined CI variables for pipelines
- added pytest and integration regression tests with golden pipelines
- removed apply method from JobBuilderImpl on build
- removed duplicate of PipelineBuilderImpl
- updated documentation
- fixed some bugs and errors

### [28.07.26 - 0.0.4]
- added GitlabCiBuilderImpl
- added BaseLinux and _base param for JobBuilderImpl
- changed base tags from `immortal` to `static-k8s`

### [31.05.26 - 0.0.3]
- removed pipeline annotation
- fixed workflow for gitlab-ci and pipeline

### [31.05.26 - 0.0.2]
- added JobbuilderImpl and PipelineBuilderImpl
- updated CI schema
