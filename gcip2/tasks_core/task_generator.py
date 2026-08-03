from collections.abc import Iterator

from gcip2.tasks_core.task_builder import Task, TaskBuilderImpl


class TaskGenerator:
    def load_tasks(self) -> Iterator[Task]:
        raise NotImplementedError


class TaskGeneratorImpl(TaskGenerator):
    def _auto_load_tasks(self) -> Iterator[Task]:
        for name, cls in vars(type(self)).items():
            if name.startswith("task_") and isinstance(cls, type) and issubclass(cls, TaskBuilderImpl):
                yield cls().apply().build()

    @staticmethod
    def builder(task_class: type[TaskBuilderImpl]) -> TaskBuilderImpl:
        return task_class()

    def load_tasks(self) -> Iterator[Task]:
        yield from self._auto_load_tasks()
