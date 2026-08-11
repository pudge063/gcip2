from typing import Self

from gcip2 import GitlabCiBuilderImpl, PipelineBuilderImpl
from gcip2.pipeline.jobs.base import BaseLinux
from gcip2.pipeline_core import (
    ArtifactsReports,
    ArtifactsReportsCoverage,
    JobBuilderImpl,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    WorkflowAutoCancelOnNewCommit,
    WorkflowRule,
    WorkflowWhen,
)


class RunUnitTests(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.model.name = "unit-tests"
        self.model.coverage = "/TOTAL.*?(\\d+%)$/"
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


class Pipeline(PipelineBuilderImpl):
    def apply(self: Self) -> Self:

        for module in ["job", "pipeline"]:
            self.model.jobs.append(
                self.job(RunUnitTests)
                .apply()
                .add_to_name(f":{module}")
                .with_script(
                    [
                        (
                            f"pytest -v tests/unit/test_{module}.py --junitxml=pytest.xml "
                            "--cov=gcip2 --cov-report=term --cov-report=xml:coverage.xml"
                        ),
                    ]
                )
                .with_artifacts(
                    paths=["coverage.xml", "pytest.xml"],
                    reports=ArtifactsReports(
                        coverage_report=ArtifactsReportsCoverage(
                            coverage_format="cobertura",
                            path="coverage.xml",
                        ),
                        junit=["pytest.xml"],
                    ),
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
