## Changelog

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
