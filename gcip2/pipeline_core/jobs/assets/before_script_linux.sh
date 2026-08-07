#!/usr/bin/env sh
set -o errexit -o nounset -o xtrace
section="$(date +'%s'):before_script_setup"
printf '\e[0Ksection_start:%s[collapsed=true]\r\e[0K%s\n' "${section}" "setup"
CI_RUNNER_DIR="$(readlink -f "${CI_RUNNER_DIR:-.}")"
export CI_RUNNER_DIR
export UV_LINK_MODE=copy
uv sync --directory "${CI_RUNNER_DIR}"
venv="$(dirname "$(dirname "$(uv run --directory "${CI_RUNNER_DIR}" which python)")")"
echo "using venv '${venv}'"
. "${venv}/bin/activate"
printf '\e[0Ksection_end:%s\r\e[0K\n' "${section}"
