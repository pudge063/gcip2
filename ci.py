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
    Needs,
    Pipeline,
    PipelineBuilderImpl,
    Rule,
    RuleChanges,
    Stage,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
)


class PreCommit(JobBuilderImpl):
    def apply(self: Self) -> Self:
        self.model.name = "pre-commit"
        self.model.script = [
            "pip3 install poetry",
            "poetry install",
            ". .venv/bin/activate",
            "poetry run pre-commit run -av",
        ]
        self.with_image(image="python:3.11")
        self.with_stage("pre-commit")
        return self


class Build(JobBuilderImpl):
    def apply(self: Self):
        dotenv_file = "dotenv.txt"

        self.with_stage("build")
        self.model.script = [
            f"echo PARENT_JOB_ID=$CI_JOB_ID > {dotenv_file}",
            "mkdir -p out",
            "touch out/test_$CI_JOB_ID",
        ]
        self.with_artifacts(
            paths=[
                "out/*",
                "build/*",
                "_build/*",
            ],
            reports=ArtifactsReports(dotenv=[dotenv_file]),
        )
        return self


class CheckDotenv(JobBuilderImpl):
    def apply(self: Self):

        self.with_stage("check")
        self.model.script = [
            f"echo $PARENT_JOB_ID",
            "ls -la out",
        ]
        return self


class Ci(PipelineBuilderImpl):
    def _add_build_jobs(self) -> list[Job]:
        platforms = ["arm", "amd64", "dev-441", "dev-442", "dev-443", "dev-313"]

        jobs: list[Job] = []

        for platform in platforms:
            build_job = self.job(Build).apply().with_name(f"build:{platform}")

            check_job = self.job(CheckDotenv).apply().with_name(f"check:{platform}").with_needs([build_job.model.name])

            jobs.extend([build_job, check_job])

        return jobs

    def apply(self: Self) -> Self:
        self.model.jobs.append(self.job(PreCommit).apply().with_stage("pre-commit"))
        self.model.jobs.extend(self._add_build_jobs())
        self.model.stages = ["pre-commit", "build", "check"]
        self.with_workflow(
            Workflow(
                name="default",
                auto_cancel=WorkflowAutoCancel(
                    on_job_failure=WorkflowAutoCancelOnJobFailure.NONE,
                    on_new_commit=WorkflowAutoCancelOnNewCommit.NONE,
                ),
                rules=[
                    Rule(
                        if_="$CI_DEFAULT_BRANCH == $CI_COMMIT_BRANCH",
                        variables={
                            "TEST": "1",
                        },
                    )
                ],
            )
        )
        self.with_default(Default(tags=["immortal"]))
        return self
