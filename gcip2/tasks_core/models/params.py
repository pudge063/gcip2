import dataclasses
import typing

import injector
import pydantic

from gcip2.project_config import ProjectConfig


class Param(pydantic.BaseModel):
    name: str
    default: typing.Any = None
    long: str

    short: typing.Optional[str] = ""
    type: typing.Callable[[typing.Any], typing.Any] = lambda x: x
    help: typing.Optional[str] = None
    env_var: typing.Optional[str] = None
    inverse: typing.Optional[str] = None


@injector.inject
@dataclasses.dataclass
class Params:
    config: ProjectConfig

    def ci(self):
        return Param(
            name="ci",
            long="ci",
            type=bool,
            default=False,
            env_var="CI",
        )

    def from_config(self, key: str, **kwargs):
        return Param(
            name=f"extra__{key}",
            long=key.replace("_", "-"),
            default=(self.config.extra.model_extra or {}).get(key),
            **kwargs,
        )
