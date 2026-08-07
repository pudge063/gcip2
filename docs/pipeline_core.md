### CI Model API

This module provides **strongly-typed Python models** for describing GitLab CI/CD pipelines. It is built on top of **Pydantic**, allowing pipelines to be defined, validated, and serialized into GitLab-compatible YAML/JSON structures.

#### Main classes

* **`Pipeline`** – Root object representing an entire GitLab pipeline.
* **`Job`** – Represents a single CI job.
* **`JobTemplate`** – Base model containing all supported GitLab job attributes.
* **`JobBuilderImpl`** – Base class for implementing reusable job builders using the Builder pattern.
* **`Workflow`** – Defines pipeline-level workflow configuration and rules.
* **`Trigger`** – Configuration for downstream and child pipelines.
* **`Artifacts`** / **`ArtifactsReports`** – Job artifact and report configuration.
* **`Needs`** – Defines job dependencies.
* **`Image`** / **`Services`** – Container image and service configuration.
* **`Default`** – Default settings inherited by all jobs.
* **`GlobalVariables`** / **`JobVariables`** – Pipeline and job variable definitions.

#### Features

* Full type safety using **Pydantic** models.
* Serialization via `BaseModel.dump()`, producing GitLab-compatible output.
* JSON Schema validation through `Pipeline.validate_pipeline()`.
* Support for most GitLab CI keywords, including:

  * jobs
  * stages
  * workflow
  * rules
  * variables
  * artifacts
  * services
  * triggers
  * includes
  * defaults

#### Job builders

`JobBuilderImpl` provides a fluent API for constructing reusable jobs:

```python
job = BuildJob().with_name("build").with_stage("build").with_image("python:3.12").build()
```

Builders support inheritance through the `_base` class attribute, allowing common job configuration to be shared across multiple builders.

#### Validation

A pipeline can be validated against the bundled GitLab CI JSON schema:

```python
pipeline.validate_pipeline()
```

This raises a `jsonschema.ValidationError` if the generated pipeline is invalid.

#### Serialization

All models inherit from `BaseModel`, which provides the `dump()` helper:

```python
pipeline.dump()
```

The resulting dictionary:

* excludes `None` values,
* excludes default values,
* uses GitLab field aliases (for example, `if` instead of `if_`),
* is ready for YAML or JSON serialization.
