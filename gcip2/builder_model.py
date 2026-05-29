from abc import ABC, abstractmethod
from typing import Any, Self

from .ci_model import Artifacts, Job, Needs, Pipeline, Trigger, TriggerIncludeArtifact


def pipeline(func: Any):

    func.__gcip2_pipeline__ = True

    return func


class BasePipeline(ABC):

    @abstractmethod
    def impl(self: Self) -> Pipeline:
        pass


class TriggerPipeline:
    def impl(self: Self) -> Pipeline:
        build_pipeline_job = Job(
            name="build-pipeline",
            script=[
                "pip3 install poetry",
                "poetry install && . .venv/bin/activate",
                "gcip2 build-pipeline",
            ],
            tags=["immortal"],
            artifacts=Artifacts(paths=["out"]),
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
