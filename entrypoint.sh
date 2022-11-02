#!/usr/bin/env bash

# Start sshd
echo "Starting ssh server..."
service ssh restart

echo "Git config..."
git config --global --add safe.directory /root/host

if [ $# -eq 0 ]
  then
    source startup_script.sh
else
    source startup_script.sh "$@"
fi