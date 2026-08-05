from gcip2 import tasks_core


def flavor() -> tasks_core.Param:
    return tasks_core.Param(
        name="flavor",
        long="flavor",
        default="release",
        type=str,
    )


def insecure() -> tasks_core.Param:
    return tasks_core.Param(
        name="insecure",
        long="insecure",
        default=False,
        type=bool,
        inverse="secure",
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
