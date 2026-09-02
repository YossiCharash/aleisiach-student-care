#!/bin/sh
# Apply database migrations before the app boots, then hand off to the container command.
# Runs on every container host that uses the image's default entrypoint (cloud deploys included),
# so the schema always exists before startup queries it.
set -e

alembic upgrade head

exec "$@"
