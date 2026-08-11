from typing import Self

from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl, pipeline_core
from gcip2.pipeline.jobs import base

from tasks._consts import Tasks


class ShowPackageVersion(pipeline_core.JobBuilderImpl):
    _base = base.BaseTask
    _task = Tasks.show_package_version


class CheckPythonVersion(pipeline_core.JobBuilderImpl):
    _base = base.BaseTask
    _task = Tasks.check_python_version


workflow = pipeline_core.Workflow(
    name="default",
    auto_cancel=pipeline_core.WorkflowAutoCancel(
        on_job_failure=pipeline_core.WorkflowAutoCancelOnJobFailure.NONE,
        on_new_commit=pipeline_core.WorkflowAutoCancelOnNewCommit.NONE,
    ),
    rules=[
        pipeline_core.WorkflowRule(
            if_='$CI_PIPELINE_SOURCE == "merge_request_event"',
            when=pipeline_core.WorkflowWhen.ALWAYS,
        ),
        pipeline_core.WorkflowRule(
            if_='$CI_PIPELINE_SOURCE == "web"',
            when=pipeline_core.WorkflowWhen.ALWAYS,
        ),
        pipeline_core.WorkflowRule(
            if_='$CI_PIPELINE_SOURCE == "api"',
            when=pipeline_core.WorkflowWhen.ALWAYS,
        ),
        pipeline_core.WorkflowRule(when=pipeline_core.WorkflowWhen.NEVER),
    ],
)


default = pipeline_core.Default(
    tags=["static-k8s"],
    image=pipeline_core.Image(
        name="ghcr.io/astral-sh/uv:python3.12-bookworm",
    ),
)


class Pipeline(PipelineBuilderImpl):
    def apply(self: Self) -> Self:
        self.add_jobs(
            (
                self.job(base.PreCommit).apply(),
                self.job(ShowPackageVersion).apply().with_name("show-package-version"),
                self.job(CheckPythonVersion).apply().with_name("check-python-version"),
            )
        )
        self.with_default(default)

        return self


class GitlabCi(GitlabCiBuilderImpl):
    def apply(self: Self) -> Self:
        super(GitlabCi, self).apply()
        self.with_workflow(workflow=workflow)
        self.with_default(default)
        return self
