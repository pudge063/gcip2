import enum
from typing import Optional

import pydantic


class VaultAuthMethod(str, enum.Enum):
    APPROLE = "approle"
    JWKS = "jwks"


class Vault(pydantic.BaseModel):
    url: str
    auth_method: VaultAuthMethod
    app_role_id_env_var: Optional[str] = None
    app_role_secret_id_env_var: Optional[str] = None
    mount_point: Optional[str] = None
    path: Optional[str] = None
