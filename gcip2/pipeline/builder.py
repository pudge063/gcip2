import importlib.util
import os
import pathlib
import sys
from difflib import unified_diff
from enum import Enum
from typing import Any, Optional, Self, TypeVar

import injector
import yaml

from gcip2.ci.jobs import trigger
from gcip2.logging import logger as LOGGER
from gcip2.pipeline.dumper import CustomDumper
from gcip2.pipeline.pipeline import GitlabCiBuilderImpl, PipelineBuilderImpl
from gcip2.pipeline_core import JobBuilderImpl, Pipeline, Stage, WorkflowRule, WorkflowWhen

T = TypeVar("T", PipelineBuilderImpl, GitlabCiBuilderImpl)


class TriggerPipelineDefaults(str, Enum):
    out_file = "out/pipeline.gitlab-ci.yml"


class PipelineBuilder:
    yaml_dumper = CustomDumper

    @injector.inject
    def __init__(self, di: injector.Injector) -> None:
        self._di = di

    @staticmethod
    def show_file_diff(path: pathlib.Path, data: str):
        old_data = path.read_text() if path.exists() else ""

        diff = unified_diff(
            old_data.splitlines(),
            data.splitlines(),
            fromfile="old",
            tofile="new",
            lineterm="",
        )

        diff_data = [s for s in diff]
        diff_string = "\n".join([f"pipeline: {path}"] + diff_data)

        LOGGER.warning(diff_string) if diff_data else LOGGER.info(f"pipeline: {path} has no changes")

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
        path_str = str(path.parent)
        sys.path.insert(0, path_str)
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.remove(path_str)

        for obj in module.__dict__.values():
            if isinstance(obj, type) and issubclass(obj, obj_type) and obj is not obj_type:
                return self._di.create_object(obj)

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

        self.show_file_diff(path=path, data=data)

        path.write_text(data)

    def build_gitlab_ci(
        self: Self,
        ci_file_path: pathlib.Path,
        out_gitlab_ci: pathlib.Path,
    ) -> None:
        _build_trigger_pipeline = self._di.create_object(trigger.BuildTriggerPipeline)
        _trigger_pipeline = self._di.create_object(trigger.TriggerPipeline)

        pipeline_entry = self.load_pipeline(ci_file_path, obj_type=GitlabCiBuilderImpl)

        pipeline_obj: Pipeline = pipeline_entry.apply().build()

        downstream_rule = WorkflowRule(
            if_='$CI_PIPELINE_SOURCE == "parent_pipeline"',
            when=WorkflowWhen.ALWAYS,
        )

        if not pipeline_obj.jobs:
            pipeline_obj.jobs = [
                _build_trigger_pipeline.apply(),
                _trigger_pipeline.apply(),
            ]

        if pipeline_obj.workflow and pipeline_obj.workflow.rules and downstream_rule not in pipeline_obj.workflow.rules:
            pipeline_obj.workflow.rules = [downstream_rule] + pipeline_obj.workflow.rules

        if not pipeline_obj.stages:
            pipeline_obj.stages = [Stage.JOBS]

        self.build_pipeline_file(
            pipeline=pipeline_obj,
            path=out_gitlab_ci,
        )

    def build_pipeline(
        self: Self,
        ci_file_path: pathlib.Path,
        out_pipeline_path: pathlib.Path,
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
            path=out_pipeline_path,
        )
