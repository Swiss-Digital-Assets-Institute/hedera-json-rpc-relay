#!/bin/bash -e

IFS=',' read -ra SERVICE_LIST <<<${{ env.SERVICES }}

for service in "${SERVICE_LIST[@]}"; do
  SERVICE=$service yq eval -i '.services.[env(SERVICE)].image="${{ env.REGISTRY }}$SERVICE:${{ steps.vars.outputs.image_tag }}"' docker-compose.yml
done