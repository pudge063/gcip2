from enum import Enum
from typing import Self

from gcip2 import Base, BaseLinux, GitlabCiBuilderImpl, PipelineBuilderImpl
from gcip2.pipeline_core import (
    Default,
    Image,
    JobBuilderImpl,
    JobRule,
    JobWhen,
    Trigger,
    TriggerForward,
    TriggerIncludeArtifact,
    TriggerStrategy,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    WorkflowAutoCancelOnNewCommit,
    WorkflowRule,
    WorkflowWhen,
)


class Stages(str, Enum):
    pre_commit = "pre-commit"
    publish = "publish"
    test = "test"


class JobName(str, Enum):
    pre_commit = "pre-commit"
    build_test_pipeline = "build-test-pipeline"
    trigger_test_pipeline = "trigger-test-pipeline"
    publish = "publish"


class PreCommit(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.with_name(JobName.pre_commit.value)
        self.model.script = [
            "pre-commit run -av",
        ]
        self.with_stage(Stages.pre_commit)
        return self


class BuildTestPipeline(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.with_stage(Stages.test)
        self.model.script = [
            "cd gcip2/tests/base_pipeline",
            "gcip2 build-pipeline",
        ]
        self.with_artifacts(["gcip2/tests/base_pipeline/out"])
        return self


class TriggerTestPipeline(JobBuilderImpl):
    _base = Base

    def apply(self: Self) -> Self:
        self.with_stage(Stages.test)

        return self


class PublishPackage(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.model.name = JobName.publish.value
        self.model.script = [
            "poetry build",
            "poetry config pypi-token.pypi ${PYPI_TOKEN}",
            "poetry publish",
        ]
        self.model.rules = [
            JobRule(if_="$CI_COMMIT_TAG =~ '/^v\\d+\\.\\d+\\.\\d+$/'", when=JobWhen.ALWAYS),
            JobRule(when=JobWhen.NEVER),
        ]
        self.with_stage(Stages.publish)
        self.with_when(JobWhen.MANUAL)
        return self


workflow = Workflow(
    name="default",
    auto_cancel=WorkflowAutoCancel(
        on_job_failure=WorkflowAutoCancelOnJobFailure.NONE,
        on_new_commit=WorkflowAutoCancelOnNewCommit.NONE,
    ),
    rules=[
        WorkflowRule(
            if_='$CI_PIPELINE_SOURCE == "merge_request_event"',
            when=WorkflowWhen.ALWAYS,
        ),
        WorkflowRule(
            if_="$CI_COMMIT_TAG =~ '/^v\\d+\\.\\d+\\.\\d+$/'",
            when=WorkflowWhen.ALWAYS,
        ),
        WorkflowRule(
            if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH",
            when=WorkflowWhen.ALWAYS,
        ),
        WorkflowRule(when=WorkflowWhen.NEVER),
    ],
)


class Pipeline(PipelineBuilderImpl):
    def _add_name_suffix(self, job: JobBuilderImpl, suffix: str) -> JobBuilderImpl:
        if not job.model.name:
            raise ValueError("Not found job name.")
        job.model.name = job.model.name + f":{suffix}"
        print(job.model.name)
        return job

    def apply(self: Self) -> Self:
        self.model.stages = [Stages.pre_commit, Stages.publish, Stages.test]

        self.model.jobs.append(self.job(PreCommit).apply())

        for test in ["e1", "e2", "e3", "pipeline", "secrets", "artifacts"]:
            build_test_job = (
                self.job(BuildTestPipeline).apply().with_name(f"{JobName.build_test_pipeline.value}:{test}")
            )
            trigger_test_job = (
                self.job(TriggerTestPipeline)
                .apply()
                .with_name(f"{JobName.trigger_test_pipeline.value}:{test}")
                .with_needs([f"{JobName.build_test_pipeline.value}:{test}"])
            )
            trigger_test_job.model.trigger = Trigger(
                strategy=TriggerStrategy.DEPEND,
                include=[
                    TriggerIncludeArtifact(
                        job=f"{JobName.build_test_pipeline.value}:{test}",
                        artifact="gcip2/tests/base_pipeline/out/pipeline.gitlab-ci.yml",
                    )
                ],
                forward=TriggerForward(yaml_variables=True, pipeline_variables=True),
            )

            self.model.jobs.extend([build_test_job, trigger_test_job])

        self.model.jobs.append(self.job(PublishPackage).apply().with_needs(["pre-commit"]))

        self.with_default(
            Default(
                tags=["static-k8s"],
                image=Image(
                    name="pfeiffermax/python-poetry:1.17.0-poetry2.2.1-python3.12.12-trixie",
                ),
            )
        )
        self.with_workflow(workflow=workflow)

        return self


class GitlabCi(GitlabCiBuilderImpl):
    def apply(self: Self) -> Self:
        super(GitlabCi, self).apply()
        self.with_workflow(workflow=workflow)
        self.with_default(
            Default(
                tags=["static-k8s"],
                image=Image(
                    name="pfeiffermax/python-poetry:1.17.0-poetry2.2.1-python3.12.12-trixie",
                ),
            )
        )
        return self
