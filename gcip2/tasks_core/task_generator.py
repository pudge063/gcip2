from collections.abc import Iterator

from gcip2.tasks_core.task_builder import Task, TaskBuilderImpl


class TaskGenerator:
    def load_tasks(self) -> Iterator[Task]:
        raise NotImplementedError


class TaskGeneratorImpl(TaskGenerator):
    @staticmethod
    def builder(task_class: type[TaskBuilderImpl]) -> TaskBuilderImpl:
        return task_class()

    def load_tasks(self) -> Iterator[Task]:
        yield from ()
