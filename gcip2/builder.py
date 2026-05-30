import importlib.util
import os
import pathlib
from enum import Enum
from typing import Any, Optional, Self

import yaml
from typing_extensions import override

from .pipeline_core import (
    Artifacts,
    Job,
    JobBuilderImpl,
    Needs,
    Pipeline,
    PipelineBuilderImpl,
    Trigger,
    TriggerIncludeArtifact,
)


class CustomDumper(yaml.SafeDumper):
    @staticmethod
    def str_presenter(
        dumper: yaml.representer.BaseRepresenter,
        data: str,
    ) -> yaml.ScalarNode:
        if "\n" in data:
            return dumper.represent_scalar(  # type: ignore
                "tag:yaml.org,2002:str",
                data,
                style="|",
            )

        return dumper.represent_scalar(  # type: ignore
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


class TriggerPipelineDefaults(str, Enum):
    build_pipeline = "build-pipeline"
    trigger_pipeline = "trigger-pipeline"
    out_dir = "out"
    out_file = "out/pipeline.gitlab-ci.yml"


class PipelineBuilder:
    yaml_dumper = CustomDumper

    @staticmethod
    def _gen_build_pipeline_job():
        return Job(
            name=TriggerPipelineDefaults.build_pipeline,
            before_script=[
                "pip3 install poetry",
            ],
            script=[
                "poetry install && . .venv/bin/activate",
                "gcip2 build-pipeline",
            ],
            tags=["immortal"],
            artifacts=Artifacts(paths=[TriggerPipelineDefaults.out_dir]),
        )

    @staticmethod
    def _gen_trigger_pipeline_job():
        return Job(
            name=TriggerPipelineDefaults.trigger_pipeline,
            trigger=Trigger(
                include=[
                    TriggerIncludeArtifact(
                        artifact=TriggerPipelineDefaults.out_file,
                        job=TriggerPipelineDefaults.build_pipeline,
                    )
                ],
            ),
            needs=[
                Needs(
                    job=TriggerPipelineDefaults.build_pipeline,
                    artifacts=True,
                )
            ],
        )

    def build_gitlab_ci(
        self: Self,
        out_gitlab_ci: Any,
        default_tags: str,
    ) -> None:
        pipeline_obj = Pipeline(
            jobs=[
                self._gen_build_pipeline_job(),
                self._gen_trigger_pipeline_job(),
            ]
        )
        self.build_pipeline_file(
            pipeline=pipeline_obj,
            path=out_gitlab_ci,
            default_tags=default_tags,
        )

    def load_pipeline(self: Self, path: Any) -> PipelineBuilderImpl:
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

            if isinstance(obj, type) and issubclass(obj, PipelineBuilderImpl) and obj is not PipelineBuilderImpl:
                return obj()

        raise RuntimeError("Pipeline class not found")

    def render_pipeline(self: Self, pipeline: Pipeline):
        pipeline = Pipeline.model_validate(pipeline, strict=True)
        result: dict[str, Any] = pipeline.dump(exclude=["jobs"])

        for job in pipeline.jobs:
            if isinstance(job, JobBuilderImpl):
                job = job.build()
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
        pipeline_copy = pipeline.model_copy(deep=True)
        if default_tags:
            for job in pipeline_copy.jobs:
                if job.name == TriggerPipelineDefaults.build_pipeline:
                    job.tags = default_tags.split(sep=" ")

        data = yaml.dump(
            self.render_pipeline(pipeline=pipeline_copy),
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
            pipeline: Pipeline = pipeline_entry()  # type: ignore

        # class API
        else:
            pipeline: Pipeline = pipeline_entry.apply().build()

        self.build_pipeline_file(
            pipeline=pipeline,  # type: ignore
            path=pathlib.Path(out_pipeline_path),
        )
