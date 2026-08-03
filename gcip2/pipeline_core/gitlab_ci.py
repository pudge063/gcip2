import typing

from gcip2.pipeline_core import Default, JobBuilderImpl, Pipeline, Stage, Workflow
from gcip2.project_config import ProjectConfig


class GitlabCiBuilder:
    def build(self) -> Pipeline:
        raise NotImplementedError


class GitlabCiBuilderImpl(GitlabCiBuilder):
    _config = ProjectConfig()

    def __init__(self) -> None:
        self.model: Pipeline = Pipeline()

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
