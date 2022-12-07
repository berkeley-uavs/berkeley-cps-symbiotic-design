#!/bin/bash

make uninstall

base_image=pmallozzi/devenvs:base-310
image_name=${base_image}-symcps


echo "Building docker image for amd64 and arm64 architecture"
docker pull ${base_image}
docker buildx build --push --platform linux/amd64,linux/arm64 -f ./Dockerfile -t ${image_name} --push . --no-cache
