from enum import Enum
from typing import Self

from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl
from gcip2.pipeline.jobs.base import BaseLinux
from gcip2.pipeline_core import (
    JobBuilderImpl,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    WorkflowAutoCancelOnNewCommit,
    WorkflowRule,
    WorkflowWhen,
)


class Stages(str, Enum):
    pre_commit = "pre-commit"


class PreCommit(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.with_name("pre-commit")
        self.model.script = [
            "pre-commit run -av --color=always",
        ]
        self.with_stage(Stages.pre_commit)
        return self


class Pipeline(PipelineBuilderImpl):
    def apply(self: Self) -> Self:
        self.model.stages = [Stages.pre_commit]
        self.add_jobs((self.job(PreCommit).apply(),))
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
