from enum import Enum
from typing import Self

from _tasks._consts import Tasks
from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl, pipeline_core
from gcip2.pipeline.jobs import base


class Stages(str, Enum):
    initialization = "initialization"


class Initialization(pipeline_core.JobBuilderImpl):
    _name = Tasks.initialize_project_pipeline
    _base = base.BaseTask

    def apply(self: Self) -> Self:
        return self.with_stage(Stages.initialization).with_compose_image("base_python")


class RunInitializedPipeline(pipeline_core.JobBuilderImpl):
    _name = Tasks.run_initialized_pipeline
    _base = base.BaseTask

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
            workflow=pipeline_core.Workflow(
                name="default",
                auto_cancel=pipeline_core.WorkflowAutoCancel(
                    on_job_failure=pipeline_core.WorkflowAutoCancelOnJobFailure.NONE,
                    on_new_commit=pipeline_core.WorkflowAutoCancelOnNewCommit.NONE,
                ),
                rules=[
                    pipeline_core.WorkflowRule(
                        if_='$PARENT_PIPELINE_SOURCE == "merge_request_event"',
                        when=pipeline_core.WorkflowWhen.ALWAYS,
                    ),
                    pipeline_core.WorkflowRule(
                        if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH",
                        when=pipeline_core.WorkflowWhen.ALWAYS,
                    ),
                    pipeline_core.WorkflowRule(when=pipeline_core.WorkflowWhen.NEVER),
                ],
            )
        )
        return self
