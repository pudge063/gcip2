from gcip2.tasks_core.task_builder import TaskBuilderImpl
from gcip2.tasks_core.task_generator import TaskGeneratorImpl

from ._actions import (
    CheckSecret,
    CheckShellCmd,
    CheckUvVersion,
    GitSetupInsteadofAction,
)


class DummyTask1(TaskBuilderImpl):
    _basename = "test-task-1"

    def apply(self):
        self.with_actions(
            (
                GitSetupInsteadofAction,
                CheckUvVersion,
                CheckShellCmd,
                CheckSecret,
            )
        )
        return self


class DummyTask2(TaskBuilderImpl):
    _basename = "test-task-2"

    def apply(self):
        self.with_actions(
            (
                CheckShellCmd,
                CheckSecret,
            )
        )
        return self


class TaskGenerator(TaskGeneratorImpl):
    def load_tasks(self):
        yield (self.builder(DummyTask1).apply().build())
        yield (self.builder(DummyTask2).apply().build())


TASK_GENERATOR = TaskGenerator()
