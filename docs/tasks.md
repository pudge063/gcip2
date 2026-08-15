# Tasks System

The **Tasks System** provides a reusable framework for defining and executing automation workflows.

A task is a named, configurable operation composed of one or more **actions**. Actions contain the actual execution logic, while tasks define how those actions are combined and which parameters are available.

The system is designed to work with:

- CLI commands;
- GitLab CI/CD pipelines;
- project configuration;
- reusable Python and shell actions;
- dynamically generated task variants.

The main goal is to keep automation logic **declarative, reusable, and composable**.

---

## Architecture

The Tasks System is built around four main concepts:

- **Task** — a named automation workflow.
- **Action** — a single executable operation.
- **Parameter** — a configurable input available to actions.
- **Task Generator** — discovers and creates the available tasks.

A simplified execution flow looks like this:

```text
                    Task Generator
                          │
                          ▼
                    Task Builder
                          │
                          ▼
                         Task
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Action 1     Action 2     Action 3
             │            │            │
             └────────────┴────────────┘
                          │
                          ▼
                    Task parameters
```

A task does not need to contain execution logic itself. Instead, it defines:

1. which actions should be executed;
2. which parameters are available;
3. which name should be used to identify the task.

---

# Tasks

A task represents a named automation workflow.

Each task consists of:

- **Task name** — a unique identifier used to execute the task.
- **Actions** — an ordered collection of operations.
- **Parameters** — configurable values passed to actions.
- **Documentation** — a description displayed by the CLI.

A minimal task looks like this:

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

The task can then be executed by its name:

```bash
dothat run test-task
```

---

## Task Name

Every task must have a unique name.

The simplest way to define a task name is with a string:

```python
class MyTask(TaskBuilderImpl):
    _basename = "my-task"
```

The name becomes the identifier used by the CLI:

```bash
dothat run my-task
```

### Enum-based task names

Task names can also be defined using an enum.

```python
from enum import Enum


class Tasks(Enum):
    MY_TASK = "my-task"


class MyTask(TaskBuilderImpl):
    _basename = Tasks.MY_TASK
```

When an enum is used, its **value** is stored as the task name.

In this example, the resulting task name is:

```text
my-task
```

Using an enum can be useful when task names are shared between multiple parts of the application.

---

# Task Name Suffixes

A task can be reused to create multiple task variants using `with_name()`.

This is useful when several jobs have:

- the same actions;
- the same base implementation;
- different parameters;
- different names in the generated CI configuration.

For example:

```text
test-task:target-1
test-task:target-2
```

Both tasks can use the same task implementation while receiving different parameters.

## Example

Suppose a base task is defined as:

```python
class TestBaseTask(TaskBuilderImpl):
    _basename = "test-task"

    def apply(self):
        return self.with_actions((TestAction,))
```

The task generator can create multiple variants:

```python
class TaskGenerator(TaskGeneratorImpl):
    def load_tasks(self) -> Iterator[Task]:
        yield from super().load_tasks()

        targets = [
            "target-1",
            "target-2",
        ]

        for target in targets:
            yield (
                self.builder(TestBaseTask)
                .apply()
                .with_name(target)
                .with_params(
                    (
                        self._params.ci(),
                        _params.flavor(),
                        _params.insecure(),
                    )
                )
                .build()
            )


TASK_GENERATOR = TaskGenerator()
```

This produces two tasks:

```text
test-task:target-1
test-task:target-2
```

Both tasks use the same actions, but they can have different parameter values.

### Generated GitLab jobs

For example, this allows generating multiple GitLab jobs:

```yaml
test-task:target-1:
  stage: jobs
  script:
    - dothat run ${CI_JOB_NAME}

test-task:target-2:
  stage: jobs
  script:
    - dothat run ${CI_JOB_NAME}
```

The first job executes:

```text
test-task:target-1
```

and the second:

```text
test-task:target-2
```

This makes task variants particularly useful for matrix-like CI configurations.

---

# Task Documentation

Tasks can expose a human-readable description through their `doc` field.

The description is displayed by the CLI.

Use:

```bash
dothat list
```

to see all registered tasks:

```text
R build-pipeline                  gcip2.tasks_core.ci_tasks._tasks.BuildPipeline
R build-gitlab-ci                 gcip2.tasks_core.ci_tasks._tasks.BuildGitlabCi
R init                            gcip2.tasks_core.ci_tasks._tasks.InitializeDefaultProject
R check-package-version           _tasks._tasks.CheckPackageVersion
R create-version-tag              _tasks._tasks.CreateVersionTag
R publish-package                 _tasks._tasks.PublishPackage
R initialize-project-pipeline     _tasks._tasks.InitializeProjectPipeline
R run-initialized-pipeline        _tasks._tasks.RunInitializedPipeline
R test-task:test-1                test task
R test-task:test-2                test task
R test-vault-task                 _tasks._tasks.TestVaultSecret
```

The command provides a quick overview of all available tasks.

---

## Task Details

Use:

```bash
dothat help TASK_NAME
```

to display detailed information about a task.

For example:

```bash
dothat help test-task:test-1
```

Output:

```text
test-task:test-1  test task
  --ci                             (config: ci, environ: CI)
  --flavor                         (config: flavor)
  --insecure                       (config: insecure, opposite of secure)
```

The help output shows:

- task name;
- task description;
- available parameters;
- configuration names;
- environment variable mappings;
- parameter relationships such as opposite flags.

---

# Actions

Actions contain the actual execution logic.

A task should generally describe **what should be executed**, while an action describes **how a particular operation is executed**.

Actions are reusable and can be shared between multiple tasks.

There are currently two built-in action types:

- `InteractivePythonAction`
- `InteractiveShlex`

---

## `InteractivePythonAction`

`InteractivePythonAction` is used for operations implemented in Python.

Example:

```python
class CheckVersion(InteractivePythonAction):
    def impl(self, *, version: str, **_):
        LOGGER.info(version)
```

The implementation receives task parameters as keyword arguments.

In this example, the `version` parameter is available directly:

```python
version
```

Additional parameters can be ignored using:

```python
**_
```

This is useful when an action only requires a subset of the parameters defined by a task.

---

## `InteractiveShlex`

`InteractiveShlex` is used for shell command execution.

Example:

```python
class CheckCommand(InteractiveShlex):
    def impl(self, *, command: str, **_) -> list[str]:
        return [
            "echo",
            command,
        ]
```

The action returns a command represented as a list of arguments.

For example:

```python
[
    "echo",
    "hello",
]
```

is equivalent to executing:

```bash
echo hello
```

Using an argument list avoids unnecessary shell parsing and makes command construction explicit.

---

# Action Execution

Actions are executed **sequentially and in the order in which they are defined**.

For example:

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

The order is significant when later actions depend on the result or side effects of earlier actions.

---

## Action Parameters

Task parameters are passed to actions as keyword arguments.

For example:

```python
action.execute(
    version="1.0.0",
    enabled=True,
)
```

An action can declare only the parameters it needs:

```python
class PrintVersion(InteractivePythonAction):
    def impl(self, *, version: str, **_):
        print(version)
```

The same task can contain actions requiring different subsets of the available parameters.

For example:

```text
Task parameters
      │
      ├── version ──────────► PrintVersion
      │
      ├── enabled ──────────► EnableFeature
      │
      └── environment ──────► Deploy
```

This allows actions to remain small and reusable.

---

# Parameters

Parameters define the configurable inputs of a task.

A parameter can define:

- its internal name;
- its CLI name;
- its default value;
- its type;
- configuration mapping;
- environment mapping;
- relationships with other parameters.

A simple parameter can be defined as:

```python
def version():
    return Param(
        name="version",
        long="version",
        default="latest",
        type=str,
    )
```

The parameter is then attached to a task:

```python
self.with_params((version(),))
```

The value becomes available to actions:

```python
class PrintVersion(InteractivePythonAction):
    def impl(self, *, version: str, **_):
        print(version)
```

---

# Parameter Sources

Parameter values can come from multiple sources.

The Tasks System supports combining defaults, CLI arguments, and project configuration.

## Default Values

A parameter can define a default:

```python
Param(
    name="version",
    default="latest",
)
```

If no other value is provided, the action receives:

```text
latest
```

---

## CLI Arguments

Parameters can be overridden from the command line.

For example:

```bash
dothat run test-task --version 2.0.0
```

The explicitly provided CLI value takes precedence over the default:

```text
default: latest
CLI:     2.0.0
             │
             ▼
         version=2.0.0
```

---

## Project Configuration

Values can also be provided through the project configuration.

For example, `environment.toml` can contain:

```toml
[extra]
version = "1.2.3"
```

The configuration value becomes available to actions using the corresponding configuration namespace:

```python
def impl(self, *, extra__version: str, **_):
    print(extra__version)
```

The `__` separator represents the configuration hierarchy.

For example:

```text
extra.version
     │
     ▼
extra__version
```

This makes configuration values accessible without requiring each action to load configuration files directly.

---

# Task Generator

`TaskGenerator` is responsible for discovering and creating the available tasks.

A generator returns an iterator of tasks:

```python
class TaskGenerator(TaskGeneratorImpl):
    def load_tasks(self):
        yield (self.builder(TestTask).apply().build())


TASK_GENERATOR = TaskGenerator()
```

The task registry is populated from the tasks returned by the generator.

The CLI can then discover and execute those tasks:

```bash
dothat list
```

and:

```bash
dothat run test-task
```

---

## Task Discovery

The CLI loads tasks from the configured module.

For example, `environment.toml` can contain:

```toml
[extra.tasks]
module = "_tasks"
```

The configured module is used as the source of task definitions.

This allows projects to provide their own task implementations without modifying the core Tasks System.

The `module` field is optional. If it is not set, no additional tasks are loaded from a custom module — only the built-in tasks remain available.

---

# Building a Task

The typical task creation flow is:

```python
self.builder(MyTask)
    .apply()
    .with_name("my-variant")
    .with_params(
        (
            parameter(),
        )
    )
    .build()
```

Each step has a specific responsibility:

| Method | Purpose |
|---|---|
| `builder()` | Creates a builder for the task |
| `apply()` | Applies the task's default configuration |
| `with_name()` | Adds a suffix to the task name |
| `with_params()` | Adds or overrides task parameters |
| `build()` | Creates the final task |

This makes task construction explicit and allows the same task implementation to be reused with different configurations.

---

# Example Task

The following example defines a task that checks a Vault secret:

```python
class TestVaultSecret(TaskBuilderImpl):
    _basename = "test-vault-secret"

    def apply(self):
        return self.with_actions((CheckSecretAction,)).with_params((vault_section(),))
```

The task consists of:

- the `test-vault-secret` name;
- the `CheckSecretAction` action;
- the `vault_section` parameter.

It can then be executed with:

```bash
dothat run test-vault-secret
```

---

# Using Tasks in GitLab CI

Tasks can be integrated into GitLab CI jobs through `JobBuilderImpl`.

For example:

```python
class TestSecretHandlerInTask(JobBuilderImpl):
    _task = "test-vault-secret"
```

The generated GitLab job executes the task:

```yaml
script:
  - dothat run test-vault-secret
```

This keeps the GitLab job definition thin while moving the actual automation logic into reusable tasks and actions.

---

## Using the Current GitLab Job Name

When multiple jobs use task name suffixes, the GitLab job name can be used to select the corresponding task.

For example:

```yaml
script:
  - dothat run ${CI_JOB_NAME}
```

Given the following jobs:

```text
test-task:target-1
test-task:target-2
```

GitLab provides:

```text
CI_JOB_NAME=test-task:target-1
```

for the first job and:

```text
CI_JOB_NAME=test-task:target-2
```

for the second.

Therefore:

```bash
dothat run ${CI_JOB_NAME}
```

automatically executes the task corresponding to the current GitLab job.

This is especially useful for dynamically generated task variants.

---

# Complete Execution Flow

A typical execution looks like this:

```text
GitLab CI Job
      │
      ▼
dothat run test-vault-secret
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

The flow can be summarized as:

1. GitLab starts a job.
2. The job invokes the `dothat` CLI.
3. The CLI resolves the requested task name.
4. The task is loaded from the task registry.
5. Task parameters are resolved from defaults, configuration, and CLI arguments.
6. Actions are executed sequentially.
7. Each action receives the parameters required by its implementation.

---

# Design Principles

The Tasks System follows several principles.

## Reusability

Actions should implement small, reusable pieces of functionality.

A single action can be used by multiple tasks:

```text
                 ┌── Task A
                 │
CheckVersion ────┼── Task B
                 │
                 └── Task C
```

This avoids duplicating implementation logic.

---

## Composition

Tasks are built by composing actions:

```python
self.with_actions(
    (
        PrepareAction,
        BuildAction,
        TestAction,
        PublishAction,
    )
)
```

Complex workflows can therefore be assembled from smaller components.

---

## Declarative Task Definitions

A task primarily describes its workflow rather than implementing it directly.

Instead of:

```python
class MyTask:
    # lots of execution logic
```

the preferred approach is:

```python
class MyTask(TaskBuilderImpl):
    _basename = "my-task"

    def apply(self):
        return self.with_actions(
            (
                PrepareAction,
                BuildAction,
                PublishAction,
            )
        )
```

The actual execution logic remains inside the actions.

---

## Separation of Concerns

The main components have separate responsibilities:

```text
TaskGenerator
    │
    │ discovers tasks
    ▼
TaskBuilder
    │
    │ configures tasks
    ▼
Task
    │
    │ defines workflow
    ▼
Action
    │
    │ performs operation
    ▼
External system / process
```

This separation makes the system easier to extend and test.

---

# CLI Reference

## List tasks

Display all available tasks:

```bash
dothat list
```

---

## Show task details

Display a task's parameters and documentation:

```bash
dothat help TASK_NAME
```

Example:

```bash
dothat help test-task:test-1
```

---

## Execute a task

Run a task by name:

```bash
dothat run TASK_NAME
```

Example:

```bash
dothat run test-vault-secret
```

Parameters can be overridden from the CLI:

```bash
dothat run test-task --version 2.0.0
```

---

# Features

The Tasks System provides:

- Declarative task definitions.
- Reusable action components.
- Sequential action execution.
- Configurable task parameters.
- CLI parameter overrides.
- Default parameter values.
- Project configuration integration.
- Enum-based task names.
- Task name suffixes and task variants.
- Automatic task discovery.
- GitLab CI/CD integration.
- Dynamic GitLab job/task mapping.
- Python-based actions.
- Shell-based actions.
- Extensible task and action architecture.
- Centralized task documentation through the CLI.

---

# Summary

The Tasks System separates **workflow definition** from **execution logic**.

A typical implementation follows this structure:

```text
Task Generator
      │
      ▼
Task Builder
      │
      ├── Name
      ├── Parameters
      └── Actions
             │
             ├── Python Action
             ├── Shell Action
             └── Custom Action
```

Tasks provide the reusable workflow definition, parameters provide configuration, and actions perform the actual work.

This architecture makes it possible to define an automation workflow once and reuse it across:

- local CLI execution;
- multiple task variants;
- GitLab CI jobs;
- different environments;
- different parameter configurations.

The result is a consistent and composable way to build automation workflows without duplicating execution logic across CI configuration and application code.
