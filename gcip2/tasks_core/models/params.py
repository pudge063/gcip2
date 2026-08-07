import typing
from dataclasses import dataclass

import pydantic


class Param(pydantic.BaseModel):
    name: str
    default: typing.Any = None
    long: str

    short: typing.Optional[str] = ""
    type: typing.Callable[[typing.Any], typing.Any] = lambda x: x
    help: typing.Optional[str] = None
    env_var: typing.Optional[str] = None
    inverse: typing.Optional[str] = None


@dataclass
class Params:
    def ci(self):
        return Param(
            name="ci",
            long="ci",
            type=bool,
            default=False,
            env_var="CI",
        )
