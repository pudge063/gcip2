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
                _actions.SetupSsh,
                _actions.CheckUvVersion,
                _actions.CheckInsecureParam,
            )
        )
        return self


class TestVaultSecret(TaskBuilderImpl):
    _basename = Tasks.test_vault_task

    def apply(self):
        return self.with_actions((_actions.TestVaultSecretAction,)).with_params(
            (_params.vault_section(default="vault-with-approle"),)
        )


class RunInitializationPipeline(TaskBuilderImpl):
    _basename = Tasks.run_initialization_pipeline

    def apply(self):
        return self.with_actions(
            (
                _actions.SetupSsh,
                _actions.InitializePipeline,
                _actions.RunInitializationPipeline,
            )
        ).with_params((_params.flavor(),))


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
    task_run_initialization_pipeline = RunInitializationPipeline

    def load_tasks(self) -> Iterator[Task]:
        yield from super().load_tasks()

        targets = self._config.extra.get("targets", [])

        for target in targets:
            yield (
                self.builder(TestBaseTask)
                .apply()
                .with_name(target)
                .with_params(
                    (
                        _params.flavor(),
                        _params.insecure(),
                    )
                )
                .build()
            )

        yield (self.builder(TestVaultSecret).apply().build())


TASK_GENERATOR = TaskGenerator()
