#!/bin/bash
# QuickHire ECS 一次性初始化脚本 — 在服务器上只跑一次
set -e

PROJECT_DIR="/opt/quickhire"

echo "=== Installing nginx ==="
dnf install -y nginx

echo "=== Configuring nginx ==="
cp "$PROJECT_DIR/quickhire-v2/nginx.conf" /etc/nginx/conf.d/quickhire.conf
# 确保 nginx user 能访问项目
chown -R root:root "$PROJECT_DIR"
systemctl enable --now nginx

echo "=== Installing Node.js 20 ==="
dnf install -y nodejs20 || {
    # fallback: nodejs from nodesource
    curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
    dnf install -y nodejs
}

echo "=== Configuring systemd service ==="
cp "$PROJECT_DIR/quickhire-v2/backend/quickhire.service" /etc/systemd/system/
sed -i 's/User=www-data/User=root/' /etc/systemd/system/quickhire.service
systemctl daemon-reload
systemctl enable quickhire

echo "=== Creating .env from template ==="
if [ ! -f "$PROJECT_DIR/quickhire-v2/backend/.env" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/quickhire-v2/backend/.env"
    echo "!!! Please edit $PROJECT_DIR/quickhire-v2/backend/.env and add your API key !!!"
fi

echo "=== Setup complete ==="
echo "Next: edit .env with your API key, then trigger CI/CD"
