#!/usr/bin/env bash

# Start sshd
echo "Starting ssh server..."
service ssh restart

if [ $# -eq 0 ]
  then
    source startup_script.sh
else
    source startup_script.sh "$@"
fi