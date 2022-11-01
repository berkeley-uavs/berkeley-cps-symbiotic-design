#!/usr/bin/env bash

echo "importing dependencies..."
mv /home/headless/dependencies/ /home/headless/code/__pypackages__/
exec "$@"