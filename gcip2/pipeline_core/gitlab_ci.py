import typing

import pydantic

from gcip2.pipeline_core import Default, JobBuilderImpl, Pipeline, Stage, Workflow
from gcip2.project_config import ProjectConfig


class GitlabCiBuilderImpl(Pipeline):
    model: Pipeline = pydantic.Field(
        repr=False,
        default_factory=Pipeline,
        init=False,
    )

    _config = ProjectConfig()

    def apply(self: typing.Self) -> typing.Self:
        return self

    def build(self: typing.Self) -> Pipeline:
        if not self.model.stages:
            self.model.stages = [Stage.JOBS]
        return self.model.model_copy(deep=True)

    @staticmethod
    def job(job_class: type[JobBuilderImpl]) -> JobBuilderImpl:
        return job_class()

    def with_workflow(self, workflow: Workflow = Workflow()):
        self.model.workflow = workflow
        return self

    def with_default(self, default: Default = Default()):
        self.model.default = default
        return self
