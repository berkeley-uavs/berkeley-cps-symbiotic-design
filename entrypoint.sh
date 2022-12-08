#!/usr/bin/env bash

echo "Git config..."
git config --global --add safe.directory /root/host

echo "Pulling from github..."
git pull

echo "Run docker-init"
make docker-init

echo "Starting startup script..."
source startup_script.sh "$@"