import importlib
import inspect
import pkgutil

from gcip2.tasks_core.task_builder import TaskBuilderImpl


def load_tasks(package: str) -> dict[str, type[TaskBuilderImpl]]:
    package_module = importlib.import_module(package)

    result: dict[str, type[TaskBuilderImpl]] = {}

    for _, module_name, _ in pkgutil.iter_modules(package_module.__path__):
        module = importlib.import_module(f"{package}.{module_name}")

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, TaskBuilderImpl) and cls is not TaskBuilderImpl and cls.task_name:
                result[cls.task_name] = cls

    return result
