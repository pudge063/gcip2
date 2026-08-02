import enum
import pathlib

from jinja2 import Environment, PackageLoader, select_autoescape

from gcip2.logging import logger as LOGGER


class TemplateNames(str, enum.Enum):
    @property
    def template_path(self) -> str:
        return self.value + ".j2"

    @property
    def output_name(self) -> str:
        return self.value

    CI = "ci.py"
    PRE_COMMIT_CONFIG = ".pre-commit-config.yaml"
    ENVIRONMENT_TOML = "environment.toml"
    POETRY_TOML = "poetry.toml"
    PYPROJECT_TOML = "pyproject.toml"
    GITIGNORE = ".gitignore"


class TemplateGenerator:
    def __init__(self) -> None:
        self.env = Environment(
            loader=PackageLoader("gcip2", "initialization/templates"),
            autoescape=select_autoescape(),
        )

    def render_template(self, file_template: str):
        template = self.env.get_template(file_template).render()
        return template

    def generate_file_from_template(
        self,
        file_path: pathlib.Path,
        file_template: str,
        overwrite: bool = False,
    ):
        if file_path.exists() and not overwrite:
            LOGGER.warning(f"file: {file_path} already exists.")
            return

        file_content = self.render_template(file_template=file_template)
        file_path.write_text(file_content + "\n", encoding="utf-8")

    def generate_base_structure(self, overwrite: bool = False):
        out_dir = pathlib.Path.cwd()
        for item in TemplateNames:
            file_path = out_dir / item.output_name
            file_template = item.template_path

            self.generate_file_from_template(
                file_path=file_path,
                file_template=file_template,
                overwrite=overwrite,
            )
