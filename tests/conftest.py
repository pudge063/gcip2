import pathlib

import injector
import pytest

from gcip2.di import Module
from gcip2.tasks_core.models.actions import ActionBuilderImpl
from gcip2.tasks_core.task_builder import TaskBuilderImpl

REPO_ROOT = pathlib.Path(__file__).parents[1]


@pytest.fixture
def di() -> injector.Injector:
    return injector.Injector([Module(config_path=REPO_ROOT / "environment.toml")])


@pytest.fixture
def build_dummy_task(di: injector.Injector):
    def _build(task_class: type[TaskBuilderImpl]):
        return di.create_object(task_class).apply().build()

    return _build


@pytest.fixture
def build_dummy_action(di: injector.Injector):
    def _build(action_class: type[ActionBuilderImpl]):
        return di.create_object(action_class)

    return _build
