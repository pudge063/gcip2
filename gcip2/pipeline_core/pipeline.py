from collections.abc import Iterable
from typing import Self

import pydantic

from gcip2.pipeline_core import Default, Job, JobBuilderImpl, Pipeline, Stage, Workflow
from gcip2.project_config import ProjectConfig


class PipelineBuilderImpl(Pipeline):
    model: Pipeline = pydantic.Field(
        repr=False,
        default_factory=Pipeline,
        init=False,
    )

    _config = ProjectConfig()

    def apply(self: Self) -> Self:
        return self

    def build(self: Self) -> Pipeline:
        if not self.model.stages:
            self.model.stages = [Stage.JOBS]
        return self.model.model_copy(deep=True)

    @staticmethod
    def job(job_class: type[JobBuilderImpl]) -> JobBuilderImpl:
        return job_class()

    def add_jobs(self, jobs: Iterable[Job]):
        self.model.jobs.extend(jobs)

    def with_workflow(self, workflow: Workflow = Workflow()):
        self.model.workflow = workflow
        return self

    def with_default(self, default: Default = Default()):
        self.model.default = default
        return self
