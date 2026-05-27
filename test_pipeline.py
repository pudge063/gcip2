from gcip2 import Pipeline, Job, Stage, Image, BasePipeline, pipeline

# class CustomPipeline(BasePipeline):
#     def impl(self) -> Pipeline:
#         return Pipeline(
#             stages=[Stage.JOBS],
#             jobs=[
#                 Job(
#                     name="job-1",
#                     image=Image(name="python:3.11"),
#                     script=["echo job-1"],
#                     stage=Stage.JOBS,
#                 ),
#                 Job(
#                     name="job-2",
#                     image=Image(name="python:3.11"),
#                     script=["echo job-2"],
#                     stage=Stage.JOBS,
#                 ),
#             ],
#         )


@pipeline
def impl() -> Pipeline:
    return Pipeline(
        stages=[Stage.JOBS],
        jobs=[
            Job(
                name="job-1",
                image=Image(name="python:3.11"),
                script=["echo job-1"],
                stage=Stage.JOBS,
            ),
            Job(
                name="job-2",
                image=Image(name="python:3.11"),
                script=["echo job-2"],
                stage=Stage.JOBS,
            ),
        ],
    )
