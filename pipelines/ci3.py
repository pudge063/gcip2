from gcip2.pipeline_core import WorkflowAutoCancelOnNewCommit  # type: ignore
from gcip2.pipeline_core import (
    Artifacts,
    ArtifactsReports,
    Default,
    GlobalVariables,
    Image,
    Job,
    JobVariables,
    Needs,
    Pipeline,
    Rule,
    RuleChanges,
    Stage,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnJobFailure,
    pipeline,
)


@pipeline
def impl() -> Pipeline:

    jobs: list[Job] = []

    job_for_extend = Job(
        name=".test",
        image=Image(name="python:3.12"),
    )

    jobs.extend(
        [
            job_for_extend,
            Job(name="test", extends=job_for_extend.name, script="python3 --version", stage=Stage.JOBS),
        ]
    )

    job = Job(
        name="test-1",
        image=Image(name="python:3.11"),
        script=[
            "echo ID=$CI_JOB_ID > dotenv.txt",
            "env",
            "!reference [.test, before_script]",
        ],
        stage=Stage.JOBS,
        tags=["immortal"],
        artifacts=Artifacts(
            reports=ArtifactsReports(
                dotenv=["dotenv.txt"],
            ),
            paths=["builds/*"],
        ),
        variables={
            "TEST_JOB_VARIABLE_1": JobVariables(
                value="A",
                expand=False,
            ),
            "TEST_JOB_VARIABLE_2": "B",
        },
        rules=[
            Rule(
                if_='$CUSTOM_VAR == "1"',
                variables={
                    "RULE_TEST_VARIABLE": "1",
                },
            )
        ],
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
            name="default",
            auto_cancel=WorkflowAutoCancel(
                on_job_failure=WorkflowAutoCancelOnJobFailure.NONE,
            ),
            rules=[
                Rule(
                    if_='$CUSTOM_VAR == "1"',
                    variables={
                        "CUSTOM_VAR_CI_PIPELINE_SOURCE": "push_",
                        "RULE": "1",
                    },
                ),
                Rule(
                    if_='$CI_PIPELINE_SOURCE == "merge_request_event"',
                    changes=["out"],
                    variables={
                        "CUSTOM_VAR_CI_PIPELINE_SOURCE": "merge_request_event_",
                        "RULE": "2",
                    },
                ),
                Rule(
                    changes=RuleChanges(
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
        default=Default(
            after_script=["rm -rf .venv"],
            before_script=["poetry install && . .venv/bin/activate"],
            artifacts=Artifacts(
                paths=["logs/*"],
            ),
            image=Image(name="python:3.11"),
            tags=["immortal"],
        ),
    )
