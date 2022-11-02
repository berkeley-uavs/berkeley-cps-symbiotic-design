#!/bin/bash
echo "Building docker image..."

base_image=pmallozzi/devenvs:base-310
image_name=${base_image}-symcps

docker pull ${base_image}

docker buildx build --platform linux/amd64,linux/arm64 --output type=docker -f ./Dockerfile -t ${image_name} .
