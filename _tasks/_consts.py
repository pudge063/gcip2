from enum import Enum


class Tasks(Enum):
    test_task = "test-task"
    test_vault_task = "test-vault-task"
    initialize_project_pipeline = "initialize-project-pipeline"
    run_initialized_pipeline = "run-initialized-pipeline"
    check_package_version = "check-package-version"
    create_version_tag = "create-version-tag"
    publish_package = "publish-package"
    generate_docs = "generate-docs"


class PipelineStatus(Enum):
    success = "success"
    failed = "failed"
    running = "running"
