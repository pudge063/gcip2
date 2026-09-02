import pathlib
import typing

import injector
import pytest
from click.testing import CliRunner

from gcip2.di import Module
from gcip2.pipeline_core import JobBuilderImpl
from gcip2.project_config import ProjectConfig
from gcip2.tasks_core import (
    InteractivePythonAction,
    InteractiveShlex,
    TaskBuilderImpl,
    cli,
)
from tests.unit import _test_tasks

INJECTOR = injector.Injector([Module(config_path=pathlib.Path("environment.toml"))])


def test_taskbuilderimpl_name(build_dummy_task):
    class DummyTask(TaskBuilderImpl):
        _basename = "test-task-name"

    assert build_dummy_task(DummyTask).basename == "test-task-name"


def test_taskbuilderimpl_without_name_FAILURE(build_dummy_task):
    class DummyAction(InteractivePythonAction):
        def impl(self, **kwargs: typing.Any):
            pass

    class DummyTask(TaskBuilderImpl):
        def apply(self):
            return self.with_actions((DummyAction,))

    with pytest.raises(ValueError):
        build_dummy_task(DummyTask)


def test_taskbuilderimpl_actions(build_dummy_task):
    class DummyAction(InteractivePythonAction):
        def impl(self, **kwargs: typing.Any):
            pass

    class DummyTask(TaskBuilderImpl):
        _basename = "test-task-3"

        def apply(self):
            return self.with_actions((DummyAction,))

    assert build_dummy_task(DummyTask).actions == [DummyAction]


def test_taskbuilder_exec_task(build_dummy_task, di):
    class DummyAction(InteractiveShlex):
        def impl(self, **kwargs: typing.Any):
            return [["echo", "123"]]

    class DummyTask(TaskBuilderImpl):
        _basename = "test-task-4"

        def apply(self):
            return self.with_actions((DummyAction,))

    build_dummy_task(DummyTask).exec_task(di)


def test_action_InteractivePythonAction_impl(build_dummy_action):
    class DummyAction(InteractivePythonAction):
        def impl(self, **kwargs: typing.Any) -> None:
            raise NotImplementedError

    with pytest.raises(NotImplementedError):
        build_dummy_action(DummyAction).execute()


def test_action_InteractiveShlex_impl(build_dummy_action):
    class DummyAction(InteractiveShlex):
        def impl(self, **kwargs: typing.Any) -> list[list[str]]:
            raise NotImplementedError

    with pytest.raises(NotImplementedError):
        build_dummy_action(DummyAction).execute()


def test_action_InteractiveShlex_execute(build_dummy_action):
    class DummyAction(InteractiveShlex):
        def impl(self, **kwargs: typing.Any) -> list[list[str]]:
            return [["echo", "123"]]

    build_dummy_action(DummyAction).execute()


def test_tasks_core_cli_list():
    runner = CliRunner()

    result = runner.invoke(cli.cli, ["list", "--module", "tests.unit._test_tasks"])

    assert result.exit_code == 0


def test_tasks_core_run_1():
    runner = CliRunner()

    result = runner.invoke(cli.cli, ["run", "test-task-1", "--module", "tests.unit._test_tasks"])

    assert result.exit_code == 0


def test_tasks_core_run_2():
    runner = CliRunner()

    result = runner.invoke(cli.cli, ["run", "test-task-2", "--module", "_test_tasks"])

    assert result.exit_code == 0


def test_tasks_core_run_3_output(di, capfd):
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["run", "test-task-3", "--ci", "--module", "tests.unit._test_tasks"])
    assert result.exit_code == 0

    out, _ = capfd.readouterr()
    assert di.get(ProjectConfig).extra.get("version") in out


def test_build_command(di):
    action = di.create_object(_test_tasks.CheckShellCmd)
    assert action.impl(ci=True, extra__version=di.get(ProjectConfig).extra.get("version")) == [
        ["echo", di.get(ProjectConfig).extra.get("version")]
    ]


def test_custom_config_path():
    marker = "custom-marker"

    tmp_path = pathlib.Path("out/tmp")
    tmp_path.mkdir(exist_ok=True, parents=True)
    cfg = tmp_path / "custom.toml"
    cfg.write_text(f'[extra]\nmarker = "{marker}"')

    di = injector.Injector([Module(config_path=cfg)])

    job = di.create_object(JobBuilderImpl)

    assert job._config.extra.get("marker") == marker


def test_config_singleton(di):
    assert di.create_object(JobBuilderImpl)._config is di.get(ProjectConfig)
