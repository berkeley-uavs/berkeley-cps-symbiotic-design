#!/bin/bash
echo "Building docker image..."

base_image=pmallozzi/devenvs:base-310
image_name=${base_image}-symcps

docker pull ${base_image}

for arch in amd64 arm64 arm  ; do
    docker buildx build \
    --platform $arch \
    --output type=docker \
    --tag me/myimage:${image_name}
    .
done