#!/usr/bin/env bash

set -euo pipefail

alembic upgrade head

exec python3 -m consumer