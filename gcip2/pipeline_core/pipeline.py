from collections.abc import Iterable
from typing import Self

from gcip2.pipeline_core import Default, Job, JobBuilderImpl, Pipeline, Stage, Workflow
from gcip2.project_config import ProjectConfig


class PipelineBuilder:
    def build(self) -> Pipeline:
        raise NotImplementedError


class PipelineBuilderImpl(PipelineBuilder):
    def __init__(self) -> None:
        self.model: Pipeline = Pipeline()

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

    def add_jobs(self, jobs: Iterable[Job | JobBuilderImpl]):
        self.model.jobs.extend(jobs)

    def with_workflow(self, workflow: Workflow = Workflow()):
        self.model.workflow = workflow
        return self

    def with_default(self, default: Default = Default()):
        self.model.default = default
        return self
