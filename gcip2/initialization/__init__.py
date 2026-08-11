import pathlib
import shutil
from importlib.resources import as_file, files

from gcip2.logging import logger as LOGGER


class TemplateGenerator:
    def generate_project_structure(
        self,
        destination: pathlib.Path = pathlib.Path("."),
        force: bool = False,
    ) -> None:
        template = files("gcip2.initialization") / "templates"

        LOGGER.info("Copying project template from {}", template)

        with as_file(template) as template_path:
            self._copy_template(
                template_path,
                destination,
                force=force,
            )

    @staticmethod
    def _copy_template(
        source: pathlib.Path,
        destination: pathlib.Path,
        *,
        force: bool,
    ) -> None:
        for source_path in source.rglob("*"):
            relative_path = source_path.relative_to(source)
            destination_path = destination / relative_path

            if source_path.is_dir():
                destination_path.mkdir(parents=True, exist_ok=True)
                continue

            if destination_path.exists() and not force:
                LOGGER.debug("Skipping existing file: {}", destination_path)
                continue

            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, destination_path)
