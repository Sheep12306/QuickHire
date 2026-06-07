#!/bin/bash
set -e

PROJECT_DIR="/opt/quickhire"
BACKEND_DIR="$PROJECT_DIR/quickhire-v2/backend"
FRONTEND_DIR="$PROJECT_DIR/quickhire-v2/frontend"
VENV_DIR="$BACKEND_DIR/venv"
NGINX_STATIC="/usr/share/nginx/html/quickhire"

echo "=== Pulling latest code ==="
cd "$PROJECT_DIR"
git pull origin main

echo "=== Setting up Python venv ==="
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

echo "=== Installing backend dependencies ==="
cd "$BACKEND_DIR"
pip install -r requirements.txt

echo "=== Building frontend ==="
cd "$FRONTEND_DIR"
npm ci --legacy-peer-deps
npm run build

echo "=== Deploying frontend static files ==="
sudo mkdir -p "$NGINX_STATIC"
sudo rm -rf "$NGINX_STATIC"/*
sudo cp -r dist/* "$NGINX_STATIC"/

echo "=== Restarting backend ==="
sudo systemctl restart quickhire

echo "=== Reloading nginx ==="
sudo nginx -s reload

echo "=== Deploy complete ==="
