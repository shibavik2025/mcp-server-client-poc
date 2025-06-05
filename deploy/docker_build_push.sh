#!/bin/bash

set -e

ACR_NAME="coreaishared.azurecr.io"
NAMESPACE="coreai"

# Prompt user for Docker image name
read -p "Enter Docker image name: " IMAGE_NAME
read -p "Enter Docker image tag: " IMAGE_TAG


# Confirm the version
read -p "Using Docker image name ($IMAGE_NAME:$IMAGE_TAG). Do you want to proceed? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Check if Azure CLI (az) is logged in
if ! az account show > /dev/null 2>&1; then
    echo "Azure CLI (az) is not logged in."
    # Prompt user to log in to Azure CLI
    az login
fi


if ! docker login $ACR_NAME > /dev/null 2>&1; then
    echo "Docker is not logged in to Azure Container Registry."
    # Prompt user to log in to Docker
    read -p "Enter Docker username: " DOCKER_USERNAME
    read -s -p "Enter Docker password: " DOCKER_PASSWORD
    echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin $ACR_NAME
fi

# Build the Docker image
docker build --platform="linux/amd64" -t $IMAGE_NAME:$IMAGE_TAG .

# Tag the Docker image for ACR
ACR_IMAGE="$ACR_NAME/$NAMESPACE/$IMAGE_NAME:$IMAGE_TAG"

docker tag $IMAGE_NAME:$IMAGE_TAG $ACR_IMAGE

# Push the Docker image to ACR
docker push $ACR_IMAGE

echo "Docker image $ACR_IMAGE has been pushed to Azure Container Registry."
