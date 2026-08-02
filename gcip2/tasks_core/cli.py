import builtins

import click

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig
from gcip2.tasks_core.task_builder import TaskBuilderImpl
from gcip2.tasks_core.task_loader import load_tasks


@click.group()
def cli():
    pass


config = ProjectConfig.from_file()

TASK_REGISTRY: dict[str, type[TaskBuilderImpl]] = load_tasks(config.extra.tasks.module)


@cli.command()
def list():
    LOGGER.info(builtins.list(TASK_REGISTRY.keys()))


@cli.command()
@click.argument("task_name")
@click.option("--module", default=None)
def run(task_name: str, module: str | None):
    registry = load_tasks(module or config.extra.tasks.module) if module else TASK_REGISTRY

    task_cls = registry.get(task_name)

    if task_cls is None:
        raise click.ClickException(f"Unknown task: {task_name}")

    task = task_cls().apply().build()
    LOGGER.debug(f"running task: {task.name}")
    task.exec_task()


if __name__ == "__main__":
    cli()
