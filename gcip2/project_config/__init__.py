import enum
import pathlib
import typing

import tomllib
from pydantic import BaseModel, Field


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
    secrets: Secrets = Field(default_factory=Secrets)


class ProjectConfig(BaseModel):
    @classmethod
    def from_file(cls, path: pathlib.Path = pathlib.Path("environment.toml")) -> "ProjectConfig":
        data = tomllib.loads(path.read_text())
        return cls.model_validate(data)

    extra: Extra = Field(default_factory=Extra)
