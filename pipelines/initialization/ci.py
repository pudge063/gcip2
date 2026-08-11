from enum import Enum
from typing import Self

from _tasks._consts import Tasks
from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl
from gcip2.pipeline.jobs.base import BaseTask
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
    initialization = "initialization"


class Initialization(JobBuilderImpl):
    _name = Tasks.initialize_project_pipeline
    _base = BaseTask

    def apply(self: Self) -> Self:
        return self.with_stage(Stages.initialization).with_compose_image("base_python")


class RunInitializedPipeline(JobBuilderImpl):
    _name = Tasks.run_initialized_pipeline
    _base = BaseTask

    def apply(self: Self) -> Self:
        return (
            self.with_stage(Stages.initialization)
            .with_compose_image("base_python")
            .with_needs([Tasks.initialize_project_pipeline.value])
        )


class Pipeline(PipelineBuilderImpl):
    def apply(self: Self) -> Self:
        self.model.stages = [Stages.initialization]

        self.add_jobs(
            (
                self.job(Initialization).apply(),
                self.job(RunInitializedPipeline).apply(),
            )
        )

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
