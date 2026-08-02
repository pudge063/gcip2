from _tasks import _actions
from _tasks._consts import Tasks
from gcip2.tasks_core.task_builder import TaskBuilderImpl


class TestBaseTask(TaskBuilderImpl):
    task_name = Tasks.test_task.value

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
