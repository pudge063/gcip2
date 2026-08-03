import typing

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
