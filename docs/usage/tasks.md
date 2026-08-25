# Tasks

A **task** is a named automation workflow, run from the CLI or from a CI job:

```bash
dothat run test-task
```

A task contains no logic of its own. It declares which **actions** to run and which
**parameters** they receive, so the same definition serves local runs, CI jobs, and
generated variants.

## Defining a task

```python
class CheckVersion(TaskBuilderImpl):
    _basename = "check-version"

    def apply(self):
        return self.with_actions((PrintVersion,)).with_params((version(),))
```

`_basename` is the identifier used by the CLI and must be unique. It accepts an enum
value as well, which keeps the name in sync between the task and the CI job that runs
it:

```python
class Tasks(Enum):
    CHECK_VERSION = "check-version"


class CheckVersion(TaskBuilderImpl):
    _basename = Tasks.CHECK_VERSION
```

## Actions

An action implements a single operation and is reusable across tasks. Two base types are
provided.

`InteractivePythonAction` for Python logic:

```python
class PrintVersion(InteractivePythonAction):
    def impl(self, *, version: str, **_):
        LOGGER.info(version)
```

`InteractiveShlex` for shell commands, returned as argument lists so nothing is
re-parsed by a shell:

```python
class CheckCommand(InteractiveShlex):
    def impl(self, *, command: str, **_) -> list[list[str]]:
        return [["echo", command]]
```

Task parameters arrive as keyword arguments; an action declares only what it needs and
absorbs the rest with `**_`. Actions also inherit `self._config` and
`self._secret_handler` from their base class without defining a constructor — see
[Dependency injection](di.md).

Actions run sequentially, in declaration order:

```python
self.with_actions((PrepareAction, BuildAction, PublishAction))
```

## Parameters

A parameter defines a name, a CLI flag, a default, and optionally a type and an
environment variable:

```python
def version():
    return Param(name="version", long="version", default="latest", type=str)
```

Values are resolved in increasing order of priority:

```text
default  ──►  environment variable  ──►  configuration  ──►  CLI argument
```

Every key under `[extra]` in the project configuration is exposed to all tasks
automatically, without being declared:

```toml
[extra]
version = "1.2.3"
```

```python
class PrintVersion(InteractivePythonAction):
    def impl(self, *, extra__version: str, **_):
        print(extra__version)
```

The `__` separator represents the configuration hierarchy, so `extra.version` becomes
`extra__version`. The file is selected with the global `--config` flag and defaults to
`environment.toml`.

## Task generators

A generator produces the tasks available to the CLI. Projects export the generator
**class** — the container instantiates it:

```python
class TaskGenerator(TaskGeneratorImpl):
    task_check_version = CheckVersion
    task_publish = PublishPackage
```

Attributes prefixed with `task_` are discovered automatically. The module holding the
generator is named in the configuration:

```toml
[extra.tasks]
module = "_tasks"
```

The field is optional; without it only built-in tasks are available. Tasks from the
project module override built-in tasks of the same name.

### Variants

One implementation can produce several named tasks, which is how matrix-style CI
configurations are built:

```python
class TaskGenerator(TaskGeneratorImpl):
    def load_tasks(self) -> Iterator[Task]:
        yield from super().load_tasks()

        for target in ("target-1", "target-2"):
            yield (
                self.builder(TestBaseTask)
                .apply()
                .with_name(target)
                .with_params((self._params.ci(),))
                .build()
            )
```

This registers `test-task:target-1` and `test-task:target-2`. `self.builder()` creates
the builder through the container — do not instantiate builders directly.

| Method | Purpose |
|---|---|
| `builder()` | Creates a builder through the container |
| `apply()` | Applies the task's own configuration |
| `with_name()` | Adds a suffix to the task name |
| `with_params()` | Adds or overrides parameters |
| `build()` | Produces the final task |

## Running tasks from CI

A CI job runs a task by name, which keeps the job definition thin:

```python
class CheckVersion(JobBuilderImpl):
    _name = "check-version"
    _base = base.BaseTask
```

`BaseTask` supplies the script, so the generated job is:

```yaml
check-version:
  stage: jobs
  script:
    - dothat run ${CI_JOB_NAME}
```

`${CI_JOB_NAME}` lets one job template serve every variant: GitLab sets it to the job's
own name, so `test-task:target-1` runs the matching task with no per-job script.

## CLI

```bash
dothat list                              # all registered tasks
dothat help check-version                # parameters and documentation
dothat run check-version --version 2.0.0 # run, overriding a parameter
dothat --config other/environment.toml run check-version
```

`dothat help` shows where each parameter can come from:

```text
test-task:target-1  test task
  --ci                             (config: ci, environ: CI)
  --flavor                         (config: flavor)
  --insecure                       (config: insecure, opposite of secure)
```
