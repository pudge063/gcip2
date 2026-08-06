from collections.abc import Iterator

from gcip2.tasks_core.task_builder import Task, TaskBuilderImpl
from gcip2.tasks_core.task_generator import TaskGeneratorImpl

from tasks import _actions, _params
from tasks._consts import Tasks


class ShowPackageVersion(TaskBuilderImpl):
    _basename = Tasks.show_package_version

    def apply(self):
        self.with_actions((_actions.ShowPackageVersion,)).with_params((_params.test_param(),))
        return self


class CheckPythonVersion(TaskBuilderImpl):
    _basename = Tasks.check_python_version

    def apply(self):
        self.with_actions((_actions.CheckPythonVersion,))
        return self


class TaskGenerator(TaskGeneratorImpl):
    task_show_package_version = ShowPackageVersion

    def load_tasks(self) -> Iterator[Task]:
        yield from super().load_tasks()

        yield (self.builder(CheckPythonVersion).apply().build())


TASK_GENERATOR = TaskGenerator()
