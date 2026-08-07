import pathlib
import shutil
from importlib.resources import as_file, files

from gcip2.logging import logger as LOGGER


class TemplateGenerator:
    def generate_project_structure(self, destination: pathlib.Path = pathlib.Path(".")) -> None:
        template = files("gcip2.initialization") / "templates"

        LOGGER.info("Copying project template from {}", template)

        with as_file(template) as template_path:
            shutil.copytree(
                template_path,
                destination,
                dirs_exist_ok=True,
            )
