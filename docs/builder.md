### Pipeline Builder API

The `PipelineBuilder` is responsible for loading user-defined pipeline definitions, building typed pipeline models, validating their structure, and rendering them into GitLab CI YAML.

#### Main responsibilities

* Load pipeline definitions from Python modules.
* Instantiate user pipeline builders automatically.
* Build a `Pipeline` object from builder implementations.
* Render pipelines into GitLab-compatible YAML.
* Write the generated pipeline to disk.
* Support both standalone pipelines and top-level `.gitlab-ci.yml` generation.

#### Main methods

* **`load_pipeline(path, obj_type)`** – Dynamically imports a Python module and instantiates the first subclass of the requested builder type.
* **`render_pipeline(pipeline)`** – Converts a `Pipeline` model into a dictionary suitable for YAML serialization. Job names become top-level YAML keys, matching the GitLab CI format.
* **`build_pipeline_file(pipeline, path)`** – Serializes the pipeline and writes the resulting YAML file to disk.
* **`build_pipeline(ci_file_path, out_pipeline_path)`** – Builds a standalone pipeline from a `PipelineBuilderImpl`.
* **`build_gitlab_ci(ci_file_path, out_gitlab_ci)`** – Builds the root `.gitlab-ci.yml` from a `GitlabCiBuilderImpl`, automatically adding trigger jobs and workflow rules when required.

#### Pipeline discovery

Pipeline definitions are regular Python modules. The builder dynamically imports the module and instantiates the first class that inherits from the requested base class.

Example:

```python
class MyPipeline(PipelineBuilderImpl):
    ...
```

No manual registration is required.

#### Rendering

`render_pipeline()` transforms the internal `Pipeline` model into the structure expected by GitLab CI:

* pipeline-level fields (`workflow`, `stages`, `variables`, etc.) remain at the root level;
* each job is emitted as a top-level YAML mapping using its `name`;
* duplicate job names are rejected;
* every job must define a name before rendering.

#### YAML generation

Pipelines are serialized using a custom YAML dumper that:

* preserves key ordering;
* formats multiline strings using YAML block scalars (`|`);
* produces human-readable indentation;
* writes UTF-8 output without escaping Unicode characters.

#### Automatic workflow configuration

When building pipelines, the builder automatically injects the following workflow rule if it is not already present:

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "parent_pipeline"'
      when: always
```

This ensures that pipelines can be executed correctly when triggered as downstream (child) pipelines.

#### Output

If no output path is specified, generated pipelines are written to:

```text
out/pipeline.gitlab-ci.yml
```

Otherwise, the pipeline is written to the user-provided destination.

#### Builder workflow

The typical build process is:

1. Load the user pipeline module.
2. Instantiate the pipeline builder.
3. Execute `apply().build()` to construct a `Pipeline`.
4. Inject required workflow configuration.
5. Render the pipeline into the GitLab CI structure.
6. Serialize the result to YAML.
7. Write the generated file to disk.
