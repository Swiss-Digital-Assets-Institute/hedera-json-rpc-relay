#!/bin/bash -e

IFS=',' read -ra SERVICE_LIST <<<$SERVICES

for service in "${SERVICE_LIST[@]}"; do
  SERVICE=$service TAG="${REGISTRY}${APP_NAME}-${SERVICE}:${IMAGE_TAG}" yq eval -i '.services.[env(SERVICE)].image = env(TAG)' docker-compose.yml
done