import typing
from collections.abc import Iterable

from gcip2.pipeline_core import Default, Image, Job, JobBuilderImpl, Pipeline, Stage, Workflow
from gcip2.project_config import ProjectConfig


class GitlabCiBuilder:
    def build(self) -> Pipeline:
        raise NotImplementedError


class GitlabCiBuilderImpl(GitlabCiBuilder):
    _config = ProjectConfig.from_file()

    def __init__(self) -> None:
        self.model: Pipeline = Pipeline()

    def apply(self: typing.Self) -> typing.Self:
        return self

    def build(self: typing.Self) -> Pipeline:
        if not self.model.default:
            self.model.default = Default()

        if not self.model.default.image:
            image_data = self._config.compose.images.get("base_python")
            if not image_data:
                raise ValueError(f"image_data not found in {self._config.compose.path.name}")
            self.model.default.image = Image(name=image_data.image)

        if not self.model.default.tags:
            self.model.default.tags = ["static-k8s"]

        if not self.model.stages:
            self.model.stages = [Stage.JOBS]
        return self.model.model_copy(deep=True)

    @staticmethod
    def job(job_class: type[JobBuilderImpl]) -> JobBuilderImpl:
        return job_class()

    def add_jobs(self, jobs: Iterable[Job | JobBuilderImpl]):
        self.model.jobs.extend(jobs)

    def with_workflow(self, workflow: Workflow):
        self.model.workflow = workflow
        return self

    def with_default(self, default: Default):
        self.model.default = default
        return self
