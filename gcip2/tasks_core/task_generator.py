import dataclasses
from collections.abc import Iterator

import injector

from gcip2 import ProjectConfig
from gcip2.tasks_core.models.params import Params
from gcip2.tasks_core.task_builder import Task, TaskBuilderImpl


class TaskGenerator:
    def load_tasks(self) -> Iterator[Task]:
        raise NotImplementedError


@injector.inject
@dataclasses.dataclass
class TaskGeneratorImpl(TaskGenerator):
    _config: ProjectConfig
    _di: injector.Injector
    _params: Params

    def _auto_load_tasks(self) -> Iterator[Task]:
        for name, cls in vars(type(self)).items():
            if name.startswith("task_") and isinstance(cls, type) and issubclass(cls, TaskBuilderImpl):
                yield self._di.create_object(cls).apply().build()

    def builder(self, task_class: type[TaskBuilderImpl]) -> TaskBuilderImpl:
        return self._di.create_object(task_class)

    def load_tasks(self) -> Iterator[Task]:
        yield from self._auto_load_tasks()
