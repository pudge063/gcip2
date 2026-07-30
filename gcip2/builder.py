import importlib.util
import os
import pathlib
from enum import Enum
from typing import Any, Optional, Self, TypeVar

import yaml
from typing_extensions import override

from gcip2.pipeline_core.gitlab_ci import GitlabCiBuilderImpl
from gcip2.pipeline_core.pipeline import PipelineBuilderImpl

from .pipeline_core import JobBuilderImpl, Pipeline, Stage, WorkflowRule, WorkflowWhen
from .pipeline_core.jobs import trigger

T = TypeVar("T", PipelineBuilderImpl, GitlabCiBuilderImpl)


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
    out_file = "out/pipeline.gitlab-ci.yml"


class PipelineBuilder:
    yaml_dumper = CustomDumper

    def load_pipeline(
        self: Self,
        path: Any,
        obj_type: type[T],
    ) -> T:
        path = pathlib.Path(path)
        spec: Any = importlib.util.spec_from_file_location(
            "user_pipeline",
            path,
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for obj in module.__dict__.values():
            if isinstance(obj, type) and issubclass(obj, obj_type) and obj is not obj_type:
                return obj()

        raise RuntimeError(f"{obj_type.__name__} child class not found")

    def render_pipeline(self: Self, pipeline: Pipeline) -> dict[str, Any]:
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
        **_: Any,
    ) -> None:
        os.makedirs("out", exist_ok=True)
        pipeline_copy = pipeline.model_copy(deep=True)

        data = yaml.dump(
            self.render_pipeline(pipeline=pipeline_copy),
            sort_keys=False,
            allow_unicode=True,
            Dumper=CustomDumper,
        )

        path = path or pathlib.Path(os.getcwd()) / TriggerPipelineDefaults.out_file.value
        with open(path, "w") as f:
            f.write(data)

    def build_gitlab_ci(
        self: Self,
        ci_file_path: str,
        out_gitlab_ci: Any,
    ) -> None:
        _build_trigger_pipeline = trigger.BuildTriggerPipeline()
        _trigger_pipeline = trigger.TriggerPipeline()

        pipeline_entry = self.load_pipeline(ci_file_path, obj_type=GitlabCiBuilderImpl)

        pipeline_obj: Pipeline = pipeline_entry.apply().build()

        downstream_rule = WorkflowRule(
            if_='$CI_PIPELINE_SOURCE == "parent_pipeline"',
            when=WorkflowWhen.ALWAYS,
        )

        if not pipeline_obj.jobs:
            pipeline_obj.jobs = [_build_trigger_pipeline.apply(), _trigger_pipeline.apply()]

        if pipeline_obj.workflow and pipeline_obj.workflow.rules and downstream_rule not in pipeline_obj.workflow.rules:
            pipeline_obj.workflow.rules = [downstream_rule] + pipeline_obj.workflow.rules

        if not pipeline_obj.stages:
            pipeline_entry.stages = [Stage.JOBS]

        self.build_pipeline_file(
            pipeline=pipeline_obj,
            path=out_gitlab_ci,
        )

    def build_pipeline(
        self: Self,
        ci_file_path: str,
        out_pipeline_path: str,
    ) -> None:
        pipeline_entry: PipelineBuilderImpl = self.load_pipeline(ci_file_path, obj_type=PipelineBuilderImpl)

        pipeline_obj: Pipeline = pipeline_entry.apply().build()

        downstream_rule = WorkflowRule(
            if_='$CI_PIPELINE_SOURCE == "parent_pipeline"',
            when=WorkflowWhen.ALWAYS,
        )

        if pipeline_obj.workflow and pipeline_obj.workflow.rules and downstream_rule not in pipeline_obj.workflow.rules:
            pipeline_obj.workflow.rules = [downstream_rule] + pipeline_obj.workflow.rules

        self.build_pipeline_file(
            pipeline=pipeline_obj,
            path=pathlib.Path(out_pipeline_path),
        )
