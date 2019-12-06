#!/bin/sh

set -euo pipefail # strict mode, fail on error
set -x # verbose

docker run \
  --rm \
  -t \
  -v $PWD:/mlops \
  -v ${AZURE_CONFIG_DIR:-$HOME/.azure}:/root/.azure \
  -e SUBSCRIPTION_ID=$(az account show --query id -o tsv) \
  -e RESOURCE_GROUP=$RESOURCE_GROUP \
  -e WORKSPACE_NAME=$WORKSPACE_NAME \
  -e MODEL_NAME=$MODEL_NAME \
  -e IMAGE_NAME=$IMAGE_NAME \
  mcr.microsoft.com/mlops/python:latest \
  bash -c "cd /mlops/ && python ml_service/util/create_scoring_image.py"
