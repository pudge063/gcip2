# SecretsHandler

`SecretsHandler` provides a unified interface for accessing secrets during pipeline execution.

It is built on top of the configured secret provider (currently HashiCorp Vault) and is automatically initialized using the project's `ProjectConfig`.

A single `SecretsHandler` instance is injected into the execution context and is available throughout the framework.

## Availability

`SecretsHandler` is available from:

- `JobBuilderImpl`
- `PipelineBuilderImpl`
- All Tasks
- All Actions
- Any other execution component

This allows every part of the pipeline to access secrets without creating or configuring a Vault client manually.

---

# Configuration

`SecretsHandler` uses the Vault configuration defined in `environment.toml`.

Example:

```toml
[extra.secrets.vault.default]
url = "https://vault.company.com"
auth_method = "approle"
app_role_id_env_var = "VAULT_ROLE_ID"
app_role_secret_id_env_var = "VAULT_SECRET_ID"
mount_point = "kv"
path = "applications/my-project"
```

The configuration is loaded from:

```python
ProjectConfig.extra.secrets.vault
```

Each configured Vault section represents a separate Vault connection.

---

# Authentication

Currently, the following authentication method is supported:

- `approle`

During initialization, `SecretsHandler` authenticates automatically using the configured environment variables.

```python
app_role_id_env_var
app_role_secret_id_env_var
```

These variables must be available in the process environment.

---

# Fetching Secrets

Secrets are fetched from the configured Vault KV store.

```python
secrets = secrets_handler.fetch()
```

The returned value is a dictionary:

```python
{
    "username": "admin",
    "password": "secret"
}
```

Internally, `SecretsHandler` reads secrets from the configured:

- `mount_point`
- `path`

defined in `environment.toml`.

---

# Example Configuration

```toml
[extra.secrets.vault.default]
url = "https://vault.company.com"
auth_method = "approle"
app_role_id_env_var = "VAULT_ROLE_ID"
app_role_secret_id_env_var = "VAULT_SECRET_ID"
mount_point = "kv"
path = "applications/demo"
```

---

# Example Usage

```python
credentials = secrets_handler.fetch()

username = credentials["username"]
password = credentials["password"]
```

---

# Design Principles

- `SecretsHandler` is configured from `ProjectConfig`.
- Authentication is performed automatically during initialization.
- A single interface is used for retrieving secrets.
- No Vault-specific client setup is required inside Tasks, Actions, or Builders.
- Secrets are available anywhere the execution context is available.
- Currently, HashiCorp Vault is the supported secret backend.
