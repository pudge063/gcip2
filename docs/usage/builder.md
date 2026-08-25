# Pipeline builder

`PipelineBuilder` turns a pipeline definition into a GitLab CI file: it loads the
definition, builds the typed model, renders it, and writes the result to disk.

It is obtained from the container, not constructed directly:

```python
self._di.get(PipelineBuilder)
```

## Entry points

| Method | Purpose |
|---|---|
| `build_gitlab_ci(ci_file_path, out_gitlab_ci)` | Builds the root `.gitlab-ci.yml`, adding trigger jobs and workflow rules when needed |
| `build_pipeline(ci_file_path, out_pipeline_path)` | Builds a standalone child pipeline |
| `load_pipeline(path, obj_type)` | Imports a module and creates the first subclass of the requested builder type |
| `render_pipeline(pipeline)` | Converts a `Pipeline` model into the GitLab CI dictionary |
| `build_pipeline_file(pipeline, path)` | Serialises and writes the file |

## Discovery

Pipeline definitions are ordinary Python modules. The builder imports the module and
creates the first class inheriting from the requested base — no registration is needed:

```python
class MyPipeline(PipelineBuilderImpl): ...
```

The class is created through the container, so it receives the project configuration
along with everything else it declares.

## Rendering

`render_pipeline()` transforms the model into the structure GitLab expects:

- pipeline-level fields such as `workflow`, `stages`, and `variables` stay at the root;
- each job becomes a top-level mapping keyed by its name;
- a job without a name, or a duplicate name, is rejected.

Serialisation uses a custom YAML dumper that preserves key order, emits multiline
strings as block scalars, and writes UTF-8 without escaping non-ASCII characters.

## Output

Without an explicit path, pipelines are written to `out/pipeline.gitlab-ci.yml`.

Before writing, the builder logs a unified diff against the existing file. Unchanged
files are reported as such, so regenerating configuration in review shows exactly what
moved.
