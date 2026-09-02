from enum import Enum
from typing import Self

from _tasks._consts import Tasks
from gcip2 import BaseLinux, BaseTask, GitlabCiBuilderImpl
from gcip2.ci.jobs import base
from gcip2.ci.jobs.trigger import BuildTriggerPipeline, TriggerPipeline
from gcip2.pipeline_core import (
    ArtifactsReports,
    ArtifactsReportsCoverage,
    GlobalVariables,
    JobBuilderImpl,
    JobWhen,
    Stage,
    TriggerIncludeArtifact,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    WorkflowAutoCancelOnNewCommit,
    WorkflowRule,
    WorkflowWhen,
)


class Stages(str, Enum):
    QT = "qt"
    JOBS = Stage.JOBS.value
    PUBLISH = "publish"


class RunUnitTests(JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.model.name = "unit-tests"
        self.model.coverage = "/TOTAL.*?(\\d+%)$/"
        return self


class CheckPackageVersion(JobBuilderImpl):
    _name = Tasks.check_package_version
    _base = BaseTask

    def apply(self: Self) -> Self:
        return self.with_stage(Stages.PUBLISH)


class CreateVersionTag(JobBuilderImpl):
    _name = Tasks.create_version_tag
    _base = BaseTask

    def apply(self: Self) -> Self:
        return self.with_needs([Tasks.check_package_version.value]).with_stage(Stages.PUBLISH)


class GenerateDocs(JobBuilderImpl):
    _name = Tasks.generate_docs
    _base = BaseTask

    def apply(self):
        return (
            self.with_needs([Tasks.create_version_tag.value])
            .with_stage(Stages.PUBLISH)
            .with_artifacts(paths=["out/docs"])
        )


class PublishPackage(JobBuilderImpl):
    _name = Tasks.publish_package
    _base = BaseTask

    def apply(self: Self) -> Self:
        return self.with_needs([Tasks.create_version_tag.value]).with_stage(Stages.PUBLISH)


class GitlabCi(GitlabCiBuilderImpl):
    def _add_test_jobs(self: Self) -> Self:
        for test_name in self._config.extra.get("pipelines", []):
            build_pipeline_job = (
                self.job(BuildTriggerPipeline)
                .apply()
                .with_tags(["static-k8s"])
                # .add_to_name(f" -f pipelines/{test_name}/ci.py")
                .add_to_name(f":{test_name}")
                .with_script(["dothat run build-pipeline"])
                .update_variables({"INPUT_CI_FILE": f"pipelines/{test_name}/ci.py"})
            )
            if test_name == "config":
                build_pipeline_job.update_variables(
                    {
                        "ENVIRONMENT_TOML_PATH": "pipelines/config/environment.toml",
                    }
                )
            if test_name == "initialization":
                build_pipeline_job.with_when(JobWhen.MANUAL)

            trigger_pipeline_job = (
                self.job(TriggerPipeline)
                .apply()
                .add_to_name(f":{test_name}")
                .with_needs([build_pipeline_job.model.name])
            )
            trigger_pipeline_job.model.trigger.include = [  # type: ignore
                TriggerIncludeArtifact(
                    job=build_pipeline_job.model.name,
                    artifact="out/pipeline.gitlab-ci.yml",
                )
            ]

            self.model.jobs.extend([build_pipeline_job, trigger_pipeline_job])

        return self

    def _add_unit_tests_jobs(self: Self) -> Self:
        for module in self._config.extra.get("tests", {}).get("unit-tests", []):
            coverage_module = self._config.extra.get("tests", {}).get("coverage-module", {}).get(module, "gcip2")
            self.model.jobs.append(
                self.job(RunUnitTests)
                .apply()
                .add_to_name(f":{module}")
                .with_stage(Stages.QT)
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

        self.add_jobs((self.job(base.PreCommit).apply().with_stage(Stages.QT.value),))

        self._add_unit_tests_jobs()
        self._add_test_jobs()

        self.add_jobs(
            (
                self.job(CheckPackageVersion).apply(),
                self.job(CreateVersionTag).apply(),
                self.job(GenerateDocs).apply(),
                self.job(PublishPackage).apply(),
            )
        )

        self.model.variables = {
            "PY_COLORS": GlobalVariables(value="1"),
            "FORCE_COLOR": GlobalVariables(value="1"),
            "FF_TIMESTAMPS": GlobalVariables(value="true"),
            # "FF_USE_LEGACY_KUBERNETES_EXECUTION_STRATEGY": GlobalVariables(value="true"),
            # "FF_USE_DYNAMIC_TRACE_FORCE_SEND_INTERVAL": GlobalVariables(value="true"),
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
