#!/bin/bash

base_image=pmallozzi/devenvs:base-310
image_name=${base_image}-symcps


docker pull ${base_image}
echo "Building docker image..."
case "${1}" in
    arm )
      echo "Building docker image for arm64 architecture"
      docker buildx build --push --platform linux/arm64 -f ./Dockerfile -t ${image_name} . --no-cache
      ;;
    amd )
      echo "Building docker image for amd64 architecture"
      docker buildx build --push --platform linux/amd64 -f ./Dockerfile -t ${image_name} . --no-cache
      ;;
    * )
      echo "Building docker image for amd64 and arm64 architecture"
      docker buildx build --push --platform linux/amd64,linux/arm64 -f ./Dockerfile -t ${image_name} . --no-cache
      ;;

  esac