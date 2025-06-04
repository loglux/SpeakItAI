#!/bin/sh

CONTAINER_NAME="speekit"
IMAGE_NAME="speekit:latest"
LOG_FILE="update_speekit.log"

log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "$LOG_FILE"
}

log "--- Updating $CONTAINER_NAME ---"

# Step 1: Rebuild the image
log "Building Docker image..."
docker compose build || { log "Image build failed!"; exit 1; }

# Step 2: Stop container
log "Stopping existing container (if running)..."
docker compose stop || true

# Step 3: Remove old container
log "Removing old container (if exists)..."
docker compose rm -f || true

# Step 4: Start container again
log "Starting updated container..."
docker compose up -d || { log "Failed to start container!"; exit 1; }

log "✔ Update completed"
