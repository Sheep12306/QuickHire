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

PYTHON=python3.11

echo "=== Setting up Python venv ==="
VENV_PY=$("$VENV_DIR/bin/python3" --version 2>&1 || true)
REQUIRED_PY=$($PYTHON --version 2>&1)
if [ "$VENV_PY" != "$REQUIRED_PY" ]; then
    echo "Recreating venv ($VENV_PY -> $REQUIRED_PY)"
    rm -rf "$VENV_DIR"
fi
if [ ! -d "$VENV_DIR" ]; then
    $PYTHON -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

echo "=== Installing backend dependencies ==="
cd "$BACKEND_DIR"
pip install --upgrade pip setuptools wheel
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
if systemctl is-enabled quickhire &>/dev/null; then
    sudo systemctl restart quickhire
    echo "Backend restarted"
else
    echo "WARNING: quickhire service not registered. Run server-init.sh first."
fi

echo "=== Reloading nginx ==="
if systemctl is-active nginx &>/dev/null; then
    sudo nginx -s reload
    echo "Nginx reloaded"
else
    echo "WARNING: nginx not running. Run server-init.sh first."
fi

echo "=== Deploy complete ==="
