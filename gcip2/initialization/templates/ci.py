from enum import Enum
from typing import Self

from tasks._consts import Tasks

from gcip2 import BaseLinux, BaseTask, GitlabCiBuilderImpl, PipelineBuilderImpl
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


class JobName(str, Enum):
    pre_commit = "pre-commit"


class PreCommit(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.with_name(JobName.pre_commit.value)
        self.model.script = ["pre-commit run -av", "cat environment.toml", "ls -la"]
        return self


class ShowPackageVersion(JobBuilderImpl):
    _base = BaseTask
    _task = Tasks.show_package_version

    def apply(self):
        # self.model.script = [
        #     "rm -rf _tasks",
        #     "gcip2 init",
        #     "gciptask list",
        #     "gciptask run show-package-version",
        # ]
        return self


class CheckPythonVersion(JobBuilderImpl):
    _base = BaseTask
    _task = Tasks.check_python_version

    def apply(self):
        # self.model.script = [
        #     "rm -rf _tasks/",
        #     "gcip2 init",
        #     "gciptask list",
        #     "gciptask run check-python-version",
        # ]
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
            if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH",
            when=WorkflowWhen.ALWAYS,
        ),
        WorkflowRule(when=WorkflowWhen.NEVER),
    ],
)


default = Default(
    tags=["static-k8s"],
    image=Image(
        name="ghcr.io/astral-sh/uv:python3.12-bookworm",
    ),
)


class Pipeline(PipelineBuilderImpl):
    def apply(self: Self) -> Self:
        self.add_jobs(
            (
                self.job(PreCommit).apply(),
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
