import typing
import click
import sys

from .builder import PipelineBuilder

CallableCliOption = typing.TypeVar("CallableCliOption", bound=typing.Callable)  # type: ignore

OPTIONS: dict[str, typing.Any] = {
    "ci-file": click.option(
        "--ci-file",
        help="file with source code for pipeline",
        type=str,
        default="ci.py",
    ),
    "out-gitlab-ci": click.option(
        "--out-gitlab-ci",
        help="output file with parent trigger pipeline",
        type=str,
        default=".gitlab-ci.yml",
    ),
    "out-pipeline": click.option(
        "--out-pipeline",
        help="output file with child downstream pipeline",
        type=str,
        default="out/pipeline.gitlab-ci.yml",
    ),
}


@click.group()
def cli() -> None:
    """Gitlab DSL framework"""


def common_options(fn: CallableCliOption) -> CallableCliOption:
    for option in OPTIONS.keys():
        fn = OPTIONS[option](fn)
    return fn


BUILDER = PipelineBuilder()


@cli.command(
    "build-gitlab-ci",
    help="generate file with parent trigger pipeline",
)
@common_options
def build_gitlab_ci(
    out_gitlab_ci: str,
    **_: typing.Any,
):
    BUILDER.build_gitlab_ci(out_gitlab_ci=out_gitlab_ci)


@cli.command(
    "build-pipeline",
    help="generate file with child downstream pipeline",
)
@common_options
def build_pipeline(
    ci_file: str,
    out_pipeline: str,
    **_: typing.Any,
):
    BUILDER.build_pipeline(ci_file_path=ci_file, out_pipeline_path=out_pipeline)


if __name__ == "__main__":
    sys.exit(cli())
