from typing import Any, Optional, override
import pathlib
import yaml
import os

from . import Pipeline


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
        self,
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

    def build_pipeline(self, pipeline: Pipeline):
        pipeline = Pipeline.model_validate(pipeline, strict=True)
        result: dict[str, Any] = pipeline.dump(exclude=["jobs"])
        for job in pipeline.jobs:
            result[job.name] = job.dump(exclude=["name"])
        return result

    def build_file(self, pipeline: Pipeline, path: Optional[pathlib.Path]) -> None:
        data = yaml.dump(
            self.build_pipeline(pipeline=pipeline),
            sort_keys=False,
            allow_unicode=True,
            Dumper=CustomDumper,
        )
        path = path or pathlib.Path(os.getcwd()) / "out" / "pipeline.gitlab-ci.yml"
        with open(path, "w") as f:
            f.write(data)
