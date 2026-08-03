import typing
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ComposeImage:
    image: str


@dataclass
class Compose:
    path: Path = Path("docker-compose.yml")
    services: dict[str, ComposeImage] = field(default_factory=lambda: {})

    @classmethod
    def load(cls, path: Path = Path("docker-compose.yml")) -> "Compose":
        with path.open("r", encoding="utf-8") as f:
            data: dict[str, dict[str, typing.Any]] = yaml.safe_load(f) or {}

        services = {
            name: ComposeImage(image=service["image"])
            for name, service in data.get("services", {}).items()
            if "image" in service
        }

        return cls(path=path, services=services)

    @property
    def images(self) -> dict[str, ComposeImage]:
        return self.services
