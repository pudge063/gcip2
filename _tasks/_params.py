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


def gitlab_token_section() -> tasks_core.Param:
    return tasks_core.Param(
        name="gitlab_token_section",
        long="gitlab-token-section",
        default="gitlab-token",
        type=str,
    )


def pypi_token_section() -> tasks_core.Param:
    return tasks_core.Param(
        name="pypi_token_section",
        long="pypi-token-section",
        default="pypi-token",
        type=str,
    )
