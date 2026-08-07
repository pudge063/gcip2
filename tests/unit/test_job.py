import pytest

from gcip2 import BaseLinux, pipeline_core


def test_job_name():
    name = "test-job-name"

    job = pipeline_core.JobBuilderImpl()
    job.model.name = name
    builded_job = job.build()

    assert builded_job.name == name


def test_job_with_name():
    name = "test-job-name"

    job = pipeline_core.JobBuilderImpl().apply().with_name(name)
    builded_job = job.build()

    assert builded_job.name == name


def test_job_name_with_apply():
    name = "test-job-name"
    postfix = "test-postfix"

    job = pipeline_core.JobBuilderImpl().apply().with_name(name)
    job.model.name = f"{job.model.name}:{postfix}" if job.model.name else ""
    builded_job = job.build()

    assert builded_job.name == f"{name}:{postfix}"


def test_job_add_to_name():
    name = "test-job-name"
    postfix = "test-postfix"

    job = pipeline_core.JobBuilderImpl().apply().with_name(name)
    job.add_to_name(f":{postfix}")

    builded_job = job.build()

    assert builded_job.name == f"{name}:{postfix}"


def test_job_add_to_empty_name_FAILURE():
    postfix = "test-postfix"

    job = pipeline_core.JobBuilderImpl().apply()

    with pytest.raises(ValueError):
        job.add_to_name(f":{postfix}")


def test_job_dependencies():
    main_job_name = "test-job"
    job = pipeline_core.JobBuilderImpl().apply().with_dependencies([main_job_name]).build()

    assert job.dependencies == [main_job_name]


def test_job_with_image():
    image = "python"
    job = pipeline_core.JobBuilderImpl().apply().with_image(image).build()

    assert job.image.name == image


def test_job_with_compose_image():
    pipeline_core.JobBuilderImpl().apply().with_compose_image("base_python").build()


def test_job_with_compose_image_FAILURE():
    with pytest.raises(ValueError):
        pipeline_core.JobBuilderImpl().apply().with_compose_image("python").build()


def test_BaseLinux_before_script():
    job_BaseLinux = BaseLinux().apply()

    class TestJob(pipeline_core.JobBuilderImpl):
        _base = BaseLinux

    job = TestJob()
    builded_job = job.build()

    assert builded_job.before_script == job_BaseLinux.model.before_script


def test_BaseLinux_after_script():
    job_BaseLinux = BaseLinux().apply()

    class TestJob(pipeline_core.JobBuilderImpl):
        _base = BaseLinux

    job = TestJob()
    builded_job = job.build()

    assert builded_job.after_script == job_BaseLinux.model.after_script


def test_BaseLinux_rewrite_with_apply():
    _name = "test-baselinux-job"
    _before_script = ["echo before script"]
    _after_script = ["echo after script"]

    class TestJob(pipeline_core.JobBuilderImpl):
        _base = BaseLinux

        def apply(self):
            self.model.before_script = _before_script
            self.model.after_script = _after_script
            return self.with_name(_name)

    job = TestJob()
    builded_job = job.apply().build()

    assert (
        builded_job.name == _name
        and builded_job.before_script == _before_script
        and builded_job.after_script == _after_script
    )


def test_BaseLinux_rewrite_without_apply():
    _name = "test-baselinux-job"
    _before_script = ["echo before script"]
    _after_script = ["echo after script"]

    class TestJob(pipeline_core.JobBuilderImpl):
        _base = BaseLinux

        def apply(self):
            self.model.before_script = _before_script
            self.model.after_script = _after_script
            return self.with_name(_name)

    job = TestJob()
    builded_job = job.build()

    assert not (
        builded_job.name == _name
        and builded_job.before_script == _before_script
        and builded_job.after_script == _after_script
    )
