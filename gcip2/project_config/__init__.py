import pathlib
import tomllib
import typing

from pydantic import BaseModel, ConfigDict, Field

from gcip2.project_config.compose import Compose
from gcip2.project_config.vault_config import Vault


class Secrets(BaseModel):
    vault: dict[str, Vault] = Field(default_factory=dict)


class Tasks(BaseModel):
    module: typing.Optional[str] = None


class Extra(BaseModel):
    model_config = ConfigDict(extra="allow")

    secrets: Secrets = Field(default_factory=Secrets)

    tasks: Tasks = Field(default_factory=Tasks)

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
        data = tomllib.loads(path.read_text()) if path.exists() else {}
        return cls.model_validate(data)

    compose: Compose = Compose.load()

    extra: Extra = Field(default_factory=Extra)
