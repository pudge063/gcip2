from os import getenv as os_getenv

import hvac
import injector

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig
from gcip2.project_config.vault_config import VaultAuthMethod, VaultConfig


@injector.inject
class Vault:
    def __init__(self, vault_config: VaultConfig):
        self.vault_config = vault_config
        self.client = hvac.Client(url=self.vault_config.url)
        LOGGER.debug(f"initialized client for vault instance: {self.vault_config.url}")
        self.auth()

    def auth(self) -> None:
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


class SecretsHandler:
    @injector.inject
    def __init__(self, config: ProjectConfig) -> None:
        self._config = config

    def normalize_secret(self, secret: str) -> VaultConfig:
        if isinstance(secret, VaultConfig):
            return secret
        vault_config = self._config.extra.secrets.vault.get(secret)
        if not vault_config:
            raise ValueError(f"missing secret '{secret}'")
        return vault_config

    def fetch(self, secret: str):
        vault_config = self.normalize_secret(secret)
        LOGGER.info(f"fetching secret: '{secret}'")
        client = Vault(vault_config)
        return client.fetch()
