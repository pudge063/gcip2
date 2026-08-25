# Pipeline models

`gcip2.pipeline_core` provides typed Pydantic models describing GitLab CI/CD pipelines.
It is the data layer that the [builders](pipeline.md) assemble — nothing here reads
configuration or writes files.

## Models

| Model | Describes |
|---|---|
| `Pipeline` | Root object: stages, jobs, workflow, defaults, variables, includes |
| `Job`, `JobTemplate` | A single job and the full set of supported job attributes |
| `Workflow` | Pipeline-level workflow configuration and rules |
| `Trigger` | Downstream and child pipeline configuration |
| `Artifacts`, `ArtifactsReports` | Job artifacts and reports |
| `Needs` | Job dependencies |
| `Image`, `Services` | Container image and service configuration |
| `Default` | Settings inherited by every job |
| `GlobalVariables`, `JobVariables` | Pipeline-level and job-level variables |

Full field documentation is generated in the [API reference](../api.rst).

## Serialisation

All models inherit a shared `BaseModel` that adds `dump()`:

```python
pipeline.dump()
```

The result is ready for YAML output:

- `None` values are excluded;
- fields left at their default are excluded;
- GitLab aliases are used, so `if_` is emitted as `if`;
- values render in JSON mode, so enums become their string values.

Excluding defaults keeps generated YAML close to what a person would have written by
hand, which matters because every build logs a diff against the previous version.

## Validation

```python
pipeline.validate_pipeline()
```

Validates the serialised pipeline against the bundled GitLab CI JSON schema and raises
`jsonschema.ValidationError` when the structure is invalid — catching unknown keywords,
wrong types, and malformed rules before GitLab sees them.
