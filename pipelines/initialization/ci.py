from enum import Enum
from typing import Self

from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl
from gcip2.pipeline_core import (
    JobBuilderImpl,
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
from gcip2.pipeline_core.jobs.base import BaseLinux
from gcip2.pipeline_core.jobs.trigger import TriggerPipeline


class Stages(str, Enum):
    initialization = "initialization"


class Initialization(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        return (
            self.with_name("initialization")
            .with_script(["gcip2 init -f", "gcip2 build-pipeline"])
            .with_stage(Stages.initialization)
            .with_artifacts(paths=["out", "_tasks/"])
            .with_compose_image("base_python")
        )


class TriggerInitializationPipeline(TriggerPipeline):
    def apply(self):
        super().apply()
        self.model.trigger = Trigger(
            include=[
                TriggerIncludeArtifact(
                    artifact="out/pipeline.gitlab-ci.yml",
                    job="initialization",
                )
            ],
            strategy=TriggerStrategy.DEPEND,
            forward=TriggerForward(
                yaml_variables=True,
                pipeline_variables=True,
            ),
        )

        return (
            self.with_name("initialization/trigger-pipeline")
            .with_needs(["initialization"])
            .with_stage(Stages.initialization)
        )


class Pipeline(PipelineBuilderImpl):
    def apply(self: Self) -> Self:
        self.model.stages = [Stages.initialization]

        self.add_jobs(
            (
                self.job(Initialization).apply(),
                self.job(TriggerInitializationPipeline).apply(),
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
