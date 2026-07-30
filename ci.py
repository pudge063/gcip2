from typing import Self

import gcip2
from gcip2 import GitlabCiBuilderImpl
from gcip2.pipeline_core import (
    Default,
    Image,
    TriggerIncludeArtifact,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    WorkflowAutoCancelOnNewCommit,
    WorkflowRule,
    WorkflowWhen,
)
from gcip2.pipeline_core.jobs.trigger import BuildTriggerPipeline, TriggerPipeline

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
            if_="$CI_COMMIT_TAG =~ '/^v\\d+\\.\\d+\\.\\d+$/'",
            when=WorkflowWhen.ALWAYS,
        ),
        WorkflowRule(
            if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH",
            when=WorkflowWhen.ALWAYS,
        ),
        WorkflowRule(when=WorkflowWhen.NEVER),
    ],
)


class GitlabCi(GitlabCiBuilderImpl):
    def _add_test_jobs(self: Self) -> Self:
        for test_name in ["checkstyle", "multipipeline"]:
            build_pipeline_job = (
                self.job(BuildTriggerPipeline)
                .apply()
                .with_name(f"test/build-pipeline:{test_name}")
                .with_tags(["static-k8s"])
            )
            build_pipeline_job.model.script = [f'exec sh -c "gcip2 build-pipeline -f tests/{test_name}/ci.py"']

            trigger_pipeline_job = (
                self.job(TriggerPipeline)
                .apply()
                .with_name(f"test/trigger-pipeline:{test_name}")
                .with_needs([build_pipeline_job.model.name])  # type: ignore
            )
            trigger_pipeline_job.model.trigger.include = [  # type: ignore
                TriggerIncludeArtifact(job=build_pipeline_job.model.name, artifact="out/pipeline.gitlab-ci.yml")
            ]

            self.model.jobs.extend([build_pipeline_job, trigger_pipeline_job])
        return self

    def apply(self: Self) -> Self:
        super(GitlabCi, self).apply()

        self._add_test_jobs()

        self.with_workflow(workflow=workflow)
        self.with_default(
            Default(
                tags=["static-k8s"],
                image=Image(
                    name="pfeiffermax/python-poetry:1.17.0-poetry2.2.1-python3.12.12-trixie",
                ),
            )
        )
        return self
