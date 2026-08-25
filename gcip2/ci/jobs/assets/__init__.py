import dataclasses
import pathlib
import typing

ASSETS_DIR = pathlib.Path(__file__).parent


@dataclasses.dataclass
class TextAsset:
    script: str
    path: pathlib.Path
    relative_path: typing.ClassVar[str]

    @classmethod
    def load(cls) -> typing.Self:
        path = ASSETS_DIR / cls.relative_path
        return cls(script=path.read_text(), path=path)


class AfterScriptLinux(TextAsset):
    relative_path = "after_script_linux.sh"


class BeforeScriptLinux(TextAsset):
    relative_path = "before_script_linux.sh"


class ScriptLinux(TextAsset):
    relative_path = "script_linux.sh"
