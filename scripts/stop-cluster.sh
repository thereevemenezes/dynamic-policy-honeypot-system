#!/usr/bin/env bash
set -euo pipefail

echo "[*] Stopping k3s cleanly..."
sudo systemctl stop k3s

echo "[+] k3s stopped. You can now shut down the VM with:"
echo "    sudo shutdown now"
