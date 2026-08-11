import pathlib
import sys
import typing

import click

from gcip2.initialization import TemplateGenerator
from gcip2.pipeline.builder import PipelineBuilder

CallableCliOption = typing.TypeVar("CallableCliOption", bound=typing.Callable)  # type: ignore

BUILD_PIPELINE_OPTIONS: dict[str, typing.Any] = {
    "ci-file": click.option(
        "--ci-file",
        "-f",
        help="File with source code for pipeline. Default: `ci.py`",
        type=str,
        default="ci.py",
    ),
    "out-pipeline": click.option(
        "--out-pipeline",
        "-o",
        help="Output file with child downstream pipeline. Default: `out/pipeline.gitlab-ci.yml`",
        type=str,
        default="out/pipeline.gitlab-ci.yml",
    ),
}

BUILD_GITLAB_CI_OPTIONS: dict[str, typing.Any] = {
    "ci-file": click.option(
        "--ci-file",
        "-f",
        help="File with source code for pipeline. Default: `ci.py`",
        type=str,
        default="ci.py",
    ),
    "out-gitlab-ci": click.option(
        "--out-gitlab-ci",
        "-o",
        help="Output file with parent trigger pipeline. Default: `.gitlab-ci.yml`",
        type=str,
        default=".gitlab-ci.yml",
    ),
}

INIT_OPTIONS: dict[str, typing.Any] = {
    "force": click.option(
        "--force",
        "-f",
        is_flag=True,
        default=False,
        help="Force overwrite base project structure. Default `False`",
    ),
    "with-tasks": click.option(
        "--with-tasks/--no-tasks",
        default=True,
        help="Initialization with tasks. Default `True`.",
    ),
}


@click.group()
def cli() -> None:
    """Gitlab DSL framework"""


def build_gitlab_ci_options(fn: CallableCliOption) -> CallableCliOption:
    for option in BUILD_GITLAB_CI_OPTIONS.keys():
        fn = BUILD_GITLAB_CI_OPTIONS[option](fn)
    return fn


def build_pipeline_options(fn: CallableCliOption) -> CallableCliOption:
    for option in BUILD_PIPELINE_OPTIONS.keys():
        fn = BUILD_PIPELINE_OPTIONS[option](fn)
    return fn


def init_options(fn: CallableCliOption) -> CallableCliOption:
    for option in INIT_OPTIONS.keys():
        fn = INIT_OPTIONS[option](fn)
    return fn


BUILDER = PipelineBuilder()


@cli.command(
    "build-gitlab-ci",
    help="generate file with parent trigger pipeline",
)
@build_gitlab_ci_options
def build_gitlab_ci(
    out_gitlab_ci: str,
    ci_file: str,
):
    BUILDER.build_gitlab_ci(
        out_gitlab_ci=pathlib.Path(out_gitlab_ci),
        ci_file_path=pathlib.Path(ci_file),
    )


@cli.command(
    "build-pipeline",
    help="generate file with child downstream pipeline",
)
@build_pipeline_options
def build_pipeline(
    ci_file: str,
    out_pipeline: str,
):
    BUILDER.build_pipeline(
        ci_file_path=pathlib.Path(ci_file),
        out_pipeline_path=pathlib.Path(out_pipeline),
    )


@cli.command(
    "init",
    help="init base project structure",
)
@init_options
def init(force: bool, with_tasks: bool):
    TemplateGenerator().generate_project_structure()


if __name__ == "__main__":
    sys.exit(cli())
