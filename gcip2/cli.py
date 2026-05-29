import sys
import typing

import click

from .builder import PipelineBuilder

CallableCliOption = typing.TypeVar("CallableCliOption", bound=typing.Callable)  # type: ignore

BUILD_PIPELINE_OPTIONS: dict[str, typing.Any] = {
    "ci-file": click.option(
        "--ci-file",
        "-f",
        help="file with source code for pipeline",
        type=str,
        default="ci.py",
    ),
    "out-pipeline": click.option(
        "--out-pipeline",
        "-o",
        help="output file with child downstream pipeline",
        type=str,
        default="out/pipeline.gitlab-ci.yml",
    ),
}

BUILD_GITLAB_CI_OPTIONS: dict[str, typing.Any] = {
    "out-gitlab-ci": click.option(
        "--out-gitlab-ci",
        "-O",
        help="output file with parent trigger pipeline",
        type=str,
        default=".gitlab-ci.yml",
    ),
    "ci-tags": click.option(
        "--ci-tags",
        "-t",
        help="tags section for gitlab-ci",
        type=str,
        default="immortal",
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


BUILDER = PipelineBuilder()


@cli.command(
    "build-gitlab-ci",
    help="generate file with parent trigger pipeline",
)
@build_gitlab_ci_options
def build_gitlab_ci(
    out_gitlab_ci: str,
    ci_tags: str,
):
    BUILDER.build_gitlab_ci(
        out_gitlab_ci=out_gitlab_ci,
        default_tags=ci_tags,
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
    BUILDER.build_pipeline(ci_file_path=ci_file, out_pipeline_path=out_pipeline)


if __name__ == "__main__":
    sys.exit(cli())
