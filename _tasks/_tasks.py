from collections.abc import Iterator

from _tasks import _actions, _params
from _tasks._consts import Tasks
from gcip2.tasks_core.task_builder import Task, TaskBuilderImpl
from gcip2.tasks_core.task_generator import TaskGeneratorImpl


class TestBaseTask(TaskBuilderImpl):
    _basename = Tasks.test_task

    def apply(self):
        self.with_actions(
            (
                _actions.GitSetupInsteadofAction,
                _actions.CheckUvVersion,
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
    _basename = Tasks.test_vault_task

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


class CheckPackageVersion(TaskBuilderImpl):
    _basename = Tasks.check_package_version

    def apply(self):
        return self.with_actions((_actions.CheckVersion,))


class CreateVersionTag(TaskBuilderImpl):
    _basename = Tasks.create_version_tag

    def apply(self):
        return self.with_actions((_actions.CreateVersionTag,)).with_params((_params.gitlab_token_section(),))


class PublishPackage(TaskBuilderImpl):
    _basename = Tasks.publish_package

    def apply(self):
        return self.with_actions((_actions.PublishPackage,)).with_params((_params.pypi_token_section(),))


class TaskGenerator(TaskGeneratorImpl):
    task_check_package_version = CheckPackageVersion
    task_create_version_tag = CreateVersionTag
    task_get_publish_token = PublishPackage

    def load_tasks(self) -> Iterator[Task]:
        yield from super().load_tasks()

        yield (self.builder(TestBaseTask).apply().build())
        yield (self.builder(TestVaultSecret).apply().build())


TASK_GENERATOR = TaskGenerator()
