from collections.abc import Iterator

from gcip2.tasks_core.ci_tasks import _actions, _params
from gcip2.tasks_core.task_builder import Task, TaskBuilderImpl
from gcip2.tasks_core.task_generator import TaskGeneratorImpl


class CiAfterScript(TaskBuilderImpl):
    _basename = "ci-after-script"

    def apply(self):
        self.model.doc = "ci after script task do nothing"
        return self.with_actions((_actions.CiAfterScript,))


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


class RunPreCommit(TaskBuilderImpl):
    _basename = "pre-commit"

    def apply(self):
        return self.with_actions((_actions.RunPreCommit,)).with_doc("default pre-commit job")


class CiTaskGenerator(TaskGeneratorImpl):
    task_build_pipeline = BuildPipeline
    task_build_gitlab_ci = BuildGitlabCi
    task_init = InitializeDefaultProject
    task_ci_after_script = CiAfterScript
    task_pre_commit = RunPreCommit

    def load_tasks(self) -> Iterator[Task]:
        yield from super().load_tasks()
