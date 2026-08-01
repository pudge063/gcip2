from gcip2 import PipelineBuilderImpl, pipeline_core


def test_default_pipeline():
    pipeline: pipeline_core.Pipeline = PipelineBuilderImpl().apply().build()

    base_pipeline = pipeline_core.Pipeline()
    base_pipeline.stages = [pipeline_core.Stage.JOBS]

    assert pipeline == base_pipeline


def test_pipeline_workflow_name():
    name = "default"
    pipeline: pipeline_core.Pipeline = (
        PipelineBuilderImpl().apply().with_workflow(pipeline_core.Workflow(name=name)).build()
    )

    assert pipeline.workflow and pipeline.workflow.name == name
