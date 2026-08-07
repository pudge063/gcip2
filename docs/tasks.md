# Tasks System

The task system provides a way to define reusable automation workflows using **tasks** and **actions**.

A task represents a named operation that executes a sequence of actions with configurable parameters.

The system is designed to integrate with CLI execution and GitLab CI jobs.

---

## Overview

A task consists of:

- **Task name** — unique identifier used for execution.
- **Actions** — ordered list of operations executed by the task.
- **Parameters** — configurable values passed to actions.

Execution flow:

```text
TaskGenerator
      │
      ▼
TaskBuilder
      │
      ▼
Task
      │
      ▼
Action 1 → Action 2 → Action 3
```

---

## Creating a Task

Tasks are created by extending `TaskBuilderImpl`.

Example:

```python
class TestTask(TaskBuilderImpl):
    _basename = "test-task"

    def apply(self):
        return self.with_actions(
            (
                MyAction,
                AnotherAction,
            )
        ).with_params((my_parameter(),))
```

## Task Name

Each task must have a unique name.

The name can be defined as a string:

```python
class MyTask(TaskBuilderImpl):
    _basename = "my-task"
```

or by using an enum:

```python
from enum import Enum


class Tasks(Enum):
    MY_TASK = "my-task"


class MyTask(TaskBuilderImpl):
    _basename = Tasks.MY_TASK
```

When an enum is used, its value is stored as the task name.

---

## Actions

Actions contain the actual execution logic.

There are two built-in action types.

### `InteractivePythonAction`

Used for Python-based operations.

```python
class CheckVersion(InteractivePythonAction):
    def impl(self, *, version: str, **_):
        LOGGER.info(version)
```

### `InteractiveShlex`

Used for shell command execution.

```python
class CheckCommand(InteractiveShlex):
    def impl(self, *, command: str, **_) -> list[str]:
        return [
            "echo",
            command,
        ]
```

---

## Action Execution

Actions are executed sequentially.

Example task:

```python
self.with_actions(
    (
        FirstAction,
        SecondAction,
        ThirdAction,
    )
)
```

Execution order:

```text
FirstAction
      │
      ▼
SecondAction
      │
      ▼
ThirdAction
```

Every action receives task parameters as keyword arguments.

Example:

```python
action.execute(
    version="1.0.0",
    enabled=True,
)
```

---

## Parameters

Parameters define configurable task inputs.

Example:

```python
def version():
    return Param(
        name="version",
        long="version",
        default="latest",
        type=str,
    )
```

Parameters are attached to a task:

```python
self.with_params((version(),))
```

The parameter value becomes available inside actions:

```python
class PrintVersion(InteractivePythonAction):
    def impl(self, *, version: str, **_):
        print(version)
```

---

## Parameter Sources

Task parameters can come from multiple sources.

### Default values

Defined in task parameters:

```python
Param(
    name="version",
    default="latest",
)
```

### CLI arguments

Example:

```bash
gciptask run test-task --version 2.0.0
```

The CLI value overrides the default value.

### Project configuration

Values from `environment.toml` can be automatically passed.

Example:

```toml
[extra]
version = "1.2.3"
```

Available in actions:

```python
def impl(self, *, extra__version: str, **_):
    print(extra__version)
```

---

## Task Generator

`TaskGenerator` is responsible for task discovery.

Example:

```python
class TaskGenerator(TaskGeneratorImpl):
    def load_tasks(self):

        yield (self.builder(TestTask).apply().build())


TASK_GENERATOR = TaskGenerator()
```

The generator returns all available tasks.

The CLI loads tasks from the configured module:

```toml
[extra.tasks]
module = "_tasks"
```

---

## Example Task

Task definition:

```python
class TestVaultSecret(TaskBuilderImpl):
    _basename = "test-vault-secret"

    def apply(self):

        return self.with_actions((CheckSecretAction,)).with_params((vault_section(),))
```

---

## Using Tasks in GitLab Jobs

Tasks can be attached to jobs through `JobBuilderImpl`.

Example:

```python
class TestSecretHandlerInTask(JobBuilderImpl):
    _task = "test-vault-secret"
```

The generated GitLab job executes:

```yaml
script:
  - gciptask run test-vault-secret
```

---

## Complete Execution Example

```text
GitLab Job
      │
      ▼
gciptask run test-vault-secret
      │
      ▼
Task Registry
      │
      ▼
TestVaultSecret
      │
      ├── CheckSecretAction
      ├── ValidateAction
      └── CleanupAction
```

---

## Features

- Declarative task definitions.
- Reusable action components.
- Sequential action execution.
- CLI parameter overrides.
- Configuration-based parameters.
- Enum-based task names.
- Automatic task discovery.
- GitLab CI integration.
- Support for Python- and shell-based actions.
- Extensible task and action architecture.
