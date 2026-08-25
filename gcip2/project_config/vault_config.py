from typing import Optional

import pydantic


class VaultConfig(pydantic.BaseModel):
    url: str
    app_role_id_env_var: Optional[str] = None
    app_role_secret_id_env_var: Optional[str] = None
    mount_point: Optional[str] = None
    path: Optional[str] = None
