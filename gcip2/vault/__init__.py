from os import getenv as os_getenv

import hvac

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig, VaultAuthMethod


class Vault:
    _config = ProjectConfig.from_file()

    def __init__(self, vault_section: str):
        self.vault_config = self._config.extra.secrets.vault[vault_section]
        self.client = hvac.Client(url=self.vault_config.url)
        LOGGER.debug(f"initialized client for vault instance: {self.vault_config.url}")
        self.auth()

    def auth(self):
        if self.vault_config.auth_method == VaultAuthMethod.APPROLE:
            LOGGER.debug(f"authorization with approle {self.vault_config.app_role_id_env_var}")
            self.client.auth.approle.login(  # type: ignore[attr-defined]
                role_id=os_getenv(str(self.vault_config.app_role_id_env_var)),
                secret_id=os_getenv(str(self.vault_config.app_role_secret_id_env_var)),
            )
        else:
            raise ValueError("Unknown auth method")

    def fetch(self) -> dict[str, str]:
        LOGGER.debug(f"fetching secret from {self.vault_config.mount_point}:{self.vault_config.path}")
        return self.client.secrets.kv.read_secret_version(  # type: ignore[attr-defined]
            mount_point=self.vault_config.mount_point,
            path=self.vault_config.path,
            raise_on_deleted_version=True,
        )["data"]["data"]


class SecretsHandler(Vault): ...
