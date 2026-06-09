#!/bin/bash

# Ensure required token is set
if [ -z "$PORTFOLIO_PAT" ]; then
  echo "Error: PORTFOLIO_PAT environment variable is not set."
  exit 1
fi

REPO_NAME=${1:-"selfhost"}

echo "Triggering portfolio rebuild for repository: $REPO_NAME..."

curl -s -X POST \
  -H "Authorization: token $PORTFOLIO_PAT" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/ankittejyadav/ankittejyadav.github.io/dispatches \
  -d "{\"event_type\": \"portfolio_update\", \"client_payload\": {\"repo\": \"$REPO_NAME\"}}"

echo "Dispatch event triggered successfully!"
