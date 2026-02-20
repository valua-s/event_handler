#!/usr/bin/env bash

set -euo pipefail

wait-for-it "${EVENT_HANDLER_SERVICE_POSTGRES_HOST}:${EVENT_HANDLER_SERVICE_POSTGRES_PORT}"

exec "$@"