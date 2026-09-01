from collections.abc import Iterable, Iterator
from typing import Any, Self

from gcip2 import BaseTask, pipeline, pipeline_core, tasks_core


class PrintEnvAction(tasks_core.InteractiveShlex):
    def impl(self, **kwargs: Any) -> Iterable[list[str]]:
        return [["printenv"]]


class PrintEnvTask(tasks_core.TaskBuilderImpl):
    _basename = "print-env"

    def apply(self):
        return self.with_actions((PrintEnvAction,))


class TaskGenerator(tasks_core.TaskGeneratorImpl):
    def load_tasks(self) -> Iterator[tasks_core.Task]:
        yield from super().load_tasks()

        yield self.builder(PrintEnvTask).apply().build()


class PrintEnvJob(pipeline_core.JobBuilderImpl):
    _base = BaseTask
    _name = "print-env"

    def apply(self: Self) -> Self:
        return self.with_compose_image("linux").update_variables(
            {
                "ENVIRONMENT_TOML_PATH": "pipelines/config/environment.toml",
            }
        )


class Pipeline(pipeline.PipelineBuilderImpl):
    def apply(self: Self) -> Self:
        self.add_jobs((self.job(PrintEnvJob).apply(),))
        return self
