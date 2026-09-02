#!/usr/bin/env bash
# Trigger a Render deploy through a service's Deploy Hook, pinned to one commit.
# Requires DEPLOY_HOOK_URL (holds its own key — never echo it) and COMMIT_SHA.
set -euo pipefail

: "${DEPLOY_HOOK_URL:?DEPLOY_HOOK_URL is required}"
: "${COMMIT_SHA:?COMMIT_SHA is required}"

separator="?"
case "${DEPLOY_HOOK_URL}" in
  *\?*) separator="&" ;;
esac

response="$(
  curl --fail-with-body --silent --show-error --retry 3 --retry-connrefused \
    --request POST "${DEPLOY_HOOK_URL}${separator}ref=${COMMIT_SHA}"
)"

echo "Render accepted a deploy of ${COMMIT_SHA}: ${response}"
