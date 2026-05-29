from gcip2 import (
    Pipeline,
    Job,
    Stage,
    Image,
    pipeline,
    Needs,
    Artifacts,
    ArtifactsReports,
)


@pipeline
def impl() -> Pipeline:

    jobs: list[Job] = []

    job = Job(
        name="test-reports",
        image=Image(name="python:3.11"),
        script=["echo ID=$CI_JOB_ID > dotenv.txt"],
        stage=Stage.JOBS,
        tags=["immortal"],
        artifacts=Artifacts(
            reports=ArtifactsReports(
                dotenv=["dotenv.txt"],
            )
        ),
    )

    jobs.append(job)

    jobs.append(
        Job(
            name="test:job-2",
            image=Image(name="python:3.11"),
            tags=["immortal"],
            script=["echo $ID"],
            stage=Stage.JOBS,
            needs=[Needs(job=job.name)],
        )
    )

    return Pipeline(
        stages=[Stage.JOBS],
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
