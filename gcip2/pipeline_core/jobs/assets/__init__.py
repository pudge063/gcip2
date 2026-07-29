import dataclasses
import pathlib
import typing

ASSERTS_DIR = pathlib.Path(__file__).parent


@dataclasses.dataclass
class TextAsset:
    script: str
    path: pathlib.Path
    relative_path: typing.ClassVar[str]

    @classmethod
    def load(cls) -> typing.Self:
        path = ASSERTS_DIR / cls.relative_path
        return cls(script=path.read_text(), path=path)


class ScriptLinux(TextAsset):
    relative_path = "script_linux.sh"
