#!/bin/sh
# Writes the runtime config consumed by the React app (window.__APP_CONFIG__).
# Run automatically by the nginx image entrypoint on container start.
set -eu

CONFIG_FILE=/usr/share/nginx/html/config.js

js_escape() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e "s/'/\\\\'/g" -e 's/</\\u003c/g' | tr '\n' ' '
}

MODE=$(js_escape "${MAINTENANCE_MODE:-}")
MESSAGE=$(js_escape "${MAINTENANCE_MESSAGE:-}")

printf "window.__APP_CONFIG__ = { MAINTENANCE_MODE: '%s', MAINTENANCE_MESSAGE: '%s' };\n" "$MODE" "$MESSAGE" > "$CONFIG_FILE"

echo "40-app-config.sh: MAINTENANCE_MODE=${MAINTENANCE_MODE:-<unset, using build-time value>}"
