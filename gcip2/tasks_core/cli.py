import builtins
import pathlib
import sys
from functools import lru_cache

import click

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig
from gcip2.tasks_core.ci_tasks import CI_TASK_GENERATOR
from gcip2.tasks_core.task_builder import Task
from gcip2.tasks_core.task_generator import TaskGenerator


@click.group()
def cli():
    pass


config = ProjectConfig.from_file()


def load_task_registry(generator: TaskGenerator) -> dict[str, Task]:
    registry: dict[str, Task] = {}

    for task in generator.load_tasks():
        if not task.basename:
            raise ValueError("Task basename is not set.")
        taskname = task.basename if not task.name else ":".join([task.basename, task.name])
        registry[taskname] = task

    return registry


@lru_cache
def load_task_registry_from_module(module: str) -> dict[str, Task]:
    module_path = str(pathlib.Path(module).parent)

    sys.path.insert(0, module_path)
    try:
        module_obj = __import__(module, fromlist=["TASK_GENERATOR"])
    finally:
        sys.path.remove(module_path)

    generator: TaskGenerator = module_obj.TASK_GENERATOR

    registry: dict[str, Task] = load_task_registry(generator)

    return registry


CI_TASK_REGISTRY: dict[str, Task] = load_task_registry(CI_TASK_GENERATOR)

TASK_REGISTRY: dict[str, Task] = {
    **CI_TASK_REGISTRY,
    **load_task_registry_from_module(config.extra.tasks.module),
}


@cli.command()
@click.option("--module", default=None)
def list(module: str):
    registry = load_task_registry_from_module(module) if module else TASK_REGISTRY

    for key, task in registry.items():
        click.echo(f"R {key:<50} {task.doc}")


@cli.command()
@click.argument("task_name")
@click.option("--module", default=None)
def help(task_name: str, module: str):
    registry = load_task_registry_from_module(module) if module else TASK_REGISTRY

    task = registry[task_name]

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
    registry = load_task_registry_from_module(module) if module else TASK_REGISTRY

    task = registry.get(task_name)

    if task is None:
        raise click.ClickException(f"Unknown task: {task_name}")
    task = task.model_copy(deep=True)

    task.parse_task_params(args=ctx.args)

    LOGGER.debug(f"running task: {task.basename}")

    task.exec_task()


if __name__ == "__main__":
    cli()
