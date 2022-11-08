#!/usr/bin/env bash
echo "Clean up and removing all installation files and folders"
rm -rf .coverage*
rm -rf .mypy_cache
rm -rf .pytest_cache
rm -rf tests/.pytest_cache
rm -rf build
rm -rf dist
rm -rf htmlcov
rm -rf site
rm -rf pip-wheel-metadata
find . -type d -name __pycache__ | xargs rm -rf
find . -name '*.rej' -delete
rm -rf .venv
rm -rf __pypackages__
rm -rf pdm.lock
rm -rf .pdm.toml
echo "Uninstall completed"