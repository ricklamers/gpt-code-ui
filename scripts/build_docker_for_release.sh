#!/bin/bash

# After Publish the GitHub New release
VERSION=$(grep -oP "(?<=version=')[^']*" setup.py)
TAG="$VERSION"

VERSION=$(cat gpt-code-ui/VERSION)
docker build -t "ricklamers/gpt-code-ui:${TAG}" --build-arg="VERSION=${TAG}" -f docker/Dockerfile.tag . 