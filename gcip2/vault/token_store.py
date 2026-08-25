import keyring

SERVICE = "gcip2-vault"


class TokenStore:
    def load(self, url: str) -> str | None:
        return keyring.get_password(SERVICE, url)

    def save(self, url: str, token: str) -> None:
        keyring.set_password(SERVICE, url, token)

    def clear(self, url: str) -> None:
        try:
            keyring.delete_password(SERVICE, url)
        except keyring.errors.PasswordDeleteError:  # type: ignore
            pass
