from gcip2.tasks_core.models.params import Param


def ci_file() -> Param:
    return Param(
        name="ci_file",
        long="ci-file",
        short="f",
        default="ci.py",
        type=str,
    )


def out_gitlab_ci(default: str) -> Param:
    return Param(
        name="out_pipeline",
        long="out-pipeline",
        short="o",
        default=default,
        type=str,
    )


def force() -> Param:
    return Param(
        name="force",
        long="force",
        short="f",
        default=False,
        type=bool,
    )
