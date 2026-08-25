# Secrets

`SecretsHandler` is the single interface for reading secrets during task execution. It
is configured from the project configuration and supplied by the container, so no
component sets up a Vault client itself.

HashiCorp Vault is currently the only supported backend.

## Fetching a secret

The handler is injected into every action as `self._secret_handler`. A section name
selects the connection:

```python
class PublishPackage(InteractivePythonAction):
    def impl(self, *, vault_section: str, **_):
        credentials = self._secret_handler.fetch(vault_section)
        token = credentials["token"]
```

The returned value is the KV data as a dictionary. Exposing the section name as a task
parameter lets one action serve several environments.

Nothing contacts Vault until `fetch()` is called. Building a pipeline or listing tasks
never authenticates, so generation works on a machine with no Vault access.

Connections are declared in the project configuration — see
[Configuration](project_config.md) for the fields.

## Authentication

The method is chosen from the environment rather than from the configuration file, so
one configuration serves both CI and local development:

```text
are both AppRole variables set?
        │
        ├── yes ──►  AppRole login
        │
        └── no  ──►  cached token  ──►  interactive login
```

**AppRole.** When both variables named in the configuration are present, the handler
authenticates with them directly. This is the CI path: the runner supplies them as
masked variables and nothing is prompted. A failed login raises immediately rather than
falling back to a prompt — a CI job has nobody to answer it.

**Cached token.** Without AppRole credentials, the handler looks for a token in the
operating system's credential store — Keychain on macOS, Secret Service on Linux,
Credential Manager on Windows. A valid token means nothing is asked. Tokens are
short-lived, so caching one is safer than exporting long-lived AppRole credentials into
a shell profile.

**Interactive login.** With no valid token cached, credentials are requested at the
terminal and the resulting token is written back to the credential store, so subsequent
runs are silent. If standard input is not a terminal, the handler raises an error naming
the environment variables it expected — turning a forgotten CI variable into a readable
failure instead of a job that hangs.

## Design notes

Configuration comes from the project file; credentials come from the environment. The
separation is deliberate, so a configuration file can be committed while credentials
stay in CI variables or a local credential store.

Authentication happens when a secret is requested, not when the handler is created.
Because the handler is a shared singleton, this keeps object creation free of network
calls and keeps Vault out of the pipeline-generation path entirely.
