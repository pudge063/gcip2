from abc import ABC, abstractmethod
from typing import Any

from .ci_model import Pipeline


class BasePipeline(ABC):

    @abstractmethod
    def impl(self) -> Pipeline:
        pass


def pipeline(func: Any):

    func.__gcip2_pipeline__ = True

    return func
