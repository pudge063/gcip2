import dataclasses
from typing import Self

import injector

from gcip2.ci.jobs import assets
from gcip2.pipeline_core import JobBuilderImpl, Stage


class Base(JobBuilderImpl):
    _base = None

    def apply(self: Self) -> Self:
        self.with_stage(Stage.JOBS)
        self.model.interruptible = True
        return self


@injector.inject
@dataclasses.dataclass
class BaseLinux(JobBuilderImpl):
    _base = Base
    _scipt_linux: assets.ScriptLinux
    _after_script_linux: assets.AfterScriptLinux
    _before_script_linux: assets.BeforeScriptLinux

    def apply(self: Self) -> Self:
        self.model.after_script = [
            self._after_script_linux.script,
            "echo Do nothing.",
        ]
        self.model.before_script = [self._before_script_linux.script]
        return self


@injector.inject
@dataclasses.dataclass
class BasePython(JobBuilderImpl):
    _base = Base
    _scipt_linux: assets.ScriptLinux
    _after_script_linux: assets.AfterScriptLinux
    _before_script_linux: assets.BeforeScriptLinux

    def apply(self: Self) -> Self:
        super().apply()
        self.model.after_script = [
            self._after_script_linux.script,
            "echo Do nothing.",
        ]
        self.model.before_script = [self._before_script_linux.script]
        return self.with_compose_image("base_python")


class BaseTask(BasePython):
    _base = BasePython

    def apply(self: Self) -> Self:
        super().apply()
        self.model.after_script = [
            self._after_script_linux.script,
            "dothat run ci-after-script",
        ]
        self.model.script = [
            self._scipt_linux.script,
            "dothat run ${CI_JOB_NAME}",
        ]
        return self.with_compose_image("base_python")


class PreCommit(JobBuilderImpl):
    _name = "pre-commit"
    _base = BaseTask

    def apply(self: Self) -> Self:
        super().apply()
        return self.with_compose_image("base_python")
