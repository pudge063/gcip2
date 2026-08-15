# ProjectConfig

`ProjectConfig` is the global project configuration loaded from the `environment.toml` file.

The configuration is initialized once during application startup and is available throughout the entire pipeline execution lifecycle.

## Availability

`ProjectConfig` can be accessed from:

- `JobBuilderImpl`
- `PipelineBuilderImpl`
- All Tasks
- All Actions
- Any other component that participates in pipeline execution

This provides a single source of truth for project-level configuration.

## Loading

The configuration is automatically loaded from the `environment.toml` file located in the project root.

```python
config = ProjectConfig.from_file()
```

If the file does not exist, an empty configuration is created with default values.

## Structure

```python
class ProjectConfig(BaseModel):
    extra: Extra
```

Currently, `ProjectConfig` contains a single top-level field:

| Field | Type | Description |
|--------|------|-------------|
| `extra` | `Extra` | Container for project-specific configuration. |

---

# Extra

The `extra` section is intentionally extensible.

Besides the predefined fields, it accepts arbitrary user-defined configuration.

```python
class Extra(BaseModel):
    secrets: Secrets
    tasks: Tasks
    # ...any custom fields
```

Unknown fields are preserved and can be accessed at runtime.

Example:

```toml
[extra.database]
host = "localhost"
port = 5432

[extra.feature_flags]
enable_new_pipeline = true
```

Usage:

```python
config.extra.database
config.extra["database"]

config.extra.feature_flags
config.extra["feature_flags"]
```

You can also safely retrieve optional values:

```python
config.extra.get("database")
config.extra.get("missing", default_value)
```

---

# Tasks Configuration

The `tasks` section defines task discovery settings.

```toml
[extra.tasks]
module = "_tasks"
```

Default value:

```python
module = None
```

This module is used for automatic task discovery.

The field is optional. If it is not set, task discovery from a custom module is skipped and only built-in tasks are registered.

---

# Secrets Configuration

Secrets are configured under the `extra.secrets` section.

Currently, Vault-based secret providers are supported.

Example:

```toml
[extra.secrets.vault.default]
url = "https://vault.company.com"
auth_method = "approle"
app_role_id_env_var = "VAULT_ROLE_ID"
app_role_secret_id_env_var = "VAULT_SECRET_ID"
mount_point = "kv"
path = "applications/project"
```

## Vault Configuration

| Field | Type | Required | Description |
|--------|------|----------|-------------|
| `url` | `string` | Yes | Vault server URL. |
| `auth_method` | `approle` \| `jwks` | Yes | Authentication method. |
| `app_role_id_env_var` | `string` | No | Environment variable containing the AppRole ID. |
| `app_role_secret_id_env_var` | `string` | No | Environment variable containing the AppRole Secret ID. |
| `mount_point` | `string` | No | Vault mount point. |
| `path` | `string` | No | Secret path inside Vault. |

Multiple Vault configurations can be defined:

```toml
[extra.secrets.vault.default]
url = "https://vault.company.com"
auth_method = "approle"

[extra.secrets.vault.production]
url = "https://vault-prod.company.com"
auth_method = "jwks"
```

---

# Example

```toml
[extra.tasks]
module = "_tasks"

[extra.secrets.vault.default]
url = "https://vault.company.com"
auth_method = "approle"
app_role_id_env_var = "VAULT_ROLE_ID"
app_role_secret_id_env_var = "VAULT_SECRET_ID"

[extra.database]
host = "localhost"
port = 5432

[extra.notifications]
slack_channel = "#ci"
```

Usage:

```python
config.extra.tasks.module

config.extra.secrets.vault["default"]

config.extra.database.host
config.extra.notifications.slack_channel
```

---

# Design Principles

- `ProjectConfig` is loaded once from `environment.toml`.
- It is globally available across the entire pipeline execution.
- It provides strongly typed configuration for built-in sections (`tasks`, `secrets`).
- It allows arbitrary project-specific configuration through the extensible `extra` section.
- Custom configuration is preserved and accessible without requiring framework changes.
