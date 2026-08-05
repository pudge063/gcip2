from typing import Self

from _tasks import _consts
from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl
from gcip2.pipeline_core import (
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
    _name = _consts.Tasks.test_task
    _base = BaseTask


class Pipeline(PipelineBuilderImpl):
    def apply(self: Self) -> Self:
        targets = self._config.extra.get("targets", [])
        for target in targets:
            for job_name_suffix in ["", " --insecure", " --secure"]:
                self.model.jobs.append(self.job(TestTasks).apply().add_to_name(f":{target}{job_name_suffix}"))
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
