import typing
from collections.abc import Iterable

from pydantic import BaseModel, Field

from gcip2.tasks_core.actions import ActionBuilderImpl


class TaskBuilder(BaseModel):
    name: typing.Optional[str] = None

    actions: typing.Optional[list[type["ActionBuilderImpl"]]] = None

    params: typing.Optional[list[typing.Any]] = None

    def exec_task(self):
        if not self.actions:
            raise RuntimeError("not found actions to execute.")
        for action_cls in self.actions:
            action = action_cls()
            action.execute()


class TaskBuilderImpl(TaskBuilder):
    task_name: typing.ClassVar[str | None] = None

    model: TaskBuilder = Field(
        repr=False,
        default_factory=TaskBuilder,
        init=False,
    )

    def apply(self):
        return self

    def build(self) -> TaskBuilder:
        if not self.task_name:
            raise ValueError("task name not set.")

        if self.task_name:
            self.model.name = self.task_name
        return self.model.model_copy(deep=True)

    def with_actions(self, actions: Iterable[type["ActionBuilderImpl"]]):
        self.model.actions = list(actions)
        return self
