## Example: Defining a Pipeline

A pipeline is defined by creating classes that inherit from `PipelineBuilderImpl` and `JobBuilderImpl`. Jobs encapsulate reusable CI logic, while the pipeline builder assembles them into a complete GitLab pipeline.

### Define stages

Stages can be represented as an `Enum` for type safety:

```python
class Stages(str, Enum):
    PRE_COMMIT = "pre-commit"
```

### Define a job

Jobs inherit from `JobBuilderImpl` and implement the `apply()` method to configure the underlying `Job` model.

```python
class PreCommit(JobBuilderImpl):
    _base = BaseLinux

    def apply(self):
        self.model.name = "pre-commit"
        self.model.script = [
            "ls -la",
            "pre-commit run -av",
        ]
        self.with_stage(Stages.PRE_COMMIT)
        return self
```

The `_base` attribute allows the job to inherit common configuration from another builder (for example, a shared Linux job template).

### Configure the workflow

Pipeline-wide workflow rules are defined once and reused by both the pipeline and the root `.gitlab-ci.yml` builder.

```python
workflow = Workflow(
    name="default",
    rules=[
        WorkflowRule(
            if_='$CI_PIPELINE_SOURCE == "merge_request_event"',
            when=WorkflowWhen.ALWAYS,
        ),
        WorkflowRule(
            if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH",
            when=WorkflowWhen.ALWAYS,
        ),
        WorkflowRule(when=WorkflowWhen.NEVER),
    ],
)
```

### Build the pipeline

A pipeline builder assembles stages, jobs, defaults, variables, and workflow configuration.

```python
class Pipeline(PipelineBuilderImpl):
    def apply(self):
        self.model.stages = [Stages.PRE_COMMIT]

        self.model.jobs.append(self.job(PreCommit).apply())

        self.with_default(
            Default(
                tags=["static-k8s"],
                image=Image(
                    name="python:3.12",
                ),
            )
        )

        self.with_workflow(workflow)

        return self
```

### Build the root GitLab CI configuration

For the repository's root `.gitlab-ci.yml`, inherit from `GitlabCiBuilderImpl`:

```python
class GitlabCi(GitlabCiBuilderImpl):
    def apply(self):
        super().apply()

        self.with_workflow(workflow)

        self.with_default(
            Default(
                tags=["static-k8s"],
                image=Image(name="python:3.12"),
            )
        )

        return self
```

### Generated pipeline

The example above produces a pipeline equivalent to:

```yaml
workflow:
  name: default
  auto_cancel:
    on_job_failure: none
    on_new_commit: none
  rules:
    - if: $CI_PIPELINE_SOURCE == "parent_pipeline"
      when: always
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: always
    - if: $CI_COMMIT_TAG =~ '/^v\d+\.\d+\.\d+$/'
      when: always
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: always
    - when: never

stages:
  - pre-commit

default:
  image:
    name: pfeiffermax/python-poetry:1.17.0-poetry2.2.1-python3.12.12-trixie
  tags:
    - static-k8s

pre-commit:
  before_script:
    - |
      #!/usr/bin/env sh
      set -o errexit -o nounset -o xtrace
      section="$(date +'%s'):setup"
      printf '\e[0Ksection_start:%s[collapsed=true]\r\e[0K%s\n' "${section}" "setup"
      # shellcheck disable=SC2086
      poetry install
      . ".venv/bin/activate"
      printf '\e[0Ksection_end:%s\r\e[0K\n' "${section}"
  after_script:
    - |
      #!/usr/bin/env sh
      set -o errexit -o nounset -o xtrace
      section="$(date +'%s'):setup"
      printf '\e[0Ksection_start:%s[collapsed=true]\r\e[0K%s\n' "${section}" "setup"
      # shellcheck disable=SC2086
      poetry install
      . ".venv/bin/activate"
      printf '\e[0Ksection_end:%s\r\e[0K\n' "${section}"
    - echo Do nothing.
  script:
    - ls -la
    - pre-commit run -av
  stage: pre-commit
  interruptible: true
```

### Build process

A typical project consists of two builder entry points:

* **`Pipeline`** — generates the reusable child pipeline (`pipeline.gitlab-ci.yml`).
* **`GitlabCi`** — generates the repository's root `.gitlab-ci.yml`, configuring trigger jobs and shared pipeline settings.

Both builders share the same typed models and fluent API, making it easy to keep pipeline configuration reusable and consistent.
