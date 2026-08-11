import pathlib

from gcip2.initialization import TemplateGenerator
from gcip2.pipeline.builder import PipelineBuilder
from gcip2.tasks_core.models.actions import InteractivePythonAction, InteractiveShlex


class BuildPipeline(InteractivePythonAction):
    def impl(self, *, ci_file: str, out_pipeline: str, **_) -> None:
        builder = PipelineBuilder()
        builder.build_pipeline(
            ci_file_path=pathlib.Path(ci_file),
            out_pipeline_path=pathlib.Path(out_pipeline),
        )


class BuildGitlabCi(InteractivePythonAction):
    def impl(self, *, ci_file: str, out_pipeline: str, **_) -> None:
        builder = PipelineBuilder()
        builder.build_gitlab_ci(
            ci_file_path=pathlib.Path(ci_file),
            out_gitlab_ci=pathlib.Path(out_pipeline),
        )


class InitializeDefaultProject(InteractivePythonAction):
    def impl(self, *, force: bool, **_) -> None:
        templategenerator = TemplateGenerator()
        templategenerator.generate_project_structure(force=force)


class RunPreCommit(InteractiveShlex):
    def impl(self, **_) -> list[list[str]]:
        return [["pre-commit", "run", "-av"]]
