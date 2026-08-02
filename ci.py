from enum import Enum
from typing import Self

from gcip2 import BaseLinux, GitlabCiBuilderImpl
from gcip2.pipeline_core import (
    ArtifactsReports,
    ArtifactsReportsCoverage,
    Default,
    GlobalVariables,
    Image,
    JobBuilderImpl,
    Stage,
    TriggerIncludeArtifact,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    WorkflowAutoCancelOnNewCommit,
    WorkflowRule,
    WorkflowWhen,
)
from gcip2.pipeline_core.jobs.trigger import BuildTriggerPipeline, TriggerPipeline


class Stages(str, Enum):
    JOBS = Stage.JOBS.value
    UNIT_TESTS = "unit-tests"
    PUBLISH = "publish"


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
            auto_cancel=WorkflowAutoCancel(
                on_new_commit=WorkflowAutoCancelOnNewCommit.INTERRUPTIBLE,
            ),
        ),
        WorkflowRule(
            if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH",
            when=WorkflowWhen.ALWAYS,
        ),
        WorkflowRule(when=WorkflowWhen.NEVER),
    ],
)


class RunUnitTests(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.model.name = "unit-tests"
        self.model.coverage = "/TOTAL.*?(\\d+%)$/"
        return self


class GitlabCi(GitlabCiBuilderImpl):
    def _add_test_jobs(self: Self) -> Self:
        for test_name in ["checkstyle", "multipipeline", "integration", "publish"]:
            build_pipeline_job = (
                self.job(BuildTriggerPipeline)
                .apply()
                .with_name(f"{test_name}/build-pipeline")
                .with_tags(["static-k8s"])
            )
            build_pipeline_job.model.script = [f'exec sh -c "gcip2 build-pipeline -f pipelines/{test_name}/ci.py"']

            trigger_pipeline_job = (
                self.job(TriggerPipeline)
                .apply()
                .with_name(f"{test_name}/trigger-pipeline")
                .with_needs([build_pipeline_job.model.name])  # type: ignore
            )
            trigger_pipeline_job.model.trigger.include = [  # type: ignore
                TriggerIncludeArtifact(job=build_pipeline_job.model.name, artifact="out/pipeline.gitlab-ci.yml")
            ]

            if test_name == "publish":
                build_pipeline_job.with_stage(Stages.PUBLISH)
                trigger_pipeline_job.with_stage(Stages.PUBLISH)

            self.model.jobs.extend([build_pipeline_job, trigger_pipeline_job])

        return self

    def _add_unit_tests_jobs(self: Self) -> Self:
        for module in ["job", "pipeline"]:
            self.model.jobs.append(
                self.job(RunUnitTests)
                .apply()
                .add_to_name(f":{module}")
                .with_stage(Stages.UNIT_TESTS)
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

    def apply(self: Self) -> Self:
        super(GitlabCi, self).apply()

        self.model.stages = list(Stages)

        self._add_test_jobs()

        self._add_unit_tests_jobs()

        self.model.variables = {"PY_COLORS": GlobalVariables(value="1"), "FORCE_COLOR": GlobalVariables(value="1")}

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
