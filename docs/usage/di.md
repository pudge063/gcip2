# Dependency injection

Builders, tasks, and actions need the project configuration and shared services such as
the secrets handler. Rather than reading files themselves, they **declare** what they
need and a container supplies it.

The container is built once, in the CLI, from the `--config` flag:

```python
@click.group()
@click.option("--config", type=pathlib.Path, default=pathlib.Path("environment.toml"))
@click.pass_context
def cli(ctx: click.Context, config: pathlib.Path):
    ctx.obj = injector.Injector([Module(config_path=config)])
```

Everything below this point receives its dependencies from that container, which is why
`--config` reaches job builders without being passed down by hand.

## Declaring a dependency

A class lists its dependencies as constructor parameters and marks the constructor:

```python
class TaskRegistry:
    @injector.inject
    def __init__(self, config: ProjectConfig) -> None:
        self._config = config
```

The container matches parameters **by type annotation**: it finds who provides
`ProjectConfig`, calls that provider, and passes the result in.

Framework base classes are dataclasses, so subclasses inherit injected fields without
writing a constructor:

```python
@injector.inject
@dataclasses.dataclass
class ActionBuilderImpl(ABC):
    _di: injector.Injector
    _config: ProjectConfig
    _secret_handler: SecretsHandler
```

```python
class BuildGitlabCi(InteractivePythonAction):
    def impl(self, *, ci_file: str, out_pipeline: str, **_) -> None:
        self._di.get(PipelineBuilder).build_gitlab_ci(...)
```

Adding a field in a subclass means repeating both decorators:

```python
@injector.inject
@dataclasses.dataclass
class BaseLinux(JobBuilderImpl):
    _base = Base
    _script_linux: assets.ScriptLinux
```

## The module

`gcip2/di.py` defines what the container knows.

```python
class Module(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(ConfigPath, to=ConfigPath(self.config_path))
        binder.bind(TaskRegistry, scope=injector.singleton)
        binder.bind(SecretsHandler, scope=injector.singleton)

    @injector.singleton
    @injector.provider
    def provide_config(self, cfg_path: ConfigPath) -> ProjectConfig:
        return ProjectConfig.from_file(cfg_path.path)
```

A method decorated with `@injector.provider` registers itself under its **return type** —
the method name is irrelevant. `@injector.singleton` caches the result, so the
configuration file is read once per process no matter how many jobs are built. Providers
are lazy: nothing runs until a dependency is first requested.

`binder.bind()` takes what is requested, optionally what to return, and optionally a
scope:

| Form | Meaning |
|---|---|
| `bind(X, to=instance)` | Always return this object |
| `bind(X, to=SomeClass)` | Resolve `X` by building `SomeClass` |
| `bind(X, to=callable)` | Call this to produce `X` |
| `bind(X, scope=singleton)` | Build `X` itself, but only once |

An unbound class still resolves — the container builds it on demand — so these bindings
exist to make services *shared*, not to register them.

`ConfigPath` wraps `pathlib.Path` because binding `pathlib.Path` directly would supply
the configuration path to every parameter annotated as a path anywhere in the codebase.

## Getting objects out

| | `get(X)` | `create_object(X)` |
|---|---|---|
| Honours bindings and scope for `X` | yes | no |
| Resolves `X`'s own dependencies | yes | yes |
| Returns | the shared instance, if bound as a singleton | always a new instance |

Use `get()` for services and `create_object()` when the class is only known at runtime —
loaded from a user module, passed as an argument, or read from a class attribute.

## Where the container appears

Almost nowhere. A class needs `_di` only if it creates objects whose classes it cannot
name in advance:

| Location | Creates |
|---|---|
| `PipelineBuilder.load_pipeline` | The pipeline class found in the project's `ci.py` |
| `PipelineBuilder.build_gitlab_ci` | The trigger job builders |
| `_BasePipelineBuilder.job` | A job builder passed as an argument |
| `JobBuilderImpl._apply_base` | The builder named by `_base` |
| `Task.exec_task` | The action classes listed by the task |
| `TaskGeneratorImpl` | Task builders and auto-discovered tasks |

Everywhere else, declare the dependency by type. Taking `injector.Injector` just to call
`get()` inside hides what a class actually needs and makes it harder to test.

## Testing

Because the container is created per call rather than at import time, tests build their
own:

```python
@pytest.fixture
def di() -> injector.Injector:
    return injector.Injector([Module(config_path=REPO_ROOT / "environment.toml")])


def test_job_name(di):
    job = di.create_object(pipeline_core.JobBuilderImpl)
    job.model.name = "test-job"

    assert job.build().name == "test-job"
```

A different configuration is a different path:

```python
def test_config_path_is_respected(tmp_path):
    cfg = tmp_path / "custom.toml"
    cfg.write_text('[extra]\nmarker = "from-custom"\n')

    di = injector.Injector([Module(config_path=cfg)])

    assert di.create_object(JobBuilderImpl)._config.extra.get("marker") == "from-custom"
```

To replace a service rather than the configuration file, pass an extra module — later
modules win:

```python
def override(binder: injector.Binder) -> None:
    binder.bind(SecretsHandler, to=FakeSecretsHandler())


di = injector.Injector([Module(), override])
```

Builders must always be created through the container: calling `JobBuilderImpl()`
directly raises `TypeError`, because the generated constructor expects the injected
fields.
