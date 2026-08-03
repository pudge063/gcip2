from gcip2 import tasks_core


def test_param() -> tasks_core.Param:
    return tasks_core.Param(
        name="test_param",
        long="test-param",
        default="test-default",
        type=str,
    )


def test_bool_param() -> tasks_core.Param:
    return tasks_core.Param(
        name="allow_failure",
        long="allow-failure",
        default=False,
        type=bool,
        inverse="disallow-failure",
    )


def vault_section(default: str) -> tasks_core.Param:
    return tasks_core.Param(
        name="vault_section",
        long="vault-section",
        default=default,
        type=str,
    )
