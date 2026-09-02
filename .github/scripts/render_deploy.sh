#!/usr/bin/env bash
# Trigger a Render deploy for one service at an exact commit and wait for its outcome.
# Usage: render_deploy.sh <service-id> <commit-sha>   (RENDER_API_KEY must be set)
set -euo pipefail

readonly API_ROOT="https://api.render.com/v1/services"

service_id="${1:?service id is required}"
commit_sha="${2:?commit sha is required}"
poll_interval_seconds="${RENDER_POLL_INTERVAL_SECONDS:-15}"
timeout_seconds="${RENDER_DEPLOY_TIMEOUT_SECONDS:-1800}"
: "${RENDER_API_KEY:?RENDER_API_KEY is required}"

render_api() {
  curl --fail --silent --show-error --retry 3 --retry-connrefused \
    --header "Authorization: Bearer ${RENDER_API_KEY}" \
    --header "Accept: application/json" \
    "$@"
}

start_deploy() {
  render_api --request POST \
    --header "Content-Type: application/json" \
    --data "{\"commitId\":\"${commit_sha}\",\"clearCache\":\"do_not_clear\"}" \
    "${API_ROOT}/${service_id}/deploys" | jq -r '.id'
}

deploy_status() {
  render_api "${API_ROOT}/${service_id}/deploys/${1}" | jq -r '.status'
}

deploy_id="$(start_deploy)"
echo "Render deploy ${deploy_id} started for service ${service_id} at ${commit_sha}"

deadline=$((SECONDS + timeout_seconds))
while ((SECONDS < deadline)); do
  status="$(deploy_status "${deploy_id}")"
  case "${status}" in
    live)
      echo "Deploy ${deploy_id} is live"
      exit 0
      ;;
    build_failed | update_failed | pre_deploy_failed | canceled | deactivated)
      echo "Deploy ${deploy_id} ended as ${status}" >&2
      exit 1
      ;;
    *)
      echo "Deploy ${deploy_id}: ${status}"
      sleep "${poll_interval_seconds}"
      ;;
  esac
done

echo "Deploy ${deploy_id} did not finish within ${timeout_seconds}s" >&2
exit 1
