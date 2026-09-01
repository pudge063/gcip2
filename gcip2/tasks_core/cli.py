import builtins
import dataclasses
import pathlib

import click
import injector

from gcip2.di import Module
from gcip2.logging import logger as LOGGER
from gcip2.tasks_core.registry import TaskRegistry
from gcip2.tasks_core.task_builder import Task


@dataclasses.dataclass
class DothatContext:
    di: injector.Injector


def get_registry(di: injector.Injector, module: str | None) -> dict[str, Task]:
    if module:
        return di.get(TaskRegistry).load_tasks_from_module(module)
    return di.get(TaskRegistry).tasks


@click.group()
@click.option(
    "--config",
    type=pathlib.Path,
    envvar="ENVIRONMENT_TOML_PATH",
    default=pathlib.Path(
        "environment.toml",
    ),
)
@click.pass_context
def cli(ctx: click.Context, config: pathlib.Path):
    ctx.obj = DothatContext(di=injector.Injector([Module(config_path=config)]))


@cli.command()
@click.option("--module", default=None)
@click.pass_obj
def list(dothat_context: DothatContext, module: str | None):
    _registry = get_registry(dothat_context.di, module)

    for key, task in _registry.items():
        click.echo(f"R {key:<50} {task.doc}")


@cli.command()
@click.argument("task_name")
@click.option("--module", default=None)
@click.pass_obj
def help(dothat_context: DothatContext, task_name: str, module: str):
    _registry = get_registry(di=dothat_context.di, module=module)

    task = _registry[task_name]

    click.echo(f"{task_name}  {task.doc}")

    for param in task.params:
        description: builtins.list[str] = [f"config: {param.name}"]

        if param.env_var:
            description.append(f"environ: {param.env_var}")
        if param.type is bool and param.inverse:
            description.append(f"opposite of {param.inverse}")

        click.echo(f"  --{param.long:<30} ({', '.join(description)})")


@cli.command(
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
    }
)
@click.argument("task_name")
@click.pass_context
@click.option("--module", default=None)
def run(ctx: click.Context, task_name: str, module: str | None):
    _registry = get_registry(di=ctx.obj.di, module=module)

    task = _registry.get(task_name)

    if task is None:
        raise click.ClickException(f"Unknown task: {task_name}")
    task = task.model_copy(deep=True)

    task.parse_task_params(args=ctx.args, di=ctx.obj.di)

    LOGGER.debug(f"running task: {task.basename}")

    task.exec_task(inj=ctx.obj.di)


if __name__ == "__main__":
    cli()
