import builtins
from functools import lru_cache

import click

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig
from gcip2.tasks_core.task_builder import Task
from gcip2.tasks_core.task_generator import TaskGenerator


@click.group()
def cli():
    pass


config = ProjectConfig.from_file()


@lru_cache
def load_task_registry(module: str) -> dict[str, Task]:
    module_obj = __import__(module, fromlist=["TASK_GENERATOR"])

    generator: TaskGenerator = module_obj.TASK_GENERATOR

    registry: dict[str, Task] = {}

    for task in generator.load_tasks():
        if not task.basename:
            raise ValueError("Task basename is not set.")
        taskname = task.basename if not task.name else ":".join([task.basename, task.name])
        registry[taskname] = task

    return registry


TASK_REGISTRY: dict[str, Task] = load_task_registry(config.extra.tasks.module)


@cli.command()
@click.option("--module", default=None)
def list(module: str):
    registry = load_task_registry(module) if module else TASK_REGISTRY
    LOGGER.info(builtins.list(registry.keys()))


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
    registry = load_task_registry(module) if module else TASK_REGISTRY

    task = registry.get(task_name)

    if task is None:
        raise click.ClickException(f"Unknown task: {task_name}")
    task = task.model_copy(deep=True)

    task.parse_task_params(args=ctx.args)

    LOGGER.debug(f"running task: {task.basename}")

    task.exec_task()


if __name__ == "__main__":
    cli()
