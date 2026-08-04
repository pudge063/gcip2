from gcip2 import PipelineBuilderImpl
from gcip2.pipeline_core import (
    Default,
    Image,
    Pipeline,
    Stage,
    Workflow,
    WorkflowAutoCancel,
    WorkflowAutoCancelOnNewCommit,
    WorkflowRule,
    WorkflowWhen,
)


def test_default_pipeline():
    pipeline: Pipeline = PipelineBuilderImpl().apply().build()

    base_pipeline = Pipeline()
    base_pipeline.stages = [Stage.JOBS]
    base_pipeline.workflow = Workflow(
        auto_cancel=WorkflowAutoCancel(on_new_commit=WorkflowAutoCancelOnNewCommit.NONE),
        rules=[
            WorkflowRule(
                if_='$CI_PIPELINE_SOURCE == "push" && $CI_OPEN_MERGE_REQUESTS',
                when=WorkflowWhen.NEVER,
            ),
            WorkflowRule(
                when=WorkflowWhen.ALWAYS,
            ),
        ],
    )
    base_pipeline.default = Default(
        image=Image(name="ghcr.io/astral-sh/uv:python3.12-bookworm"),
        tags=["static-k8s"],
    )

    assert pipeline == base_pipeline


def test_pipeline_workflow_name():
    name = "default"
    pipeline: Pipeline = PipelineBuilderImpl().apply().with_workflow(Workflow(name=name)).build()

    assert pipeline.workflow and pipeline.workflow.name == name
