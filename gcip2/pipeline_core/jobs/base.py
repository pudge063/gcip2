from typing import Self

from gcip2.pipeline_core import JobBuilderImpl, Stage

from ..jobs import assets


class Base(JobBuilderImpl):
    _base = None

    def apply(self: Self) -> Self:
        self.with_stage(Stage.JOBS)
        self.model.interruptible = True
        return self


class BaseLinux(JobBuilderImpl):
    _base = Base
    _scipt_linux: assets.ScriptLinux = assets.ScriptLinux.load()

    def apply(self: Self) -> Self:
        self.model.after_script = [
            self._scipt_linux.script,
            "echo Do nothing.",
        ]
        self.model.before_script = [self._scipt_linux.script]
        return self
