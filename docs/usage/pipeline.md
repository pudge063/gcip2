# Pipelines

A pipeline is defined in Python and rendered to YAML at build time. A project normally
has two entry points in `ci.py`:

| Builder | Produces |
|---|---|
| `PipelineBuilderImpl` | `out/pipeline.gitlab-ci.yml` — the child pipeline with the actual jobs |
| `GitlabCiBuilderImpl` | `.gitlab-ci.yml` — the repository root, which triggers the child |

## Jobs

A job inherits from `JobBuilderImpl` and configures the underlying `Job` model in
`apply()`:

```python
class PreCommit(JobBuilderImpl):
    _name = "pre-commit"
    _base = base.BaseLinux

    def apply(self):
        self.model.script = ["pre-commit run -av"]
        return self.with_stage(Stages.PRE_COMMIT)
```

`_name` sets the job name in the generated YAML. `_base` inherits configuration from
another builder — here `BaseLinux`, which supplies the shared `before_script` and
`after_script`. Values set by the job itself win over those from its base.

Jobs are created by `self.job()`, never by calling the class directly:

```python
self.job(PreCommit).apply()
```

That is what gives a job `self._config`, the script assets, and everything else supplied
by the container. See [Dependency injection](di.md).

Since the configuration is available, jobs can be generated from it:

```python
class UnitTests(JobBuilderImpl):
    _base = base.BasePython

    def apply(self):
        for module in self._config.extra.get("tests", {}).get("unit-tests", []):
            ...
```

Images are referenced by name from the project's compose file rather than hard-coded:

```python
self.with_compose_image("base_python")
```

## Building a pipeline

```python
class Stages(str, Enum):
    PRE_COMMIT = "pre-commit"


class Pipeline(PipelineBuilderImpl):
    def apply(self):
        self.model.stages = [Stages.PRE_COMMIT]
        self.add_jobs((self.job(PreCommit).apply(),))
        self.with_workflow(workflow)
        return self
```

`build()` fills in anything left unset: a default image taken from the compose file, the
`static-k8s` tag, and a single `jobs` stage. Setting them explicitly overrides those
defaults.

Workflow rules are usually defined once and shared between both builders:

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

A `parent_pipeline` rule is prepended automatically, so a child pipeline is always
allowed to run when triggered by its parent.

## Root configuration

```python
class GitlabCi(GitlabCiBuilderImpl):
    def apply(self):
        super().apply()
        self.with_workflow(workflow)
        return self
```

When this builder declares no jobs, two trigger jobs are added for you: one that builds
the child pipeline and one that triggers it from the resulting artifact.

## Generated output

```yaml
workflow:
  name: default
  rules:
    - if: $CI_PIPELINE_SOURCE == "parent_pipeline"
      when: always
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: always
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: always
    - when: never

stages:
  - pre-commit

default:
  image:
    name: python:3.12
  tags:
    - static-k8s

pre-commit:
  before_script:
    - |
      #!/usr/bin/env sh
      set -o errexit -o nounset -o xtrace
      uv sync
      . ".venv/bin/activate"
  script:
    - pre-commit run -av
  stage: pre-commit
  interruptible: true
```

The `before_script` block comes from `BaseLinux` and is not written in the job
definition.

## Building

```bash
dothat run build-gitlab-ci
dothat run build-pipeline -f pipelines/my-pipeline/ci.py
```

Both commands log a diff against the previous version of the file, so changes to
generated configuration are visible in review.
