#!/usr/bin/env bash

echo "pulling the submodules"
git submodule init
git submodule update --remote --merge
#echo "creating conda environment..."
#conda create --prefix ./.venv python=3.10 -y
#echo "activating conda environment..."
#source "$(conda info --base)/etc/profile.d/conda.sh"
#conda activate ./.venv
#echo "installing conda dependencies..."
#conda env update --file conda-dependencies.yml --prune
pdm install
echo "pdm dependencies installed"