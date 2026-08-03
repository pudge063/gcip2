from collections.abc import Iterator

from _tasks import _actions, _params
from _tasks._consts import Tasks
from gcip2.tasks_core.task_builder import Task, TaskBuilderImpl
from gcip2.tasks_core.task_generator import TaskGeneratorImpl


class TestBaseTask(TaskBuilderImpl):
    task_name = Tasks.test_task

    def apply(self):
        self.with_actions(
            (
                _actions.GitSetupInsteadofAction,
                _actions.CheckPoetryVersion,
                _actions.CheckShellCmd,
            )
        ).with_params(
            (
                _params.test_param(),
                _params.test_bool_param(),
            )
        )
        return self


class TestVaultSecret(TaskBuilderImpl):
    task_name = Tasks.test_vault_task

    def apply(self):
        return self.with_actions(
            (
                _actions.GitSetupInsteadofAction,
                _actions.TestVaultSecretAction,
            )
        ).with_params(
            (
                _params.vault_section(default="vault-with-approle"),
                _params.test_param(),
            )
        )


class TaskGenerator(TaskGeneratorImpl):
    def load_tasks(self) -> Iterator[Task]:
        yield (self.builder(TestBaseTask).apply().build())
        yield (self.builder(TestVaultSecret).apply().build())


TASK_GENERATOR = TaskGenerator()
