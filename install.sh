#!/bin/bash

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║         Outline RU Access - Installer              ║"
echo "║     VPN для доступа к российским ресурсам          ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Запустите скрипт от root: sudo ./install.sh"
  exit 1
fi

echo "📦 Устанавливаю Outline VPN..."
echo ""

# Install Outline
bash -c "$(wget -qO- https://raw.githubusercontent.com/Jigsaw-Code/outline-server/master/src/server_manager/install_scripts/install_server.sh)"

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║              ✅ Установка завершена!               ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "📱 Скачайте Outline Client: https://getoutline.org/get-started/"
echo "🔧 Скачайте Outline Manager: https://getoutline.org/get-started/#step-1"
echo ""
