#!/usr/bin/env sh
set -o errexit -o nounset -o xtrace
section="$(date +'%s'):before_script_setup"
printf '\e[0Ksection_start:%s[collapsed=true]\r\e[0K%s\n' "${section}" "setup"
# shellcheck disable=SC2086
poetry install
. ".venv/bin/activate"
printf '\e[0Ksection_end:%s\r\e[0K\n' "${section}"
