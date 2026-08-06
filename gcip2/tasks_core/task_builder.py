import os
import typing
from collections.abc import Iterable
from enum import Enum

import pydantic

from gcip2 import ProjectConfig
from gcip2.tasks_core.models.actions import ActionBuilderImpl
from gcip2.tasks_core.models.params import Param, Params


class Task(pydantic.BaseModel):
    basename: typing.Optional[str] = None

    name: typing.Optional[str] = None

    actions: typing.Optional[list[type["ActionBuilderImpl"]]] = None

    parsed_params: dict[str, typing.Any] = {}

    params: list[Param] = pydantic.Field(default_factory=lambda: [])

    def parse_task_params(self, args: list[str]):
        _config = ProjectConfig.from_file()

        if _config.extra.model_extra:
            for key, val in _config.extra.model_extra.items():
                self.parsed_params[f"extra__{key}"] = val

        args_iter = iter(args)

        for arg in args_iter:
            if not arg.startswith("--"):
                continue

            key = arg.removeprefix("--")

            param = next(
                (p for p in self.params if key in [p.long, p.inverse]),
                None,
            )

            if not param:
                raise ValueError(f"Unknown parameter: --{key}")

            if param.type is bool:
                self.parsed_params[param.name] = True if key == param.long else False
                continue

            try:
                value = next(args_iter)
            except StopIteration as err:
                raise StopIteration from err

            self.parsed_params[param.name] = param.type(value)

    def exec_task(self):
        if not self.actions:
            raise RuntimeError("not found actions to execute.")
        for action_cls in self.actions:
            action = action_cls()
            action.execute(**self.parsed_params)


class TaskBulder:
    def build(self) -> Task:
        raise NotImplementedError


class TaskBuilderImpl(TaskBulder):
    _basename: typing.ClassVar[str | Enum | None] = None

    _params: Params = Params()

    def __init__(self):
        self.model = Task()

    def apply(self):
        return self

    def build(self) -> Task:
        if not self._basename:
            raise ValueError("task name not set.")

        if isinstance(self._basename, str):
            self.model.basename = self._basename
        else:
            self.model.basename = self._basename.value

        return self.model.model_copy(deep=True)

    def with_actions(self, actions: Iterable[type[ActionBuilderImpl]]):
        self.model.actions = list(actions)
        return self

    def with_params(self: typing.Self, params: Iterable[Param]) -> typing.Self:
        self.model.params = list(params)

        params_dict = {}
        for param in params:
            params_dict[param.name] = os.getenv(param.env_var, param.default) if param.env_var else param.default
        self.model.parsed_params = params_dict

        return self

    def replace_param(self, param_name: str, param: str, default: str):
        self.model.parsed_params[param_name] = param or default

    def with_name(self, name: str):
        self.model.name = name
        return self
