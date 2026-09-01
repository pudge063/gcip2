import importlib.util
import pathlib
import sys

import injector

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig
from gcip2.tasks_core.ci_tasks._tasks import CiTaskGenerator
from gcip2.tasks_core.task_builder import Task
from gcip2.tasks_core.task_generator import TaskGenerator


class TaskRegistry:
    @injector.inject
    def __init__(self, config: ProjectConfig, di: injector.Injector) -> None:
        self._di = di
        self._config = config

        self._tasks: dict[str, Task] | None = None

    def _load_module(self, module: str):

        module_path = pathlib.Path(module)

        LOGGER.debug(f"Tasks loaded from module: {module_path}")

        if module_path.is_file():
            module_name = module_path.stem

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load module from {module_path}")

            module_obj = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module_obj
            spec.loader.exec_module(module_obj)
            return module_obj

        sys.path.insert(0, str(module_path.parent))

        try:
            module_obj = __import__(module, fromlist=["TaskGenerator"])
        finally:
            sys.path.remove(str(module_path.parent))

        return module_obj

    def _load_tasks_from_generator(self, generator: TaskGenerator) -> dict[str, Task]:
        registry: dict[str, Task] = {}

        for task in generator.load_tasks():
            if not task.basename:
                raise ValueError("Task basename is not set.")
            taskname = task.basename if not task.name else ":".join([task.basename, task.name])
            registry[taskname] = task

        return registry

    def load_tasks_from_module(self, module: str | None) -> dict[str, Task]:
        if not module:
            LOGGER.warning("module with tasks not found")
            return {}

        module_obj = self._load_module(module)

        generator: TaskGenerator = self._di.create_object(module_obj.TaskGenerator)

        registry: dict[str, Task] = self._load_tasks_from_generator(generator)

        return registry

    @property
    def tasks(self) -> dict[str, Task]:
        if self._tasks is None:
            self._tasks = {
                **self._load_tasks_from_generator(self._di.create_object(CiTaskGenerator)),
                **self.load_tasks_from_module(self._config.extra.tasks.module),
            }
        return self._tasks
