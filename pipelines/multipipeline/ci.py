from typing import Self

from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl
from gcip2.ci.jobs.base import BaseLinux
from gcip2.pipeline_core import (
    JobBuilderImpl,
    Parallel,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    WorkflowAutoCancelOnNewCommit,
    WorkflowRule,
    WorkflowWhen,
)


class MatrixJob(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.model.name = "matrix-job"
        self.model.parallel = Parallel(matrix=[{"TEST_VARIABLE": ["1", "2", "3", "4", "5"]}])
        self.model.script = ["echo $TEST_VARIABLE"]
        return self


class Pipeline(PipelineBuilderImpl):
    def apply(self: Self) -> Self:
        self.model.jobs.append(self.job(MatrixJob).apply())
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
        return self
