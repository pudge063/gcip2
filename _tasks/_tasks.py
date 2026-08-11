from collections.abc import Iterator

from _tasks import _actions, _params
from _tasks._consts import Tasks
from gcip2.tasks_core.task_builder import Task, TaskBuilderImpl
from gcip2.tasks_core.task_generator import TaskGeneratorImpl


class TestBaseTask(TaskBuilderImpl):
    _basename = Tasks.test_task

    def apply(self):
        self.model.doc = "test task"
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


class InitializeProjectPipeline(TaskBuilderImpl):
    _basename = Tasks.initialize_project_pipeline

    def apply(self):
        return self.with_actions(
            (
                _actions.SetupSsh,
                _actions.SetupGitInsteadOf,
                _actions.UpdateTestProject,
            )
        ).with_params((_params.flavor(),))


class RunInitializedPipeline(TaskBuilderImpl):
    _basename = Tasks.run_initialized_pipeline

    def apply(self):
        return self.with_actions((_actions.RunInitializationPipeline,))


class CheckPackageVersion(TaskBuilderImpl):
    _basename = Tasks.check_package_version

    def apply(self):
        return self.with_actions((_actions.CheckVersion,)).with_params((self._params.ci(),))


class CreateVersionTag(TaskBuilderImpl):
    _basename = Tasks.create_version_tag

    def apply(self):
        return self.with_actions((_actions.CreateVersionTag,)).with_params(
            (
                self._params.ci(),
                _params.gitlab_token_section(),
            )
        )


class PublishPackage(TaskBuilderImpl):
    _basename = Tasks.publish_package

    def apply(self):
        return self.with_actions((_actions.PublishPackage,)).with_params(
            (
                self._params.ci(),
                _params.pypi_token_section(),
            )
        )


class TaskGenerator(TaskGeneratorImpl):
    task_check_package_version = CheckPackageVersion
    task_create_version_tag = CreateVersionTag
    task_get_publish_token = PublishPackage
    task_initialize_project_pipeline = InitializeProjectPipeline
    task_run_initialization_pipeline = RunInitializedPipeline

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
                        self._params.ci(),
                        _params.flavor(),
                        _params.insecure(),
                    )
                )
                .build()
            )

        yield (self.builder(TestVaultSecret).apply().build())


TASK_GENERATOR = TaskGenerator()
