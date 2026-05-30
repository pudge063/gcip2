import tomllib

from gcip2.pipeline_core import pipeline  # pyright: ignore[reportUnusedImport]
from gcip2.pipeline_core import Artifacts, CiBuilder, Image, Job, Needs, Pipeline, Stage


class CustomPipeline(CiBuilder):
    def impl(self) -> Pipeline:
        with open("environment.toml", "r") as f:
            config = tomllib.loads(f.read())

        components = config["components"]

        build_jobs: list[Job] = []
        publish_jobs: list[Job] = []
        for component in components:
            build_job = Job(
                name=f"build:{components[component]['name']}",
                image=Image(name=config["pipeline"]["build"]["image"]),
                script=[f"echo build job {components[component]['name']}"],
                stage=Stage.JOBS,
                tags=config["pipeline"]["build"]["tags"],
                artifacts=Artifacts(paths=components[component]["artifacts"]),
            )
            build_jobs.append(build_job)

            publish_jobs.append(
                Job(
                    name=f"publish:{components[component]['name']}",
                    image=Image(name=config["pipeline"]["build"]["image"]),
                    script=[f"echo build job {components[component]['name']}"],
                    stage=Stage.JOBS,
                    tags=config["pipeline"]["build"]["tags"],
                    needs=[Needs(job=build_job.name)],
                ),
            )

        jobs = build_jobs + publish_jobs

        script = ["""echo 123
poetry run python --version
rm -rf *.log
"""]

        jobs.append(
            Job(
                name="test:job-1",
                stage="test",
                image=Image(name="python:3.11"),
                tags=["immortal-test"],
                script=script,
            )
        )

        jobs.append(
            Job(
                name="test:job-2",
                stage="test",
                image=Image(name="python:3.11"),
                tags=["immortal-test"],
                script=["echo 123", "poetry install"],
            )
        )

        return Pipeline(
            stages=[Stage.JOBS, "test"],
            jobs=jobs,
        )


# @pipeline
# def impl() -> Pipeline:
#     return Pipeline(
#         stages=[Stage.JOBS],
#         jobs=[
#             Job(
#                 name="job-1",
#                 image=Image(name="python:3.11"),
#                 script=["echo job-1"],
#                 stage=Stage.JOBS,
#             ),
#             Job(
#                 name="job-2",
#                 image=Image(name="python:3.11"),
#                 script=["echo job-2"],
#                 stage=Stage.JOBS,
#             ),
#         ],
#     )
