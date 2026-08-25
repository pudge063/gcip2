# Configuration

`ProjectConfig` is the project's configuration, read from a TOML file. The file is
chosen with the global `--config` flag and defaults to `environment.toml` in the working
directory:

```bash
dothat --config other/environment.toml run build-gitlab-ci
```

It is read once per process and supplied by the container, so builders, tasks, and
actions access it as `self._config` without loading anything themselves. See
[Dependency injection](di.md).

If the file does not exist, an empty configuration with default values is used.

## The extra section

`ProjectConfig` has one top-level field, `extra`, which holds both the sections the
framework understands and any project-specific keys:

```toml
[extra.tasks]
module = "_tasks"

[extra.database]
host = "localhost"
port = 5432
```

Unknown keys are preserved and readable at runtime:

```python
self._config.extra.database.host
self._config.extra["database"]
self._config.extra.get("database")
self._config.extra.get("missing", fallback)
```

Every key under `[extra]` is also passed to tasks automatically as `extra__<key>`, so
actions can use configuration values without reading the file. See
[Tasks](tasks.md).

## Task discovery

```toml
[extra.tasks]
module = "_tasks"
```

Names the module exporting the project's `TaskGenerator` class. The field is optional;
without it only built-in tasks are registered.

## Secrets

Vault connections are declared under `extra.secrets.vault`, one named section per
connection:

```toml
[extra.secrets.vault.default]
url = "https://vault.company.com"
auth_method = "approle"
app_role_id_env_var = "VAULT_ROLE_ID"
app_role_secret_id_env_var = "VAULT_SECRET_ID"
mount_point = "kv"
path = "applications/my-project"
```

| Field | Required | Description |
|---|---|---|
| `url` | yes | Vault server URL |
| `auth_method` | yes | `approle` or `jwks` |
| `app_role_id_env_var` | no | Name of the variable holding the AppRole ID |
| `app_role_secret_id_env_var` | no | Name of the variable holding the AppRole secret ID |
| `mount_point` | no | KV mount point |
| `path` | no | Secret path within the mount |

The AppRole fields hold **variable names, not values** — credentials never appear in the
configuration file. See [Secrets](secrets.md).
