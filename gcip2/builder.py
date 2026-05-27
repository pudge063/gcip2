from typing import Any, Optional
import pathlib
import yaml
import os

from . import Pipeline


class PipelineBuilder:
    def build_pipeline(self, pipeline: Pipeline):
        pipeline = Pipeline.model_validate(pipeline, strict=True)
        result: dict[str, Any] = pipeline.dump(exclude=["jobs"])
        for job in pipeline.jobs:
            result[job.name] = job.dump(exclude=["name"])
        print(result)
        return result

    def build_file(self, pipeline: Pipeline, path: Optional[pathlib.Path]) -> None:
        data = yaml.safe_dump(self.build_pipeline(pipeline=pipeline))
        path = path or pathlib.Path(os.getcwd()) / "out" / "pipeline.gitlab-ci.yml"
        with open(path, "w") as f:
            f.write(data)
