import importlib.util
import pathlib
from typing import Any


from . import PipelineBuilder, BasePipeline, Pipeline


def load_pipeline(path: Any):
    path = pathlib.Path(path)
    spec: Any = importlib.util.spec_from_file_location(
        "user_pipeline",
        path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for obj in module.__dict__.values():

        if callable(obj) and getattr(obj, "__gcip2_pipeline__", False):
            return obj

        if isinstance(obj, type) and issubclass(obj, BasePipeline) and obj is not BasePipeline:
            return obj()

    raise RuntimeError("Pipeline class not found")


def build_pipeline(path: str = "test_pipeline.py"):

    pipeline_entry = load_pipeline(path)

    # decorator API
    if callable(pipeline_entry):
        pipeline = pipeline_entry()

    # class API
    else:
        pipeline = pipeline_entry.impl()

    builder = PipelineBuilder()

    if not isinstance(pipeline, Pipeline):
        raise TypeError("Unexcepted type of Pipeline")

    builder.build_file(
        pipeline=pipeline,
        path=pathlib.Path("out/pipeline.gitlab-ci.yml"),
    )
