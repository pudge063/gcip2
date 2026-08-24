import builtins
import pathlib

import click
import injector

from gcip2.di import Module
from gcip2.logging import logger as LOGGER
from gcip2.tasks_core.registry import TaskRegistry
from gcip2.tasks_core.task_builder import Task


@click.group()
@click.option("--config", type=pathlib.Path, default=pathlib.Path("environment.toml"))
@click.pass_context
def cli(ctx: click.Context, config: pathlib.Path):
    ctx.obj = injector.Injector([Module(config_path=config)])


def get_registry(inj: injector.Injector, module: str | None) -> dict[str, Task]:
    if module:
        return inj.get(TaskRegistry).load_task_registry_from_module(module)
    return inj.get(TaskRegistry).tasks


@cli.command()
@click.option("--module", default=None)
@click.pass_obj
def list(inj: injector.Injector, module: str | None):
    _registry = get_registry(inj, module)

    for key, task in _registry.items():
        click.echo(f"R {key:<50} {task.doc}")


@cli.command()
@click.argument("task_name")
@click.option("--module", default=None)
@click.pass_obj
def help(inj: injector.Injector, task_name: str, module: str):
    _registry = get_registry(inj=inj, module=module)

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
    _registry = get_registry(inj=ctx.obj, module=module)

    task = _registry.get(task_name)

    if task is None:
        raise click.ClickException(f"Unknown task: {task_name}")
    task = task.model_copy(deep=True)

    task.parse_task_params(args=ctx.args)

    LOGGER.debug(f"running task: {task.basename}")

    task.exec_task()


if __name__ == "__main__":
    cli()
