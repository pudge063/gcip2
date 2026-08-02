import pytest
from _test_tasks._tasks import DummyTask1, DummyTask2
from click.testing import CliRunner

from gcip2.tasks_core import InteractivePythonAction, InteractiveShlex, TaskBuilderImpl, cli
from gcip2.tasks_core.task_loader import load_tasks


def test_taskbuilderimpl_name():
    class DummyTask(TaskBuilderImpl):
        task_name = "test-task-name"

        def apply(self):
            return self

    task = DummyTask().apply().build()

    assert task.name == "test-task-name"


def test_taskbuilderimpl_without_name_FAILURE():
    class DummyAction(InteractivePythonAction):
        def impl(self):
            pass

    class DummyTask(TaskBuilderImpl):

        def apply(self):
            return self.with_actions((DummyAction,))

    with pytest.raises(ValueError):
        DummyTask().apply().build()


def test_taskbuilderimpl_actions():
    class DummyAction(InteractivePythonAction):
        def impl(self):
            pass

    class DummyTask(TaskBuilderImpl):
        task_name = "test-task-3"

        def apply(self):
            return self.with_actions((DummyAction,))

    task = DummyTask().apply().build()

    assert task.actions == [DummyAction]


def test_taskbuilder_exec_task():
    class DummyAction(InteractiveShlex):
        def impl(self):
            return ["echo", "123"]

    class DummyTask(TaskBuilderImpl):
        task_name = "test-task-4"

        def apply(self):
            return self.with_actions((DummyAction,))

    task = DummyTask().apply().build()
    task.exec_task()


def test_action_InteractivePythonAction_impl():
    class DummyAction(InteractivePythonAction):
        def impl(self) -> None:
            raise NotImplementedError

    with pytest.raises(NotImplementedError):
        DummyAction().execute()


def test_action_InteractiveShlex_impl():
    class DummyAction(InteractiveShlex):
        def impl(self) -> list[str]:
            raise NotImplementedError

    with pytest.raises(NotImplementedError):
        DummyAction().execute()


def test_action_InteractiveShlex_execute():
    class DummyAction(InteractiveShlex):
        def impl(self) -> list[str]:
            return ["echo", "123"]

    DummyAction().execute()


def test_load_tasks():
    tasks: dict[str, type[TaskBuilderImpl]] = load_tasks(package="_test_tasks")

    assert tasks == {"test-task-1": DummyTask1, "test-task-2": DummyTask2}


def test_tasks_core_cli_list():
    runner = CliRunner()

    result = runner.invoke(cli.cli, ["list"])

    assert result.exit_code == 0


def test_tasks_core_run_1():
    runner = CliRunner()

    result = runner.invoke(cli.cli, ["run", "test-task-1", "--module", "_test_tasks"])

    assert result.exit_code == 0


def test_tasks_core_run_2():
    runner = CliRunner()

    result = runner.invoke(cli.cli, ["run", "test-task-2", "--module", "_test_tasks"])

    assert result.exit_code == 0
