#!/usr/bin/env bash

set -euo pipefail

wait-for-it "${EVENT_HANDLER_SERVICE_KAFKA_HOST}:${EVENT_HANDLER_SERVICE_KAFKA_PORT}"

exec "$@"