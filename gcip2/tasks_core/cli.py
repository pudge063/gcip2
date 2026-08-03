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

    return {task.name: task for task in generator.load_tasks() if task.name}


def parse_task_params(
    task: Task,
    args: list[str],
) -> dict[str, object]:

    config = ProjectConfig.from_file()

    params = dict(task.params)

    if config.extra.model_extra:
        for key, val in config.extra.model_extra.items():
            params[f"extra__{key}"] = val

    args_iter = iter(args)

    for arg in args_iter:
        if not arg.startswith("--"):
            continue

        key = arg.removeprefix("--")

        param = next(
            (p for p in task.arguments if p.long == key),
            None,
        )

        if param is None:
            LOGGER.error(f"Unknown parameter: --{key}")
            raise click.ClickException(f"Unknown parameter: --{key}")

        if param.type is bool:
            params[param.name] = True
            continue

        try:
            value = next(args_iter)
        except StopIteration:
            LOGGER.error(f"Missing value for --{key}")
            raise click.ClickException(f"Missing value for --{key}")

        params[param.name] = param.type(value)

    return params


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
    task.params = parse_task_params(
        task,
        ctx.args,
    )

    LOGGER.debug(f"running task: {task.name}")

    task.exec_task()


if __name__ == "__main__":
    cli()
