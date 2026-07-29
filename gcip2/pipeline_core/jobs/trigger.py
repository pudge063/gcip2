from enum import Enum
from typing import Self

from gcip2 import pipeline_core
from gcip2.pipeline_core.jobs.base import Base, BaseLinux


class TriggerPipelineDefaults(str, Enum):
    build_pipeline = "build-pipeline"
    trigger_pipeline = "trigger-pipeline"
    out_dir = "out"
    out_file = "out/pipeline.gitlab-ci.yml"


class BuildTriggerPipeline(pipeline_core.JobBuilderImpl):
    _base = BaseLinux

    def apply(self: Self) -> Self:
        self.with_name(TriggerPipelineDefaults.build_pipeline.value)
        self.model.artifacts = pipeline_core.Artifacts(paths=[TriggerPipelineDefaults.out_dir])
        self.model.script = ['exec sh -c "gcip2 build-pipeline"']
        return self


class TriggerPipeline(pipeline_core.JobBuilderImpl):
    _base = Base

    def apply(self: Self) -> Self:
        self.with_name(TriggerPipelineDefaults.trigger_pipeline.value)
        self.model.variables = {"PARENT_PIPELINE_ID": "${CI_PIPELINE_ID}"}
        self.model.needs = [
            pipeline_core.Needs(
                job=TriggerPipelineDefaults.build_pipeline,
                artifacts=True,
            )
        ]
        self.model.interruptible = False
        self.model.trigger = pipeline_core.Trigger(
            include=[
                pipeline_core.TriggerIncludeArtifact(
                    artifact=TriggerPipelineDefaults.out_file,
                    job=TriggerPipelineDefaults.build_pipeline,
                )
            ],
            strategy=pipeline_core.TriggerStrategy.DEPEND,
            forward=pipeline_core.TriggerForward(
                yaml_variables=True,
                pipeline_variables=True,
            ),
        )

        return self
