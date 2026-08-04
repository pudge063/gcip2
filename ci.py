from enum import Enum
from typing import Self

from _tasks._consts import Tasks
from gcip2 import BaseLinux, BaseTask, GitlabCiBuilderImpl
from gcip2.pipeline_core import (
    ArtifactsReports,
    ArtifactsReportsCoverage,
    GlobalVariables,
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


class RunUnitTests(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.model.name = "unit-tests"
        self.model.coverage = "/TOTAL.*?(\\d+%)$/"
        return self


class CheckPackageVersion(JobBuilderImpl):
    _base = BaseTask
    _task = Tasks.check_package_version

    def apply(self: Self) -> Self:
        return self.with_name("check-version").with_stage(Stages.PUBLISH)


class CreateVersionTag(JobBuilderImpl):
    _base = BaseTask
    _task = Tasks.create_version_tag

    def apply(self: Self) -> Self:
        return self.with_name("create-version").with_needs(["check-version"]).with_stage(Stages.PUBLISH)


class PublishPackage(JobBuilderImpl):
    _base = BaseTask
    _task = Tasks.publish_package

    def apply(self: Self) -> Self:
        self.model.name = "publish-package"
        return self.with_needs(["create-version"]).with_stage(Stages.PUBLISH)


class GitlabCi(GitlabCiBuilderImpl):
    def _add_test_jobs(self: Self) -> Self:
        for test_name in [
            "checkstyle",
            "initialization",
            "tasks",
            "vault",
            "multipipeline",
            "integration",
        ]:
            build_pipeline_job = (
                self.job(BuildTriggerPipeline)
                .apply()
                .with_name(f"{test_name}/build-pipeline")
                .with_tags(["static-k8s"])
            )
            build_pipeline_job.model.script = [
                f'exec sh -c "gcip2 build-pipeline -f pipelines/{test_name}/ci.py"',
            ]

            trigger_pipeline_job = (
                self.job(TriggerPipeline)
                .apply()
                .with_name(f"{test_name}/trigger-pipeline")
                .with_needs([build_pipeline_job.model.name])
            )
            trigger_pipeline_job.model.trigger.include = [  # type: ignore
                TriggerIncludeArtifact(
                    job=build_pipeline_job.model.name,
                    artifact="out/pipeline.gitlab-ci.yml",
                )
            ]

            if test_name == "publish":
                build_pipeline_job.with_stage(Stages.PUBLISH)
                trigger_pipeline_job.with_stage(Stages.PUBLISH)

            self.model.jobs.extend([build_pipeline_job, trigger_pipeline_job])

        return self

    def _add_unit_tests_jobs(self: Self) -> Self:
        for module in ["job", "pipeline", "tasks"]:
            coverage_module = {
                "job": "gcip2.pipeline_core",
                "pipeline": "gcip2.pipeline_core",
                "tasks": "gcip2.tasks_core",
            }.get(module, "gcip2")
            self.model.jobs.append(
                self.job(RunUnitTests)
                .apply()
                .add_to_name(f":{module}")
                .with_stage(Stages.UNIT_TESTS)
                .with_script(
                    [
                        (
                            f"pytest -v tests/unit/test_{module}.py --junitxml=pytest.xml "
                            f"--cov={coverage_module} --cov-report=term --cov-report=xml:coverage.xml"
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

        self.add_jobs(
            (
                self.job(CheckPackageVersion).apply(),
                self.job(CreateVersionTag).apply(),
                self.job(PublishPackage).apply(),
            )
        )

        self.model.variables = {
            "PY_COLORS": GlobalVariables(value="1"),
            "FORCE_COLOR": GlobalVariables(value="1"),
            # "FF_TIMESTAMPS": GlobalVariables(value="true"),
        }

        self.with_workflow(
            workflow=Workflow(
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
        )
        return self
