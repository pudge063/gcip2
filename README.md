# GCIP2

**GCIP2** is a Python DSL for building **GitLab CI/CD pipelines** using strongly typed Pydantic models and a fluent builder API.

Instead of writing large YAML files, pipelines are defined in Python, validated against the official GitLab CI schema, and rendered into GitLab-compatible YAML.

## Features

* Strongly typed GitLab CI models
* Fluent builder API
* Reusable job builders
* Pipeline inheritance
* JSON Schema validation
* Automatic YAML generation
* Dynamic pipeline discovery
* GitLab-compatible output

---

# Installation

Create `pyproject.toml` with pyproject configuration
```
[project]
name = "dev"
version = "0.0.0"
description = ""
requires-python = ">=3.11,<4.0"

```


```bash
uv add gcip2
```

---

# Quick Start

Initialize a new project:

```bash
dothat run init
```

This generates a minimal project structure:

```text
.
├── ci.py
├── pyproject.toml
├── environment.toml
└── .pre-commit-config.yaml
```

Generate a child pipeline:

```bash
dothat run build-pipeline
```

or explicitly:

```bash
dothat run build-pipeline \
    --ci-file ci.py \
    --out-pipeline out/pipeline.gitlab-ci.yml
```

Generate the root `.gitlab-ci.yml`:

```bash
dothat run build-gitlab-ci
```

or

```bash
dothat run build-gitlab-ci \
    --ci-file ci.py \
    --out-gitlab-ci .gitlab-ci.yml
```

---

# Documentation

Detailed documentation is available in the `docs/` directory.

| Document                                       | Description                                         |
| ---------------------------------------------- | --------------------------------------------------- |
| [docs/pipeline.md](https://gl.pivlab.space/rnd/gcip2/-/blob/master/docs/builder.md)               | Creating pipelines, jobs and workflow configuration |
| [docs/builder.md](https://gl.pivlab.space/rnd/gcip2/-/blob/master/docs/builder.md)                | Pipeline builder, rendering and YAML generation     |
| [docs/pipeline_core.md](https://gl.pivlab.space/rnd/gcip2/-/blob/master/docs/pipeline_core.md)    | Reference for the typed GitLab CI models            |
| [docs/secrets.md](https://gl.pivlab.space/rnd/gcip2/-/blob/master/docs/secrets.md)                | SecretsHandler with Vault integration               |
| [docs/project_config.md](https://gl.pivlab.space/rnd/gcip2/-/blob/master/docs/project_config.md)  | ProjectConfig with global environment               |
| [CHANGELOG.md](https://gl.pivlab.space/rnd/gcip2/-/blob/master/CHANGELOG.md)                      | Project changelog                                   |

---

# Project Structure

A typical project consists of two builders:

```text
ci.py
 ├── Pipeline(PipelineBuilderImpl)
 │      └── generates:
 │          out/pipeline.gitlab-ci.yml
 │
 └── GitlabCi(GitlabCiBuilderImpl)
        └── generates:
            .gitlab-ci.yml
```

`Pipeline` defines the reusable downstream pipeline, while `GitlabCi` defines the repository's root GitLab CI configuration.

---

# CLI

Initialize a project:

```bash
dothat run init
```

Force regeneration of template files:

```bash
dothat run init --force
```

Build a child pipeline:

```bash
dothat run build-pipeline
```

Build the repository `.gitlab-ci.yml`:

```bash
dothat run build-gitlab-ci
```

---

# Validation

Generated pipelines can be validated against the bundled GitLab JSON schema before rendering.

---

# External Links

* JSON Schema: [https://json-schema.org/draft-07/json-schema-release-notes#keywords](https://json-schema.org/draft-07/json-schema-release-notes#keywords)
* GitLab Pipeline Schema: [https://gitlab.com/gitlab-org/gitlab-foss/-/raw/master/app/assets/javascripts/editor/schema/ci.json](https://gitlab.com/gitlab-org/gitlab-foss/-/raw/master/app/assets/javascripts/editor/schema/ci.json)
* GitLab CI Documentation: [https://docs.gitlab.com/ci/pipeline_editor/#view-full-configuration](https://docs.gitlab.com/ci/pipeline_editor/#view-full-configuration)

---

# License

[https://gl.pivlab.space/rnd/gcip2/-/blob/master/LICENCE.md](LICENCE.md) 
