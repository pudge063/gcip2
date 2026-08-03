from typing import Self

from _tasks import _consts
from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl
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
from gcip2.pipeline_core.jobs.base import BaseTask


class TestTasks(JobBuilderImpl):
    _base = BaseTask

    _task = _consts.Tasks.test_task

    def apply(self: Self) -> Self:
        return self.with_name("test-task-job")


default = Default(
    tags=["static-k8s"],
    image=Image(
        name="pfeiffermax/python-poetry:1.17.0-poetry2.2.1-python3.12.12-trixie",
    ),
)


class Pipeline(PipelineBuilderImpl):
    def apply(self: Self) -> Self:
        self.model.jobs.append(self.job(TestTasks).apply())

        self.with_default(default=default)
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
        self.with_default(default=default)
        return self
