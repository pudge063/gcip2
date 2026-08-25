import getpass
import sys
from os import getenv as os_getenv

import hvac
import injector

from gcip2.logging import logger as LOGGER
from gcip2.project_config import ProjectConfig
from gcip2.project_config.vault_config import VaultConfig
from gcip2.vault.token_store import TokenStore


@injector.inject
class Vault:
    def __init__(self, vault_config: VaultConfig, _token_store: TokenStore):
        self.vault_config = vault_config
        self._client = hvac.Client(url=self.vault_config.url)
        LOGGER.debug(f"initialized client for vault instance: {self.vault_config.url}")

        self._tokens = _token_store
        self.auth()

    def auth(self) -> None:
        LOGGER.debug(f"authorization with approle {self.vault_config.app_role_id_env_var}")

        role_id = os_getenv(str(self.vault_config.app_role_id_env_var))
        secret_id = os_getenv(str(self.vault_config.app_role_secret_id_env_var))

        if role_id and secret_id:
            self._client.auth.approle.login(role_id=role_id, secret_id=secret_id)  # type: ignore[attr-defined]
            return
        self.auth_keyring()

    def auth_keyring(self) -> None:
        token = self._tokens.load(self.vault_config.url)
        if token:
            self._client.token = token
            if self._client.is_authenticated():
                LOGGER.debug("token from keyring is valid")
                return
            LOGGER.debug("token from keyring is expired")

        token = self.auth_interactive()
        self._client.token = token
        if not self._client.is_authenticated():
            raise ValueError("could not authenticate with the obtained token")
        self._tokens.save(self.vault_config.url, token)

    def auth_interactive(self) -> str:
        if not sys.stdin.isatty():
            raise ValueError(
                "cannot authenticate: no approle credentials in environment "
                f"({self.vault_config.app_role_id_env_var}, "
                f"{self.vault_config.app_role_secret_id_env_var}) and stdin is not a terminal"
            )
        LOGGER.info(f"authenticating to {self.vault_config.url}")
        username = input("LDAP username: ")
        password = getpass.getpass("LDAP password: ")
        return self._client.auth.ldap.login(username=username, password=password)["auth"]["client_token"]

    def fetch(self) -> dict[str, str]:
        LOGGER.debug(f"fetching secret from {self.vault_config.mount_point}:{self.vault_config.path}")
        return self._client.secrets.kv.read_secret_version(  # type: ignore[attr-defined]
            mount_point=self.vault_config.mount_point,
            path=self.vault_config.path,
            raise_on_deleted_version=True,
        )["data"]["data"]


class SecretsHandler:
    @injector.inject
    def __init__(self, config: ProjectConfig, _token_store: TokenStore) -> None:
        self._config = config
        self._tokens = _token_store

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
        client = Vault(vault_config, self._tokens)
        return client.fetch()
