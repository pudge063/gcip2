# gcip2

## Information

GitLab DSL framework for generating dynamic pipelines using GitLab components.

## Usage

### Basic Commands

| Command | Description |
|---------|-------------|
| `gcip2 build-gitlab-ci` | Generate parent trigger pipeline file |
| `gcip2 build-pipeline` | Generate child downstream pipeline file |

### build-gitlab-ci Options

Generate file with parent trigger pipeline.

| Option | Description |
|--------|-------------|
| `-t, --ci-tags TEXT` | Tags section for gitlab-ci |
| `-O, --out-gitlab-ci TEXT` | Output file with parent trigger pipeline |

### build-pipeline Options

Generate file with child downstream pipeline.

| Option | Description |
|--------|-------------|
| `-o, --out-pipeline TEXT` | Output file with child downstream pipeline |
| `-f, --ci-file TEXT` | File with source code for pipeline |

### Typical Workflow

1. Generate parent pipeline file with `build-pipeline` and `trigger-pipeline` jobs:
   ```
   gcip2 build-gitlab-ci
   ```

2. The `build-pipeline` job generates the child pipeline (by default at `out/pipeline.gitlab-ci.yml`) based on the configuration defined in `ci.py`.

## Examples

### .gitlab-ci.yml

```
build-pipeline:
  before_script:
    - pip3 install poetry
  script:
    - poetry install && . .venv/bin/activate
    - gcip2 build-pipeline
  tags:
    - immortal
  artifacts:
    paths:
      - out

trigger-pipeline:
  needs:
    - job: build-pipeline
      artifacts: true
  trigger:
    include:
      - job: build-pipeline
        artifact: out/pipeline.gitlab-ci.yml
```

### Generated Pipeline (out/pipeline.gitlab-ci.yml)

```
workflow:
  name: default
  auto_cancel:
    on_job_failure: none
    on_new_commit: none
  rules:
    - if: $CI_DEFAULT_BRANCH == $CI_COMMIT_BRANCH
      variables:
        TEST: '1'

stages:
  - pre-commit
  - build
  - check

default:
  tags:
    - immortal

pre-commit:
  image:
    name: python:3.11
  script:
    - pip3 install poetry
    - poetry install
    - . .venv/bin/activate
    - poetry run pre-commit run -av
  stage: pre-commit

build:arm:
  script:
    - echo PARENT_JOB_ID=$CI_JOB_ID > dotenv.txt
    - mkdir -p out
    - touch out/test_$CI_JOB_ID
  stage: build
  artifacts:
    paths:
      - out/*
      - build/*
      - _build/*
    reports:
      dotenv:
        - dotenv.txt

check:arm:
  script:
    - echo $PARENT_JOB_ID
    - ls -la out
  stage: check
  needs:
    - build:arm

build:amd64:
  script:
    - echo PARENT_JOB_ID=$CI_JOB_ID > dotenv.txt
    - mkdir -p out
    - touch out/test_$CI_JOB_ID
  stage: build
  artifacts:
    paths:
      - out/*
      - build/*
      - _build/*
    reports:
      dotenv:
        - dotenv.txt

check:amd64:
  script:
    - echo $PARENT_JOB_ID
    - ls -la out
  stage: check
  needs:
    - build:amd64

build:dev-441:
  script:
    - echo PARENT_JOB_ID=$CI_JOB_ID > dotenv.txt
    - mkdir -p out
    - touch out/test_$CI_JOB_ID
  stage: build
  artifacts:
    paths:
      - out/*
      - build/*
      - _build/*
    reports:
      dotenv:
        - dotenv.txt

check:dev-441:
  script:
    - echo $PARENT_JOB_ID
    - ls -la out
  stage: check
  needs:
    - build:dev-441

build:dev-442:
  script:
    - echo PARENT_JOB_ID=$CI_JOB_ID > dotenv.txt
    - mkdir -p out
    - touch out/test_$CI_JOB_ID
  stage: build
  artifacts:
    paths:
      - out/*
      - build/*
      - _build/*
    reports:
      dotenv:
        - dotenv.txt

check:dev-442:
  script:
    - echo $PARENT_JOB_ID
    - ls -la out
  stage: check
  needs:
    - build:dev-442

build:dev-443:
  script:
    - echo PARENT_JOB_ID=$CI_JOB_ID > dotenv.txt
    - mkdir -p out
    - touch out/test_$CI_JOB_ID
  stage: build
  artifacts:
    paths:
      - out/*
      - build/*
      - _build/*
    reports:
      dotenv:
        - dotenv.txt

check:dev-443:
  script:
    - echo $PARENT_JOB_ID
    - ls -la out
  stage: check
  needs:
    - build:dev-443

build:dev-313:
  script:
    - echo PARENT_JOB_ID=$CI_JOB_ID > dotenv.txt
    - mkdir -p out
    - touch out/test_$CI_JOB_ID
  stage: build
  artifacts:
    paths:
      - out/*
      - build/*
      - _build/*
    reports:
      dotenv:
        - dotenv.txt

check:dev-313:
  script:
    - echo $PARENT_JOB_ID
    - ls -la out
  stage: check
  needs:
    - build:dev-313
```

### ci.py

```
from typing import Self

from gcip2.pipeline_core import WorkflowAutoCancelOnNewCommit  # type: ignore
from gcip2.pipeline_core import (
    Artifacts,
    ArtifactsReports,
    Default,
    GlobalVariables,
    Image,
    Job,
    JobBuilderImpl,
    JobVariables,
    Needs,
    Pipeline,
    PipelineBuilderImpl,
    Rule,
    RuleChanges,
    Stage,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
)


class PreCommit(JobBuilderImpl):
    def apply(self: Self) -> Self:
        self.model.name = "pre-commit"
        self.model.script = [
            "pip3 install poetry",
            "poetry install",
            ". .venv/bin/activate",
            "poetry run pre-commit run -av",
        ]
        self.with_image(image="python:3.11")
        self.with_stage("pre-commit")
        return self


class Build(JobBuilderImpl):
    def apply(self: Self):
        dotenv_file = "dotenv.txt"

        self.with_stage("build")
        self.model.script = [
            f"echo PARENT_JOB_ID=$CI_JOB_ID > {dotenv_file}",
            "mkdir -p out",
            "touch out/test_$CI_JOB_ID",
        ]
        self.with_artifacts(
            paths=[
                "out/*",
                "build/*",
                "_build/*",
            ],
            reports=ArtifactsReports(dotenv=[dotenv_file]),
        )
        return self


class CheckDotenv(JobBuilderImpl):
    def apply(self: Self):

        self.with_stage("check")
        self.model.script = [
            f"echo $PARENT_JOB_ID",
            "ls -la out",
        ]
        return self


class Ci(PipelineBuilderImpl):
    def _add_build_jobs(self) -> list[Job]:
        platforms = ["arm", "amd64", "dev-441", "dev-442", "dev-443", "dev-313"]

        jobs: list[Job] = []

        for platform in platforms:
            build_job = self.job(Build).apply().with_name(f"build:{platform}")

            check_job = self.job(CheckDotenv).apply().with_name(f"check:{platform}").with_needs([build_job.model.name])

            jobs.extend([build_job, check_job])

        return jobs

    def apply(self: Self) -> Self:
        self.model.jobs.append(self.job(PreCommit).apply().with_stage("pre-commit"))
        self.model.jobs.extend(self._add_build_jobs())
        self.model.stages = ["pre-commit", "build", "check"]
        self.with_workflow(
            Workflow(
                name="default",
                auto_cancel=WorkflowAutoCancel(
                    on_job_failure=WorkflowAutoCancelOnJobFailure.NONE,
                    on_new_commit=WorkflowAutoCancelOnNewCommit.NONE,
                ),
                rules=[
                    Rule(
                        if_="$CI_DEFAULT_BRANCH == $CI_COMMIT_BRANCH",
                        variables={
                            "TEST": "1",
                        },
                    )
                ],
            )
        )
        self.with_default(Default(tags=["immortal"]))
        return self
```

## External Links

- JSON Schema: [https://json-schema.org/draft-07/json-schema-release-notes#keywords](https://json-schema.org/draft-07/json-schema-release-notes#keywords)
- Pipeline Schema: [https://gitlab.com/gitlab-org/gitlab-foss/-/raw/master/app/assets/javascripts/editor/schema/ci.json](https://gitlab.com/gitlab-org/gitlab-foss/-/raw/master/app/assets/javascripts/editor/schema/ci.json)
- GitLab Documentation: [https://docs.gitlab.com/ci/pipeline_editor/#view-full-configuration](https://docs.gitlab.com/ci/pipeline_editor/#view-full-configuration)