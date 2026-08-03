from gcip2 import tasks_core


def test_param() -> tasks_core.Param:
    return tasks_core.Param(
        name="test_param",
        long="test-param",
        default="test-default",
        type=str,
    )
