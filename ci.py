from gcip2 import (
    Artifacts,
    ArtifactsReports,
    Image,
    Job,
    Needs,
    Pipeline,
    Stage,
    pipeline,
    Workflow,
    WorkflowAutoCancel,
    Rules,
    WorkflowAutoCancelOnNewCommit,
    WorkflowAutoCancelOnJobFailure,
    RulesChanges,
    JobVariables,
    GlobalVariables,
)


@pipeline
def impl() -> Pipeline:

    jobs: list[Job] = []

    job = Job(
        name="test-1",
        image=Image(name="python:3.11"),
        script=["echo ID=$CI_JOB_ID > dotenv.txt"],
        stage=Stage.JOBS,
        tags=["immortal"],
        artifacts=Artifacts(
            reports=ArtifactsReports(
                dotenv=["dotenv.txt"],
            )
        ),
        variables={
            "TEST_JOB_VARIABLE_1": JobVariables(
                value="A",
                expand=False,
            ),
            "TEST_JOB_VARIABLE_2": "B",
        },
    )

    jobs.append(job)

    jobs.append(
        Job(
            name="test-2",
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
        workflow=Workflow(
            name="default name",
            auto_cancel=WorkflowAutoCancel(
                on_job_failure=WorkflowAutoCancelOnJobFailure.NONE,
            ),
            rules=[
                Rules(
                    if_='CI_PIPELINE_SOURCE == "merge_request_event"',
                    changes=["out"],
                    variables={
                        "CUSTOM_VARIABLE": "test_value_1",
                        "RULE": "1",
                    },
                ),
                Rules(
                    changes=RulesChanges(
                        paths=[
                            "pipelines",
                            "examples",
                        ],
                    ),
                    variables={
                        "CUSTOM_VARIABLE": "test_value_2",
                        "RULE": "2",
                    },
                ),
            ],
        ),
        variables={
            "CUSTOM_VARIABLE": GlobalVariables(
                value="test_value",
                description="test custom variable",
                expand=True,
            )
        },
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
