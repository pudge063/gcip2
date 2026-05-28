from gcip2 import (
    Pipeline,
    Job,
    Stage,
    Image,
    pipeline,
    IncludeComponent,
    BaseInput,
)


@pipeline
def impl() -> Pipeline:
    stages: list[Stage | str] = [Stage.JOBS]
    jobs: list[Job] = []

    jobs.append(
        Job(
            name="test:job-1",
            stage="test",
            image=Image(name="python:3.11"),
            tags=["immortal-test"],
            script=[
                "echo 123",
                "echo 321",
            ],
        )
    )

    return Pipeline(
        stages=stages,
        jobs=jobs,
        include=[
            IncludeComponent(
                component="$CI_SERVER_FQDN/ci-components/git-config/gitlab-ci@master",
                inputs={
                    "gitconfig": BaseInput(
                        description="path to ssh config",
                        default="$HOME/.ssh/config",
                    )
                },
            ),
        ],
    )
