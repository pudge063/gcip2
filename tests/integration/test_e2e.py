import subprocess
from pathlib import Path

import pytest

PIPELINES = [p.name for p in Path("tests/integration/data").iterdir() if (p / "ci.py").exists()]


@pytest.mark.parametrize("pipeline", PIPELINES, ids=PIPELINES)
def test_simple_pipeline(pipeline: str):

    base_path = Path("tests/integration")

    base_data_path = base_path / "data" / pipeline
    base_golden_path = base_path / "golden" / pipeline

    output_path = base_data_path / "out"
    output_path.mkdir(exist_ok=True)

    input_file = base_data_path / "ci.py"
    output_file = output_path / "pipeline.gitlab-ci.yml"

    subprocess.run(
        [
            "dothat",
            "run",
            "build-pipeline",
            "-f",
            str(input_file),
            "-o",
            str(output_file),
        ],
        check=True,
    )

    golden_file = base_golden_path / "pipeline.gitlab-ci.yml"
    expected = golden_file.read_text()

    actual = output_file.read_text()

    assert actual == expected
