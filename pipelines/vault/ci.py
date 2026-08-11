from typing import Self

from _tasks._consts import Tasks
from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl
from gcip2.pipeline.jobs.base import BaseTask
from gcip2.pipeline_core import (
    Default,
    Image,
    JobBuilderImpl,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    WorkflowAutoCancelOnNewCommit,
    WorkflowRule,
    WorkflowWhen,
)


class TestSecretHandlerInTask(JobBuilderImpl):
    _base = BaseTask
    _name = Tasks.test_vault_task


default = Default(
    tags=["static-k8s"],
    image=Image(
        name="ghcr.io/astral-sh/uv:python3.12-bookworm",
    ),
)


class Pipeline(PipelineBuilderImpl):
    def apply(self: Self) -> Self:

        self.add_jobs((self.job(TestSecretHandlerInTask).apply(),))

        self.with_default(default)
        return self


class GitlabCi(GitlabCiBuilderImpl):
    def apply(self: Self) -> Self:
        super(GitlabCi, self).apply()
        self.with_workflow(
            workflow=Workflow(
                name="default",
                auto_cancel=WorkflowAutoCancel(
                    on_job_failure=WorkflowAutoCancelOnJobFailure.NONE,
                    on_new_commit=WorkflowAutoCancelOnNewCommit.NONE,
                ),
                rules=[
                    WorkflowRule(
                        if_='$PARENT_PIPELINE_SOURCE == "merge_request_event"',
                        when=WorkflowWhen.ALWAYS,
                    ),
                    WorkflowRule(
                        if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH",
                        when=WorkflowWhen.ALWAYS,
                    ),
                    WorkflowRule(when=WorkflowWhen.NEVER),
                ],
            )
        )
        self.with_default(default)
        return self
