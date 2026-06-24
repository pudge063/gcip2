from enum import Enum
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
    JobWhen,
    Needs,
    Pipeline,
    PipelineBuilderImpl,
    Rule,
    RuleChanges,
    Stage,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    WorkflowRule,
    WorkflowWhen,
)


class Stages(str, Enum):
    pre_commit = "pre-commit"
    publish = "publish"


class PreCommit(JobBuilderImpl):
    def apply(self: Self) -> Self:
        self.model.name = "pre-commit"
        self.model.script = [
            "pre-commit run -av",
        ]
        self.with_stage(Stages.pre_commit)
        self.with_poetry_before_script()
        return self


class PublishPackage(JobBuilderImpl):
    def apply(self: Self) -> Self:
        self.model.name = "publish"
        self.model.script = [
            "poetry build",
            "poetry config pypi-token.pypi ${PYPI_TOKEN}",
            "poetry publish",
        ]
        self.with_stage(Stages.publish)
        self.with_when(JobWhen.MANUAL)
        self.with_poetry_before_script()
        return self


class Ci(PipelineBuilderImpl):
    def apply(self: Self) -> Self:
        self.model.stages = [Stages.pre_commit, Stages.publish]

        self.model.jobs.append(self.job(PreCommit).apply())
        self.model.jobs.append(self.job(PublishPackage).apply().with_needs(["pre-commit"]))

        self.with_workflow(
            Workflow(
                name="default",
                auto_cancel=WorkflowAutoCancel(
                    on_job_failure=WorkflowAutoCancelOnJobFailure.NONE,
                    on_new_commit=WorkflowAutoCancelOnNewCommit.NONE,
                ),
                rules=[
                    WorkflowRule(
                        if_='$CI_PIPELINE_SOURCE == "web"',
                        when=WorkflowWhen.ALWAYS,
                    ),
                    WorkflowRule(when=WorkflowWhen.NEVER),
                ],
            )
        )
        self.with_default(
            Default(
                tags=["immortal"],
                image=Image(
                    name="pfeiffermax/python-poetry:1.17.0-poetry2.2.1-python3.12.12-trixie",
                ),
            )
        )
        return self
