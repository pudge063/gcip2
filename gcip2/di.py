import pathlib

import injector

from gcip2.project_config import ProjectConfig
from gcip2.tasks_core.registry import TaskRegistry


class ConfigPath:
    def __init__(self, path: pathlib.Path) -> None:
        self.path = path


class Module(injector.Module):
    def __init__(self, config_path: pathlib.Path = pathlib.Path("environment.toml")) -> None:
        self.config_path = config_path

    def configure(self, binder: injector.Binder) -> None:
        binder.bind(ConfigPath, to=ConfigPath(self.config_path), scope=injector.singleton)
        binder.bind(TaskRegistry, scope=injector.singleton)

    @injector.singleton
    @injector.provider
    def provide_config(self, cfg_path: ConfigPath) -> ProjectConfig:
        return ProjectConfig.from_file(cfg_path.path)
