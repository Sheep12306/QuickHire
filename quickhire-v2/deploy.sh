#!/bin/bash
set -e

PROJECT_DIR="/opt/quickhire"
BACKEND_DIR="$PROJECT_DIR/quickhire-v2/backend"
FRONTEND_DIR="$PROJECT_DIR/quickhire-v2/frontend"
VENV_DIR="$BACKEND_DIR/venv"
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
# NOTE: dist/.user.ini is write-protected by Alibaba Cloud hosting panel.
# We set emptyOutDir: false in vite.config.js so vite overwrites in place.
npm ci --legacy-peer-deps
npm run build

echo "=== Restarting backend ==="
# Clear stale Python bytecode cache
find "$BACKEND_DIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "$BACKEND_DIR" -name "*.pyc" -delete 2>/dev/null || true
chown -R quickhire:quickhire "$BACKEND_DIR" 2>/dev/null || true
sudo systemctl restart quickhire 2>/dev/null || systemctl restart quickhire 2>/dev/null || {
    echo "WARNING: Could not restart quickhire service. Trying pkill..."
    sudo pkill -f "uvicorn main:app" 2>/dev/null || pkill -f "uvicorn main:app" 2>/dev/null || true
}

echo "=== Deploy complete ==="
