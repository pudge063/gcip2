from typing import Self

from gcip2.pipeline_core import JobBuilderImpl, Stage

from . import assets


class Base(JobBuilderImpl):
    _base = None

    def apply(self: Self) -> Self:
        self.with_stage(Stage.JOBS)
        self.model.interruptible = True
        return self


class BaseLinux(JobBuilderImpl):
    _base = Base
    _scipt_linux: assets.ScriptLinux = assets.ScriptLinux.load()
    _after_script_linux: assets.AfterScriptLinux = assets.AfterScriptLinux.load()
    _before_script_linux: assets.BeforeScriptLinux = assets.BeforeScriptLinux.load()

    def apply(self: Self) -> Self:
        self.model.after_script = [
            self._after_script_linux.script,
            "echo Do nothing.",
        ]
        self.model.before_script = [self._before_script_linux.script]
        return self


class BasePython(JobBuilderImpl):
    _base = Base
    _scipt_linux: assets.ScriptLinux = assets.ScriptLinux.load()
    _after_script_linux: assets.AfterScriptLinux = assets.AfterScriptLinux.load()
    _before_script_linux: assets.BeforeScriptLinux = assets.BeforeScriptLinux.load()

    def apply(self: Self) -> Self:
        super().apply()
        self.model.after_script = [
            self._after_script_linux.script,
            "echo Do nothing1.",
        ]
        self.model.before_script = [self._before_script_linux.script]
        return self.with_compose_image("base_python")


class BaseTask(BasePython):
    _base = BaseLinux
    _scipt_linux: assets.ScriptLinux = assets.ScriptLinux.load()
    _after_script_linux: assets.AfterScriptLinux = assets.AfterScriptLinux.load()
    _before_script_linux: assets.BeforeScriptLinux = assets.BeforeScriptLinux.load()

    def apply(self: Self) -> Self:
        super().apply()
        self.model.after_script = [
            self._after_script_linux.script,
            "echo Do nothing.",
        ]
        self.model.script = [self._scipt_linux.script, "dothat run ${CI_JOB_NAME}"]
        self.model.before_script = [self._before_script_linux.script]
        return self.with_compose_image("base_python")
