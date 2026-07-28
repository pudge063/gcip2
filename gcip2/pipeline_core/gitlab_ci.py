import typing

import pydantic

from ..pipeline_core import Default, JobBuilderImpl, Pipeline, Workflow


class GitlabCiBuilderImpl(Pipeline):
    model: Pipeline = pydantic.Field(
        repr=False,
        default_factory=Pipeline,
        init=False,
    )

    def apply(self: typing.Self) -> typing.Self:
        return self

    def build(self: typing.Self) -> Pipeline:
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
