#!/bin/bash
set -e

PROJECT_DIR="/opt/quickhire"
BACKEND_DIR="$PROJECT_DIR/quickhire-v2/backend"
FRONTEND_DIR="$PROJECT_DIR/quickhire-v2/frontend"
VENV_DIR="$BACKEND_DIR/venv"
PYTHON=python3.11

echo "=== Pulling latest code ==="
cd "$PROJECT_DIR"
git fetch origin main
git reset --hard origin/main

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

echo "=== Restarting backend ==="
systemctl restart quickhire

echo "=== Deploy complete ==="
