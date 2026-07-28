from . import Default, JobBuilderImpl, PipelineBuilderImpl, Workflow


class GitlabCiBuilderImpl(PipelineBuilderImpl):

    @staticmethod
    def job(job_class: type[JobBuilderImpl]) -> JobBuilderImpl:
        return job_class()

    def with_workflow(self, workflow: Workflow = Workflow()):
        self.model.workflow = workflow
        return self

    def with_default(self, default: Default = Default()):
        self.model.default = default
        return self
