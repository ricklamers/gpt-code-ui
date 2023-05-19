#!/bin/bash
VERSION=$(grep -oP "(?<=version=')[^']*" setup.py)
TAG="v$VERSION"
TITLE="$TAG"
DESCRIPTION="Install with \`pip install gpt-code-ui\` or download bundle and run \`pip install -e .\`."

# If $GH_API_TOKEN print error
if [ -z "$GH_API_TOKEN" ]; then
    echo "Error: Please set the GH_API_TOKEN environment variable."
    exit 1
fi

API_JSON=$(printf '{"tag_name": "%s", "target_commitish": "main", "name": "%s", "body": "%s", "draft": false, "prerelease": false}' "$TAG" "$TITLE" "$DESCRIPTION")

curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $GH_API_TOKEN" --data "$API_JSON" https://api.github.com/repos/ricklamers/gpt-code-ui/releases
