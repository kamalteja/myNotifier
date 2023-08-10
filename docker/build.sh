#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd $SCRIPT_DIR/.. &> /dev/null
python -m piptools compile --resolver=backtracking --strip-extras -o requirements.txt pyproject.toml
popd

# Build containers
docker-compose -f $SCRIPT_DIR/docker-compose.yaml build