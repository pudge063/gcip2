from abc import ABC, abstractmethod
from typing import Any

from .ci_model import Pipeline, Job, Trigger, TriggerIncludeArtifact, Needs


class BasePipeline(ABC):

    @abstractmethod
    def impl(self) -> Pipeline:
        pass


class TriggerPipeline(BasePipeline):
    def impl(self) -> Pipeline:
        build_pipeline_job = Job(
            name="build-pipeline",
            script=[
                "poetry install && . .venv/bin/activate",
                "build-pipeline",
            ],
            tags=["immortal"],
        )

        return Pipeline(
            jobs=[
                build_pipeline_job,
                Job(
                    name="trigger-pipeline",
                    trigger=Trigger(
                        include=[
                            TriggerIncludeArtifact(
                                artifact="out/pipeline.gitlab-ci.yml",
                                job="build-pipeline",
                            )
                        ],
                    ),
                    needs=[
                        Needs(
                            job=build_pipeline_job.name,
                            artifacts=True,
                        )
                    ],
                ),
            ]
        )


def pipeline(func: Any):

    func.__gcip2_pipeline__ = True

    return func
