import enum
import os
import typing

T = typing.TypeVar("T")


class VarEnum(str, enum.Enum):
    @typing.override
    def __repr__(self) -> str:
        return self.name

    @typing.override
    def __str__(self) -> str:
        return self.__repr__()

    def __call__(self) -> typing.Optional[str]:
        return self.getenv()

    def getenv(self, default: typing.Optional[T] = None) -> typing.Optional[T | str]:
        return os.getenv(key=self.name, default=default)

    def must(self) -> str:
        value = self.getenv()
        if not value:
            raise ValueError(f"could not get variable from env: {self.name}")
        return value


class Predefined(VarEnum, enum.Enum):
    CHAT_CHANNEL = enum.auto()
    CHAT_INPUT = enum.auto()
    CI_API_V4_URL = enum.auto()
    CI_COMMIT_BRANCH = enum.auto()
    CI_DEFAULT_BRANCH = enum.auto()
    CI_PIPELINE_SOURCE = enum.auto()
    CI_JOB_IMAGE = enum.auto()
