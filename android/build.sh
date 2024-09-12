#!/usr/bin/env bash

set -euo pipefail

# securely asks for a password after showing a prompt and put it into a variable, only if that
# variable is not set yet (typically as an environment variable)
fun_password_input() {
  local prompt="$1"
  local varname="$2"

  if [ "${!varname:-}" == "" ]; then
    echo "${prompt}"
    # source: https://stackoverflow.com/a/56861186
    read -r -s "${varname}"
  fi
}

fun_password_input "Input keystore password:" "SIGNING_STORE_PASSWORD"
fun_password_input "Input key password:" "SIGNING_KEY_PASSWORD"

SIGNING_STORE_PASSWORD="$SIGNING_STORE_PASSWORD" SIGNING_KEY_PASSWORD="$SIGNING_KEY_PASSWORD" ./gradlew build"$@"
