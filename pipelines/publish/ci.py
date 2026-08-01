from typing import Self

from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl, Predefined
from gcip2.pipeline_core import (
    Default,
    Image,
    JobBuilderImpl,
    JobRule,
    JobWhen,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    WorkflowAutoCancelOnNewCommit,
    WorkflowRule,
    WorkflowWhen,
)
from gcip2.pipeline_core.jobs.base import BaseLinux


class PublishPackage(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.model.name = "publish-package"

        publish_cmd = "poetry publish"
        publish_cmd += " --dry-run" if not Predefined.CI_COMMIT_TAG.getenv() else ""

        self.model.script = [
            "poetry build",
            "poetry config pypi-token.pypi ${PYPI_TOKEN}",
            publish_cmd,
        ]
        self.model.rules = [
            JobRule(if_="$CI_COMMIT_TAG =~ '/^v\\d+\\.\\d+\\.\\d+$/'"),
            JobRule(when=JobWhen.ALWAYS),
        ]
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
    def apply(self: Self) -> Self:

        self.model.jobs.append(self.job(PublishPackage).apply())

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
