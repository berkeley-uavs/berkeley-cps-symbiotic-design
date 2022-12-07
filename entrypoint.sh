#!/usr/bin/env bash

# Start sshd
echo "Starting ssh server..."
service ssh restart

echo "Git config..."
git config --global --add safe.directory /root/host

echo "Pulling from github..."
git pull

echo "Starting startup script..."
source startup_script.sh "$@"