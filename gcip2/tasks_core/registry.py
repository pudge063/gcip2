import pathlib
import sys

import injector

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig
from gcip2.tasks_core.ci_tasks._tasks import CI_TASK_GENERATOR
from gcip2.tasks_core.task_builder import Task
from gcip2.tasks_core.task_generator import TaskGenerator


class TaskRegistry:
    @injector.inject
    def __init__(self, config: ProjectConfig) -> None:
        self._config = config
        self._tasks: dict[str, Task] | None = None

    def load_task_registry(self, generator: TaskGenerator) -> dict[str, Task]:
        registry: dict[str, Task] = {}

        for task in generator.load_tasks():
            if not task.basename:
                raise ValueError("Task basename is not set.")
            taskname = task.basename if not task.name else ":".join([task.basename, task.name])
            registry[taskname] = task

        return registry

    def load_task_registry_from_module(self, module: str | None) -> dict[str, Task]:
        if not module:
            LOGGER.warning("module with tasks not found")
            return {}

        module_path = str(pathlib.Path(module).parent)

        sys.path.insert(0, module_path)
        try:
            module_obj = __import__(module, fromlist=["TASK_GENERATOR"])
        finally:
            sys.path.remove(module_path)

        generator: TaskGenerator = module_obj.TASK_GENERATOR

        registry: dict[str, Task] = self.load_task_registry(generator)

        return registry

    @property
    def tasks(self) -> dict[str, Task]:
        if self._tasks is None:
            self._tasks = {
                **self.load_task_registry(CI_TASK_GENERATOR),
                **self.load_task_registry_from_module(self._config.extra.tasks.module),
            }
        return self._tasks
