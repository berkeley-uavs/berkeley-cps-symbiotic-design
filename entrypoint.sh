#!/usr/bin/env bash

# Start sshd
echo "Starting ssh server..."
service ssh restart

echo "Git config..."
git config --global --add safe.directory /root/host


source startup_script.sh "$@"