from enum import Enum


class Tasks(Enum):
    test_task = "test-task"
    test_vault_task = "test-vault-task"
    run_initialization_pipeline = "run-initialization-pipeline"
    check_package_version = "check-package-version"
    create_version_tag = "create-version-tag"
    publish_package = "publish-package"
