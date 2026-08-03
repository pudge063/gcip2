import typing
from collections.abc import Iterable
from enum import Enum

import pydantic

from gcip2.tasks_core.models.actions import ActionBuilderImpl
from gcip2.tasks_core.models.params import Param


class Task(pydantic.BaseModel):
    name: typing.Optional[str] = None

    actions: typing.Optional[list[type["ActionBuilderImpl"]]] = None

    params: dict[str, typing.Any] = {}

    arguments: list[Param] = pydantic.Field(default_factory=lambda: [])

    def exec_task(self):
        if not self.actions:
            raise RuntimeError("not found actions to execute.")
        for action_cls in self.actions:
            action = action_cls()
            action.execute(**self.params)


class TaskBulder:
    def build(self) -> Task:
        raise NotImplementedError


class TaskBuilderImpl(TaskBulder):
    _basename: typing.ClassVar[str | Enum | None] = None

    def __init__(self):
        self.model = Task()

    def apply(self):
        return self

    def build(self) -> Task:
        if not self._basename:
            raise ValueError("task name not set.")

        if isinstance(self._basename, str):
            self.model.name = self._basename
        else:
            self.model.name = self._basename.value

        return self.model.model_copy(deep=True)

    def with_actions(self, actions: Iterable[type[ActionBuilderImpl]]):
        self.model.actions = list(actions)
        return self

    def with_params(self: typing.Self, params: Iterable[Param]) -> typing.Self:
        self.model.arguments = list(params)

        params_dict = {}
        for param in params:
            params_dict[param.name] = param.default
        self.model.params = params_dict

        return self
