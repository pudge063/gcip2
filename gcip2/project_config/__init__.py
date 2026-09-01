import pathlib
import tomllib
import typing

from pydantic import BaseModel, ConfigDict, Field

from gcip2.logging import logger as LOGGER
from gcip2.project_config.compose import Compose
from gcip2.project_config.vault_config import VaultConfig


class Secrets(BaseModel):
    vault: dict[str, VaultConfig] = Field(default_factory=dict)


class System(BaseModel):
    tasks_module: typing.Optional[str] = None
    compose_path: typing.Optional[str] = None


class Extra(BaseModel):
    model_config = ConfigDict(extra="allow")

    secrets: Secrets = Field(default_factory=Secrets)

    system: System = Field(default_factory=System)

    def __getitem__(self, key: str) -> typing.Any:
        if key == "secrets":
            return self.secrets

        if self.model_extra is None:
            raise KeyError(key)

        return self.model_extra[key]

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        if key == "secrets":
            return self.secrets

        return (self.model_extra or {}).get(key, default)


class ProjectConfig(BaseModel):
    @classmethod
    def from_file(
        cls,
        path: pathlib.Path = pathlib.Path("environment.toml"),
    ) -> "ProjectConfig":
        if not path.exists():
            LOGGER.debug("ProjectConfig is not provided: file is not exists")
            data = {}
        else:
            data = tomllib.loads(path.read_text())

        _cfg = cls.model_validate(data)

        compose_path = _cfg.extra.system.compose_path or "docker-compose.yml"
        LOGGER.warning(compose_path)
        _cfg.compose = Compose.load(pathlib.Path(compose_path))

        return _cfg

    compose: Compose = Field(default_factory=Compose)

    extra: Extra = Field(default_factory=Extra)
