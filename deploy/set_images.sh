#!/bin/bash -e

IFS=',' read -ra SERVICE_LIST <<<$SERVICES

for service in "${SERVICE_LIST[@]}"; do
  SERVICE=$service yq eval -i '.services.[env(SERVICE)].image="$REGISTRY$SERVICE:$IMAGE_TAG"' docker-compose.yml
done