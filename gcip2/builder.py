import importlib.util
import os
import pathlib
from typing import Any, Optional, Self

import yaml
from typing_extensions import override

from . import BasePipeline, Pipeline, TriggerPipeline


class CustomDumper(yaml.SafeDumper):
    @staticmethod
    def str_presenter(
        dumper: yaml.representer.BaseRepresenter,
        data: str,
    ) -> yaml.ScalarNode:
        if "\n" in data:
            return dumper.represent_scalar(
                "tag:yaml.org,2002:str",
                data,
                style="|",
            )

        return dumper.represent_scalar(
            "tag:yaml.org,2002:str",
            data,
        )

    yaml_representers = {
        **yaml.SafeDumper.yaml_representers,
        str: str_presenter,
    }

    @override
    def increase_indent(
        self: Self,
        flow: bool = False,
        indentless: bool = False,
    ):
        return super().increase_indent(flow, False)

    @override
    def write_line_break(self, data: Optional[str] = None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()


class PipelineBuilder:
    yaml_dumper = CustomDumper

    def build_gitlab_ci(
        self: Self,
        out_gitlab_ci: Any,
        default_tags: str,
    ) -> None:
        pipeline_obj = TriggerPipeline()
        self.build_pipeline_file(
            pipeline=pipeline_obj.impl(),
            path=out_gitlab_ci,
            default_tags=default_tags,
        )

    def load_pipeline(self: Self, path: Any) -> BasePipeline:
        path = pathlib.Path(path)
        spec: Any = importlib.util.spec_from_file_location(
            "user_pipeline",
            path,
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for obj in module.__dict__.values():

            if callable(obj) and getattr(obj, "__gcip2_pipeline__", False):
                return obj  # type: ignore

            if isinstance(obj, type) and issubclass(obj, BasePipeline) and obj is not BasePipeline:
                return obj()

        raise RuntimeError("Pipeline class not found")

    def render_pipeline(self: Self, pipeline: Pipeline):
        pipeline = Pipeline.model_validate(pipeline, strict=True)
        result: dict[str, Any] = pipeline.dump(exclude=["jobs"])

        for job in pipeline.jobs:
            if not job.name:
                raise ValueError("Job name is missing.")
            if job.name in result.keys():
                raise ValueError("Job with same name already added.")
            result[job.name] = job.dump(exclude=["name"])
        return result

    def build_pipeline_file(
        self: Self,
        pipeline: Pipeline,
        path: Optional[pathlib.Path],
        default_tags: Optional[str] = None,
        **_: Any,
    ) -> None:
        os.makedirs("out", exist_ok=True)

        if default_tags:
            for job in pipeline.jobs:
                if job.name == "build-pipeline":
                    job.tags = default_tags.split(sep=" ")

        data = yaml.dump(
            self.render_pipeline(pipeline=pipeline),
            sort_keys=False,
            allow_unicode=True,
            Dumper=CustomDumper,
        )
        path = path or pathlib.Path(os.getcwd()) / "out" / "pipeline.gitlab-ci.yml"
        with open(path, "w") as f:
            f.write(data)

    def build_pipeline(self: Self, ci_file_path: str, out_pipeline_path: str) -> None:
        pipeline_entry = self.load_pipeline(ci_file_path)

        # decorator API
        if callable(pipeline_entry):
            pipeline = pipeline_entry()  # type: ignore

        # class API
        else:
            pipeline = pipeline_entry.impl()

        if not isinstance(pipeline, Pipeline):
            raise TypeError("Unexcepted type of Pipeline")

        self.build_pipeline_file(
            pipeline=pipeline,
            path=pathlib.Path(out_pipeline_path),
        )
