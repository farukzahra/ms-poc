#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
RG="${AZURE_RESOURCE_GROUP:-rg-ai-sales-poc}"
LOCATION="${AZURE_LOCATION:-eastus}"
IMAGE="${CONTAINER_IMAGE:-}"

echo "Deploying ms-poc infrastructure to $RG ($LOCATION)..."

az group create --name "$RG" --location "$LOCATION" --output none

DEPLOY_ARGS=""
if [ -n "$IMAGE" ]; then
  DEPLOY_ARGS="--parameters containerImage=$IMAGE"
fi

az deployment sub create \
  --location "$LOCATION" \
  --template-file "$ROOT/infrastructure/azure/bicep/main.bicep" \
  --parameters environmentName=ms-poc-dev \
  $DEPLOY_ARGS \
  --output table

echo "Done. Set CONTAINER_IMAGE to your ACR image after building:"
echo "  az acr build -r <acr> -t ms-poc-api:latest -f apps/api/Dockerfile ."
