import enum
import pathlib
import typing

import tomllib
from pydantic import BaseModel, ConfigDict, Field


class VaultAuthMethod(str, enum.Enum):
    APPROLE = "approle"
    JWKS = "jwks"


class Vault(BaseModel):
    url: str
    auth_method: VaultAuthMethod
    app_role_id_env_var: typing.Optional[str] = None
    app_role_secret_id_env_var: typing.Optional[str] = None
    mount_point: typing.Optional[str] = None
    path: typing.Optional[str] = None


class Secrets(BaseModel):
    vault: dict[str, Vault] = Field(default_factory=dict)


class Extra(BaseModel):
    model_config = ConfigDict(extra="allow")

    secrets: Secrets = Field(default_factory=Secrets)

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
    def from_file(cls, path: pathlib.Path = pathlib.Path("environment.toml")) -> "ProjectConfig":
        data = tomllib.loads(path.read_text()) if path.exists() else {}
        return cls.model_validate(data)

    extra: Extra = Field(default_factory=Extra)
