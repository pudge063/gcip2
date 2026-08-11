import sys
import typing

import click

from gcip2.initialization import TemplateGenerator

CallableCliOption = typing.TypeVar("CallableCliOption", bound=typing.Callable)  # type: ignore


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


def init_options(fn: CallableCliOption) -> CallableCliOption:
    for option in INIT_OPTIONS.keys():
        fn = INIT_OPTIONS[option](fn)
    return fn


@cli.command(
    "init",
    help="init base project structure",
)
@init_options
def init(force: bool, with_tasks: bool):
    TemplateGenerator().generate_project_structure()


if __name__ == "__main__":
    sys.exit(cli())
