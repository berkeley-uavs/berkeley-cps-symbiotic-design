#!/bin/bash
echo "Building docker image..."
docker pull pmallozzi/devenvs:base-310
docker buildx build --platform linux/amd64,linux/arm64 -f ./Dockerfile -t pmallozzi/devenvs:base-310-symcps .
docker buildx build --load -t pmallozzi/devenvs:base-310-symcps .

