from collections.abc import Iterator

from gcip2.tasks_core.ci_tasks import _actions, _params
from gcip2.tasks_core.task_builder import Task, TaskBuilderImpl
from gcip2.tasks_core.task_generator import TaskGeneratorImpl


class BuildGitlabCi(TaskBuilderImpl):
    _basename = "build-gitlab-ci"

    def apply(self):
        return self.with_actions((_actions.BuildGitlabCi,)).with_params(
            (
                _params.ci_file(),
                _params.out_gitlab_ci(".gitlab-ci.yml"),
            )
        )


class BuildPipeline(TaskBuilderImpl):
    _basename = "build-pipeline"

    def apply(self):
        return self.with_actions((_actions.BuildPipeline,)).with_params(
            (
                _params.ci_file(),
                _params.out_gitlab_ci("out/pipeline.gitlab-ci.yml"),
            )
        )


class InitializeDefaultProject(TaskBuilderImpl):
    _basename = "init"

    def apply(self):
        return self.with_actions((_actions.InitializeDefaultProject,)).with_params((_params.force(),))


class TaskGenerator(TaskGeneratorImpl):
    task_build_pipeline = BuildPipeline
    task_build_gitlab_ci = BuildGitlabCi
    task_init = InitializeDefaultProject

    def load_tasks(self) -> Iterator[Task]:
        yield from super().load_tasks()


CI_TASK_GENERATOR = TaskGenerator()
