from _tasks import _actions
from gcip2.tasks_core.task_builder import TaskBuilderImpl


class DummyTask1(TaskBuilderImpl):
    task_name = "test-task-1"

    def apply(self):
        self.with_actions(
            (
                _actions.GitSetupInsteadofAction,
                _actions.CheckPoetryVersion,
                _actions.CheckShellCmd,
                _actions.CheckSecret,
            )
        )
        return self


class DummyTask2(TaskBuilderImpl):
    task_name = "test-task-2"

    def apply(self):
        self.with_actions(
            (
                _actions.CheckShellCmd,
                _actions.CheckSecret,
            )
        )
        return self
